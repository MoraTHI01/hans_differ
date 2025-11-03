import argparse
from dataclasses import dataclass, asdict
import json

import webvtt

from topic_segmentation.segmenter import SemanticPauseSegmenter, SemanticPauseSegmenterConfig


@dataclass
class RawSegment:
    result_index: int
    interval: tuple[float, float]
    text: str

    def update_end(self, end: float):
        self.interval = (self.interval[0], end)


@dataclass
class TopicResultRaw:
    type: str = "TopicResultRaw"
    language: str = "UNK"
    result: list[RawSegment] | None = None


def run_topic_segmentation(
    sentences: list[str], intervals: list[tuple[float, float]], embedding_model: str, device: str
) -> TopicResultRaw:
    """Run unsupervised topic segmentation algorithm on transcript sentences."""
    pause_durations = [intervals[n + 1][0] - itv[1] for n, itv in enumerate(intervals[:-1])]

    config = SemanticPauseSegmenterConfig(model_id=embedding_model, device=device)
    segmenter = SemanticPauseSegmenter(config)
    segmentation = segmenter(sentences, pause_durations)

    segments = []
    idx = 0
    current_segment = None
    segmentation.append(1)  # add final boundary to segmentation to treat them as end markers
    for topic_end, sentence, interval in zip(segmentation, sentences, intervals):
        if current_segment is None:
            current_segment = RawSegment(result_index=idx, text=sentence, interval=interval)
        else:
            current_segment.text += f" {sentence}"
        if topic_end:
            current_segment.update_end(interval[1])
            segments.append(current_segment)
            current_segment = None
            idx += 1
    return TopicResultRaw(result=segments)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments when script is run."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=str, help="Path to the transcript .vtt file")
    parser.add_argument("-o", "--output-file", type=str, help="Path to output topic result .json file")
    parser.add_argument(
        "-m",
        "--embedding-model",
        type=str,
        help="Model to be used for embedding sentence, choose one from https://huggingface.co/sentence-transformers",
    )
    parser.add_argument("-d", "--device", default="cpu", type=str, help="Device: 'cpu' or 'cuda'")
    return parser.parse_args()


def main():
    args = parse_args()
    captions = webvtt.read(args.input_file)
    sentences = []
    intervals = []
    for n, caption in enumerate(captions):
        sentences.append(caption.text)
        intervals.append((caption.start_in_seconds, caption.end_in_seconds))
    if len(sentences) < 2:
        # If there is an empty transcript or only one sentence, segmentation does not make sense.
        # Treat transcript as one segment instead.
        text = " ".join(sentences)
        video_segment = RawSegment(result_index=0, text=text, interval=(intervals[0][0], intervals[-1][1]))
        topic_result = TopicResultRaw(result=[video_segment])
    else:
        topic_result = run_topic_segmentation(sentences, intervals, args.embedding_model, args.device)
    with open(args.output_file, "w", encoding="utf-8") as outp:
        json.dump(asdict(topic_result), outp, indent=2, ensure_ascii=False)
    print("Topic Segmentation done, file saved to", args.output_file)


if __name__ == "__main__":
    main()
