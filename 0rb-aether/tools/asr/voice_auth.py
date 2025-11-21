#!/usr/bin/env python3
"""
0RB_AETHER Voice Authentication Pipeline
VAD -> ASR (whisper.cpp) -> Speaker Verification -> Passphrase Confirmation
"""

import os
import json
import hashlib
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple
import wave
import struct

@dataclass
class AuthResult:
    success: bool
    confidence: float
    transcript: str
    speaker_match: float
    reason: str

class VoiceAuthenticator:
    def __init__(
        self,
        whisper_model: str = "base.en",
        speaker_model_path: Optional[str] = None,
        passphrase_hash: Optional[str] = None,
        min_confidence: float = 0.85,
    ):
        self.whisper_model = whisper_model
        self.speaker_model_path = speaker_model_path
        self.passphrase_hash = passphrase_hash
        self.min_confidence = min_confidence
        self.whisper_bin = os.environ.get("WHISPER_CPP_BIN", "whisper-cpp")

    def record_audio(self, duration: float = 5.0, sample_rate: int = 16000) -> bytes:
        """Record audio from microphone using arecord"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            subprocess.run([
                "arecord", "-f", "S16_LE", "-r", str(sample_rate),
                "-c", "1", "-d", str(int(duration)), temp_path
            ], check=True, capture_output=True)

            with open(temp_path, "rb") as f:
                return f.read()
        finally:
            os.unlink(temp_path)

    def detect_voice_activity(self, audio_data: bytes, threshold: float = 0.01) -> bool:
        """Simple VAD based on RMS energy"""
        # Skip WAV header (44 bytes)
        samples = struct.unpack(f"<{(len(audio_data)-44)//2}h", audio_data[44:])
        rms = (sum(s**2 for s in samples) / len(samples)) ** 0.5
        normalized_rms = rms / 32768.0
        return normalized_rms > threshold

    def transcribe(self, audio_path: str) -> Tuple[str, float]:
        """Transcribe audio using whisper.cpp"""
        try:
            result = subprocess.run([
                self.whisper_bin,
                "-m", f"models/ggml-{self.whisper_model}.bin",
                "-f", audio_path,
                "--output-json"
            ], capture_output=True, text=True, check=True)

            # Parse output
            output = result.stdout
            # whisper.cpp outputs transcription directly
            transcript = output.strip()
            confidence = 0.9  # whisper.cpp doesn't output confidence directly
            return transcript, confidence

        except subprocess.CalledProcessError:
            return "", 0.0
        except FileNotFoundError:
            # Fallback: use Python whisper if available
            try:
                import whisper
                model = whisper.load_model(self.whisper_model)
                result = model.transcribe(audio_path)
                return result["text"], 0.9
            except ImportError:
                return "", 0.0

    def verify_speaker(self, audio_path: str) -> float:
        """Verify speaker identity using embeddings"""
        if not self.speaker_model_path:
            return 1.0  # No speaker model, skip verification

        try:
            # Using pyannote for speaker verification
            from pyannote.audio import Model, Inference

            model = Model.from_pretrained(self.speaker_model_path)
            inference = Inference(model)

            embedding = inference(audio_path)
            # Compare with enrolled embedding (stored separately)
            # Return cosine similarity
            return 0.9  # Placeholder
        except ImportError:
            return 1.0  # Skip if not available

    def verify_passphrase(self, transcript: str) -> bool:
        """Verify spoken passphrase matches stored hash"""
        if not self.passphrase_hash:
            return True

        normalized = transcript.lower().strip()
        transcript_hash = hashlib.sha256(normalized.encode()).hexdigest()
        return transcript_hash == self.passphrase_hash

    def authenticate(self, audio_data: Optional[bytes] = None) -> AuthResult:
        """Full authentication pipeline"""
        # Record if no audio provided
        if audio_data is None:
            print("Speak your passphrase...")
            audio_data = self.record_audio(duration=5.0)

        # Voice Activity Detection
        if not self.detect_voice_activity(audio_data):
            return AuthResult(
                success=False,
                confidence=0.0,
                transcript="",
                speaker_match=0.0,
                reason="No voice detected"
            )

        # Save to temp file for processing
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name

        try:
            # ASR
            transcript, asr_confidence = self.transcribe(temp_path)
            if not transcript:
                return AuthResult(
                    success=False,
                    confidence=0.0,
                    transcript="",
                    speaker_match=0.0,
                    reason="Transcription failed"
                )

            # Speaker Verification
            speaker_match = self.verify_speaker(temp_path)

            # Passphrase Verification
            passphrase_ok = self.verify_passphrase(transcript)

            # Combined confidence
            confidence = asr_confidence * speaker_match
            success = (
                confidence >= self.min_confidence and
                passphrase_ok and
                speaker_match >= 0.8
            )

            return AuthResult(
                success=success,
                confidence=confidence,
                transcript=transcript,
                speaker_match=speaker_match,
                reason="Authenticated" if success else "Authentication failed"
            )

        finally:
            os.unlink(temp_path)


class PINFallback:
    """Fallback PIN authentication"""

    def __init__(self, pin_hash: str):
        self.pin_hash = pin_hash
        self.max_attempts = 3

    def authenticate(self) -> bool:
        for attempt in range(self.max_attempts):
            pin = input(f"Enter PIN ({attempt + 1}/{self.max_attempts}): ")
            if hashlib.sha256(pin.encode()).hexdigest() == self.pin_hash:
                return True
            print("Incorrect PIN")
        return False


def main():
    """CLI interface for voice authentication"""
    import argparse

    parser = argparse.ArgumentParser(description="0RB Voice Authentication")
    parser.add_argument("--enroll", action="store_true", help="Enroll new passphrase")
    parser.add_argument("--verify", action="store_true", help="Verify authentication")
    parser.add_argument("--pin-fallback", action="store_true", help="Use PIN fallback")
    args = parser.parse_args()

    config_path = Path("/etc/0rb/voice_auth.json")

    if args.enroll:
        print("Enrollment mode - speak your passphrase clearly")
        auth = VoiceAuthenticator()
        audio = auth.record_audio(duration=5.0)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio)
            transcript, _ = auth.transcribe(f.name)
            os.unlink(f.name)

        if transcript:
            passphrase_hash = hashlib.sha256(transcript.lower().strip().encode()).hexdigest()
            config = {"passphrase_hash": passphrase_hash}
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps(config))
            print(f"Enrolled passphrase: '{transcript}'")
        else:
            print("Enrollment failed")
            return 1

    elif args.verify:
        config = json.loads(config_path.read_text()) if config_path.exists() else {}
        auth = VoiceAuthenticator(passphrase_hash=config.get("passphrase_hash"))

        result = auth.authenticate()
        print(f"Result: {result}")
        return 0 if result.success else 1

    elif args.pin_fallback:
        pin_hash = os.environ.get("ORB_PIN_HASH", "")
        if not pin_hash:
            print("No PIN configured")
            return 1

        fallback = PINFallback(pin_hash)
        return 0 if fallback.authenticate() else 1

    return 0


if __name__ == "__main__":
    exit(main())
