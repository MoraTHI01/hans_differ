#!/usr/bin/env python
"""
Convert a mod9 raw asr result to asr_result.json
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import sys
import json


options = sys.argv
x = len(options)

if x < 5:
    print("Error: Not enough parameters!")
    print("Usage:")
    print(
        "  python3 convert_to_asr_result.py <input-file> <asr-engine-info-file> <asr-model-info-file> <used-asr-model> <output-file>"
    )
    print("Example:")
    print(
        "  python3 convert_to_asr_result.py 'asr_result_raw.json' 'asr_engine_info.json' 'asr_model_info.json' 'en_video' 'asr_result.json'"
    )
else:
    input_file = options[1]
    asr_engine_info = options[2]
    asr_model_info = options[3]
    asr_model_used = options[4]
    output_file = options[5]

    result = {"type": "AsrResult", "result": [], "meta": {"engine": {"name": "mod9"}, "asr_model": asr_model_used}}

    file1 = open(input_file, "r", encoding="UTF-8")
    Lines = file1.readlines()
    for line in Lines:
        data = json.loads(line.strip())
        if "transcript" in data:
            result["result"].append(data)
        elif "status" in data:
            result["meta"]["status"] = data["status"]
    file1.close()

    file2 = open(asr_engine_info, "r", encoding="UTF-8")
    Lines = file2.readlines()
    for line in Lines:
        data = json.loads(line.strip())
        if "version" in data:
            result["meta"]["engine"]["version"] = data["version"]
        if "hostname" in data:
            result["meta"]["engine"]["hostname"] = data["hostname"]
        if "build" in data:
            result["meta"]["engine"]["build"] = data["build"]
        if "license_type" in data:
            result["meta"]["engine"]["license_type"] = data["license_type"]
    file2.close()

    file3 = open(asr_model_info, "r", encoding="UTF-8")
    Lines = file3.readlines()
    for line in Lines:
        data = json.loads(line.strip())
        if "asr_models" in data:
            asr_models = data["asr_models"]
            for item in asr_models:
                if "name" in item:
                    if item["name"] == asr_model_used:
                        result["meta"]["asr_model_info"] = item
    file3.close()

    with open(output_file, "w", encoding="UTF-8") as fp:
        fp.writelines(json.dumps(result, indent=4))
