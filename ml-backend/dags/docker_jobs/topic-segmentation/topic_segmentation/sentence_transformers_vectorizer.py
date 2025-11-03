import torch

from sentence_transformers import SentenceTransformer


class SentenceTransformersVectorizer:
    def __init__(self, model_id: str, device: str = "cpu"):
        self._model_id = model_id
        self._device = device
        print(f"SentenceTransformerVectorizer: use '{self._device}' for encoding sentences")
        self._model = SentenceTransformer(self._model_id, device=self._device)

    def __call__(self, sentences: list[str]) -> torch.Tensor:
        """
        Embed sentences to vectors of fixed size.

        :param sentences: list of sentences as strings
        :return: torch tensor (num_sentences * embedding_dim)
        """
        embeddings = self._model.encode(sentences, convert_to_tensor=True, device=self._device)
        return embeddings if self._device == "cpu" else embeddings.detach().cpu()
