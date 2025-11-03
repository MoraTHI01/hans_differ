"""
Preload translation models
"""

import time
import sys
import json
from transformers import FSMTForConditionalGeneration, FSMTTokenizer


def main():
    """
    Preload translation models
    """
    mnames = ["facebook/wmt19-en-de", "facebook/wmt19-de-en"]
    tests = ["Machine learning is great, isn't it?", "Wie großartig ist maschinelles Lernen?"]
    for i in range(0, 2):
        mname = mnames[i]
        tokenizer = FSMTTokenizer.from_pretrained(mname)
        model = FSMTForConditionalGeneration.from_pretrained(mname)
        input = tests[i]
        input_ids = tokenizer.encode(input, return_tensors="pt")
        outputs = model.generate(input_ids)
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(decoded)


if __name__ == "__main__":
    main()
