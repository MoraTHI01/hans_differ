#!/usr/bin/env python
"""
LLM remote operators.
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2023, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


from os import access
from urllib.request import urlopen
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
import requests
import json

# Specify minio version to be used in all PythonVirtualenvOperator
PIP_REQUIREMENT_MINIO = "minio"


def verify_llm_result(llm_response_json):
    """
    Verify llm result content
    """
    import json
    from airflow.exceptions import AirflowFailException

    if not "generated_text" in llm_response_json:
        raise AirflowFailException("Error no generated_text found!")
    elif "error" in llm_response_json:
        error = llm_response_json["error"]
        raise AirflowFailException(f"Error with the remote request occured! Error: {error}")
    return True


def parse_time_to_seconds(time_str):
    """
    Convert HH:MM:SS.MS to seconds
    """
    try:
        if time_str in ["00:00:00.000", "00:00:00", "00:00"]:
            return 0.0
        # Split the timestamp into hours, minutes, seconds, and milliseconds
        ms_c = time_str.count(".")
        sep_c = time_str.count(":")
        print(f"'.' detected: {ms_c}")
        print(f"':' detected: {sep_c}")
        days = 0.0
        hours = 0.0
        if sep_c == 3:
            days, time_str = time_str.split(":", 1)
        if sep_c >= 2 and ms_c > 0:
            hours, time_str = time_str.split(":", 1)

        milliseconds = 0.0
        if ms_c > 0:
            minutes, seconds, milliseconds = map(int, time_str.replace(".", ":").split(":"))
        elif sep_c == 2:
            hours, minutes, seconds = map(int, time_str.replace(".", ":").split(":"))
        elif sep_c == 1:
            minutes, seconds = map(int, time_str.replace(".", ":").split(":"))

        # Calculate total seconds
        total_seconds = float(
            int(days) * 86400 + int(hours) * 3600 + int(minutes) * 60 + int(seconds) + (int(milliseconds) / 1000.0)
        )
        return total_seconds
    except ValueError:
        raise ValueError("Invalid time format. Expected 'HH:MM:SS.MS'.")


def parse_timestamp(subtext):
    """
    Parse webvtt timestamp
    """
    from modules.operators.llm_remote import parse_time_to_seconds

    if "(" in subtext and ")" in subtext and subtext.count(":") > 0:
        text_arr = subtext.split("(")
        timestamp_found = False
        for elem in text_arr:
            if ":" in elem or "-->" in elem:
                timestamp = elem.strip().replace(")", "").replace(" ", "")
                print(f"timestamp: {timestamp}")
                if "-->" in timestamp:
                    start_time_text = timestamp.split("-->")[0].strip()
                else:
                    start_time_text = timestamp.strip()
                print(f"start_time_text: {start_time_text}")
                try:
                    seconds_s = parse_time_to_seconds(start_time_text)
                except ValueError:
                    seconds_s = None
                if seconds_s is not None:
                    timestamp_found = True
                    print(f"Converted timestamp in seconds: {seconds_s}")
                    return seconds_s
        if timestamp_found is False:
            print("Error converting timestamp!")
            exit(1)
    else:
        raise ValueError(f"Failed to parse webvtt timestamp from text: {subtext}")


def create_topic_result(llm_response_json):
    """
    Parses llm response and creates ShortSummaryResult
    """
    import json
    import re
    from airflow.exceptions import AirflowFailException
    from modules.operators.llm_remote import verify_llm_result
    from modules.operators.llm_remote import parse_timestamp

    if verify_llm_result(llm_response_json) is True:
        result = {"type": "TopicResult", "language": "en", "result": []}
        result_index = 0
        text = llm_response_json["generated_text"]
        text_arr = text.split("\\\\n")
        text_arr_length = len(text_arr)
        print(text_arr_length)
        print(text_arr)
        if text_arr_length == 1:
            text_arr[0] = text_arr[0].replace("\\n", "\n")
            text_arr = text_arr[0].split("\n")
            text_arr_length = len(text_arr)
        print(text_arr_length)
        print(text_arr)
        print("\nAnalyzing\n")
        pattern_numbering = r"^(\d+)\."

        # Check if the text matches the pattern
        result_item = {}
        start_found = False
        curr_time_s = None
        time_found = False
        curr_summary = ""
        for subtext in text_arr:
            subtext = subtext.strip()
            if len(subtext) > 0:
                print(f"Subtext: {subtext}")
                match_starts_numbering = re.match(pattern_numbering, subtext)
                if match_starts_numbering:
                    print(f"Numbering found: {subtext}")
                    try:
                        curr_time_s = parse_timestamp(subtext)
                        title = subtext.split("(")[0].strip()
                        if "*" in subtext:
                            curr_summary = subtext.split("*")[1].strip()
                        time_found = True
                    except ValueError:
                        curr_time_s = None
                        title = subtext.strip()

                    if "result_index" in result_item:
                        # Append previous result to final result
                        result_item["interval"][1] = curr_time_s
                        result["result"].append(result_item)
                        result_item = {}
                    result_item["result_index"] = result_index
                    result_item["interval"] = [0.0, 0.0]
                    if start_found is True and time_found is True:
                        result_item["interval"][0] = curr_time_s
                        time_found = False
                    elif time_found is True:
                        start_found = True
                        time_found = False
                    result_item["title"] = title
                    if len(curr_summary) > 0:
                        result_item["summary"] = curr_summary
                        curr_summary = ""
                    result_index = result_index + 1
                if "*" in subtext:
                    curr_summary = subtext.split("*")[1].strip()
                    result_item["summary"] = curr_summary
                    curr_summary = ""

        if "result_index" in result_item:
            # Append previous result to final result
            result_item["interval"][1] = 86400.0
            result["result"].append(result_item)

        print(f"Result: {result}")
        return result


def create_short_summary_result(llm_response_json):
    """
    Parses llm response and creates ShortSummaryResult
    """
    import json
    from airflow.exceptions import AirflowFailException
    from modules.operators.llm_remote import verify_llm_result

    if verify_llm_result(llm_response_json) is True:
        result = {"type": "ShortSummaryResult", "language": "en", "result": []}
        text = llm_response_json["generated_text"]
        text_arr = text.split("\\\\n")
        text_arr_length = len(text_arr)
        if text_arr_length == 1:
            text_arr = text_arr[0].split("\\n")
            text_arr_length = len(text_arr)
        print(text_arr_length)
        print(text_arr)
        print("\nAnalyzing\n")
        for subtext in text_arr:
            subtext = subtext.strip().replace("   ", " ").replace("  ", " ")
            if len(subtext) > 0:
                print(f"Subtext: {subtext}")
                result["result"].append({"result_index": 0, "summary": subtext})
        print(f"Result: {result}")
        return result


def create_summary_result(llm_response_json):
    """
    Parses llm response and creates ShortSummaryResult
    """
    import json
    from airflow.exceptions import AirflowFailException
    from modules.operators.llm_remote import verify_llm_result

    if verify_llm_result(llm_response_json) is True:
        result = {"type": "SummaryResult", "language": "en", "result": []}
        text = llm_response_json["generated_text"]
        text_arr = text.split("\\\\n", 1)
        text_arr_length = len(text_arr)
        if text_arr_length == 1:
            text_arr = text_arr[0].split("\\n", 1)
            text_arr_length = len(text_arr)
        print(text_arr_length)
        print(text_arr)
        print("\nAnalyzing\n")
        if text_arr_length > 1:
            title = text_arr[0].strip().replace("\\\\n\\\\n", "").strip()
            summary = text_arr[1].strip().replace("\\n", "", 1).replace("\\n\\n", "").strip()
            result["result"].append({"result_index": 0, "title": title, "summary": summary})
        else:
            for subtext in text_arr:
                subtext = subtext.strip().replace("   ", " ").replace("  ", " ")
                if len(subtext) > 0:
                    print(f"Subtext: {subtext}")
                    result["result"].append({"result_index": 0, "summary": subtext})
        print(f"Result: {result}")
        return result


def remove_initial_markers(text: str, markers: tuple[str, ...]) -> str:
    """Remove initial tokens which might be added by the LLM."""
    if text.split(":")[0].lower() in markers:
        return text.split(":", 1)[1].strip()
    return text


def remove_quotes(text: str) -> str:
    """Remove quotes if text is quoted like 'text'."""
    removal_ongoing = True
    while removal_ongoing:
        left, right = text[0], text[-1]
        if left == '"' and right == '"':
            text = text[1:-1]  # remove " quotes
        elif left == "'" and right == "'":
            text = text[1:-1]  # remove ' quotes
        else:  # no quotes found, stop removal
            removal_ongoing = False
    return text


def extend_topic_result(url: str, topic_result_data: dict, meta_data: dict) -> dict:
    """Extend raw topic result file with English topic summaries and titles."""

    def _request_and_post_process(mode: str, _text: str, max_tokens: int, rm_quotes: bool = False) -> str:
        prompt = create_llm_prompt(mode, _text, meta_data)
        llm_response_json = request_llm_service(url, prompt, max_tokens).json()
        verify_llm_result(llm_response_json)
        gen_text = llm_response_json["generated_text"]
        return gen_text.replace("\n", " ").strip()

    for n, segment in enumerate(topic_result_data["result"]):
        text = segment.pop("text")
        # 1. Generate topic summary
        summary = _request_and_post_process("topic_summary", text, 512)
        print("Topic summary generated by LLM:", summary)
        # 2. Generate topic title
        title = _request_and_post_process("topic_title", text, 64, rm_quotes=True)
        print("Topic title generated by LLM:", title)

        title = (
            remove_initial_markers(title, ("title")).replace("\\n", "").replace("''", "").replace("### ", "").strip()
        )
        title = remove_quotes(title)
        summary = remove_initial_markers(summary, ("summary", "text summary"))
        summary = remove_quotes(summary)

        print(f"Final title and summary:\n-> '{title}'\n-> '{summary}'")
        segment["title"] = title
        segment["summary"] = summary
    topic_result_data["type"] = "TopicResult"
    topic_result_data["language"] = "en"
    return topic_result_data


def create_questionnaire_result(mode, url: str, topic_result_data: dict, meta_data: dict) -> dict:
    """Extend raw topic result file with English topic summaries and titles."""
    from dataclasses import dataclass
    from typing import Optional, Union
    from pydantic import BaseModel, constr, conint, conlist
    import re

    # Classes to constrain LLM output

    class MultipleChoiceAnswer(BaseModel):
        index: conint(ge=0, lt=4)
        answer: constr(max_length=120)

    class MultipleChoiceQuestion(BaseModel):
        question: constr(max_length=240)
        answers: conlist(item_type=MultipleChoiceAnswer, min_length=4, max_length=4)
        correct_answer_index: conint(ge=0, lt=4)
        correct_answer_explanation: constr(max_length=512)

    # Result data classes

    @dataclass
    class RawSegment:
        result_index: int
        interval: tuple[float, float]
        text: str

    @dataclass
    class QuestionnaireResult:
        type: str = "QuestionnaireResult"
        language: str = "UNK"
        result: Optional[list[RawSegment]] = None

    def _request_and_post_process(
        mode: str, grade: str, _text: str, max_tokens: int, avoid: str = None, **kwargs
    ) -> str:
        print("***********************")
        print(f"input text: {_text}")
        print(f"avoid: {avoid}")
        prompt = create_llm_prompt(mode + "_" + grade, _text, meta_data, avoid)
        print(f"prompt: {prompt}")
        return request_llm_service(url, prompt, max_tokens, MultipleChoiceQuestion.model_json_schema(), **kwargs)

    quests_per_grade = 1
    seg_count = len(topic_result_data["result"])
    for n, segment in enumerate(topic_result_data["result"]):
        print(f"Segment: {n + 1}/{seg_count}", flush=True)
        text = segment.pop("text")
        # Generate questionnaires
        if not "questionnaire" in segment:
            segment["questionnaire"] = {"easy": [], "medium": [], "difficult": []}
        avoid = None
        for grade in ["easy", "medium", "difficult"]:
            print(f"Grade: {grade}", flush=True)
            quest_count = 0
            while quest_count < quests_per_grade:
                print(f"Text: {text}", flush=True)
                # Custom params - "Reduce creativity" for the LLM, since we need a parsable JSON format:
                #  - do_sample=False: Always generate the most probable next token instead of sampling
                #  - increase penalties for repetition and frequency
                #  - decrease max_tokens to force the model to be more concise when generating the JSON
                params = {"do_sample": False, "temperature": 0.15}
                questionnaire_resp = _request_and_post_process(mode, grade, text, 8192, avoid, **params)
                try:
                    llm_response_json = questionnaire_resp.json()
                    verify_llm_result(llm_response_json)
                    gen_text = llm_response_json["generated_text"].replace("\n", " ").strip()
                    print(f"gen_text: {gen_text}")
                    print(f"Topic questionnaire generated by LLM: {gen_text}", flush=True)
                    questionnaire = json.loads(gen_text.replace("\n", "").replace(" ?", "?").strip())
                except Exception as e2:
                    print(f"Error parsing question JSON: {e2}", flush=True)
                    print("-> Try another time with shortened text", flush=True)
                    text = shorten_transcript(text)
                    params["temperature"] = 0.15
                    params["frequency_penalty"] = 0.3
                    params["repetition_penalty"] = 1.2
                    questionnaire_resp = _request_and_post_process(mode, grade, text, 4096, avoid, **params).strip()
                    llm_response_json = questionnaire_resp.json()
                    verify_llm_result(llm_response_json)
                    gen_text = llm_response_json["generated_text"].replace("\n", " ").strip()
                    print(f"gen_text: {gen_text}")
                    print(f"Topic questionnaire generated by LLM: {gen_text}", flush=True)
                    questionnaire = json.loads(gen_text.replace("\n", "").replace(" ?", "?").strip())

                questionnaire["creator"] = "llm"
                questionnaire["editor"] = ""
                segment["questionnaire"][grade].append(
                    {"index": quest_count, "type": "mcq_one_correct", "mcq": questionnaire}
                )
                if avoid is None:
                    avoid = ""
                avoid += questionnaire["question"] + "\n"
                print(f"Generated question: {quest_count + 1}", flush=True)
                quest_count += 1

    topic_result_data["type"] = "QuestionnaireResult"
    topic_result_data["language"] = "en"
    return topic_result_data


def create_keywords_result(url: str, slides_text: str, slides_language: str, meta_data: dict) -> dict:
    """Create list of keywords using LLM prompt with enforced json schema."""
    from typing import List
    from pydantic import BaseModel
    import re

    class Keywords(BaseModel):
        keywords: List[str]

    # Prompt LLM
    slides_text = shorten_transcript(slides_text)
    prompt = create_llm_prompt("keywords", slides_text, meta_data)
    llm_params = {"do_sample": False, "repetition_penalty": 1.2, "frequency_penalty": 0.3}
    try:
        llm_response = request_llm_service(
            url, prompt, max_new_tokens=12288, schema=Keywords.model_json_schema(), **llm_params
        )
        llm_response_json = llm_response.json()
        verify_llm_result(llm_response_json)
        gen_text = llm_response_json["generated_text"]
        keywords = json.loads(gen_text)["keywords"]
        print("***** Keywords generated by LLM:", keywords)
    except Exception as e:
        print(f"Error parsing keywords JSON: {e}")
        print("-> Fallback to extracting the keywords from the generated text using regex")
        print(f"gen_text: {gen_text}")
        keyword_list = re.findall(r'"(.*?)"', gen_text.strip().replace("\\n", " "))
        keywords = [s for s in keyword_list if s != "keywords" and len(s) < 33]
        print("***** Keywords extracted by regex:", keywords)
    # Post-process keywords
    keywords = [kw.strip() for kw in keywords if 3 <= len(kw.strip()) <= 40]
    keywords = list(set(keywords))
    # Remove keywords that are part of the metadata
    title = meta_data["title"].lower()
    course = meta_data["description"]["course"].lower()
    faculty = meta_data["description"]["faculty"].lower()
    lecturer = meta_data["description"]["lecturer"].lower()
    lecturer_short = [p for p in lecturer.split() if p.lower().rstrip(".") not in ["prof", "dr"]]
    lecturer_short = " ".join(lecturer_short)
    university = meta_data["description"]["university"].lower()
    keywords = [
        kw for kw in keywords if kw.lower() not in [title, course, faculty, lecturer, lecturer_short, university]
    ]
    print("***** Post-processed keywords:", keywords)
    # Create keyword count dictionary (counts will be added later based on raw transcript)
    keyword_2_count = {kw: 0 for kw in keywords}
    keywords_result_data = dict()
    keywords_result_data["type"] = "KeywordsResult"
    keywords_result_data["language"] = slides_language
    keywords_result_data["keywords"] = keyword_2_count
    return keywords_result_data


def calc_token_len(text):
    """
    Give an approx. number of tokens
    """
    import tiktoken

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(text))
    return num_tokens


def tokenizers_normalize_text(text):
    """
    Normalize text using tokenizers
    """
    from tokenizers import normalizers
    from tokenizers.normalizers import NFD, StripAccents

    normalizer = normalizers.Sequence([NFD(), StripAccents()])
    return normalizer.normalize_str(text)


def remove_punctuation(text, punctuation='.!?"、。।，@<”,;¿¡&%#*~【】，…‥「」『』〝〟″⟨⟩♪・‹›«»～′$+="'):
    """
    Remove punctuation
    """
    for member in punctuation:
        text = text.replace(member, "")
    return text


def get_most_frequent_words(text):
    """
    Get most frequent words list
    """
    from collections import Counter

    freq = Counter(text.split())
    # print(freq)
    mc = freq.most_common(5)
    words = [item[0].lower() for item in mc]
    words.remove("-->")
    print(words)
    return words


def remove_most_frequent_words(text):
    """
    Removes stop words to lower final token size
    """
    from modules.operators.llm_remote import get_most_frequent_words

    freq_words = get_most_frequent_words(text)
    words = [word for word in text.split() if word.lower() not in freq_words]
    return " ".join(words).strip()


def remove_until_next_word(text):
    """
    Remove specific word until next word
    """
    import re

    # Define a regular expression pattern to match "-->" followed by any non-space characters
    pattern = r"^-->\s*"

    # Replace the pattern with an empty string to remove it until the next word
    result = re.sub(pattern, "", text)

    return result


def remove_sentences(text, val=7):
    """
    Remove every x sentences from text
    """
    import re

    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences_shrink = [item for i, item in enumerate(sentences) if (i + 1) % val != 0]
    return " ".join(sentences_shrink)


def remove_word(text, val=7):
    """
    Remove words x sentences from text
    """
    words = text.split(" ")
    words_shrink = [item for i, item in enumerate(words) if (i + 1) % val != 0]
    return " ".join(words_shrink)


def shorten_transcript(context_data: str) -> str:
    # shrink token size by removing stop words from text if approx. token size is too big
    print(f"context_data before ascii: {context_data}")
    context_data_tk_len = calc_token_len(context_data)
    print(f"Token length before ascii: {context_data_tk_len}")
    context_data = tokenizers_normalize_text(context_data).encode("ascii", "ignore").decode().replace("\n", " ")
    print(f"context_data ascii: {context_data}")
    context_data_tk_len = calc_token_len(context_data)
    print(f"Token length ascii: {context_data_tk_len}")

    token_limit = 20480  # 10240 7168 6120
    context_data_tk_len_prev = context_data_tk_len
    stop_now = False
    if context_data_tk_len > token_limit:
        while context_data_tk_len > token_limit and not stop_now:
            context_data = remove_sentences(context_data)
            context_data_tk_len = calc_token_len(context_data)
            print(f"Token length after remove sentences: {context_data_tk_len}")
            if context_data_tk_len_prev > context_data_tk_len:
                context_data_tk_len_prev = context_data_tk_len
            else:
                stop_now = True
    if stop_now is True:
        if context_data_tk_len > token_limit:
            while context_data_tk_len > token_limit:
                context_data = remove_word(context_data)
                context_data_tk_len = calc_token_len(context_data)
                print(f"Token length after remove sentences: {context_data_tk_len}")
    print(f"context_data final: {context_data}")
    context_data_tk_len = calc_token_len(context_data)
    print(f"Token length final: {context_data_tk_len}")
    return context_data


def create_llm_prompt(mode: str, context_data: str, meta_data: dict, avoid: str = None) -> str:
    title = meta_data["title"]
    course = meta_data["description"]["course"]
    context_sentence = f"strictly rely on the following video transcript: {context_data}"
    system_prompt = "### System:\\nYour name is HAnSi. HAnSi is an AI that follows instructions extremely well. Help as much as you can. Remember, be safe, and don't do anything illegal. You respond in English.\\n\\n"
    message = ""
    if mode == "summary":
        message = f"Create a text summary focussing on the lecture title '{course}' and the video title '{title}' omit newline and omit characters '!', '?', and '=' and {context_sentence}"
    elif mode == "short_summary":
        message = f"Create a text summary focussing on the lecture title '{course}' and the video title '{title}' omit newline and omit characters '!', '?', and '=' and {context_sentence} Shorten the summary to a maximum of 3 sentences containing the main topic."
    elif mode == "topic":
        message = f"Create chapter titles and subtitles from the provided video transcript of video '{title}' in relation to the lecture title '{course}' in chronological order together with the start time {context_sentence} Respond with all chapter titles and subtitles included in the video content together with the short summary and start time extracted from the previous transcript similar to the following example: 1. Introduction (00:00:00.000 --> 00:00:04.480) * The video discusses the historical-sociological development of industrialisation, where the epochs are becoming narrower and the division of epochs is coming closer. The video also talks about the bourgeois revolution and the German revolution, and how the state's freedom of action was limited after the Napoleonic wars. The video also touches on the ideas of democracy and the industrial revolution, and how the state's freedom of action was limited after the Napoleonic wars."
    elif mode == "topic_summary":
        message = (
            f"Generate a text summary for the following lecture transcript snippet: \\n'{context_data}'. \\n"
            f"Omit newline and omit characters '!', '?', and '='. "
            f"Shorten the summary to a maximum of 3 sentences containing the main topic."
            f"Your response should comprise only the generated summary, like in the following example:"
            f"The Industrial Revolution began in late 18th-century England, "
            f"introducing technologies like the steam engine. This shift transformed agrarian economies "
            f"into industrial powerhouses, reshaping global trade and society."
        )
    elif mode == "topic_title":
        message = (
            f"Generate a title for the following lecture transcript snippet: \\n'{context_data}'. \\n"
            f"Omit newline and omit characters '!', '?', and '='. "
            f"The title should be short and concise and addressing the main topic of the lecture transcript."
            f"Your response should comprise only the title, as in the following example: Industrial Revolution."
        )
    elif "questionnaire" in mode:
        difficulty = mode.rsplit("_")[-1]
        message = (
            f"Create a single {difficulty} difficult multiple choice question (max. 240 chars) with 4 short answers (max. 120 chars) with unique index from 0 to 3."
            f"Provide the correct answers associated index and a short explanation (max. 512 chars) as valid JSON without any newlines strictly following the schema."
            f"Use only the following text for the generation: \\n'{context_data}'. \\n"
            f"Avoid the following already generated questions: \\n'{avoid}'. \\n"
        )
    elif mode == "keywords":
        message = (
            f"Generate a list of keywords from the following lecture slides text: \\n'{context_data}'. \\n"
            "Omit newline and omit characters '!', '?', and '='. "
            "Your response should be in JSON format and contain a maximum of 50 elements in the keywords array, like in the following example:"
            '{"keywords": ["Industrial Revolution", "18th-century England", "steam engine", '
            '"agrarian economies", "industrial powerhouses", "global trade", "society"]}.'
        )
    else:
        raise AirflowFailException(f"Error: llm mode '{mode}' not supported!")
    return f"'{system_prompt}'### Human: '${message}'\\n\\n### Assistant:\\n"


def request_llm_service(url: str, prompt: str, max_new_tokens: int = 2048, schema=None, **kwargs):
    headers = {"Content-Type": "application/json"}
    if schema is None:
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_new_tokens, "temperature": 0.15}}
    else:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                # "response_format": {"type": "json_object", "schema": dict(schema)},
                "grammar": {"type": "json", "value": dict(schema)},
                "temperature": 0.15,
            },
        }
    if kwargs:
        print(f"Additional llm generation parameters set: {kwargs}")
    for param, value in kwargs.items():
        payload["parameters"][param] = value
    print(f"Sending request to llm: {url}")
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    print("Response status code:", response.status_code)
    print("Response content:", response.content)
    return response


def prompt_llm_remote(
    mode,
    context_data,
    context_data_key,
    download_data,
    download_meta_urn_key,
    upload_llm_result_data,
    upload_llm_result_urn_key,
    use_orchestrator=False,
):
    """
    Creates a remote request to a LLM using a specific prompt template mode.

    :param str mode: 'summary', 'short_summary', 'topic' or 'topic_summary'
    :param str asr_de_data: XCOM data containing URN for the asr_result_de.json.
    :param str asr_de_data_key: XCOM Data key to used to determine the URN for the asr_result_de.json.
    :param str asr_en_data: XCOM data containing URN for the asr_result_en.json.
    :param str asr_en_data_key: XCOM Data key to used to determine the URN for the asr_result_en.json.
    :param str asr_locale_data: XCOM Data which contains the asr locale.
    :param str asr_locale_key: XCOM Data key to used to determine the asr locale.
    :param str download_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.
    :param str upload_llm_result_data: XCOM data containing URN for the upload of the llm result to assetdb-temp
    :param str upload_llm_result_urn_key: XCOM Data key to used to determine the URN for the upload of the llm result.
    :param bool use_orchestrator: Orchestrator between client and llm: client <-> orchestrator <-> llm , default: False, values: True, False
    """
    import json
    import time
    import requests
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from modules.connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config, get_connection_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.llm_remote import calc_token_len, tokenizers_normalize_text, remove_sentences, remove_word
    from modules.operators.llm_remote import (
        create_short_summary_result,
        create_summary_result,
        extend_topic_result,
        create_questionnaire_result,
        create_keywords_result,
    )
    from modules.operators.llm_remote import shorten_transcript, create_llm_prompt, request_llm_service

    # Get llm remote config
    config = get_connection_config("llm_remote")
    llm_schema = config["schema"]
    llm_host = config["host"]
    llm_port = str(config["port"])

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider and connect assetdb_temp_connector
    connector_provider.configure({"assetdb_temp": assetdb_temp_config})
    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Load metadata File
    metadata_urn = get_data_from_xcom(download_data, [download_meta_urn_key])
    meta_response = assetdb_temp_connector.get_object(metadata_urn)
    if "500 Internal Server Error" in meta_response.data.decode("utf-8"):
        raise AirflowFailException()

    meta_data = json.loads(meta_response.data)
    meta_response.close()
    meta_response.release_conn()

    url_base = llm_schema + "://" + llm_host + ":" + llm_port
    if use_orchestrator is True:
        url_demand = url_base + "/demand_llm_service"
        url_info = url_base + "/info"
        # TODO: call demand and check availability with info until LLM is available
        url = url_base + "/llm_service/generate"
    else:
        url = url_base + "/generate"

    if mode == "topic_summary":
        # Load context files: topic result file
        topic_result_urn = get_data_from_xcom(context_data, [context_data_key])
        topic_result_response = assetdb_temp_connector.get_object(topic_result_urn)
        if "500 Internal Server Error" in topic_result_response.data.decode("utf-8"):
            raise AirflowFailException()
        topic_result_data = json.loads(topic_result_response.data)
        topic_result_response.close()
        topic_result_response.release_conn()

        data = extend_topic_result(url, topic_result_data, meta_data)
        mime_type = HansType.get_mime_type(HansType.TOPIC_RESULT_EN)
    elif mode == "questionnaire":
        # Load context files: topic result raw
        topic_result_urn = get_data_from_xcom(context_data, [context_data_key])
        topic_result_response = assetdb_temp_connector.get_object(topic_result_urn)
        if "500 Internal Server Error" in topic_result_response.data.decode("utf-8"):
            raise AirflowFailException()
        topic_result_data = json.loads(topic_result_response.data)
        topic_result_response.close()
        topic_result_response.release_conn()

        data = create_questionnaire_result(mode, url, topic_result_data, meta_data)
        mime_type = HansType.get_mime_type(HansType.QUESTIONNAIRE_RESULT_EN)
    elif mode == "keywords":
        # Load context files: slides meta data
        slides_meta_urn_base = get_data_from_xcom(context_data, [context_data_key])
        slides_meta_urn = slides_meta_urn_base + "/slides.meta.json"
        slides_meta_data = assetdb_temp_connector.get_object(slides_meta_urn)
        if "500 Internal Server Error" in slides_meta_data.data.decode("utf-8"):
            raise AirflowFailException()
        slides_meta_dict = json.loads(slides_meta_data.data)
        slides_meta_data.close()
        slides_meta_data.release_conn()
        print("***** Slides meta data:", slides_meta_dict)
        print("***** Slides meta data keys:", slides_meta_dict.keys())
        slides_words = slides_meta_dict["words"]
        slides_text = " ".join(slides_words)
        slides_language = slides_meta_dict["language"]
        data = create_keywords_result(
            url=url, slides_text=slides_text, slides_language=slides_language, meta_data=meta_data
        )
        mime_type = HansType.get_mime_type(HansType.KEYWORDS_RESULT)

    else:
        # Load context files: subtitles file
        context_urn = get_data_from_xcom(context_data, [context_data_key])
        context_response = assetdb_temp_connector.get_object(context_urn)
        if "500 Internal Server Error" in context_response.data.decode("utf-8"):
            raise AirflowFailException()
        context_data = str(context_response.data).replace("WEBVTT", "", 1).replace('"', "").replace("\\n", "\n")
        context_response.close()
        context_response.release_conn()

        context_data = shorten_transcript(context_data)
        prompt = create_llm_prompt(mode, context_data, meta_data)
        llm_response_json = request_llm_service(url, prompt, 512).json()
        # Store data
        data = None
        mime_type = None
        if mode == "summary":
            data = create_summary_result(llm_response_json)
            mime_type = HansType.get_mime_type(HansType.SUMMARY_RESULT_EN)
        elif mode == "short_summary":
            data = create_short_summary_result(llm_response_json)
            mime_type = HansType.get_mime_type(HansType.SHORT_SUMMARY_RESULT_EN)
        elif mode == "topic":
            data = create_topic_result(llm_response_json)
            mime_type = HansType.get_mime_type(HansType.TOPIC_RESULT_EN)
        else:
            raise AirflowFailException("Error mode not supported!")

    stream_bytes = BytesIO(json.dumps(data).encode("utf-8"))
    meta_minio = {}
    upload_llm_result_urn = get_data_from_xcom(upload_llm_result_data, [upload_llm_result_urn_key])
    (success, object_name) = assetdb_temp_connector.put_object(
        upload_llm_result_urn, stream_bytes, mime_type, meta_minio
    )
    if not success:
        print(f"Error uploading llm result for {mode} on url {upload_llm_result_urn} to assetdb-temp!")
        raise AirflowFailException()

    return json.dumps({"result": object_name})


def op_llm_remote_prompt(
    dag,
    dag_id,
    task_id_suffix,
    mode,
    context_data,
    context_data_key,
    download_data,
    download_meta_urn_key,
    upload_llm_result_data,
    upload_llm_result_urn_key,
    use_orchestrator=False,
):
    """
    Provides PythonVirtualenvOperator to request a LLM using a specific prompt template mode.

    :param DAG dag: Airflow DAG which uses the operator.
    :param str dag_id: The Airflow DAG id of the DAG where the operator is executed.
    :param str task_id_suffix: Suffix for the operator task_id.

    :param str mode: 'summary', 'short_summary' or 'topic_summary'
    :param str asr_de_data: XCOM data containing URN for the asr_result_de.json.
    :param str asr_de_data_key: XCOM Data key to used to determine the URN for the asr_result_de.json.
    :param str asr_en_data: XCOM data containing URN for the asr_result_en.json.
    :param str asr_en_data_key: XCOM Data key to used to determine the URN for the asr_result_en.json.
    :param str asr_locale_data: XCOM Data which contains the asr locale.
    :param str asr_locale_key: XCOM Data key to used to determine the asr locale.
    :param str download_data: XCOM data containing URN for the meta data.
    :param str download_meta_urn_key: XCOM Data key to used to determine the URN for the meta data.
    :param str upload_llm_result_data: XCOM data containing URN for the upload of the llm result to assetdb-temp
    :param str upload_llm_result_urn_key: XCOM Data key to used to determine the URN for the upload of the llm result.
    :param bool use_orchestrator: Orchestrator between client and llm: client <-> orchestrator <-> llm , default: False, values: True, False

    :return: PythonVirtualenvOperator Operator to create opensearch document on the assetdb-temp storage.
    """
    from modules.operators.xcom import gen_task_id

    return PythonVirtualenvOperator(
        task_id=gen_task_id(dag_id, "op_llm_remote_prompt", task_id_suffix),
        python_callable=prompt_llm_remote,
        op_args=[
            mode,
            context_data,
            context_data_key,
            download_data,
            download_meta_urn_key,
            upload_llm_result_data,
            upload_llm_result_urn_key,
            use_orchestrator,
        ],
        requirements=[PIP_REQUIREMENT_MINIO, "eval-type-backport", "tiktoken", "tokenizers==0.14.0", "pydantic"],
        python_version="3",
        dag=dag,
    )
