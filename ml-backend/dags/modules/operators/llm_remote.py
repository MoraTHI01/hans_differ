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


def verify_llm_result(response):
    """
    Verify llm result content
    """
    from airflow.exceptions import AirflowFailException

    if response and len(response) < 1:
        raise AirflowFailException("Error no text length is 0!")
    elif response is None:
        raise AirflowFailException(f"Error with the remote request occured!")
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


def create_topic_result(llm_response):
    """
    Parses llm response and creates ShortSummaryResult
    """
    import json
    import re
    from airflow.exceptions import AirflowFailException
    from modules.operators.llm_remote import verify_llm_result
    from modules.operators.llm_remote import parse_timestamp

    if verify_llm_result(llm_response) is True:
        result = {"type": "TopicResult", "language": "en", "result": []}
        result_index = 0
        text = llm_response
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


def create_short_summary_result(llm_response):
    """
    Parses llm response and creates ShortSummaryResult
    """
    import json
    from airflow.exceptions import AirflowFailException
    from modules.operators.llm_remote import verify_llm_result

    if verify_llm_result(llm_response) is True:
        result = {"type": "ShortSummaryResult", "language": "en", "result": []}
        text = llm_response
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


def create_summary_result(llm_response):
    """
    Parses llm response and creates ShortSummaryResult
    """
    import json
    from airflow.exceptions import AirflowFailException
    from modules.operators.llm_remote import verify_llm_result

    if verify_llm_result(llm_response) is True:
        result = {"type": "SummaryResult", "language": "en", "result": []}
        text = llm_response
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


def extend_topic_result(llm_connector, prompt_base, topic_result_data: dict, meta_data: dict) -> dict:
    """Extend raw topic result file with English topic summaries and titles."""
    from llm.helpers import remove_initial_markers, remove_quotes

    def _request_and_post_process(
        llm_connector, prompt_base, mode: str, _text: str, max_tokens: int, rm_quotes: bool = False
    ) -> str:
        custom_config = {}
        custom_config["max_new_tokens"] = max_tokens
        messages = create_llm_messages(prompt_base, mode, _text, meta_data)
        gen_text = llm_connector.query_llm(messages=messages, custom_config=custom_config)
        # gen_text = gen_text.replace("\n", " ").replace("\\n", " ").strip()
        print(f"gen_text: {gen_text}")
        if len(gen_text) < 1:
            print(f"Empty gen_text for input text: {_text}")
            custom_config = {}
            custom_config["temperature"] = 0.0
            custom_config["frequency_penalty"] = 0.3
            messages = create_llm_messages(prompt_base, mode, _text, meta_data)
            gen_text = llm_connector.query_llm(messages=messages, custom_config=custom_config)
            # gen_text = gen_text.replace("\n", " ").strip()
        return gen_text

    for n, segment in enumerate(topic_result_data["result"]):
        text = segment.pop("text")
        # 1. Generate topic summary
        summary = _request_and_post_process(llm_connector, prompt_base, "topic_summary", text, 512)
        print("Topic summary generated by LLM:", summary)
        # 2. Generate topic title
        title = _request_and_post_process(llm_connector, prompt_base, "topic_title", text, 64, rm_quotes=True)
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


def create_questionnaire_result(llm_connector, prompt_base, mode, topic_result_data: dict, meta_data: dict) -> dict:
    """Extend raw topic result file with English topic summaries and titles."""
    from dataclasses import dataclass
    from typing import Optional, Union
    from pydantic import BaseModel, constr, conint, conlist
    from llm.helpers import shorten_transcript

    def _request_and_post_process(
        llm_connector, prompt_base, mode: str, grade: str, _text: str, custom_config: dict = {}, avoid: str = None
    ) -> str:
        import json
        from llm.schema_base import MultipleChoiceQuestion

        print("***********************")
        print(f"input text: {_text}")
        print(f"avoid: {avoid}")
        messages = create_llm_messages(prompt_base, mode + "_" + grade, _text, meta_data, avoid)
        print(f"messages: {messages}")
        response = llm_connector.query_llm(
            messages=messages, schema=MultipleChoiceQuestion.model_json_schema(), custom_config=custom_config
        )
        return json.loads(response)

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
                try:
                    questionnaire = _request_and_post_process(llm_connector, prompt_base, mode, grade, text, {}, avoid)
                    print(f"Topic questionnaire generated by LLM: {questionnaire}", flush=True)
                except Exception:
                    print("-> Try another time with shortened text", flush=True)
                    text = shorten_transcript(text, model_id=llm_connector.llm_model_id)
                    #  - do_sample=False: Always generate the most probable next token instead of sampling
                    #  - decrease max_tokens to force the model to be more concise when generating the JSON
                    custom_config = {}
                    custom_config["temperature"] = 0.0
                    custom_config["frequency_penalty"] = 0.3
                    custom_config["max_new_tokens"] = 4096
                    questionnaire = _request_and_post_process(
                        llm_connector, prompt_base, mode, grade, text, custom_config, avoid
                    )
                    print(f"Topic questionnaire generated by LLM: {questionnaire}", flush=True)

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


def create_keywords_result(llm_connector, prompt_base, slides_text: str, slides_language: str, meta_data: dict) -> dict:
    """Create list of keywords using LLM prompt with enforced json schema."""
    from typing import List
    from pydantic import BaseModel
    from llm.helpers import shorten_transcript
    import re
    import json

    class Keywords(BaseModel):
        keywords: List[str]

    # Prompt LLM
    slides_text = shorten_transcript(slides_text, model_id=llm_connector.llm_model_id)
    messages = create_llm_messages(prompt_base, "keywords", slides_text, meta_data)
    #  - do_sample=False: Always generate the most probable next token instead of sampling
    custom_config = {}
    custom_config["temperature"] = 0.0
    custom_config["max_new_tokens"] = 12288
    response = ""
    try:
        response = llm_connector.query_llm(
            messages=messages, schema=Keywords.model_json_schema(), custom_config=custom_config
        )
        response_json = json.loads(response)
        keywords = response_json["keywords"]
        print("***** Keywords generated by LLM:", keywords)
    except Exception as e:
        print(f"Error parsing keywords JSON: {e}")
        print("-> Fallback to extracting the keywords from the generated text using regex")
        print(f"gen_text: {response}")
        keyword_list = re.findall(r'"(.*?)"', response.strip().replace("\\n", " "))
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


def create_llm_messages(
    prompt_base, mode: str, context_data: str, meta_data: dict, avoid: str = None
) -> list[dict[str, str]]:
    from llm.helpers import gen_messages

    title = meta_data["title"]
    course = meta_data["description"]["course"]
    lang = "en"
    context_sentence = prompt_base.get_context_sentence(context_data, lang=lang)
    system_prompt = prompt_base.get_short_system_prompt(lang=lang) + prompt_base.get_force_language_english_addon(
        lang=lang
    )

    user_prompt = ""
    if mode == "summary":
        user_prompt = prompt_base.get_summary_prompt(title, course, context_sentence, lang=lang)
    elif mode == "short_summary":
        user_prompt = prompt_base.get_short_summary_prompt(title, course, context_sentence, lang=lang)
    elif mode == "topic":
        user_prompt = prompt_base.get_topic_prompt(title, course, context_sentence, lang=lang)
    elif mode == "topic_summary":
        user_prompt = prompt_base.get_topic_summary_prompt(context_data, lang=lang)
    elif mode == "topic_title":
        user_prompt = prompt_base.get_topic_title_prompt(context_data, lang=lang)
    elif "questionnaire" in mode:
        difficulty = mode.rsplit("_")[-1]
        avoid_enabled = False
        if avoid and len(avoid) > 0:
            avoid_enabled = True
        user_prompt = prompt_base.get_questionaire_prompt(difficulty, context_data, avoid_enabled, avoid, lang=lang)
    elif mode == "keywords":
        user_prompt = prompt_base.get_keywords_prompt(context_data, lang=lang)
    else:
        raise AirflowFailException(f"Error: llm mode '{mode}' not supported!")
    return gen_messages(system_prompt=system_prompt, user_prompt=user_prompt, context_sentence=context_sentence)


def prompt_llm_remote(
    mode,
    context_data,
    context_data_key,
    download_data,
    download_meta_urn_key,
    upload_llm_result_data,
    upload_llm_result_urn_key,
    llm_configs={},
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
    :param dict llm_configs: Configurations for all llm models
    """
    import json
    import time
    import requests
    from io import BytesIO
    from airflow.exceptions import AirflowFailException
    from connectors.connector_provider import connector_provider
    from modules.operators.connections import get_assetdb_temp_config, get_connection_config
    from modules.operators.transfer import HansType
    from modules.operators.xcom import get_data_from_xcom
    from modules.operators.llm_remote import (
        create_short_summary_result,
        create_summary_result,
        extend_topic_result,
        create_questionnaire_result,
        create_keywords_result,
    )
    from modules.operators.llm_remote import create_llm_messages
    from llm.prompt_base import PromptBase
    from llm.helpers import shorten_transcript

    # llm model and engine configuration
    prompt_base = PromptBase()

    # Get llm remote config
    llm_remote_config = get_connection_config("llm_remote")
    llm_remote_config["llm_task"] = llm_configs["llm_task"]
    llm_remote_config["llm_model_id"] = llm_configs["llm_model_id"]

    # Get assetdb-temp config from airflow connections
    assetdb_temp_config = get_assetdb_temp_config()

    # Configure connector_provider
    connector_provider.configure({"assetdb_temp": assetdb_temp_config, "llm_remote_config": llm_remote_config})
    # Connect to assetdb temp
    assetdb_temp_connector = connector_provider.get_assetdbtemp_connector()
    assetdb_temp_connector.connect()

    # Connect to llm
    llm_connector = connector_provider.get_llm_connector()
    llm_connector.connect()

    # Load metadata File
    metadata_urn = get_data_from_xcom(download_data, [download_meta_urn_key])
    meta_response = assetdb_temp_connector.get_object(metadata_urn)
    if "500 Internal Server Error" in meta_response.data.decode("utf-8"):
        raise AirflowFailException()

    meta_data = json.loads(meta_response.data)
    meta_response.close()
    meta_response.release_conn()

    model = llm_configs["llm_model_id"]  # "mistralai/Pixtral-12B-2409"
    print(f"Model: {model}")

    if mode == "topic_summary":
        # Load context files: topic result file
        topic_result_urn = get_data_from_xcom(context_data, [context_data_key])
        topic_result_response = assetdb_temp_connector.get_object(topic_result_urn)
        if "500 Internal Server Error" in topic_result_response.data.decode("utf-8"):
            raise AirflowFailException()
        topic_result_data = json.loads(topic_result_response.data)
        topic_result_response.close()
        topic_result_response.release_conn()

        data = extend_topic_result(llm_connector, prompt_base, topic_result_data, meta_data)
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

        data = create_questionnaire_result(llm_connector, prompt_base, mode, topic_result_data, meta_data)
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
            llm_connector=llm_connector,
            prompt_base=prompt_base,
            slides_text=slides_text,
            slides_language=slides_language,
            meta_data=meta_data,
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

        context_data = shorten_transcript(context_data, model_id=llm_connector.llm_model_id)
        messages = create_llm_messages(prompt_base, mode, context_data, meta_data)
        # Store data
        data = None
        mime_type = None
        custom_config = {}
        if mode == "summary":
            custom_config["max_new_tokens"] = 8192
            llm_response = llm_connector.query_llm(messages=messages, custom_config=custom_config)
            data = create_summary_result(llm_response)
            mime_type = HansType.get_mime_type(HansType.SUMMARY_RESULT_EN)
        elif mode == "short_summary":
            custom_config["max_new_tokens"] = 4096
            llm_response = llm_connector.query_llm(messages=messages, custom_config=custom_config)
            data = create_short_summary_result(llm_response)
            mime_type = HansType.get_mime_type(HansType.SHORT_SUMMARY_RESULT_EN)
        elif mode == "topic":
            custom_config["max_new_tokens"] = 2048
            llm_response = llm_connector.query_llm(messages=messages, custom_config=custom_config)
            data = create_topic_result(llm_response)
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
    llm_configs={},
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
    :param dict llm_configs: Configurations for all llm models

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
            llm_configs,
        ],
        requirements=["/opt/hans-modules/dist/hans_shared_modules-0.1-py3-none-any.whl", "eval-type-backport"],
        # pip_install_options=["--force-reinstall"],
        python_version="3",
        dag=dag,
    )
