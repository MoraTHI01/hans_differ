from dataclasses import dataclass

import scipy
import torch
import numpy as np
from sentence_transformers import util


@dataclass
class InterSentenceScorerConfig:
    similarity_measure: str = "cosine"  # one of ('cosine', 'dot', 'euclidean')
    smooth_scores: bool = True
    num_smooth_rounds: int = 2
    smoothing_width: int = 1


class InterSentenceScorer:
    def __init__(self, config: InterSentenceScorerConfig):
        self.cfg = config
        if config.similarity_measure == "cosine":
            self.similarity_metric = util.cos_sim
        elif config.similarity_measure == "dot":
            self.similarity_metric = util.dot_score
        elif config.similarity_measure == "euclidean":
            self.similarity_metric = scipy.spatial.distance.euclidean
        else:
            raise ValueError(
                (
                    f"Similarity metric '{config.similarity_measure}' not valid, "
                    f"choose one of ('cosine', 'dot', 'euclidean')"
                )
            )

    def __call__(self, context_pairs: list[tuple[torch.Tensor, torch.Tensor]]) -> list[float]:
        """
        Calculate inter sentence similarity scores based on context embedding pairs.

        :param context_pairs: pairs of (left_context, right_context) embeddings
        :return: similarity scores of left and right contexts
        """
        sim_scores = []
        for right, left in context_pairs:
            sim_score = self.similarity_metric(right, left)
            sim_scores.append(float(sim_score))
        if self.cfg.smooth_scores:
            sim_scores = self._smooth(sim_scores)
        return sim_scores

    def _smooth(self, scores: list[float]) -> list[float]:
        for _ in range(self.cfg.num_smooth_rounds):
            scores = self._run_smoothing_round(scores)
        return scores

    def _run_smoothing_round(self, scores) -> list[float]:
        smoothed_scores = []
        for i in range(len(scores)):
            left_edge = max(0, i - self.cfg.smoothing_width)
            right_edge = min(len(scores), i + self.cfg.smoothing_width + 1)
            window = scores[left_edge:right_edge]
            smoothed_scores.append(np.mean(window).item())
        assert len(scores) == len(smoothed_scores)
        return smoothed_scores
