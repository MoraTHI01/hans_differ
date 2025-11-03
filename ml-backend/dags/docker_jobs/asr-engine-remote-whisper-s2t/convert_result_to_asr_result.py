"""
Convert combined word level combined result to our ASR result structure
"""

import argparse
from convert_helpers import dump_json, read_json_file, write_to_file


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


def main():
    """
    Convert a whisper-s2t word level combined ASR result our ASR result structure
    """
    args = parse_args()
    asr_combined_result_data = read_json_file(args.input_file)
    asr_result = {}
    asr_result["result"] = []
    asr_result["type"] = "AsrResult"
    asr_result["meta"] = asr_combined_result_data["meta"]

    for item in asr_combined_result_data["result"]:
        segment = {}
        segment["result_index"] = item["result_index"]
        segment["interval"] = item["interval"]
        segment["transcript"] = item["transcript"]
        segment["confidence"] = item["confidence"]
        segment["words"] = item["words"]
        asr_result["result"].append(segment)

    write_to_file(args.output_file, dump_json(asr_result))


if __name__ == "__main__":
    main()
