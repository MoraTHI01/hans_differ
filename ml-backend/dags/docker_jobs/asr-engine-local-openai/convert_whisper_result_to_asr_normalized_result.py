"""
Convert a whisper word level ASR result our ASR result normalized structure (transcript)
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


def text_contains_punctuation(text):
    """
    Remove punctuation and capitalization and convert to lower case
    """
    curr_text = text.strip()
    if curr_text.endswith("..."):
        return False
    return curr_text.endswith(".") or curr_text.endswith(":") or curr_text.endswith("!") or curr_text.endswith("?")


def create_segment(result_index):
    """
    Create a new segment
    """
    segment = {}
    segment["result_index"] = result_index
    segment["words_formatted"] = []
    segment["transcript_formatted"] = ""
    return segment


def main():
    """
    Convert a whisper word level ASR result our ASR result structure
    """
    args = parse_args()
    whisper_data = read_json_file(args.input_file)
    asr_result = {}
    asr_result["result"] = []
    asr_result["type"] = "AsrNormalizedResult"

    # Create final transcript or asr_result
    word_count = 0
    all_words = []
    for item in whisper_data["segments"]:
        for word in item["words"]:
            curr_word = {}
            curr_word["word"] = word["word"].lstrip()
            curr_word["interval"] = [word["start"], word["end"]]
            curr_word["index"] = word_count
            word_count = word_count + 1
            all_words.append(curr_word)

    result_index = 0

    # Reorg segments by sentence
    segment = create_segment(result_index)
    result_index = result_index + 1
    start = all_words[0]["interval"][0]
    segment["transcript_formatted"] = all_words[0]["word"]
    segment["words_formatted"].append(all_words[0])
    offset = 0
    word_arr_length = len(all_words)
    for index in range(1, word_arr_length):
        if index + offset < word_arr_length:
            segment["transcript_formatted"] = segment["transcript_formatted"] + " " + all_words[index + offset]["word"]
            segment["words_formatted"].append(all_words[index + offset])
            if (
                index + offset + 1 < word_arr_length
                and text_contains_punctuation(all_words[index + offset]["word"])
                and all_words[index + offset + 1]["word"].strip()[0]
                == all_words[index + offset + 1]["word"].strip()[0].upper()
            ):
                end = all_words[index + offset]["interval"][1]
                segment["interval"] = [start, end]
                asr_result["result"].append(segment)
                if index + offset + 1 < word_arr_length:
                    segment = create_segment(result_index)
                    result_index = result_index + 1
                    offset = offset + 1
                    start = all_words[index + offset]["interval"][0]
                    segment["transcript_formatted"] = all_words[index + offset]["word"]
                    segment["words_formatted"].append(all_words[index + offset])

    write_to_file(args.output_file, dump_json(asr_result))


if __name__ == "__main__":
    main()
