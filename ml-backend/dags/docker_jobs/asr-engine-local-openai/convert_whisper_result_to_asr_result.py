"""
Convert a whisper word level ASR result our ASR result structure
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
        "-m",
        "--model",
        default="large-v2",
        type=str,
        help="Model used to create the whisper word level ASR result json file",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="en",
        type=str,
        help="Language used for the model to create the whisper word level ASR result json file",
    )
    parser.add_argument("-v", "--version", default="0815", type=str, help="Whisper package version")
    parser.add_argument(
        "-o", "--output-file", default="uuid.json", type=str, help="Output file for converted ASR json result"
    )
    return parser.parse_args()


def normalize_text(text):
    """
    Remove punctuation and capitalization and convert to lower case
    """
    return "".join(c for c in text if c not in ".,;:!?").lower().lstrip()


def main():
    """
    Convert a whisper word level ASR result our ASR result structure
    """
    args = parse_args()
    whisper_data = read_json_file(args.input_file)
    asr_result = {}
    asr_result["result"] = []
    asr_result["type"] = "AsrResult"
    asr_result["meta"] = {
        "asr_model": {"model": args.model, "language": args.language, "license_type": "MIT"},
        "engine": {"name": "whisper", "version": args.version, "license_type": "MIT"},
    }

    word_count = 0

    # Create final transcript or asr_result
    transcript_entry = "transcript"
    words_entry = "words"

    result_index = 0
    for item in whisper_data["segments"]:
        segment = {}
        segment["interval"] = [item["start"], item["end"]]
        segment[transcript_entry] = item["text"].lstrip()
        segment[transcript_entry] = normalize_text(segment[transcript_entry])

        segment["result_index"] = result_index
        result_index = result_index + 1

        # segment["confidence"] = item["probability"]
        segment[words_entry] = []
        for word in item["words"]:
            curr_word = {}
            curr_word["interval"] = [word["start"], word["end"]]
            curr_word["word"] = word["word"].lstrip()
            curr_word["word"] = normalize_text(curr_word["word"])
            curr_word["index"] = word_count
            curr_word["confidence"] = word["probability"]
            segment[words_entry].append(curr_word)
            word_count = word_count + 1
        asr_result["result"].append(segment)

    write_to_file(args.output_file, dump_json(asr_result))


if __name__ == "__main__":
    main()
