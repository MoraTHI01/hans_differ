"""
Convert a whisper word level ASR result our ASR result normalized structure (transcript)
"""

import argparse
from convert_helpers import read_json_file
from whisper.utils import format_timestamp


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input-file",
        default="uuid.wav.word.json",
        type=str,
        help="Input file whisper word level ASR json result",
    )
    parser.add_argument(
        "-o", "--output-file", default="uuid.json", type=str, help="Output file for converted ASR json result"
    )
    return parser.parse_args()


class AsrResultWriteVTT:
    extension: str = "vtt"
    always_include_hours: bool = False
    decimal_marker: str = "."

    def write_asr_result(self, result: dict, file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            print("WEBVTT\n", file=f)
            for start, end, text in self.iterate_result(result):
                print(f"{start} --> {end}\n{text}\n", file=f, flush=True)

    def iterate_result(self, result: dict):
        for segment in result["result"]:
            segment_start = self.asr_result_format_timestamp(segment["interval"][0])
            segment_end = self.asr_result_format_timestamp(segment["interval"][1])
            segment_text = segment["transcript_formatted"].strip().replace("-->", "->")

            if word_timings := segment.get("words", None):
                all_words = [timing["word"] for timing in word_timings]
                all_words[0] = all_words[0].strip()  # remove the leading space, if any
                last = segment_start
                for i, this_word in enumerate(word_timings):
                    start = self.asr_result_format_timestamp(this_word["interval"][0])
                    end = self.asr_result_format_timestamp(this_word["interval"][1])
                    if last != start:
                        yield last, start, segment_text

                    yield start, end, "".join(
                        [f"<u>{word}</u>" if j == i else word for j, word in enumerate(all_words)]
                    )
                    last = end

                if last != segment_end:
                    yield last, segment_end, segment_text
            else:
                yield segment_start, segment_end, segment_text

    def asr_result_format_timestamp(self, seconds: float):
        return format_timestamp(
            seconds=seconds, always_include_hours=self.always_include_hours, decimal_marker=self.decimal_marker
        )


def main():
    """
    Convert a whisper word level ASR result our ASR result structure
    """
    args = parse_args()
    asr_normalized_result_data = read_json_file(args.input_file)

    my_writer = AsrResultWriteVTT()
    my_writer.write_asr_result(result=asr_normalized_result_data, file_path=args.output_file)


if __name__ == "__main__":
    main()
