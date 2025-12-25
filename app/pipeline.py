"""
Mental Wellness Companion - Main Pipeline

Pipeline Flow:
Voice → Noise removal → Voice isolation → Prosody emotion → 
Whisper STT → Emotion fusion → Wellness logic → 
Empathetic text → Emotional voice response
"""

import asyncio
from typing import Optional, Tuple
from dataclasses import dataclass
from loguru import logger
import time

from configs.config import config
from modules.audio_processor import audio_processor
from modules.prosody_emotion import prosody_detector
from modules.speech_to_text import transcriber
from modules.text_emotion import text_analyzer
from modules.emotion_fusion import emotion_fusion, FusedEmotionResult
from modules.wellness_engine import wellness_engine, WellnessSuggestion
from modules.response_generator import response_generator, ResponseContext
from modules.text_to_speech import emotion_tts
from modules.safety_checker import safety_checker, SafetyCheckResult


@dataclass
class PipelineResult:
    """Complete result from the wellness pipeline."""
    # Input
    original_audio_path: str
    processed_audio_path: str
    
    # Transcription
    transcribed_text: str
    detected_language: str
    
    # Emotion Analysis
    voice_emotion: str
    voice_confidence: float
    text_emotion: str
    fused_emotion: str
    emotion_intensity: float
    intensity_level: str
    all_emotions: dict
    
    # Safety
    safety_result: SafetyCheckResult
    
    # Response
    empathetic_response: str
    
    # Timing
    processing_time: float
    
    # Optional fields with defaults
    wellness_suggestion: Optional[WellnessSuggestion] = None
    response_audio_path: Optional[str] = None


class WellnessPipeline:
    """
    Main orchestrator for the Mental Wellness Companion.
    
    Pipeline Steps:
    1. Audio cleaning (noise reduction, VAD)
    2. Voice emotion detection (Prosody)
    3. Speech-to-text (Whisper)
    4. Text emotion analysis (LLM)
    5. Emotion fusion (voice + text)
    6. Safety check
    7. Wellness suggestion selection
    8. Empathetic response generation
    9. Emotion-aware TTS
    """
    
    def __init__(self):
        logger.info("Initializing Mental Wellness Pipeline...")
        
        # All modules are singletons, already initialized
        self.audio_processor = audio_processor
        self.prosody_detector = prosody_detector
        self.transcriber = transcriber
        self.text_analyzer = text_analyzer
        self.emotion_fusion = emotion_fusion
        self.wellness_engine = wellness_engine
        self.response_generator = response_generator
        self.tts = emotion_tts
        self.safety_checker = safety_checker
        
        logger.info("Pipeline initialized successfully")
    
    async def process(self, audio_path: str) -> PipelineResult:
        """
        Process audio through the complete wellness pipeline.
        
        Args:
            audio_path: Path to input audio file
            
        Returns:
            PipelineResult with all analysis and response
        """
        start_time = time.time()
        logger.info(f"Starting pipeline processing: {audio_path}")
        
        # ========================================
        # STEP 1: Audio Processing
        # ========================================
        logger.info("Step 1: Audio processing (noise reduction, VAD)")
        
        processed_audio, sample_rate, processed_path = self.audio_processor.process_audio(
            audio_path
        )
        
        logger.info(f"Audio processed: {len(processed_audio)/sample_rate:.2f}s")
        
        # ========================================
        # STEP 2: Parallel - Voice Emotion + STT
        # ========================================
        logger.info("Step 2: Voice emotion detection + Speech-to-text (parallel)")
        
        # Run prosody detection and transcription in parallel
        voice_emotion_task = self.prosody_detector.detect_emotion_from_file(processed_path)
        
        # Transcription (synchronous but fast)
        transcription = self.transcriber.transcribe_multilingual(processed_path)
        
        # Get voice emotion result
        voice_emotion = await voice_emotion_task
        
        logger.info(f"Transcription: '{transcription.text[:100]}...'")
        logger.info(f"Voice emotion: {voice_emotion.primary_emotion} ({voice_emotion.confidence:.2f})")
        
        # ========================================
        # STEP 3: Text Emotion Analysis
        # ========================================
        logger.info("Step 3: Text emotion analysis")
        
        text_emotion = await self.text_analyzer.analyze_text(transcription.text)
        
        logger.info(f"Text emotion: {text_emotion.primary_emotion} ({text_emotion.confidence:.2f})")
        
        # ========================================
        # STEP 4: Emotion Fusion
        # ========================================
        logger.info("Step 4: Emotion fusion (voice 65% + text 35%)")
        
        fused_emotion = self.emotion_fusion.fuse_emotions(voice_emotion, text_emotion)
        
        logger.info(
            f"Fused emotion: {fused_emotion.primary_emotion} "
            f"(intensity: {fused_emotion.intensity_level})"
        )
        
        # ========================================
        # STEP 5: Safety Check
        # ========================================
        logger.info("Step 5: Safety check")
        
        safety_result = self.safety_checker.check_safety(
            transcription.text,
            fused_emotion
        )
        
        if safety_result.is_crisis:
            logger.warning(f"SAFETY ALERT: Crisis detected - {safety_result.crisis_type}")
        
        # ========================================
        # STEP 6: Wellness Suggestion
        # ========================================
        logger.info("Step 6: Wellness suggestion selection")
        
        wellness_suggestion = None
        if not safety_result.should_skip_suggestion:
            wellness_suggestion = self.wellness_engine.get_suggestion(fused_emotion)
            logger.info(f"Suggestion: {wellness_suggestion.title}")
        else:
            logger.info("Skipping suggestion (prioritizing comfort)")
        
        # ========================================
        # STEP 7: Empathetic Response Generation
        # ========================================
        logger.info("Step 7: Generating empathetic response")
        
        # Create context for response generator
        response_context = self.response_generator.create_context(
            transcribed_text=transcription.text,
            emotion_result=fused_emotion,
            suggestion=wellness_suggestion
        )
        
        # Generate response
        empathetic_response = await self.response_generator.generate_response(response_context)
        
        # Add crisis resources if needed
        if safety_result.is_crisis:
            resource_text = self.safety_checker.get_resource_text(safety_result.crisis_resources)
            empathetic_response += resource_text
        
        logger.info(f"Response generated: {len(empathetic_response)} chars")
        
        # ========================================
        # STEP 8: Emotion-Aware TTS
        # ========================================
        logger.info("Step 8: Text-to-speech synthesis")
        
        response_audio_path = self.tts.synthesize(
            text=empathetic_response,
            emotion=fused_emotion.primary_emotion
        )
        
        if response_audio_path:
            logger.info(f"TTS output: {response_audio_path}")
        else:
            logger.info("TTS skipped (not available)")
        
        # ========================================
        # Complete - Build Result
        # ========================================
        processing_time = time.time() - start_time
        
        result = PipelineResult(
            original_audio_path=audio_path,
            processed_audio_path=processed_path,
            transcribed_text=transcription.text,
            detected_language=transcription.language,
            voice_emotion=voice_emotion.primary_emotion,
            voice_confidence=voice_emotion.confidence,
            text_emotion=text_emotion.primary_emotion,
            fused_emotion=fused_emotion.primary_emotion,
            emotion_intensity=fused_emotion.intensity,
            intensity_level=fused_emotion.intensity_level,
            all_emotions=fused_emotion.all_emotions,
            safety_result=safety_result,
            empathetic_response=empathetic_response,
            wellness_suggestion=wellness_suggestion,
            response_audio_path=response_audio_path,
            processing_time=processing_time
        )
        
        logger.info(f"Pipeline complete in {processing_time:.2f}s")
        
        return result
    
    def process_sync(self, audio_path: str) -> PipelineResult:
        """
        Synchronous wrapper for process().
        Use this from non-async code.
        """
        return asyncio.run(self.process(audio_path))


# Create singleton instance
pipeline = WellnessPipeline()


def process_audio(audio_path: str) -> PipelineResult:
    """
    Convenience function to process audio.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        PipelineResult with complete analysis
    """
    return pipeline.process_sync(audio_path)