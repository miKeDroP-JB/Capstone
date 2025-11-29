#!/usr/bin/env python3
"""
VOICE ENGINE - Custom TTS/STT for AI Calling
High-quality voice synthesis and recognition.

Supports:
- ElevenLabs (highest quality)
- OpenAI TTS (good quality, fast)
- PlayHT (good alternative)
- Deepgram (best STT)
- Whisper (local STT)

Love - Loyalty - Honor - Everybody Eats
"""

import asyncio
import aiohttp
import base64
import json
import os
import wave
import io
from datetime import datetime
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

class TTSProvider(Enum):
    ELEVENLABS = "elevenlabs"
    OPENAI = "openai"
    PLAYHT = "playht"
    LOCAL = "local"


class STTProvider(Enum):
    DEEPGRAM = "deepgram"
    WHISPER_API = "whisper_api"
    WHISPER_LOCAL = "whisper_local"
    GOOGLE = "google"


@dataclass
class VoiceConfig:
    """Voice engine configuration"""
    # TTS settings
    tts_provider: TTSProvider = TTSProvider.ELEVENLABS
    tts_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs Rachel
    tts_model: str = "eleven_turbo_v2"
    tts_speed: float = 1.0
    tts_stability: float = 0.5
    tts_similarity: float = 0.75

    # STT settings
    stt_provider: STTProvider = STTProvider.DEEPGRAM
    stt_model: str = "nova-2"
    stt_language: str = "en-US"

    # Audio settings
    sample_rate: int = 16000
    channels: int = 1
    audio_format: str = "pcm"

    # API Keys (from environment)
    elevenlabs_api_key: str = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    deepgram_api_key: str = field(default_factory=lambda: os.getenv("DEEPGRAM_API_KEY", ""))
    playht_api_key: str = field(default_factory=lambda: os.getenv("PLAYHT_API_KEY", ""))


@dataclass
class Voice:
    """A voice profile"""
    id: str
    name: str
    provider: TTSProvider
    description: str = ""
    preview_url: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class TTSResult:
    """Result from TTS synthesis"""
    audio_data: bytes
    duration_ms: int
    characters: int
    provider: TTSProvider
    voice_id: str
    latency_ms: int


@dataclass
class STTResult:
    """Result from STT recognition"""
    text: str
    confidence: float
    words: List[Dict[str, Any]]  # word, start, end, confidence
    duration_ms: int
    provider: STTProvider
    latency_ms: int
    is_final: bool = True


# ═══════════════════════════════════════════════════════════════
# VOICE ENGINE
# ═══════════════════════════════════════════════════════════════

class VoiceEngine:
    """
    Custom voice engine for AI calling.
    Handles TTS and STT with multiple providers.
    """

    # Pre-configured voices for sales
    SALES_VOICES = {
        "professional_male": Voice(
            id="pNInz6obpgDQGcFmaJgB",
            name="Adam",
            provider=TTSProvider.ELEVENLABS,
            description="Professional male voice, great for B2B",
            tags=["male", "professional", "american"],
        ),
        "professional_female": Voice(
            id="21m00Tcm4TlvDq8ikWAM",
            name="Rachel",
            provider=TTSProvider.ELEVENLABS,
            description="Professional female voice, warm and friendly",
            tags=["female", "professional", "american"],
        ),
        "friendly_male": Voice(
            id="VR6AewLTigWG4xSOukaG",
            name="Arnold",
            provider=TTSProvider.ELEVENLABS,
            description="Friendly casual male voice",
            tags=["male", "casual", "american"],
        ),
        "energetic_female": Voice(
            id="EXAVITQu4vr4xnSDxMaL",
            name="Bella",
            provider=TTSProvider.ELEVENLABS,
            description="Energetic and enthusiastic",
            tags=["female", "energetic", "american"],
        ),
    }

    def __init__(self, config: VoiceConfig = None):
        self.config = config or VoiceConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self._audio_cache: Dict[str, bytes] = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    # ═══════════════════════════════════════════════════════════
    # TEXT TO SPEECH
    # ═══════════════════════════════════════════════════════════

    async def synthesize(
        self,
        text: str,
        voice_id: str = None,
        provider: TTSProvider = None,
        cache: bool = True,
    ) -> TTSResult:
        """
        Synthesize speech from text.
        Returns audio data ready for playback or streaming.
        """
        provider = provider or self.config.tts_provider
        voice_id = voice_id or self.config.tts_voice_id

        # Check cache
        cache_key = f"{provider.value}:{voice_id}:{hash(text)}"
        if cache and cache_key in self._audio_cache:
            return TTSResult(
                audio_data=self._audio_cache[cache_key],
                duration_ms=0,
                characters=len(text),
                provider=provider,
                voice_id=voice_id,
                latency_ms=0,
            )

        start_time = datetime.now()

        if provider == TTSProvider.ELEVENLABS:
            result = await self._synthesize_elevenlabs(text, voice_id)
        elif provider == TTSProvider.OPENAI:
            result = await self._synthesize_openai(text, voice_id)
        elif provider == TTSProvider.PLAYHT:
            result = await self._synthesize_playht(text, voice_id)
        else:
            raise ValueError(f"Unsupported TTS provider: {provider}")

        latency = int((datetime.now() - start_time).total_seconds() * 1000)
        result.latency_ms = latency

        # Cache result
        if cache:
            self._audio_cache[cache_key] = result.audio_data

        return result

    async def _synthesize_elevenlabs(self, text: str, voice_id: str) -> TTSResult:
        """Synthesize using ElevenLabs API"""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": self.config.elevenlabs_api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "text": text,
            "model_id": self.config.tts_model,
            "voice_settings": {
                "stability": self.config.tts_stability,
                "similarity_boost": self.config.tts_similarity,
            },
        }

        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                audio_data = await response.read()
                return TTSResult(
                    audio_data=audio_data,
                    duration_ms=len(audio_data) // 32,  # Rough estimate
                    characters=len(text),
                    provider=TTSProvider.ELEVENLABS,
                    voice_id=voice_id,
                    latency_ms=0,
                )
            else:
                error = await response.text()
                raise Exception(f"ElevenLabs API error: {error}")

    async def _synthesize_openai(self, text: str, voice_id: str) -> TTSResult:
        """Synthesize using OpenAI TTS API"""
        url = "https://api.openai.com/v1/audio/speech"

        headers = {
            "Authorization": f"Bearer {self.config.openai_api_key}",
            "Content-Type": "application/json",
        }

        # OpenAI voice options: alloy, echo, fable, onyx, nova, shimmer
        voice = voice_id if voice_id in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"] else "alloy"

        payload = {
            "model": "tts-1-hd",
            "input": text,
            "voice": voice,
            "response_format": "pcm",
        }

        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                audio_data = await response.read()
                return TTSResult(
                    audio_data=audio_data,
                    duration_ms=len(audio_data) // 32,
                    characters=len(text),
                    provider=TTSProvider.OPENAI,
                    voice_id=voice,
                    latency_ms=0,
                )
            else:
                error = await response.text()
                raise Exception(f"OpenAI TTS error: {error}")

    async def _synthesize_playht(self, text: str, voice_id: str) -> TTSResult:
        """Synthesize using PlayHT API"""
        url = "https://api.play.ht/api/v2/tts"

        headers = {
            "Authorization": f"Bearer {self.config.playht_api_key}",
            "X-User-ID": os.getenv("PLAYHT_USER_ID", ""),
            "Content-Type": "application/json",
        }

        payload = {
            "text": text,
            "voice": voice_id,
            "output_format": "mp3",
        }

        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                audio_data = await response.read()
                return TTSResult(
                    audio_data=audio_data,
                    duration_ms=len(audio_data) // 32,
                    characters=len(text),
                    provider=TTSProvider.PLAYHT,
                    voice_id=voice_id,
                    latency_ms=0,
                )
            else:
                error = await response.text()
                raise Exception(f"PlayHT error: {error}")

    async def stream_synthesize(
        self,
        text: str,
        voice_id: str = None,
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream TTS audio chunks for low-latency playback.
        Essential for real-time conversation.
        """
        voice_id = voice_id or self.config.tts_voice_id

        # ElevenLabs streaming endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

        headers = {
            "xi-api-key": self.config.elevenlabs_api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "text": text,
            "model_id": self.config.tts_model,
            "voice_settings": {
                "stability": self.config.tts_stability,
                "similarity_boost": self.config.tts_similarity,
            },
        }

        async with self.session.post(url, headers=headers, json=payload) as response:
            async for chunk in response.content.iter_chunked(1024):
                yield chunk

    # ═══════════════════════════════════════════════════════════
    # SPEECH TO TEXT
    # ═══════════════════════════════════════════════════════════

    async def transcribe(
        self,
        audio_data: bytes,
        provider: STTProvider = None,
    ) -> STTResult:
        """
        Transcribe audio to text.
        Returns transcription with word-level timestamps.
        """
        provider = provider or self.config.stt_provider
        start_time = datetime.now()

        if provider == STTProvider.DEEPGRAM:
            result = await self._transcribe_deepgram(audio_data)
        elif provider == STTProvider.WHISPER_API:
            result = await self._transcribe_whisper_api(audio_data)
        else:
            raise ValueError(f"Unsupported STT provider: {provider}")

        latency = int((datetime.now() - start_time).total_seconds() * 1000)
        result.latency_ms = latency

        return result

    async def _transcribe_deepgram(self, audio_data: bytes) -> STTResult:
        """Transcribe using Deepgram API"""
        url = "https://api.deepgram.com/v1/listen"

        headers = {
            "Authorization": f"Token {self.config.deepgram_api_key}",
            "Content-Type": "audio/wav",
        }

        params = {
            "model": self.config.stt_model,
            "language": self.config.stt_language,
            "punctuate": "true",
            "utterances": "true",
            "smart_format": "true",
        }

        async with self.session.post(url, headers=headers, params=params, data=audio_data) as response:
            if response.status == 200:
                data = await response.json()
                result = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0]

                return STTResult(
                    text=result.get("transcript", ""),
                    confidence=result.get("confidence", 0),
                    words=result.get("words", []),
                    duration_ms=int(data.get("metadata", {}).get("duration", 0) * 1000),
                    provider=STTProvider.DEEPGRAM,
                    latency_ms=0,
                )
            else:
                error = await response.text()
                raise Exception(f"Deepgram error: {error}")

    async def _transcribe_whisper_api(self, audio_data: bytes) -> STTResult:
        """Transcribe using OpenAI Whisper API"""
        url = "https://api.openai.com/v1/audio/transcriptions"

        headers = {
            "Authorization": f"Bearer {self.config.openai_api_key}",
        }

        # Create form data with audio file
        data = aiohttp.FormData()
        data.add_field('file', audio_data, filename='audio.wav', content_type='audio/wav')
        data.add_field('model', 'whisper-1')
        data.add_field('response_format', 'verbose_json')
        data.add_field('timestamp_granularities[]', 'word')

        async with self.session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                result = await response.json()

                return STTResult(
                    text=result.get("text", ""),
                    confidence=0.95,  # Whisper doesn't return confidence
                    words=result.get("words", []),
                    duration_ms=int(result.get("duration", 0) * 1000),
                    provider=STTProvider.WHISPER_API,
                    latency_ms=0,
                )
            else:
                error = await response.text()
                raise Exception(f"Whisper API error: {error}")

    async def stream_transcribe(
        self,
        audio_stream: AsyncGenerator[bytes, None],
    ) -> AsyncGenerator[STTResult, None]:
        """
        Stream STT for real-time transcription.
        Essential for live conversation.
        """
        # Deepgram streaming endpoint
        url = f"wss://api.deepgram.com/v1/listen?model={self.config.stt_model}&language={self.config.stt_language}"

        # In production: implement WebSocket connection to Deepgram
        # For now, batch process chunks

        buffer = b""
        async for chunk in audio_stream:
            buffer += chunk
            if len(buffer) >= 16000:  # ~1 second of audio
                result = await self.transcribe(buffer)
                yield result
                buffer = b""

    # ═══════════════════════════════════════════════════════════
    # VOICE MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def get_voices(self, provider: TTSProvider = None) -> List[Voice]:
        """Get available voices"""
        provider = provider or self.config.tts_provider

        if provider == TTSProvider.ELEVENLABS:
            return list(self.SALES_VOICES.values())
        else:
            return []

    async def clone_voice(
        self,
        name: str,
        audio_samples: List[bytes],
        description: str = "",
    ) -> Voice:
        """
        Clone a voice from audio samples.
        Requires ElevenLabs API.
        """
        url = "https://api.elevenlabs.io/v1/voices/add"

        headers = {
            "xi-api-key": self.config.elevenlabs_api_key,
        }

        data = aiohttp.FormData()
        data.add_field('name', name)
        data.add_field('description', description)

        for i, sample in enumerate(audio_samples):
            data.add_field(
                f'files',
                sample,
                filename=f'sample_{i}.mp3',
                content_type='audio/mpeg'
            )

        async with self.session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                result = await response.json()
                return Voice(
                    id=result["voice_id"],
                    name=name,
                    provider=TTSProvider.ELEVENLABS,
                    description=description,
                )
            else:
                error = await response.text()
                raise Exception(f"Voice cloning error: {error}")

    # ═══════════════════════════════════════════════════════════
    # UTILITIES
    # ═══════════════════════════════════════════════════════════

    def audio_to_wav(self, audio_data: bytes, sample_rate: int = 16000) -> bytes:
        """Convert raw PCM to WAV format"""
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(audio_data)
        return buffer.getvalue()

    def wav_to_audio(self, wav_data: bytes) -> bytes:
        """Extract PCM audio from WAV"""
        buffer = io.BytesIO(wav_data)
        with wave.open(buffer, 'rb') as wav:
            return wav.readframes(wav.getnframes())

    def save_audio(self, audio_data: bytes, filepath: str, format: str = "wav"):
        """Save audio to file"""
        if format == "wav":
            wav_data = self.audio_to_wav(audio_data)
            Path(filepath).write_bytes(wav_data)
        else:
            Path(filepath).write_bytes(audio_data)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

async def main():
    """Demo the voice engine"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                      VOICE ENGINE                             ║
║                                                               ║
║   Custom TTS/STT for high-quality AI calling                  ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    config = VoiceConfig()
    engine = VoiceEngine(config)

    print("Available voices:")
    for key, voice in engine.SALES_VOICES.items():
        print(f"  [{key}] {voice.name}: {voice.description}")

    print("\nTo synthesize speech, set your API keys:")
    print("  export ELEVENLABS_API_KEY=your_key")
    print("  export OPENAI_API_KEY=your_key")
    print("  export DEEPGRAM_API_KEY=your_key")

    # Demo synthesis (if API key available)
    if config.elevenlabs_api_key:
        async with engine:
            print("\nSynthesizing test speech...")
            result = await engine.synthesize(
                "Hello! This is your AI sales assistant. How can I help you today?",
                voice_id=engine.SALES_VOICES["professional_female"].id,
            )
            print(f"  Generated {len(result.audio_data)} bytes in {result.latency_ms}ms")
    else:
        print("\n  [!] Set ELEVENLABS_API_KEY to test synthesis")


if __name__ == "__main__":
    asyncio.run(main())
