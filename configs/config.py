"""
Mental Wellness Companion - Configuration Settings
Contains all configurable parameters for the application.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AudioConfig:
    """Audio processing configuration."""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    max_recording_seconds: int = 120
    silence_threshold: float = 0.01
    min_speech_duration: float = 0.5
    vad_aggressiveness: int = 2  # 0-3, higher = more aggressive


@dataclass
class EmotionConfig:
    """Emotion detection configuration."""
    # Emotion fusion weights
    voice_weight: float = 0.65
    text_weight: float = 0.35
    
    # Intensity thresholds
    mild_threshold: float = 0.3
    moderate_threshold: float = 0.5
    high_threshold: float = 0.7
    crisis_threshold: float = 0.85
    
    # Supported emotions
    emotions: List[str] = field(default_factory=lambda: [
        "sadness", "anger", "fear", "anxiety", 
        "joy", "neutral", "confusion", "frustration"
    ])
    
    # Emotion to wellness module mapping
    emotion_modules: Dict[str, List[str]] = field(default_factory=lambda: {
        "sadness": ["guided_meditation", "journaling", "self_compassion", "breathing"],
        "anger": ["breathing", "grounding", "yoga", "body_scan"],
        "anxiety": ["mindfulness", "body_scan", "reassurance", "grounding"],
        "fear": ["safety_grounding", "calming_exercises", "reassurance", "breathing"],
        "frustration": ["breathing", "grounding", "reflection", "yoga"],
        "confusion": ["reflection", "mindfulness", "journaling"],
        "joy": ["gratitude", "mindfulness", "reflection"],
        "neutral": ["general_wellness", "reflection", "mindfulness"]
    })


@dataclass
class TTSConfig:
    """Text-to-Speech configuration."""
    model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"
    
    # Emotion-based voice settings
    emotion_voice_settings: Dict[str, Dict] = field(default_factory=lambda: {
        "sadness": {"speed": 0.85, "pitch": 0.95, "warmth": "high"},
        "anger": {"speed": 0.90, "pitch": 1.0, "warmth": "medium"},
        "anxiety": {"speed": 0.88, "pitch": 0.98, "warmth": "high"},
        "fear": {"speed": 0.82, "pitch": 0.95, "warmth": "very_high"},
        "frustration": {"speed": 0.88, "pitch": 1.0, "warmth": "medium"},
        "neutral": {"speed": 0.92, "pitch": 1.0, "warmth": "medium"},
        "joy": {"speed": 0.95, "pitch": 1.02, "warmth": "medium"},
        "confusion": {"speed": 0.90, "pitch": 1.0, "warmth": "medium"}
    })


@dataclass
class LLMConfig:
    """LLM configuration for response generation."""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 300
    temperature: float = 0.7


@dataclass
class SafetyConfig:
    """Safety and crisis detection configuration."""
    crisis_keywords: List[str] = field(default_factory=lambda: [
        "suicide", "kill myself", "end it all", "don't want to live",
        "hurt myself", "self harm", "no point", "give up",
        "hopeless", "can't go on", "want to die", "ending my life"
    ])
    
    crisis_resources: Dict[str, str] = field(default_factory=lambda: {
        "US": "988 Suicide & Crisis Lifeline: Call or text 988",
        "UK": "Samaritans: 116 123",
        "India": "iCall: 9152987821 | Vandrevala Foundation: 1860-2662-345",
        "International": "Find your local helpline at findahelpline.com"
    })


@dataclass
class AppConfig:
    """Main application configuration."""
    audio: AudioConfig = field(default_factory=AudioConfig)
    emotion: EmotionConfig = field(default_factory=EmotionConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    
    # API Keys from environment
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    hume_api_key: str = field(default_factory=lambda: os.getenv("HUME_API_KEY", ""))
    hume_secret_key: str = field(default_factory=lambda: os.getenv("HUME_SECRET_KEY", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    
    # Debug settings
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


# Global config instance
config = AppConfig()
