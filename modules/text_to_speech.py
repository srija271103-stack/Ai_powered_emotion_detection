"""
Emotion-Aware Text-to-Speech Module - FIXED VERSION
====================================================
FIXES:
- Generates UNIQUE audio file for each request (no caching)
- Uses timestamp + random ID in filename
- Cleans up old TTS files

EMPATHETIC TTS RESPONSE RULES:
- SAD/DEPRESSED: Speak softly, gently, and reassuringly. Slow pace.
- ANGRY/FRUSTRATED: Speak calmly and grounding. Do NOT match anger.
- HAPPY: Speak warmly and positively. Encourage reflection.
- NEUTRAL/CONFUSED: Speak supportive and clarifying.
"""

import os
import tempfile
import time
import uuid
from typing import Dict, Optional
from dataclasses import dataclass
from loguru import logger
from pathlib import Path

from configs.config import config


@dataclass
class VoiceSettings:
    """Voice synthesis settings for emotion-aware TTS."""
    speed: float
    pitch: float
    warmth: str
    tone_description: str


class EmotionAwareTTS:
    """
    Text-to-Speech with emotion-aware voice modulation.
    
    FIXED: Now generates unique files every time (no caching issues)
    """
    
    def __init__(self):
        self.tts = None
        self.tts_engine = None
        self.model_name = config.tts.model_name
        
        # Create a dedicated TTS output directory
        self.output_dir = Path(tempfile.gettempdir()) / "emovoice_tts"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean old files on startup
        self._cleanup_old_files()
        
        # Emotion-specific voice settings
        self.emotion_voice_settings = {
            # SAD - Soft, warm, slow, comforting
            "sad": VoiceSettings(
                speed=0.80,
                pitch=0.95,
                warmth="very_high",
                tone_description="soft, gentle, reassuring, slow pace"
            ),
            "sadness": VoiceSettings(
                speed=0.80,
                pitch=0.95,
                warmth="very_high",
                tone_description="soft, gentle, reassuring, slow pace"
            ),
            
            # ANGRY - Calm, grounding, steady
            "angry": VoiceSettings(
                speed=0.88,
                pitch=1.0,
                warmth="high",
                tone_description="calm, grounding, steady"
            ),
            "anger": VoiceSettings(
                speed=0.88,
                pitch=1.0,
                warmth="high",
                tone_description="calm, grounding, steady"
            ),
            
            # HAPPY - Warm, positive
            "happy": VoiceSettings(
                speed=0.95,
                pitch=1.02,
                warmth="medium",
                tone_description="warm, positive, encouraging"
            ),
            "joy": VoiceSettings(
                speed=0.95,
                pitch=1.02,
                warmth="medium",
                tone_description="warm, positive, encouraging"
            ),
            
            # NEUTRAL - Supportive, clear
            "neutral": VoiceSettings(
                speed=0.92,
                pitch=1.0,
                warmth="medium",
                tone_description="supportive, clarifying, balanced"
            ),
            
            # FEAR/ANXIETY
            "fear": VoiceSettings(
                speed=0.82,
                pitch=0.95,
                warmth="very_high",
                tone_description="very gentle, protective, warm"
            ),
            "anxiety": VoiceSettings(
                speed=0.85,
                pitch=0.98,
                warmth="very_high",
                tone_description="reassuring, gentle, steady"
            ),
        }
        
        self._init_tts()
    
    def _cleanup_old_files(self, max_age_seconds: int = 3600):
        """Clean up TTS files older than max_age_seconds."""
        try:
            current_time = time.time()
            for file_path in self.output_dir.glob("tts_*.mp3"):
                if current_time - file_path.stat().st_mtime > max_age_seconds:
                    file_path.unlink()
                    logger.debug(f"Cleaned up old TTS file: {file_path}")
            for file_path in self.output_dir.glob("tts_*.wav"):
                if current_time - file_path.stat().st_mtime > max_age_seconds:
                    file_path.unlink()
                    logger.debug(f"Cleaned up old TTS file: {file_path}")
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
    
    def _init_tts(self):
        """Initialize TTS engine."""
        # Try gTTS first (most reliable)
        try:
            from gtts import gTTS
            self.tts = "gtts"
            self.tts_engine = "gtts"
            logger.info("✅ gTTS initialized as TTS engine")
            return
        except ImportError:
            logger.warning("gTTS not installed, trying Coqui TTS...")
        
        # Try Coqui TTS
        try:
            from TTS.api import TTS
            self.tts = TTS(self.model_name)
            self.tts_engine = "coqui"
            logger.info(f"✅ Coqui TTS initialized: {self.model_name}")
            return
        except Exception as e:
            logger.warning(f"Coqui TTS not available: {e}")
        
        self.tts = None
        self.tts_engine = None
        logger.warning("⚠️ No TTS engine available")
    
    def get_voice_settings(self, emotion: str) -> VoiceSettings:
        """Get voice settings for emotion."""
        emotion_lower = emotion.lower()
        return self.emotion_voice_settings.get(
            emotion_lower,
            self.emotion_voice_settings["neutral"]
        )
    
    def synthesize(
        self,
        text: str,
        emotion: str = "neutral",
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Synthesize speech with emotion-appropriate voice.
        
        FIXED: Always generates a NEW unique file (no caching)
        
        Args:
            text: Text to speak
            emotion: Detected emotion for voice styling
            output_path: Optional path (ignored - always creates unique file)
            
        Returns:
            Path to generated audio file, or None if failed
        """
        if not self.tts:
            logger.warning("TTS not available")
            return None
        
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS")
            return None
        
        # Get emotion-based settings
        settings = self.get_voice_settings(emotion)
        
        # ============================================
        # FIXED: Always generate UNIQUE filename
        # Using timestamp + UUID to ensure no caching
        # ============================================
        timestamp = int(time.time() * 1000)  # Milliseconds
        unique_id = uuid.uuid4().hex[:8]
        
        if self.tts_engine == "gtts":
            suffix = ".mp3"
        else:
            suffix = ".wav"
        
        filename = f"tts_{emotion}_{timestamp}_{unique_id}{suffix}"
        output_path = str(self.output_dir / filename)
        
        logger.info(f"🔊 Generating TTS: {filename}")
        logger.info(f"   Emotion: {emotion}")
        logger.info(f"   Style: {settings.tone_description}")
        
        try:
            if self.tts_engine == "gtts":
                return self._synthesize_gtts(text, settings, output_path)
            elif self.tts_engine == "coqui":
                return self._synthesize_coqui(text, settings, output_path)
            else:
                return None
                
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _synthesize_gtts(
        self,
        text: str,
        settings: VoiceSettings,
        output_path: str
    ) -> Optional[str]:
        """Synthesize using Google TTS."""
        from gtts import gTTS
        
        # Slow parameter based on speed setting
        slow = settings.speed < 0.9
        
        tts = gTTS(text=text, lang='en', slow=slow)
        tts.save(output_path)
        
        # Apply warmth processing if needed
        if settings.warmth in ["high", "very_high"]:
            output_path = self._apply_warmth(output_path, settings.warmth)
        
        logger.info(f"✅ TTS saved: {output_path}")
        return output_path
    
    def _synthesize_coqui(
        self,
        text: str,
        settings: VoiceSettings,
        output_path: str
    ) -> Optional[str]:
        """Synthesize using Coqui TTS."""
        self.tts.tts_to_file(
            text=text,
            file_path=output_path,
            speed=settings.speed
        )
        
        # Apply warmth processing if needed
        if settings.warmth in ["high", "very_high"]:
            output_path = self._apply_warmth(output_path, settings.warmth)
        
        logger.info(f"✅ TTS saved: {output_path}")
        return output_path
    
    def _apply_warmth(self, audio_path: str, warmth_level: str) -> str:
        """Apply warmth processing to soften the voice."""
        try:
            import librosa
            import soundfile as sf
            import numpy as np
            from scipy.signal import butter, filtfilt
            
            y, sr = librosa.load(audio_path, sr=None)
            
            # Low-pass filter for warmth
            if warmth_level == "very_high":
                cutoff = 5500
            else:
                cutoff = 7000
            
            nyquist = sr / 2
            normalized_cutoff = cutoff / nyquist
            b, a = butter(2, normalized_cutoff, btype='low')
            y_warm = filtfilt(b, a, y)
            
            # Normalize
            y_warm = y_warm / np.max(np.abs(y_warm)) * 0.95
            
            sf.write(audio_path, y_warm, sr)
            
            return audio_path
            
        except Exception as e:
            logger.warning(f"Warmth processing failed: {e}")
            return audio_path


class MockTTS:
    """Mock TTS for testing."""
    
    def synthesize(self, text: str, emotion: str = "neutral", output_path: Optional[str] = None) -> Optional[str]:
        logger.info(f"[MOCK TTS] {emotion}: '{text[:50]}...'")
        return None
    
    def get_voice_settings(self, emotion: str) -> VoiceSettings:
        return VoiceSettings(speed=0.92, pitch=1.0, warmth="medium", tone_description="mock")


def get_tts():
    """Get TTS instance."""
    tts_instance = EmotionAwareTTS()
    if tts_instance.tts is None:
        logger.warning("Using mock TTS")
        return MockTTS()
    return tts_instance


# Singleton instance
emotion_tts = get_tts()