from dataclasses import dataclass

from topic_segmentation.sentence_transformers_vectorizer import SentenceTransformersVectorizer
from topic_segmentation.window_embedder import WindowEmbedderConfig, WindowEmbedder
from topic_segmentation.inter_sentence_scorer import InterSentenceScorerConfig, InterSentenceScorer
from topic_segmentation.boundary_identifiers.depth_pause_scorer import DepthPauseScorer, DepthPauseScorerConfig


@dataclass
class SemanticPauseSegmenterConfig:
    """
    Config class for Semantic Pause Scorer, incl. defaults.

    :param model_id: Pre-trained model for sentence encoding, see https://huggingface.co/sentence-transformers
    :param window_embedder_config: Config for window embeddings
    :param inter_sentence_scorer_config: Config for inter sentence scorer
    :param depth_scorer_config: Config for depth scorer (boundary detection)
    """

    model_id: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    device: str = "cpu"
    window_embedder_config: WindowEmbedderConfig = WindowEmbedderConfig()
    inter_sentence_scorer_config: InterSentenceScorerConfig = InterSentenceScorerConfig()
    depth_scorer_config: DepthPauseScorerConfig = DepthPauseScorerConfig()


class SemanticPauseSegmenter:
    """
    Segmenter algorithm based on semantic sentence embedding and pause scores.

    Paper introducing algorithm (without pause score): https://arxiv.org/abs/2106.12978
    Sentence embedding models from: https://huggingface.co/sentence-transformers

    :param config: Semantic pause segmenter config incl. defaults
    """

    def __init__(self, config: SemanticPauseSegmenterConfig):
        self.cfg = config
        self.vectorizer = SentenceTransformersVectorizer(self.cfg.model_id, self.cfg.device)
        self.window_embedder = WindowEmbedder(self.cfg.window_embedder_config)
        self.inter_sentence_scorer = InterSentenceScorer(self.cfg.inter_sentence_scorer_config)
        self.depth_scorer = DepthPauseScorer(self.cfg.depth_scorer_config)

    def __call__(self, sentences: list[str], pause_durations: list[float]) -> list[int]:
        """
        Perform segmentation on sentences and return inter sentence boundary labels.

        :param sentences: sentences of transcript to be segmented into thematically coherent blocks
        :param pause_durations: list of pause durations (in seconds) between sentences
        :return: list of inter sentence boundary labels; 0: no change, 1: change
        """
        embeddings = self.vectorizer(sentences)
        context_pairs = self.window_embedder(embeddings, sentences)
        semantic_scores = self.inter_sentence_scorer(context_pairs)
        return self.depth_scorer(semantic_scores, pause_durations)
