#!/usr/bin/env python
"""
Helper to normalize asr_result.json to transcript.json using spacy

NLP:
https://spacy.io/usage
https://spacy.io/usage/linguistic-features
https://spacy.io/api/token#attributes
https://spacy.io/models/en
https://spacy.io/models/de

Punctuation:
https://github.com/oliverguhr/deepmultilingualpunctuation/
https://huggingface.co/oliverguhr/fullstop-punctuation-multilang-large
https://github.com/oliverguhr/fullstop-deep-punctuation-prediction

Related:
https://mmsankosho.com/en/nlp-for-learners-parsing-with-stanza/
https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import argparse
import json
import re
import spacy
import sys
import wordtodigits
import zahlwort2num as zw2n
from deepmultilingualpunctuation import PunctuationModel


def capitalize_spacy(nlp_pipline, text, prev_sentence_ended):
    """Capitalize"""
    document = nlp_pipline(text)
    words_capitalized = []
    w_prev_tag = ""
    for token in document:
        # print(token.text, str(token.i), token.tag_)
        # print("")
        if args.locale == "en":
            if (
                (token.i == 0 and prev_sentence_ended and w_prev_tag != "$,")
                or (len(token.text) >= 2 and "i" == token.text[0] and "'" == token.text[1])
                or "i" == token.text
            ):
                words_capitalized.append(token.text.capitalize())
            else:
                words_capitalized.append(token.text.lower())
        elif args.locale == "de":
            if (token.i == 0 and prev_sentence_ended and w_prev_tag != "$,") or (token.tag_ in ["NN", "NNE"]):
                temp_cap_word = token.text.capitalize()
                # audio-podcast to Audio-Podcast
                if "-" in temp_cap_word and temp_cap_word[-1] != "-":
                    minus_index = temp_cap_word.rfind("-")
                    search_str = temp_cap_word[minus_index] + temp_cap_word[minus_index + 1]
                    replace_str = search_str.upper()
                    temp_cap_word = temp_cap_word[:minus_index] + replace_str + temp_cap_word[minus_index + 2 :]
                words_capitalized.append(temp_cap_word)
            else:
                words_capitalized.append(token.text.lower())
        w_prev_tag = token.tag_
    return (document, words_capitalized)


def spoken_number_conversion_spacy(nlp_ner, current_sentence, sentences):
    """Spoken number conversion"""
    doc2 = nlp_ner(current_sentence)
    for ent in doc2.ents:
        # print(ent.text, ent.label_)
        if ent.label_ in ["CARDINAL", "ORDINAL", "QUANTITY"]:
            number = None
            if args.locale == "en":
                number = wordtodigits.convert(ent.text)
            elif args.locale == "de":
                number = zw2n.convert(ent.text)
            if number is None:
                raise Exception("Failed to convert number!")
            number_words_list = ent.text.lower().split(" ")
            sentences = replace_number_words_in_sentences(sentences, ent.text, number_words_list, number)
    return sentences


def replace_number_words_in_sentences(sentences_input, number_words_text, number_words_lowered, number_converted):
    """Injected converted number into sentences structure"""
    for sentence in sentences_input:
        if number_words_text.lower() in sentence["transcript_formatted"].lower():
            compiled = re.compile(re.escape(number_words_text), re.IGNORECASE)
            sentence["transcript_formatted"] = compiled.sub(number_converted, sentence["transcript_formatted"])
            start_number_interval = None
            end_number_interval = None
            pop_index_list = []
            index = 0
            first_word_to_pop_index = 0
            for word_formatted in sentence["words_formatted"]:
                if start_number_interval is None:
                    if word_formatted["word"].lower() == number_words_lowered[0]:
                        start_number_interval = word_formatted["interval"][0]
                        first_word_to_pop_index = index
                if end_number_interval is None:
                    if word_formatted["word"].lower() == number_words_lowered[-1]:
                        end_number_interval = word_formatted["interval"][1]
                if word_formatted["word"].lower() in number_words_lowered:
                    pop_index_list.append(index)
                index += 1
            pop_count2 = 0
            for pop_number_index in pop_index_list:
                sentence["words_formatted"].pop(pop_number_index - pop_count2)
                pop_count2 += 1
            sentence["words_formatted"].insert(
                first_word_to_pop_index,
                {"interval": [start_number_interval, end_number_interval], "word": number_converted},
            )
    return sentences


def check_error_in_sentence_structure(sentences_input, prev_stage, check_sentence_interval=False):
    """
    Detect errors in words, ensure each word has an valid interval entry
    returns: bool: False if no error in sentence structure, True otherwise.
    """
    for sentenceitem in sentences_input:
        if check_sentence_interval is True:
            if sentenceitem["interval"] is None or len(sentenceitem["interval"]) < 2:
                print(f"Error after stage: {prev_stage}: Sentence interval is empty!")
                print(f"SentenceItem: {sentenceitem}")
                return True
        for worditem in sentenceitem["words_formatted"]:
            if worditem["word"] and len(worditem["word"]) < 1:
                print(f"Error after stage: {prev_stage}: Word is empty!")
                print(f"WordItem: {worditem}")
                return True
            if worditem["interval"] is None or len(worditem["interval"]) < 2:
                print(f"Error after stage: {prev_stage}: Word interval is empty!")
                print(f"WordItem: {worditem}")
                return True
    return False


def currency_symbol_conversion(locale, sentences_input):
    """Convert currency symbols, e.g. 'dollar' to '$'"""
    currency_symbols = [
        {"word": {"en": ["dollar", "dollars"], "de": ["dollar"]}, "symbol": "$"},
        {"word": {"en": ["euro"], "de": ["euro"]}, "symbol": "€"},
        {"word": {"en": ["pound", "pounds"], "de": ["pfund"]}, "symbol": "£"},
        {"word": {"en": ["yen"], "de": ["yen"]}, "symbol": "¥"},
    ]
    for sentence in sentences_input:
        for currency_symbol in currency_symbols:
            for currency_symbol_word in currency_symbol["word"][locale]:
                if currency_symbol_word in sentence["transcript_formatted"].lower():
                    compiled = re.compile(re.escape(currency_symbol_word), re.IGNORECASE)
                    sentence["transcript_formatted"] = compiled.sub(
                        currency_symbol_word, sentence["transcript_formatted"]
                    )
                    for word_formatted in sentence["words_formatted"]:
                        if currency_symbol_word in word_formatted["word"].lower():
                            word_formatted["word"] = currency_symbol_word
    return sentences_input


def replace_minus_and_combine_with_number(sentences_input):
    """Replace minus text before numbers and combine it with the number"""
    for sentence in sentences_input:
        search_sentence = sentence["transcript_formatted"].lower()
        m = re.search(r"\d", search_sentence)
        if m:
            # print("Digit found at position", m.start())
            # minus = 5 chars, + whitespace between e.g. minus 444
            if m.start() - 7 >= 0:
                found_index = search_sentence.find("minus", m.start() - 7, m.start())
                if found_index != -1:
                    compiled = re.compile(re.escape("minus"), re.IGNORECASE)
                    sentence["transcript_formatted"] = compiled.sub("-", sentence["transcript_formatted"])
                    word_minus_index = 0
                    word_minus_start_interval = None
                    for word_formatted in sentence["words_formatted"]:
                        if "minus" in word_formatted["word"].lower():
                            word_minus_start_interval = word_formatted["interval"][0]
                            break
                        word_minus_index += 1
                    sentence["words_formatted"][word_minus_index + 1]["word"] = (
                        "-" + sentence["words_formatted"][word_minus_index + 1]["word"]
                    )
                    sentence["words_formatted"][word_minus_index + 1]["interval"][0] = word_minus_start_interval
                    sentence["words_formatted"].pop(word_minus_index)
    return sentences_input


def generate_asr_normalized_result(word_items, pred, sent, sent_index):
    """Generate AsrNormalizedResult"""
    temp_transcript = ""
    # print("")
    # ["ist",""0.9"] prediction item is an array consisting of word, label and likelihood
    for curr_word_pred, label_pred, _ in pred:
        current_word_interval = None
        word_found = False
        current_word = curr_word_pred.lower()
        # print("Current word: " + current_word)
        for item in word_items:
            if "words" in item and word_found is False:
                if len(item["words"]) > 0:
                    word_index = 0
                    for temp_word_item in item["words"]:
                        if "word" in temp_word_item:
                            temp_word = temp_word_item["word"].lower()
                            if (
                                temp_word == current_word
                                or len(temp_word) == 2
                                and temp_word[-1] in ".,?!:-"
                                and temp_word[0] == current_word
                            ):
                                if "interval" in temp_word_item:
                                    current_word_interval = temp_word_item["interval"]
                                    # print("")
                                    # print(f"Remove word on index {word_index}: {temp_word}")
                                    item["words"].pop(word_index)
                                    # print(f"Input words new: {input_words}")
                                    word_found = True
                                    break
                                else:
                                    print("Error word interval is empty!")
                                    exit(1)
                        word_index = word_index + 1
            if word_found:
                break
        if current_word_interval is None:
            print("Error word interval is None!")
            print("Current word: " + current_word)
            exit(1)
        # print("")
        temp_transcript += current_word.lower()
        sent[sent_index]["words_formatted"].append({"interval": current_word_interval, "word": current_word.lower()})
        # Check if char is in the following strings:
        if label_pred == "0" or label_pred is None:
            # Sentence continues, word with no special symbols add space
            temp_transcript += " "
        elif label_pred in ",-":
            # Sentence continues, word with above symbols
            temp_transcript += label_pred + " "
        elif label_pred in ".?!:":
            # Sentence ended
            temp_transcript += label_pred
            # Get bouding interval for sentence
            start_interval = sent[sent_index]["words_formatted"][0]["interval"][0]
            end_interval = sent[sent_index]["words_formatted"][-1]["interval"][1]
            # Add capitalization
            # print(f"Adding sentence: {temp_transcript}")
            (doc, words_cap) = capitalize_spacy(nlp, temp_transcript, True)

            # Combine you 're to you're again
            # print("Combine you 're to you're again")
            pop_indexes = []
            word_cap_index = 0
            for word_cap in words_cap:
                if "'" in word_cap and word_cap_index > 0 and word_cap[0] == "'" or "n't" == word_cap:
                    words_cap[word_cap_index - 1] += word_cap
                    pop_indexes.append(word_cap_index)
                word_cap_index += 1
            pop_counter = 0
            for pop_index2 in pop_indexes:
                words_cap.pop(pop_index2 - pop_counter)
                pop_counter += 1
            # print("Combine you 're to you're again: finished.")

            # Overwrite capitalized words
            temp_transcript_cap = ""
            word_items_non_cap = sent[sent_index]["words_formatted"]
            # print(f"Words not capitalized: {word_items_non_cap}")
            # print(f"Words capitalized: {words_cap}")
            word_cap_index = 0
            word_cap_len = len(words_cap)
            for word_cap in words_cap:
                if word_cap == "." or word_cap == "!" or word_cap == "?" or word_cap == ":":
                    # print("Sentence end symbol found: %s", word_cap)
                    temp_transcript_cap = temp_transcript_cap + word_cap
                elif word_cap == "," or word_cap == "-":
                    # print("Sentence continue symbol found: %s", word_cap)
                    temp_transcript_cap = temp_transcript_cap + word_cap + " "
                else:
                    # print(f"Captializing word: {word_cap}")
                    temp_word_index = 0
                    search_word = word_cap.lower()
                    search_word_found = False
                    for word_item_non_cap in word_items_non_cap:
                        if (
                            word_item_non_cap["word"] == search_word
                            or search_word[-1] in ".,?!:-"
                            and word_item_non_cap["word"] == search_word[:-1]
                        ):
                            # print(f"Word '{word_cap}' found on index {temp_word_index}!")
                            search_word_found = True
                            break
                        temp_word_index += 1
                    if not search_word_found:
                        raise Exception(
                            f"Word '{search_word}' was not found in non capitalized words: {word_items_non_cap}"
                        )
                    try:
                        # print(f"Overwrite with capitalized word '{word_cap}' on index {temp_word_index}")
                        sent[sent_index]["words_formatted"][temp_word_index]["word"] = word_cap
                    except Exception as exc:
                        raise Exception(f"Failed to store capitalized word '{word_cap}'!") from exc
                    if word_cap_index + 1 < word_cap_len:
                        next_word = words_cap[word_cap_index + 1]
                        if (
                            next_word == "."
                            or next_word == "!"
                            or next_word == "?"
                            or next_word == ":"
                            or next_word == ","
                            or next_word == "-"
                        ):
                            temp_transcript_cap = temp_transcript_cap + word_cap
                        else:
                            temp_transcript_cap = temp_transcript_cap + word_cap + " "
                    else:
                        temp_transcript_cap = temp_transcript_cap + word_cap + " "
                # print(f"transcript_cap: {temp_transcript_cap}")
                word_cap_index += 1
            # print("Word capitalization: finished")

            try:
                sent[sent_index]["transcript_formatted"] = temp_transcript_cap.strip()
            except Exception as exc:
                raise Exception("Failed to store formatted transcript!") from exc
            # print("Store initial formatted transcript: finished")
            check_error_in_sentence_structure(sent, "Store initial formatted transcript")

            # Do spoken number conversion (missing is if word "minus" is before number)
            # print("spoken number conversion")
            sent = spoken_number_conversion_spacy(nlp_ner, sent[sent_index]["transcript_formatted"], sent)
            # print("Spoken number conversion: finished")
            check_error_in_sentence_structure(sent, "Spoken number conversion")

            # Minus conversion if before number
            # print("minus conversion")
            sent = replace_minus_and_combine_with_number(sent)
            # print("Minus conversion: finished")
            check_error_in_sentence_structure(sent, "Minus conversion")

            # Currency Symbol Conversion
            # print("currency symbol conversion")
            sent = currency_symbol_conversion(args.locale, sent)
            # print("Currency symbol conversion: finished")
            check_error_in_sentence_structure(sent, "Currency symbol conversion")

            sent[sent_index]["interval"].append(start_interval)
            sent[sent_index]["interval"].append(end_interval)
            temp_transcript = ""
            sent_index = sent_index + 1
            check_error_in_sentence_structure(sent, "Current sentence interval added", True)

            sent.append({"interval": [], "transcript_formatted": "", "words_formatted": [], "result_index": sent_index})
        print(".", end=" ")

    # Clear last empty sentence
    if sent[-1]["transcript_formatted"] == "":
        sent.pop()
    return sent


parser = argparse.ArgumentParser(description="Helper to normalize asr_result.json to transcript.json using spacy")
parser.add_argument("inputFile", type=str, help="asr_result.json input file path")
parser.add_argument("locale", type=str, help="asr locale for processing")
parser.add_argument("outputFile", type=str, help="transcript.json output file path")
args = parser.parse_args()

try:
    # Load NLP neural pipline
    if args.locale == "en":
        nlp = spacy.load("en_core_web_trf")
        nlp_ner = spacy.load("en_core_web_md")
    elif args.locale == "de":
        nlp = spacy.load("de_dep_news_trf")
        nlp_ner = spacy.load("de_core_news_md")

    # Load punctuation model
    punctuation_model = PunctuationModel(model="oliverguhr/fullstop-punctuation-multilang-large")
    print("Loading nlp models: finished")

    # Read asr_result.json file
    f = open(args.inputFile, "r", encoding="utf-8")
    data = json.load(f)
    f.close()
    results = data["result"]
    print("Reading asr_result.json: finished")

    # Load full transcript text
    input_text = ""
    # Load full words structure
    input_words = []
    for result_item in results:
        transcript_temp = result_item["transcript"].lower()
        if "<unk> " in transcript_temp:
            transcript_temp = transcript_temp.replace("<unk> ", "")
        if "<unk>" in transcript_temp:
            transcript_temp = transcript_temp.replace("<unk>", "")
        if "[noise] " in transcript_temp:
            transcript_temp = transcript_temp.replace("[noise] ", "")
        if "[noise]" in transcript_temp:
            transcript_temp = transcript_temp.replace("[noise]", "")
        if "o._d." in transcript_temp:
            transcript_temp = transcript_temp.replace("o._d.", "od")
        if "o._k." in transcript_temp:
            transcript_temp = transcript_temp.replace("o._k.", "ok")
        if "r._c." in transcript_temp:
            transcript_temp = transcript_temp.replace("r._c.", "rc")
        if "f._t._e.s" in transcript_temp:
            transcript_temp = transcript_temp.replace("f._t._e.s", "ftes")
        if "e._z." in transcript_temp:
            transcript_temp = transcript_temp.replace("e._z.", "ez")
        if len(transcript_temp) > 0:
            input_text += " " + transcript_temp
            remove_special_words = []
            remove_special_word_index = 0
            for word_item in result_item["words"]:
                curr_word = word_item["word"].lower()
                if curr_word == "<unk>" or curr_word == "[noise]" or word_item["word"] == "":
                    remove_special_words.append(remove_special_word_index)
                if curr_word == "o._d.":
                    result_item["words"][remove_special_word_index]["word"] = "od"
                elif curr_word == "o._k.":
                    result_item["words"][remove_special_word_index]["word"] = "ok"
                elif curr_word == "r._c.":
                    result_item["words"][remove_special_word_index]["word"] = "rc"
                elif curr_word == "f._t._e.s":
                    result_item["words"][remove_special_word_index]["word"] = "ftes"
                elif curr_word == "e._z.":
                    result_item["words"][remove_special_word_index]["word"] = "ez"
                remove_special_word_index += 1
            pop_count = 0
            for remove_index in remove_special_words:
                pop_index = remove_index - pop_count
                if remove_index < len(result_item["words"]):
                    result_item["words"].pop(pop_index)
                    pop_count += 1
            if len(result_item["words"]) > 0:
                input_words.append({"words": result_item["words"]})

    print("Input text cleaning: finished")
    # print(f"Input words cleaned: {input_words}")

    # Restore punctuation
    clean_text = punctuation_model.preprocess(input_text)
    print("Restore punctuation preprocessing: finished")
    prediction = punctuation_model.predict(clean_text)
    # text_punctuation = punctuation_model.prediction_to_text(prediction)
    print("Restore punctuation prediction: finished")

    sentence_index = 0
    sentences = [{"interval": [], "transcript_formatted": "", "words_formatted": [], "result_index": sentence_index}]
    sentences = generate_asr_normalized_result(input_words, prediction, sentences, sentence_index)
    print(".")
    print("Generate AsrNormalizedResult: finished")
    check_error_in_sentence_structure(sentences, "Generate AsrNormalizedResult", True)

    # Postproccessing: Add punctuation marks to corresponding words
    global_index = 0
    for sent_item in sentences:
        # "You're a fool for traveling alone, so completely unprepared."
        word_array = sent_item["transcript_formatted"].split(" ")
        for word in word_array:
            # Find char in string works
            if word[0] in ".,?!:-" or word[-1] in ".,?!:-":
                curr_index = 0
                for update_word_item in sent_item["words_formatted"]:
                    if update_word_item["word"] == word[:-1]:
                        # alone = alone,
                        sent_item["words_formatted"][curr_index]["word"] = word
                    curr_index = curr_index + 1
        # Create global word index of the complete transcript
        for item_index in range(len(sent_item["words_formatted"])):
            sent_item["words_formatted"][item_index]["index"] = global_index
            item_index += 1
            global_index += 1
        print(".", end=" ")
    print(".")
    print("Postproccessing: finished")
    check_error_in_sentence_structure(sentences, "Postproccessing", True)

    # Save back complete result
    final_result_data = {}
    final_result_data["result"] = sentences
    final_result_data["type"] = "AsrNormalizedResult"

    # Write output file
    with open(args.outputFile, "w", encoding="utf-8") as outfile:
        json.dump(final_result_data, outfile, indent=None, separators=(",", ":"))
    print("Saving final result: finished")
    sys.exit(0)
except Exception as e:
    print("Unexpected error occured:")
    print(e)
    sys.exit(-1)
