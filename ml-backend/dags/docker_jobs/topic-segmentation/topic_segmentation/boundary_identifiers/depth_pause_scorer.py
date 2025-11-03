from dataclasses import dataclass

from topic_segmentation.utils import normalize_scores
from topic_segmentation.boundary_identifiers.depth_scorer import DepthScorer, DepthScorerConfig


@dataclass
class DepthPauseScorerConfig(DepthScorerConfig):
    semantic_weight: float = 0.5


class DepthPauseScorer(DepthScorer):
    def __init__(self, config: DepthPauseScorerConfig):
        super().__init__(config)
        self.cfg = config
        self.alpha = self.cfg.semantic_weight  # weight for acoustic scores
        self.beta = 1 - self.alpha  # weight for pause scores

    def __call__(
        self, semantic_scores: list[float], pause_scores: list[float], compute_joint_score_first: bool = True
    ) -> list[int]:
        """
        Compute depth scores based on similarity scores and pause durations.

        Instead of considering the points with the lowest similarities,
        we compare the points with the highest similarity drops,
        considering the left and right context of the point.

        :param semantic_scores: inter sentence similarity scores
        :param pause_scores: inter sentence pause durations
        :param compute_joint_score_first: join scores before computing local maxima
        :return: depth scores (same length as input sim scores)
        """
        depth_scores = self._compute_depth_scores(semantic_scores)
        depth_scores = self._normalize_and_weight_scores(depth_scores, self.alpha)
        pause_scores = self._normalize_and_weight_scores(pause_scores, self.beta)
        if compute_joint_score_first:
            joint_scores = [d + pause_scores[n] for n, d in enumerate(depth_scores)]
            local_maxima = self._get_local_maxima(joint_scores)
            threshold = self._compute_threshold(joint_scores)
        else:
            local_maxima = self._get_local_maxima(depth_scores)
            local_maxima = [(n, lm + pause_scores[n]) for n, lm in local_maxima]  # add pause scores
            threshold = self._compute_combined_threshold(depth_scores, pause_scores)
        local_maxima_ids_filtered = [i for i, m in local_maxima if m >= threshold]
        return [1 if n in local_maxima_ids_filtered else 0 for n in range(len(depth_scores))]

    @staticmethod
    def _normalize_and_weight_scores(scores: list[float], weight: float) -> list[float]:
        """Normalize scores to [0;1] and reduce scores acc to weight"""
        return [weight * score for score in normalize_scores(scores)]

    def _compute_combined_threshold(self, depth_scores: list[float], pause_scores: list[float]) -> float:
        depth_threshold = self._compute_threshold(depth_scores)
        pause_threshold = self._compute_threshold(pause_scores)
        return depth_threshold + pause_threshold
