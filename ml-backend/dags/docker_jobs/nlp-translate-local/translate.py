"""
Translate llm output de <-> en
Input is a llm json prompt response:
{
    "generated_text" : ""
}
"""

import argparse
import sys
import json
import torch
from transformers import FSMTForConditionalGeneration, FSMTTokenizer
from utils import read_json_file, write_to_file, dump_json


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=str, help="Path to llm json file")
    parser.add_argument("-d", "--device", default="cpu", type=str, help="Device: 'cpu' or 'cuda'")
    parser.add_argument(
        "-l", "--language", default="de", type=str, help="Target langauge, default: 'de', values: 'de', 'en'"
    )
    parser.add_argument("-o", "--output-file", type=str, help="Path to output json TopicResult")
    return parser.parse_args()


def translate(tokenizer, model, text):
    """
    Translate text
    """
    input_ids = tokenizer.encode(text.strip(), return_tensors="pt")
    outputs = model.generate(input_ids)
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded.strip()


def main():
    """
    Compare kaldi word alignments with cleaned transcript txt file
    """
    args = parse_args()
    data = read_json_file(args.input_file)
    if not "type" in data:
        print("Error no type found!")
        exit(1)
    data["language"] = args.language.strip().lower()
    mname = "facebook/wmt19-en-de"
    if data["language"] == "de":
        mname = "facebook/wmt19-en-de"
    elif data["language"] == "en":
        mname = "facebook/wmt19-de-en"
    if args.device.lower() == "cuda":
        if not torch.cuda.is_available():
            print("Error cuda requested but cuda is not available!")
            exit(1)
    tokenizer = FSMTTokenizer.from_pretrained(mname)
    model = FSMTForConditionalGeneration.from_pretrained(mname)
    data_type = data["type"]
    print(f"LLM Datatype: {data_type}")
    if data_type == "TopicResult":
        print(f"Start translating {data_type}")
        for item in data["result"]:
            if "title" in item.keys():
                item["title"] = translate(tokenizer, model, item["title"])
            if "summary" in item.keys():
                item["summary"] = translate(tokenizer, model, item["summary"])
        print("Result")
        print(data)
        write_to_file(args.output_file, dump_json(data))
    elif data_type == "ShortSummaryResult" or data_type == "SummaryResult":
        print(f"Start translating {data_type}")
        for item in data["result"]:
            if "summary" in item.keys():
                item["summary"] = translate(tokenizer, model, item["summary"])
        print("Result")
        print(data)
        write_to_file(args.output_file, dump_json(data))
    else:
        print(f"Error wrong JSON type found! Type: {data_type}")
        exit(1)


if __name__ == "__main__":
    main()
