"""NVIDIA Riva TTS audio generation for contact center transcripts."""

import io
import logging
import struct
import wave
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Voice mappings by speaker role and sentiment
AGENT_VOICE = "English-US.Male-1"
CUSTOMER_VOICES = {
    "neutral": "English-US.Female-1",
    "satisfied": "English-US.Female-2",
    "frustrated": "English-US.Male-2",
    "angry": "English-US.Male-3",
    "confused": "English-US.Female-1",
}

# Silence duration in seconds between turns
SILENCE_DURATION = 0.5


def _generate_silence_wav(duration_seconds: float, sample_rate: int = 22050) -> bytes:
    """Generate a WAV file containing silence."""
    num_samples = int(sample_rate * duration_seconds)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * num_samples)
    return buf.getvalue()


def _concat_wav_bytes(wav_list: list[bytes]) -> bytes:
    """Concatenate multiple WAV byte objects into one WAV file."""
    if not wav_list:
        return _generate_silence_wav(0.1)

    all_frames = b""
    params = None

    for wav_data in wav_list:
        buf = io.BytesIO(wav_data)
        try:
            with wave.open(buf, "rb") as wf:
                if params is None:
                    params = wf.getparams()
                all_frames += wf.readframes(wf.getnframes())
        except Exception as e:
            logger.warning(f"Could not read WAV segment: {e}")

    if params is None:
        return _generate_silence_wav(0.1)

    out_buf = io.BytesIO()
    with wave.open(out_buf, "wb") as wf:
        wf.setparams(params)
        wf.writeframes(all_frames)
    return out_buf.getvalue()


class AudioGenerator:
    """
    Generates audio from transcripts using NVIDIA Riva TTS.

    Requires RIVA_ENDPOINT environment variable to be set.
    Falls back to placeholder WAV files if Riva is not available.
    """

    def __init__(self, riva_endpoint: str | None = None):
        self.riva_endpoint = riva_endpoint
        self._riva_client = None

    def _get_riva_client(self):
        """Get or create Riva TTS client."""
        if self._riva_client is not None:
            return self._riva_client

        if not self.riva_endpoint:
            return None

        try:
            import riva.client
            auth = riva.client.Auth(uri=self.riva_endpoint)
            self._riva_client = riva.client.SpeechSynthesisServiceStub(auth.channel)
            return self._riva_client
        except ImportError:
            logger.warning("nvidia-riva-client not installed. Using placeholder audio.")
            return None
        except Exception as e:
            logger.warning(f"Could not connect to Riva at {self.riva_endpoint}: {e}")
            return None

    def _synthesize_turn(self, text: str, voice: str) -> bytes:
        """Synthesize a single turn of speech. Returns WAV bytes."""
        client = self._get_riva_client()

        if client is not None:
            try:
                import riva.client
                req = riva.client.SynthesizeSpeechRequest(
                    text=text[:500],  # Truncate very long turns
                    language_code="en-US",
                    encoding=riva.client.AudioEncoding.LINEAR_PCM,
                    sample_rate_hz=22050,
                    voice_name=voice,
                )
                resp = client.Synthesize(req)
                # Wrap raw PCM in WAV container
                buf = io.BytesIO()
                with wave.open(buf, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(22050)
                    wf.writeframes(resp.audio)
                return buf.getvalue()
            except Exception as e:
                logger.warning(f"Riva synthesis failed: {e}")

        # Fallback: generate silence placeholder of appropriate length
        # Approximate: 150 words per minute, 5 chars per word
        estimated_duration = max(0.5, len(text) / (150 * 5) * 60)
        return _generate_silence_wav(min(estimated_duration, 30))

    def generate_transcript_audio(self, transcript: dict) -> bytes:
        """Generate a single audio file for a transcript. Returns WAV bytes."""
        customer_sentiment = transcript.get("customer", {}).get("sentiment", "neutral")
        customer_voice = CUSTOMER_VOICES.get(customer_sentiment, CUSTOMER_VOICES["neutral"])

        silence = _generate_silence_wav(SILENCE_DURATION)
        segments = []

        for turn in transcript.get("conversation", []):
            speaker = turn.get("speaker", "agent")
            text = turn.get("text", "")
            if not text.strip():
                continue

            voice = AGENT_VOICE if speaker == "agent" else customer_voice
            audio_segment = self._synthesize_turn(text, voice)
            segments.append(audio_segment)
            segments.append(silence)

        if not segments:
            return _generate_silence_wav(1.0)

        return _concat_wav_bytes(segments)

    def generate_batch_audio(
        self,
        transcripts: list[dict],
        artifacts_dir: Path,
        job_id: str,
    ) -> Path:
        """
        Generate audio for all transcripts in a batch.
        Returns path to the ZIP file containing all WAV files.
        """
        zip_path = artifacts_dir / f"{job_id}_audio.zip"
        zip_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, transcript in enumerate(transcripts):
                transcript_id = transcript.get("id", f"transcript_{i}")
                logger.info(f"Generating audio for transcript {transcript_id} ({i+1}/{len(transcripts)})")

                wav_bytes = self.generate_transcript_audio(transcript)
                wav_filename = f"{transcript_id}.wav"
                zf.writestr(wav_filename, wav_bytes)

        return zip_path
