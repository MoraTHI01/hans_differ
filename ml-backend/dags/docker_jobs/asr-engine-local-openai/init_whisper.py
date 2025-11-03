"""
Preload whisper models
"""

import argparse
import time
import whisper


def main():
    """
    Preload whisper models
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("model_sizes", nargs="*", help="Whisper model sizes to download, e.g. 'medium'")
    args = parser.parse_args()
    for model_size in args.model_sizes:
        print(f"Preloading whisper model: {model_size}")
        _ = whisper.load_model(model_size)
        time.sleep(10)


if __name__ == "__main__":
    main()
