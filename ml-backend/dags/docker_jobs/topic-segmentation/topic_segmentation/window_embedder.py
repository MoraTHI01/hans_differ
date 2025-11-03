from dataclasses import dataclass

import torch


@dataclass
class WindowEmbedderConfig:
    window_size: int = 12
    pool_method: str = "avg"  # one of ("avg", "max")
    pad_vector: str | None = "mean"  # one of (None, "mean")
    pad_share: float = 0.5
    use_weighted_avg: bool = False  # Avg sentences with weights depending on the length of the sentences


class WindowEmbedder:
    def __init__(self, config: WindowEmbedderConfig):
        self.cfg = config
        if self.cfg.pool_method == "avg":
            self.pool_method = torch.nn.AvgPool2d
        elif self.cfg.pool_method == "max":
            self.pool_method = torch.nn.MaxPool2d
            if self.cfg.use_weighted_avg:
                raise ValueError(f"Max pooling cannot be used together with weighted average")
        else:
            raise ValueError(f"Pool method '{self.cfg.pool_method}' not valid, choose one of ('max', 'avg')")

    def __call__(self, embeddings: torch.Tensor, sentences: list[str]) -> list[tuple[torch.Tensor, torch.Tensor]]:
        """
        Create context embedding pairs based on sentence embeddings.

        :param embeddings: tensor matrix of sentence embeddings (num_sentences * embedding_dim)
        :param sentences: list of sentences, corresponding to embeddings
        :return: pairs of context embeddings (left_context_tensor, right_context_tensor)
        """
        num_sentences, embedding_dim = embeddings.size()
        pad_vector = torch.mean(embeddings, dim=0, keepdim=True)
        if self.cfg.use_weighted_avg:
            sent_lens = [len(s.split()) for s in sentences]
        context_pairs = []
        for n in range(num_sentences - 1):
            left_edge_idx = max(0, n - self.cfg.window_size + 1)
            left_context = embeddings[left_edge_idx : n + 1]
            left_edged = left_context.size(0) < self.cfg.window_size
            if left_edged:
                left_context = self._pad_context(left_context, pad_vector)

            right_edge_idx = min(num_sentences, n + self.cfg.window_size + 1)
            right_context = embeddings[n + 1 : right_edge_idx]
            if right_context.size(0) < self.cfg.window_size:
                right_context = self._pad_context(right_context, pad_vector)

            if self.cfg.use_weighted_avg:
                left_sent_lens = sent_lens[left_edge_idx : n + 1]
                right_sent_lens = sent_lens[n + 1 : right_edge_idx]
                left_vector = self._create_weighted_avg_vector(left_context, left_sent_lens, left_edged)
                right_vector = self._create_weighted_avg_vector(right_context, right_sent_lens, left_edged)
            else:
                left_vector = self._create_pooled_vector(left_context)
                right_vector = self._create_pooled_vector(right_context)
            context_pairs.append((left_vector, right_vector))
        return context_pairs

    def _pad_context(self, context: torch.Tensor, pad_vector: torch.Tensor) -> torch.Tensor:
        num_pads = int(self.cfg.pad_share * (self.cfg.window_size - context.size(0)))
        return torch.cat([context] + [pad_vector] * num_pads, dim=0)

    def _create_pooled_vector(self, context: torch.Tensor) -> torch.Tensor:
        pooling = self.pool_method((context.size(0), 1))
        pooled = pooling(context.unsqueeze(0))
        return pooled.view(pooled.size(2))

    @staticmethod
    def _create_weighted_avg_vector(context: torch.Tensor, sent_lens: list[int], left_edged: bool) -> torch.Tensor:
        if len(sent_lens) < context.size(0):
            avg_sent_len = sum(sent_lens) / len(sent_lens)
            if left_edged:
                sent_lens = [avg_sent_len] * (context.size(0) - len(sent_lens)) + sent_lens
            else:
                sent_lens += [avg_sent_len] * (context.size(0) - len(sent_lens))
        weights = torch.tensor(sent_lens) / sum(sent_lens)
        weighted = weights @ context
        return weighted
