#!/usr/bin/env python
"""Common helpers for interacting with llms
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2025, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"

import re
import urllib.parse
from urllib.parse import urlparse
import requests
import tiktoken
from collections import Counter
from tokenizers import normalizers
from tokenizers.normalizers import NFD, StripAccents
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.request import ChatCompletionRequest
from mistral_common.protocol.instruct.messages import UserMessage, TextChunk, ImageURLChunk, ChunkTypes
from markdown import markdown
from bs4 import BeautifulSoup
from langdetect import DetectorFactory
from langdetect import detect

DetectorFactory.seed = 0


def calc_token_len(
    model_id: str = "gpt-3.5-turbo",
    text: str = None,
    image_data: str = None,
    chat_request: ChatCompletionRequest = None,
) -> int:
    """
    Estimate token count for text, image (URL or base64), or a chat completion request.

    If `chat_request` is provided, it will be used directly. Otherwise, a ChatCompletionRequest
    will be constructed from `text` and/or `image_data`.
    """
    # Normalize model name
    model_name = model_id.split("/")[-1]

    # Build or use provided chat_request for unified handling
    if chat_request is None:
        messages = []
        if text is not None:
            # Use raw string content or chunk list
            messages.append(UserMessage(content=[TextChunk(type=ChunkTypes.text, text=text)]))
        if image_data is not None:
            # Wrap image URL/base64 in chunk list
            messages.append(UserMessage(content=[ImageURLChunk(type=ChunkTypes.image_url, image_url=image_data)]))
        if not messages:
            raise ValueError("Provide at least one of `text`, `image_data`, or a full `chat_request`.")
        chat_request = ChatCompletionRequest(tools=[], messages=messages, model=model_name)

    # Mistral models use specialized tokenizer
    if "mistral" in model_name.lower():
        # Choose variant
        if "small-3.1-24b" in model_name.lower():
            tokenizer = MistralTokenizer.v7(is_mm=True)
        elif "small-24b" in model_name.lower():
            tokenizer = MistralTokenizer.v7(is_mm=False)
        else:
            tokenizer = MistralTokenizer.from_model(model_name)
        # Tokenize chat completion request (handles chunked content)
        tokenized = tokenizer.encode_chat_completion(chat_request)
        return len(tokenized.tokens)

    # Fallback to tiktoken for OpenAI-compatible models
    encoding = tiktoken.encoding_for_model(model_name)
    flat = []
    for msg in chat_request.messages:
        role = getattr(msg, "role", "user")
        flat.append(role)
        content = msg.content
        # Handle list of chunks
        if isinstance(content, list):
            for chunk in content:
                if hasattr(chunk, "text"):
                    flat.append(chunk.text)
                elif hasattr(chunk, "image_url"):
                    flat.append(chunk.image_url)
                else:
                    flat.append(str(chunk))
        # Handle raw string content
        else:
            flat.append(str(content))
    # Join with newline and encode
    return len(encoding.encode("\n".join(flat)))


def shorten_transcript(context_data: str, model_id: str = "gpt-3.5-turbo", token_limit=12288) -> str:
    """
    Shorten transcript text
    token limit default: 12288 previous values: 12288, 19456, 20480, 10240, 7168, 6120
    """
    # shrink token size by removing stop words from text if approx. token size is too big
    print(f"context_data before ascii: {context_data}")
    context_data_tk_len = calc_token_len(model_id=model_id, text=context_data)
    print(f"Token length before ascii: {context_data_tk_len}")
    context_data = tokenizers_normalize_text(context_data).encode("ascii", "ignore").decode().replace("\n", " ")
    print(f"context_data ascii: {context_data}")
    context_data_tk_len = calc_token_len(model_id=model_id, text=context_data)
    print(f"Token length ascii: {context_data_tk_len}")
    context_data_tk_len_prev = context_data_tk_len
    stop_now = False
    if context_data_tk_len > token_limit:
        while context_data_tk_len > token_limit and not stop_now:
            context_data = remove_sentences(context_data)
            context_data_tk_len = calc_token_len(model_id=model_id, text=context_data)
            print(f"Token length after remove sentences: {context_data_tk_len}")
            if context_data_tk_len_prev > context_data_tk_len:
                context_data_tk_len_prev = context_data_tk_len
            else:
                stop_now = True
    if stop_now is True:
        if context_data_tk_len > token_limit:
            while context_data_tk_len > token_limit:
                context_data = remove_word(context_data)
                context_data_tk_len = calc_token_len(model_id=model_id, text=context_data)
                print(f"Token length after remove sentences: {context_data_tk_len}")
    print(f"context_data final: {context_data}")
    context_data_tk_len = calc_token_len(model_id=model_id, text=context_data)
    print(f"Token length final: {context_data_tk_len}")
    return context_data


def remove_sentences(text, val=7):
    """
    Remove every x sentences from text
    """
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


def remove_punctuation(text, punctuation='.!?"、。।，@<”,;¿¡&%#*~【】，…‥「」『』〝〟″⟨⟩♪・‹›«»～′$+="'):
    """
    Remove punctuation
    """
    for member in punctuation:
        text = text.replace(member, "")
    return text


def remove_most_frequent_words(text):
    """
    Removes stop words to lower final token size
    """
    freq_words = get_most_frequent_words(text)
    words = [word for word in text.split() if word.lower() not in freq_words]
    return " ".join(words).strip()


def remove_until_next_word(text):
    """
    Remove specific word until next word
    """

    # Define a regular expression pattern to match "-->" followed by any non-space characters
    pattern = r"^-->\s*"

    # Replace the pattern with an empty string to remove it until the next word
    result = re.sub(pattern, "", text)

    return result


def remove_initial_markers(text: str, markers: tuple[str, ...]) -> str:
    """Remove initial tokens which might be added by the LLM."""
    if text.split(":")[0].lower() in markers:
        return text.split(":", 1)[1].strip()
    return text


def remove_quotes(text: str) -> str:
    """Remove quotes if text is quoted like 'text'."""
    if len(text) > 0:
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


def remove_urls(text):
    """
    Remove urls from a text
    """
    # Remove URLs that start with http or https
    return re.sub(r"http[s]?://\S+", "", text)


def get_most_frequent_words(text, top=5):
    """
    Get most frequent words list
    """
    freq = Counter(text.split())
    # print(freq)
    mc = freq.most_common(top)
    words = [item[0].lower() for item in mc]
    words.remove("-->")
    print(words)
    return words


def find_words_not_urls(text):
    """
    Find words in text which are not url
    """
    # Remove punctuation and split into words
    cleaned_text = remove_urls(text)
    return re.findall(r"\b(?!http|https)\w+\b", cleaned_text)


def find_all_urls(text):
    """
    Find urls in text
    """
    # Find all URLs using re.findall
    fin_text = text.replace("http:", " http:").replace("https:", " https:")
    urls = re.findall(r"(https?://[^\s]+)", fin_text)
    return urls


def is_url_valid(url):
    """
    Function to check if a URL is valid
    """
    try:
        response = requests.get(url, timeout=5)
        # Check if the status code is in the 2xx range (success)
        return 200 <= response.status_code < 300
    except requests.RequestException:
        # If there is any exception, treat the URL as invalid
        return False


def extract_tld(url):
    """
    Parse top level domain from url
    """
    domain = urlparse(url).netloc
    domain_parts = domain.split(".")

    if len(domain_parts) >= 2:
        return ".".join(domain_parts[-2:])
    return domain


def encode_urls_in_text(text: str) -> str:
    """
    Encode urls in text
    """
    # Regular expression to text URLs (http/https)
    url_pattern = r"https?://[^\s]+"

    # Function to encode matched URLs
    def encode_match(match):
        return urllib.parse.quote(match.group(0), safe=":/?&=")

    # Find and encode all URLs in the prompt
    encoded_text = re.sub(url_pattern, encode_match, text)
    return encoded_text


def classify_url(url):
    """
    Function to classify URL based on domain

    :return str Url class string: 'videos', 'science', 'news', 'wiki',
    'pictures', 'social' or 'other'
    """
    domain = extract_tld(url)
    video_sites = [
        "youtube.com",
        "youtu.be",
        "vimeo.com",
        "dailymotion.com",
        "twitch.tv",
        "netflix.com",
        "hulu.com",
        "primevideo.com",
        "disneyplus.com",
        "hbomax.com",
        "peacocktv.com",
        "crunchyroll.com",
        "funimation.com",
        "veoh.com",
        "bilibili.com",
        "metacafe.com",
        "odyssey.com",
        "rumble.com",
        "vudu.com",
        "tiktok.com",
        "viki.com",
        "ard.de",
        "zdf.de",
        "3sat.de",
        "ardmediathek.de",
        "arte.tv",
    ]
    science_sites = [
        "springer.com",
        "nature.com",
        "sciencedirect.com",
        "wiley.com",
        "nih.gov",
        "plos.org",
        "ieee.org",
        "jstor.org",
        "arxiv.org",
        "researchgate.net",
        "mdpi.com",
        "biorxiv.org",
        "sci-hub.se",
        "doaj.org",
        "frontiersin.org",
        "hindawi.com",
        "oup.com",
        "cambridge.org",
        "tandfonline.com",
        "acs.org",
        "books.google.com",
    ]
    news_sites = [
        "cnn.com",
        "bbc.co.uk",
        "nytimes.com",
        "theguardian.com",
        "reuters.com",
        "washingtonpost.com",
        "forbes.com",
        "foxnews.com",
        "huffpost.com",
        "latimes.com",
        "aljazeera.com",
        "ft.com",
        "bloomberg.com",
        "euronews.com",
        "independent.co.uk",
        "sky.com",
        "thetimes.co.uk",
        "deutsche-welle.com",
        "theverge.com",
        "vox.com",
        "spiegel.de",
        "faz.net",
        "welt.de",
        "taz.de",
        "bild.de",
        "zeit.de",
        "handelsblatt.com",
        "sueddeutsche.de",
        "tagesschau.de",
        "tagesspiegel.de",
        "br.de",
    ]
    image_sites = [
        "flickr.com",
        "imgur.com",
        "shutterstock.com",
        "unsplash.com",
        "pexels.com",
        "depositphotos.com",
        "photobucket.com",
        "500px.com",
        "adobe.com",
        "canva.com",
        "stock.adobe.com",
        "dreamstime.com",
        "istockphoto.com",
        "gettyimages.com",
        "freepik.com",
        "visualhunt.com",
        "burst.shopify.com",
        "pixabay.com",
        "nature.com",
    ]
    social_sites = [
        "instagram.com",
        "facebook.com",
        "twitter.com",
        "pinterest.com",
        "snapchat.com",
        "tiktok.com",
        "flickr.com",
        "tumblr.com",
        "vk.com",
        "reddit.com",
        "linkedin.com",
        "weibo.com",
        "foursquare.com",
        "ello.co",
        "dscout.com",
        "imgur.com",
        "500px.com",
    ]
    wiki_sites = [
        "wikihow.com",
        "wikimedia.org",
        "wikia.com",
        "infogalactic.com",
        "citizendium.org",
        "everipedia.org",
        "scholarpedia.org",
        "encarta.msn.com",
        "brittanica.com",
        "simple.wikipedia.org",
        "wikipedia.org",
        "starwiki.net",
        "memory-alpha.org",
        "fandom.com",
        "openstreetmap.org",
        "wikitravel.org",
    ]

    if domain in video_sites:
        return "videos"
    elif domain in science_sites:
        return "science"
    elif domain in news_sites:
        return "news"
    elif domain in wiki_sites:
        return "wiki"
    elif domain in image_sites:
        return "pictures"
    elif domain in social_sites:
        return "social"
    else:
        return "other"


def tokenizers_normalize_text(text):
    """
    Normalize text using tokenizers
    """
    normalizer = normalizers.Sequence([NFD(), StripAccents()])
    return normalizer.normalize_str(text)


def markdown_to_plain_text(markdown_text):
    """
    Convert markdown to plain text
    """
    # Convert Markdown to HTML
    html = markdown(markdown_text)
    # Use BeautifulSoup to parse HTML and extract text
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


def cleanup_text(text):
    """
    Cleanup text
    """
    if text.endswith("```"):
        text = text.replace("```markdown", "")
        text = text.rstrip("```")
    text = text.replace("\n", " ")
    text = text.replace("   ", " ")
    text = text.replace("  ", " ")
    return text.strip()


def cleanup_markdown(text):
    """
    Cleanup markdown
    """
    if text.endswith("\n```"):
        text = text.replace("```markdown\n", "")
        text = text.rstrip("\n```")
    elif text.endswith("```"):
        text = text.replace("```markdown", "")
        text = text.rstrip("```")
    return text


def detect_language(text):
    """
    Function to detect language of a text

    :return str 'en', 'de', ...
    """
    return detect(text.strip())


def gen_messages(system_prompt: str, user_prompt: str, context_sentence=None, img_input=None):
    """Create openai compat message array"""
    messages = [{"role": "system", "content": system_prompt.strip()}]
    user_content = user_prompt.strip()
    if context_sentence is not None and len(context_sentence) > 0:
        user_content += " " + context_sentence.strip()
    if img_input is None:
        messages.append({"role": "user", "content": user_content})
    else:
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_content},
                    {"type": "image_url", "image_url": {"url": img_input}},
                ],
            }
        )
    # print(json.dumps({"messages": messages}), flush=True)
    return messages
