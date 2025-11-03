from dataclasses import dataclass

import numpy as np


@dataclass
class DepthScorerConfig:
    threshold: float | None = None
    threshold_mode: str = "std"  # one of ('std', 'var'), disregarded if threshold is provided


class DepthScorer:
    def __init__(self, config: DepthScorerConfig):
        self.cfg = config

    def __call__(self, sim_scores: list[float]):
        depth_scores = self._compute_depth_scores(sim_scores)
        local_maxima = self._get_local_maxima(depth_scores)
        threshold = self._compute_threshold(depth_scores)
        local_maxima_ids_filtered = [i for i, m in local_maxima if m >= threshold]
        return [1 if n in local_maxima_ids_filtered else 0 for n in range(len(depth_scores))]

    def _compute_threshold(self, scores: list[float]) -> float:
        if self.cfg.threshold is not None:
            return self.cfg.threshold * max(scores)
        adding_mode = np.std if self.cfg.threshold_mode == "std" else np.var
        return np.mean(scores) + adding_mode(scores)

    def _compute_depth_scores(self, scores: list[float]) -> list[float]:
        """
        Compute depth scores for similarity score sequence.

        Instead of considering the points with the lowest similarities,
        we can also compare the points with the highest similarity drops,
        considering the left and right context of the point
        :param scores: inter sentence similarity scores
        :return: depth scores (same length as input sim scores)
        """
        depth_scores = []
        for i, score in enumerate(scores):
            # the original start from a window of 1 here, which also allows for negative scores
            # this also seems to work better than restricting to scores >=0
            left_edge = i if i == 0 else i - 1  # for pos scores: i
            right_edge = i if i == len(scores) - 1 else i + 1  # for pos scores: i
            while left_edge > 0 and scores[left_edge - 1] > scores[left_edge]:
                # move edge to the left until the score decreases -^---___<i
                left_edge -= 1
            while right_edge < len(scores) - 1 and scores[right_edge + 1] > scores[right_edge]:
                # move edge to the right until the score decreases i>___---^-
                right_edge += 1
            depth_score = (scores[left_edge] - score) + (scores[right_edge] - score)
            depth_scores.append(depth_score)
        return depth_scores

    def _get_local_maxima(self, scores: list[float]) -> list[tuple[int, float]]:
        """
        Go through (depth) scores and take only those (incl. index),
        that are higher than their direct neighbors
        :param scores:
        :return: list of (score_index, score)
        """
        local_maxima = []
        for i, score in enumerate(scores):
            is_higher_then_left = True if i == 0 else score > scores[i - 1]
            is_higher_then_right = True if i == len(scores) - 1 else score > scores[i + 1]
            if is_higher_then_left and is_higher_then_right:
                local_maxima.append((i, score))
        return local_maxima
