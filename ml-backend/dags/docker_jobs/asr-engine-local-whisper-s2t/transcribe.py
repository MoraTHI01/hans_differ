"""
Transcribe or translate audio using whisper-s2t
"""

import argparse
import json
import math
from importlib.metadata import version

from result_types import TranscriptionResponse, TranscriptionSegment, Word, MetaData, MetaEngine, MetaAsrModel
import whisper_s2t
from whisper_s2t.backends.ctranslate2.model import BEST_ASR_CONFIG
from whisper_s2t.backends.openai.model import ASR_OPTIONS


class WhisperS2T:
    """
    whisper-s2t recognition engine
    """

    def _get_model(
        self, device="cuda", model_name="large-v3", compute_type="float16", beam_size=5, best_of=1, word_timestamps=True
    ):
        """
        Get model
        :param str device: Name of the device, default: 'cuda', values: 'cpu', 'cuda', 'mps'
        :param str model_name: Name of whisper model size
        :param str compute_type: 'float16', 'int8', 'float32' depends on used backend
        :param int beam_size: Decoding beam size
        :param int best_of: Best of decoding
        :param int word_timestamps: Provide word level timestamps

        Note int8 is only supported for CTranslate2 backend, for others only float16 is supported for lower precision.
        https://github.com/shashikg/WhisperS2T/blob/main/docs.md#passing-custom-model-configuration
        https://github.com/shashikg/WhisperS2T/blob/main/whisper_s2t/backends/ctranslate2/model.py#L37

        :return WhisperS2TModel
        """
        model_kwargs = {"compute_type": compute_type, "device": device, "asr_options": {}}

        if device.lower() == "cpu":
            model_kwargs["compute_type"] = "float32"
            self.backend = "OpenAI"

        # Supported backends ['CTranslate2', 'HuggingFace', 'OpenAI']
        if self.backend == "CTranslate2":
            # See https://github.com/shashikg/WhisperS2T/blob/main/whisper_s2t/backends/ctranslate2/hf_utils.py#L16
            print("Using model from https://huggingface.co/Systran/faster-whisper-" + model_name)
            model_kwargs["asr_options"] = BEST_ASR_CONFIG
        elif self.backend.lower() == "openai":
            print("Using model from https://huggingface.co/openai/whisper-" + model_name)
            model_kwargs["asr_options"] = ASR_OPTIONS

        if word_timestamps is True:
            model_kwargs["asr_options"]["without_timestamps"] = False
            model_kwargs["asr_options"]["word_timestamps"] = True

        model_kwargs["asr_options"]["beam_size"] = beam_size
        if model_name in ["large-v3"] and self.backend == "CTranslate2":
            model_kwargs["n_mels"] = 128
            model_kwargs["asr_options"]["word_aligner_model"] = "Systran/faster-whisper-large-v3"

        self.meta_data.asr_model = MetaAsrModel()
        self.meta_data.asr_model.model = model_name
        if self.backend.lower() == "openai":
            self.meta_data.asr_model.model_id = "openai/whisper-" + model_name
        else:
            model_kwargs["asr_options"]["best_of"] = best_of
            self.meta_data.asr_model.model_id = "Systran/faster-whisper-" + model_name
        self.meta_data.asr_model.language = "en-US"
        self.meta_data.asr_model.license_type = "MIT"
        return whisper_s2t.load_model(model_identifier=model_name, backend=self.backend, **model_kwargs)

    def __init__(self, device="cuda", model_name="large-v3", word_timestamps=True) -> None:
        self.beam_size = 5
        self.best_of = 1
        self.word_timestamps = word_timestamps
        self.device_name = device
        # Supported backends ['CTranslate2', 'HuggingFace', 'OpenAI']
        self.backend = "CTranslate2"
        self.compute_type = "float16"
        if device.lower() == "cpu":
            self.backend = "OpenAI"
            self.compute_type = "float32"
        self.model_name = model_name
        self.meta_data = MetaData()
        self.meta_data.engine = MetaEngine()
        self.meta_data.engine.name = "whisper-s2t"
        self.meta_data.engine.version = version("whisper-s2t")
        self.meta_data.engine.license_type = "MIT"
        self.model = self._get_model(
            device=self.device_name,
            model_name=self.model_name,
            compute_type=self.compute_type,
            beam_size=self.beam_size,
            best_of=self.best_of,
            word_timestamps=self.word_timestamps,
        )
        super().__init__()

    def _remove_punctuation(
        self, text, punctuation='"\'、。।，@<>”(),.:;-¿?¡!\\&%#*~【】，…‥「」『』〝〟″⟨⟩♪・‹›«»～′$+="'
    ):
        """
        Remove punctuation
        """
        for member in punctuation:
            text = text.replace(member, "")
        return text

    def _convert_s2t_to_response(self, data):
        """
        Convert whisper s2t result to AsrResultCombined
        """
        response = TranscriptionResponse()
        response.type = "AsrResultCombined"
        response.result = []
        transcript_index = 0
        for subelem in data:
            for item in subelem:
                words = []
                words_formatted = []
                word_index = 0
                if "word_timestamps" in item:
                    for word in item["word_timestamps"]:
                        curr_word = Word()
                        curr_word.index = word_index
                        curr_word.word = self._remove_punctuation(word["word"].lower())
                        curr_word.interval = [float(word["start"]), float(word["end"])]
                        curr_word.confidence = float(word["prob"])
                        words.append(curr_word)
                        curr_word_formatted = Word()
                        curr_word_formatted.index = word_index
                        curr_word_formatted.word = word["word"]
                        curr_word_formatted.interval = [float(word["start"]), float(word["end"])]
                        curr_word.confidence = float(word["prob"])
                        words_formatted.append(curr_word_formatted)
                        word_index += 1
                else:
                    # Fallback equal distribution of words over time
                    in_words_formatted = str(item["text"]).lstrip().rstrip().split(" ")
                    start_time = float(item["start_time"])
                    end_time = float(item["end_time"])
                    duration = end_time - start_time
                    calc_word_duration = duration / len(in_words_formatted)
                    for in_word in in_words_formatted:
                        curr_start_time = start_time + calc_word_duration * word_index
                        curr_end_time = start_time + (calc_word_duration * (word_index + 1))
                        curr_word = Word()
                        curr_word.index = word_index
                        curr_word.word = self._remove_punctuation(in_word.lower())
                        curr_word.interval = [curr_start_time, curr_end_time]
                        curr_word.confidence = 1.0
                        words.append(curr_word)
                        curr_word_formatted = Word()
                        curr_word_formatted.index = word_index
                        curr_word_formatted.word = in_word
                        curr_word_formatted.interval = [curr_start_time, curr_end_time]
                        curr_word.confidence = 1.0
                        words_formatted.append(curr_word_formatted)
                        word_index += 1
                curr_transcript = TranscriptionSegment()
                curr_transcript.result_index = transcript_index
                curr_transcript.interval = [float(item["start_time"]), float(item["end_time"])]
                curr_transcript.transcript = self._remove_punctuation(item["text"].lower())
                curr_transcript.words = words
                curr_transcript.transcript_formatted = item["text"]
                curr_transcript.words_formatted = words_formatted
                curr_transcript.confidence = math.exp(float(item["avg_logprob"]))
                response.result.append(curr_transcript)
                transcript_index += 1
        return response

    def run(
        self, audio_file: str, language_id: str, batch_size: int = 48, vad: bool = True, task: str = "transcribe"
    ) -> dict:
        """
        Run transcribe or translate task using https://github.com/shashikg/WhisperS2T
        """
        files = [audio_file]
        lang_codes = [language_id]
        tasks = [task]
        # to do prompting (only supported for CTranslate2 backend)
        initial_prompts = [None]
        result = {}
        if vad is True:
            result = self.model.transcribe_with_vad(
                files,
                lang_codes=lang_codes,  # pass lang_codes for each file
                tasks=tasks,  # pass transcribe/translate
                initial_prompts=initial_prompts,  # to do prompting
                batch_size=batch_size,
            )
        else:
            result = self.model.transcribe(
                files,
                lang_codes=lang_codes,  # pass lang_codes for each file
                tasks=tasks,  # pass transcribe/translate
                initial_prompts=initial_prompts,  # to do prompting
                batch_size=batch_size,
            )
        result_converted = self._convert_s2t_to_response(result)
        result_converted.meta = self.meta_data
        result_converted.meta.asr_model.language = language_id
        return result_converted.dict()


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b", "--batch-size", default=8, type=int, help="Batch size, default: 8, values: 8, 16, 24, 32, 48"
    )
    parser.add_argument(
        "-d", "--device", default="cuda", type=str, help="Device, default: 'cuda', values: 'cpu', 'cuda', 'mps'"
    )
    parser.add_argument(
        "-m",
        "--model",
        default="large-v3",
        type=str,
        help="ASR model, default: 'large-v3', values: 'large-v3', 'medium'",
    )
    parser.add_argument("-l", "--language", default="de", type=str, help="Language id default:'de', values: 'de', 'en'")
    parser.add_argument(
        "-t",
        "--task",
        default="transcribe",
        type=str,
        help="ASR task default:'transcribe', values: 'transcribe', 'translate'",
    )
    parser.add_argument(
        "-w",
        "--word-timestamps",
        default=True,
        type=bool,
        help="Provide word level timestamps, default:'True', values: 'True', 'False'",
    )
    parser.add_argument("-v", "--vad", default=True, type=bool, help="Use VAD, default:'True', values: 'True', 'False'")
    parser.add_argument("-i", "--input-file", type=str, help="Input wav file contains audio with 16khz mono")
    parser.add_argument("-o", "--output-file", type=str, help="Output json file")
    return parser.parse_args()


def main():
    """
    Transcribe or translate audio and store result as json
    """
    args = parse_args()
    engine = WhisperS2T(device=args.device, model_name=args.model, word_timestamps=args.word_timestamps)
    result = engine.run(args.input_file, args.language, args.batch_size, args.vad, args.task)
    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
