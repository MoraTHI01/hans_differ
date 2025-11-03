def normalize_scores(scores: list[float]) -> list[float]:
    """
    Normalize scores in [0;1] using zi = (xi – min(x)) / (max(x) – min(x))
    Lowest value will be transformed to 0, highest to 1.

    :param scores: list of scores to be normalized
    :return: list of normalized scores in [0;1]
    """
    max_score = max(scores)
    min_score = min(scores)
    if max_score == min_score:
        print(f"Scores not meaningful, since they all have the same values, return values of 0.5")
        return [0.5 for _ in range(len(scores))]
    return [(s - min_score) / (max_score - min_score) for s in scores]
