"""
Emotion Fusion Module
Combines voice (prosody) and text emotions for highest accuracy
Formula: Final = 0.65 × Voice + 0.35 × Text
"""

from typing import Dict, Tuple
from dataclasses import dataclass
from loguru import logger

from configs.config import config
from modules.prosody_emotion import EmotionResult
from modules.text_emotion import TextEmotionResult


@dataclass
class FusedEmotionResult:
    """Container for fused emotion analysis."""
    primary_emotion: str
    confidence: float
    all_emotions: Dict[str, float]
    intensity: float
    intensity_level: str  # mild, moderate, high, crisis
    voice_contribution: Dict[str, float]
    text_contribution: Dict[str, float]
    key_phrases: list
    requires_crisis_response: bool


class EmotionFusion:
    """
    Fuses voice and text emotion signals for accurate detection.
    
    Why fusion works:
    - Voice captures HOW they feel (tone, pitch, rhythm)
    - Text captures WHY they feel (context, reasons)
    - Combined = highest accuracy possible
    
    Default weights:
    - Voice: 0.65 (primary - more reliable for emotional state)
    - Text: 0.35 (secondary - provides context)
    """
    
    def __init__(self):
        self.voice_weight = config.emotion.voice_weight
        self.text_weight = config.emotion.text_weight
        
        # Intensity thresholds
        self.mild_threshold = config.emotion.mild_threshold
        self.moderate_threshold = config.emotion.moderate_threshold
        self.high_threshold = config.emotion.high_threshold
        self.crisis_threshold = config.emotion.crisis_threshold
    
    def fuse_emotions(
        self,
        voice_emotion: EmotionResult,
        text_emotion: TextEmotionResult
    ) -> FusedEmotionResult:
        """
        Fuse voice and text emotions into single result.
        
        Args:
            voice_emotion: Prosody-based emotion from Hume AI
            text_emotion: Text-based emotion from LLM analysis
            
        Returns:
            FusedEmotionResult with combined analysis
        """
        logger.info("Fusing voice and text emotions...")
        
        # Get all emotion categories
        all_categories = set(
            list(voice_emotion.all_emotions.keys()) +
            list(text_emotion.all_emotions.keys())
        )
        
        # Calculate fused scores for each emotion
        fused_emotions = {}
        
        for emotion in all_categories:
            voice_score = voice_emotion.all_emotions.get(emotion, 0)
            text_score = text_emotion.all_emotions.get(emotion, 0)
            
            # Weighted fusion
            fused_score = (
                self.voice_weight * voice_score +
                self.text_weight * text_score
            )
            
            fused_emotions[emotion] = round(fused_score, 4)
        
        # Ensure required emotions exist
        for emotion in ["sadness", "anger", "fear", "anxiety", "joy", "neutral"]:
            if emotion not in fused_emotions:
                fused_emotions[emotion] = 0.0
        
        # Find primary emotion
        primary_emotion = max(fused_emotions, key=fused_emotions.get)
        confidence = fused_emotions[primary_emotion]
        
        # Calculate intensity
        intensity = self._calculate_intensity(
            fused_emotions,
            voice_emotion.intensity
        )
        
        # Determine intensity level
        intensity_level = self._get_intensity_level(intensity)
        
        # Check for crisis indicators
        requires_crisis = self._check_crisis_indicators(
            intensity,
            text_emotion.key_phrases,
            fused_emotions
        )
        
        result = FusedEmotionResult(
            primary_emotion=primary_emotion,
            confidence=round(confidence, 3),
            all_emotions=fused_emotions,
            intensity=round(intensity, 3),
            intensity_level=intensity_level,
            voice_contribution=voice_emotion.all_emotions,
            text_contribution=text_emotion.all_emotions,
            key_phrases=text_emotion.key_phrases,
            requires_crisis_response=requires_crisis
        )
        
        logger.info(
            f"Fused result: {primary_emotion} "
            f"(confidence: {confidence:.2f}, intensity: {intensity:.2f})"
        )
        
        return result
    
    def _calculate_intensity(
        self,
        emotions: Dict[str, float],
        voice_intensity: float
    ) -> float:
        """
        Calculate overall emotional intensity.
        
        Considers:
        - Distance from neutral state
        - Presence of distress emotions
        - Voice intensity signal
        """
        # Distress emotion weights
        distress_weights = {
            "sadness": 1.5,
            "fear": 1.5,
            "anxiety": 1.4,
            "anger": 1.2,
            "frustration": 1.1
        }
        
        # Calculate weighted distress score
        distress_score = 0
        for emotion, weight in distress_weights.items():
            distress_score += emotions.get(emotion, 0) * weight
        
        # Factor in neutral (lower neutral = higher intensity)
        neutral_factor = 1 - emotions.get("neutral", 0)
        
        # Combine with voice intensity
        intensity = (
            0.4 * (distress_score / sum(distress_weights.values())) +
            0.3 * neutral_factor +
            0.3 * voice_intensity
        )
        
        return min(1.0, intensity)
    
    def _get_intensity_level(self, intensity: float) -> str:
        """Convert intensity score to level string."""
        if intensity >= self.crisis_threshold:
            return "crisis"
        elif intensity >= self.high_threshold:
            return "high"
        elif intensity >= self.moderate_threshold:
            return "moderate"
        elif intensity >= self.mild_threshold:
            return "mild"
        else:
            return "low"
    
    def _check_crisis_indicators(
        self,
        intensity: float,
        key_phrases: list,
        emotions: Dict[str, float]
    ) -> bool:
        """
        Check for crisis-level distress requiring special handling.
        
        Triggers:
        - Very high intensity
        - Crisis keywords in text
        - Extreme sadness + fear combination
        """
        # Crisis keywords
        crisis_keywords = config.safety.crisis_keywords
        
        # Check intensity threshold
        if intensity >= self.crisis_threshold:
            return True
        
        # Check for crisis keywords
        phrases_text = " ".join(key_phrases).lower()
        for keyword in crisis_keywords:
            if keyword in phrases_text:
                logger.warning(f"Crisis keyword detected: {keyword}")
                return True
        
        # Check emotion combination (sadness + fear + high intensity)
        if (emotions.get("sadness", 0) > 0.6 and
            emotions.get("fear", 0) > 0.4 and
            intensity > self.high_threshold):
            return True
        
        return False
    
    def adjust_weights(
        self,
        voice_weight: float = None,
        text_weight: float = None
    ):
        """
        Adjust fusion weights dynamically.
        
        Useful for:
        - Very emotional voice but neutral text → increase voice weight
        - Clear text expression but unclear voice → increase text weight
        """
        if voice_weight is not None:
            self.voice_weight = voice_weight
        if text_weight is not None:
            self.text_weight = text_weight
        
        # Ensure weights sum to 1
        total = self.voice_weight + self.text_weight
        self.voice_weight /= total
        self.text_weight /= total
        
        logger.info(f"Adjusted weights: voice={self.voice_weight:.2f}, text={self.text_weight:.2f}")


# Singleton instance
emotion_fusion = EmotionFusion()
