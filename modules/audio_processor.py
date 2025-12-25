"""
Audio Processing Module
Handles: Noise suppression, Voice Activity Detection, Audio cleaning
"""

import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
from scipy import signal
from typing import Tuple, List, Optional
import tempfile
import os
from loguru import logger

from configs.config import config


class AudioProcessor:
    """
    Handles all audio preprocessing:
    - Noise reduction (AI-based)
    - Voice Activity Detection (VAD)
    - Audio normalization
    - Voice isolation
    """
    
    def __init__(self):
        self.sample_rate = config.audio.sample_rate
        self.silence_threshold = config.audio.silence_threshold
        self.min_speech_duration = config.audio.min_speech_duration
        
    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file and convert to mono.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            audio, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            logger.info(f"Loaded audio: {len(audio)/sr:.2f}s at {sr}Hz")
            return audio, sr
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
    
    def reduce_noise(self, audio: np.ndarray, sr: int = None) -> np.ndarray:
        """
        AI-based noise reduction using noisereduce library.
        Superior to simple filtering for emotional speech.
        
        Args:
            audio: Audio signal as numpy array
            sr: Sample rate (uses config default if None)
            
        Returns:
            Cleaned audio signal
        """
        sr = sr or self.sample_rate
        
        try:
            # Apply stationary noise reduction
            # This works well for background noise, hum, etc.
            reduced_noise = nr.reduce_noise(
                y=audio,
                sr=sr,
                stationary=True,
                prop_decrease=0.75,  # How much to reduce noise
                n_fft=2048,
                hop_length=512
            )
            
            # Apply non-stationary noise reduction for variable noise
            reduced_noise = nr.reduce_noise(
                y=reduced_noise,
                sr=sr,
                stationary=False,
                prop_decrease=0.5,
                n_fft=2048,
                hop_length=512
            )
            
            logger.info("Noise reduction applied successfully")
            return reduced_noise
            
        except Exception as e:
            logger.warning(f"Noise reduction failed, returning original: {e}")
            return audio
    
    def voice_activity_detection(self, audio: np.ndarray, sr: int = None) -> List[Tuple[int, int]]:
        """
        Detect voice segments in audio using energy-based VAD.
        Removes silence, background sounds, and non-speech segments.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            
        Returns:
            List of (start_sample, end_sample) tuples for voice segments
        """
        sr = sr or self.sample_rate
        
        # Calculate frame-level energy
        frame_length = int(0.025 * sr)  # 25ms frames
        hop_length = int(0.010 * sr)    # 10ms hop
        
        # Compute RMS energy for each frame
        rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Normalize RMS
        rms_normalized = rms / (np.max(rms) + 1e-10)
        
        # Dynamic threshold based on audio statistics
        threshold = max(self.silence_threshold, np.percentile(rms_normalized, 30))
        
        # Find voice segments
        is_speech = rms_normalized > threshold
        
        # Convert frame indices to sample indices
        voice_segments = []
        in_speech = False
        start_frame = 0
        
        for i, speech in enumerate(is_speech):
            if speech and not in_speech:
                start_frame = i
                in_speech = True
            elif not speech and in_speech:
                # Check minimum duration
                duration_frames = i - start_frame
                duration_seconds = duration_frames * hop_length / sr
                
                if duration_seconds >= self.min_speech_duration:
                    start_sample = start_frame * hop_length
                    end_sample = i * hop_length
                    voice_segments.append((start_sample, end_sample))
                
                in_speech = False
        
        # Handle case where speech continues to end
        if in_speech:
            duration_frames = len(is_speech) - start_frame
            duration_seconds = duration_frames * hop_length / sr
            
            if duration_seconds >= self.min_speech_duration:
                start_sample = start_frame * hop_length
                end_sample = len(audio)
                voice_segments.append((start_sample, end_sample))
        
        logger.info(f"Detected {len(voice_segments)} voice segments")
        return voice_segments
    
    def extract_voice_segments(self, audio: np.ndarray, segments: List[Tuple[int, int]]) -> np.ndarray:
        """
        Extract and concatenate voice segments from audio.
        
        Args:
            audio: Full audio signal
            segments: List of (start, end) sample indices
            
        Returns:
            Concatenated voice-only audio
        """
        if not segments:
            logger.warning("No voice segments found, returning original audio")
            return audio
        
        voice_audio = []
        for start, end in segments:
            voice_audio.append(audio[start:end])
            # Add small silence between segments (50ms)
            silence = np.zeros(int(0.05 * self.sample_rate))
            voice_audio.append(silence)
        
        return np.concatenate(voice_audio)
    
    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalize audio to consistent volume level.
        
        Args:
            audio: Input audio signal
            
        Returns:
            Normalized audio
        """
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val * 0.95  # Leave some headroom
        return audio
    
    def apply_gentle_compression(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply gentle dynamic range compression.
        Helps with emotional speech that may have varying volume.
        
        Args:
            audio: Input audio
            
        Returns:
            Compressed audio
        """
        # Simple soft-knee compression
        threshold = 0.5
        ratio = 3.0
        
        compressed = np.copy(audio)
        mask = np.abs(audio) > threshold
        compressed[mask] = np.sign(audio[mask]) * (
            threshold + (np.abs(audio[mask]) - threshold) / ratio
        )
        
        return self.normalize_audio(compressed)
    
    def process_audio(self, audio_path: str) -> Tuple[np.ndarray, int, str]:
        """
        Complete audio processing pipeline.
        
        Steps:
        1. Load audio
        2. Noise reduction (AI-based)
        3. Voice Activity Detection
        4. Extract voice segments
        5. Normalize and compress
        6. Save processed audio
        
        Args:
            audio_path: Path to input audio file
            
        Returns:
            Tuple of (processed_audio, sample_rate, processed_file_path)
        """
        logger.info(f"Processing audio: {audio_path}")
        
        # Step 1: Load audio
        audio, sr = self.load_audio(audio_path)
        
        # Step 2: Noise reduction
        clean_audio = self.reduce_noise(audio, sr)
        
        # Step 3: Voice Activity Detection
        voice_segments = self.voice_activity_detection(clean_audio, sr)
        
        # Step 4: Extract voice segments
        voice_only = self.extract_voice_segments(clean_audio, voice_segments)
        
        # Step 5: Normalize and compress
        normalized = self.normalize_audio(voice_only)
        final_audio = self.apply_gentle_compression(normalized)
        
        # Step 6: Save processed audio
        processed_path = self._save_processed_audio(final_audio, sr)
        
        logger.info(f"Audio processing complete: {len(final_audio)/sr:.2f}s")
        
        return final_audio, sr, processed_path
    
    def _save_processed_audio(self, audio: np.ndarray, sr: int) -> str:
        """Save processed audio to temporary file."""
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sf.write(temp_file.name, audio, sr)
        return temp_file.name


# Singleton instance
audio_processor = AudioProcessor()
