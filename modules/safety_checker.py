"""
Safety and Crisis Detection Module
Ensures responsible handling of users in distress
"""

from typing import Tuple, List, Optional
from dataclasses import dataclass
from loguru import logger

from configs.config import config
from modules.emotion_fusion import FusedEmotionResult


@dataclass
class SafetyCheckResult:
    """Result of safety assessment."""
    is_crisis: bool
    is_high_distress: bool
    crisis_type: Optional[str]  # self_harm, hopelessness, extreme_distress
    recommended_action: str
    crisis_resources: List[str]
    should_skip_suggestion: bool
    priority_message: Optional[str]


class SafetyChecker:
    """
    Safety and ethical check module.
    
    Responsibilities:
    - Detect crisis-level distress
    - Identify self-harm indicators
    - Provide appropriate crisis resources
    - Ensure responsible response behavior
    
    This is MANDATORY for any mental wellness application.
    """
    
    def __init__(self):
        self.crisis_keywords = config.safety.crisis_keywords
        self.crisis_resources = config.safety.crisis_resources
        
        # Additional patterns for detection
        self.self_harm_patterns = [
            "hurt myself", "harm myself", "cut myself",
            "end my life", "end it all", "kill myself",
            "don't want to live", "better off dead",
            "no reason to live", "give up on life"
        ]
        
        self.hopelessness_patterns = [
            "no hope", "hopeless", "nothing matters",
            "no point", "worthless", "burden",
            "nobody cares", "alone forever", "give up"
        ]
        
        self.extreme_distress_patterns = [
            "can't take it", "breaking down", "falling apart",
            "losing my mind", "can't cope", "drowning",
            "crushing me", "suffocating"
        ]
    
    def check_safety(
        self,
        transcribed_text: str,
        emotion_result: FusedEmotionResult
    ) -> SafetyCheckResult:
        """
        Perform comprehensive safety check.
        
        Args:
            transcribed_text: User's spoken words
            emotion_result: Fused emotion analysis
            
        Returns:
            SafetyCheckResult with assessment and recommendations
        """
        text_lower = transcribed_text.lower()
        
        # Check for different crisis types
        self_harm_detected = self._check_patterns(text_lower, self.self_harm_patterns)
        hopelessness_detected = self._check_patterns(text_lower, self.hopelessness_patterns)
        extreme_distress = self._check_patterns(text_lower, self.extreme_distress_patterns)
        crisis_keyword = self._check_patterns(text_lower, self.crisis_keywords)
        
        # Determine crisis type
        crisis_type = None
        is_crisis = False
        
        if self_harm_detected:
            crisis_type = "self_harm"
            is_crisis = True
            logger.warning("SAFETY: Self-harm indicators detected")
        elif hopelessness_detected and emotion_result.intensity >= 0.7:
            crisis_type = "hopelessness"
            is_crisis = True
            logger.warning("SAFETY: Hopelessness with high intensity detected")
        elif crisis_keyword:
            crisis_type = "crisis_keywords"
            is_crisis = True
            logger.warning("SAFETY: Crisis keywords detected")
        elif emotion_result.requires_crisis_response:
            crisis_type = "extreme_distress"
            is_crisis = True
            logger.warning("SAFETY: Extreme emotional distress detected")
        
        # Check high distress (not crisis, but needs careful handling)
        is_high_distress = (
            emotion_result.intensity_level in ["high", "crisis"] or
            extreme_distress
        )
        
        # Determine recommended action
        if is_crisis:
            recommended_action = "crisis_response"
            should_skip = True
            priority_message = self._get_crisis_message(crisis_type)
        elif is_high_distress:
            recommended_action = "comfort_first"
            should_skip = True
            priority_message = None
        else:
            recommended_action = "normal"
            should_skip = False
            priority_message = None
        
        # Get appropriate resources
        resources = self._get_relevant_resources(crisis_type) if is_crisis else []
        
        return SafetyCheckResult(
            is_crisis=is_crisis,
            is_high_distress=is_high_distress,
            crisis_type=crisis_type,
            recommended_action=recommended_action,
            crisis_resources=resources,
            should_skip_suggestion=should_skip,
            priority_message=priority_message
        )
    
    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if any patterns match in text."""
        return any(pattern in text for pattern in patterns)
    
    def _get_crisis_message(self, crisis_type: str) -> str:
        """Get appropriate message for crisis type."""
        messages = {
            "self_harm": (
                "I hear that you're in a lot of pain right now. "
                "You don't have to go through this alone. "
                "Please consider reaching out to someone who can help — "
                "a trusted friend, family member, or a crisis helpline."
            ),
            "hopelessness": (
                "I can hear how heavy everything feels right now. "
                "These feelings are real, and they matter. "
                "But please know that support is available, "
                "and talking to someone can help."
            ),
            "crisis_keywords": (
                "What you're going through sounds really difficult. "
                "I want you to know that you matter, and help is available. "
                "Please consider talking to someone you trust or a counselor."
            ),
            "extreme_distress": (
                "I can hear how overwhelmed you're feeling. "
                "That's an incredibly hard place to be. "
                "You don't have to face this alone — "
                "reaching out to someone can really help."
            )
        }
        
        return messages.get(crisis_type, messages["extreme_distress"])
    
    def _get_relevant_resources(self, crisis_type: str) -> List[str]:
        """Get relevant crisis resources."""
        resources = []
        
        for location, resource in self.crisis_resources.items():
            resources.append(f"{location}: {resource}")
        
        return resources
    
    def get_resource_text(self, resources: List[str]) -> str:
        """Format resources as readable text."""
        if not resources:
            return ""
        
        text = "\n\nIf you need support right now:\n"
        for resource in resources[:3]:  # Limit to 3 most relevant
            text += f"• {resource}\n"
        
        return text


# Singleton instance
safety_checker = SafetyChecker()
