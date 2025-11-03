"""
Preload whisper models
"""

import argparse
from transcribe import WhisperS2T


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--device", default="cuda", type=str, help="Device default:'cuda', values: 'cuda', 'cpu', 'mps"
    )
    parser.add_argument(
        "-m",
        "--model",
        default="large-v3",
        type=str,
        help="Whisper model size:'large-v3', values: 'large-v3', 'medium'",
    )
    return parser.parse_args()


def main():
    """
    Preload whisper models
    """
    args = parse_args()
    engine = WhisperS2T(device=args.device, model_name=args.model, word_timestamps=True)
    print(f"whisper-s2t: {engine.meta_data.engine.version}")


if __name__ == "__main__":
    main()
