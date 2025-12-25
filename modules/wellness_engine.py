"""
Mental Wellness Logic Engine
Maps emotions to appropriate wellness modules and suggestions

UPDATED: Added get_all_suggestions() method to return 4 wellness cards per emotion
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import random
from loguru import logger

from configs.config import config
from modules.emotion_fusion import FusedEmotionResult


class WellnessModule(Enum):
    """Available wellness activity modules."""
    BREATHING = "breathing"
    GROUNDING = "grounding"
    YOGA = "yoga"
    MEDITATION = "guided_meditation"
    JOURNALING = "journaling"
    SELF_COMPASSION = "self_compassion"
    MINDFULNESS = "mindfulness"
    BODY_SCAN = "body_scan"
    REASSURANCE = "reassurance"
    SAFETY_GROUNDING = "safety_grounding"
    CALMING = "calming_exercises"
    REFLECTION = "reflection"
    GRATITUDE = "gratitude"
    REST = "rest"
    GENERAL = "general_wellness"


@dataclass
class WellnessSuggestion:
    """Container for a wellness suggestion."""
    module: WellnessModule
    title: str
    description: str
    duration: str
    instructions: List[str]
    tone: str  # soft, calm, reassuring, gentle


class WellnessEngine:
    """
    Maps detected emotions to appropriate wellness activities.
    
    Core principle: Suggest ONE small, achievable activity
    Never overwhelming, always optional
    
    UPDATED: Now supports get_all_suggestions() for 4 wellness cards
    """
    
    def __init__(self):
        # Emotion to module mapping from config
        self.emotion_modules = config.emotion.emotion_modules
        
        # Detailed wellness activities
        self.activities = self._initialize_activities()
        
        # Extended emotion-specific activity lists
        # Uses emotion names from prosody detector: anger, happy, sad, neutral
        self.emotion_activity_map = {
            # SAD emotion - 4+ activities
            "sad": [
                "guided_meditation", 
                "self_compassion", 
                "positive_affirmation", 
                "nature_visualization", 
                "journaling", 
                "emotional_release",
                "color_breathing"
            ],
            "sadness": [
                "guided_meditation", 
                "self_compassion", 
                "positive_affirmation", 
                "nature_visualization", 
                "journaling", 
                "emotional_release",
                "color_breathing"
            ],
            
            # ANGRY emotion - 4+ activities
            "anger": [
                "breathing", 
                "box_breathing", 
                "cold_water_reset", 
                "grounding", 
                "movement_break", 
                "yoga",
                "body_scan"
            ],
            "angry": [
                "breathing", 
                "box_breathing", 
                "cold_water_reset", 
                "grounding", 
                "movement_break", 
                "yoga",
                "body_scan"
            ],
            
            # HAPPY emotion - 4+ activities
            "happy": [
                "gratitude", 
                "mindfulness", 
                "reflection", 
                "nature_visualization", 
                "journaling", 
                "yoga"
            ],
            "joy": [
                "gratitude", 
                "mindfulness", 
                "reflection", 
                "nature_visualization", 
                "journaling", 
                "yoga"
            ],
            
            # NEUTRAL emotion - 4+ activities
            "neutral": [
                "general_wellness", 
                "reflection", 
                "mindfulness", 
                "gratitude", 
                "breathing", 
                "nature_visualization"
            ],
            
            # FEAR/ANXIETY - 4+ activities
            "fear": [
                "safety_grounding",
                "reassurance",
                "breathing",
                "grounding",
                "calming_exercises",
                "body_scan"
            ],
            "anxiety": [
                "box_breathing",
                "grounding",
                "reassurance",
                "safety_grounding",
                "mindfulness",
                "body_scan"
            ],
        }
    
    def _initialize_activities(self) -> Dict[str, WellnessSuggestion]:
        """Initialize all wellness activity definitions."""
        return {
            "breathing": WellnessSuggestion(
                module=WellnessModule.BREATHING,
                title="Gentle Breathing",
                description="A simple breathing exercise to help you feel more grounded.",
                duration="2-3 minutes",
                instructions=[
                    "Find a comfortable position",
                    "Breathe in slowly through your nose for 4 counts",
                    "Hold gently for 4 counts",
                    "Exhale slowly through your mouth for 6 counts",
                    "Repeat 3-4 times, or as long as feels comfortable"
                ],
                tone="soft"
            ),
            "box_breathing": WellnessSuggestion(
                module=WellnessModule.BREATHING,
                title="Box Breathing",
                description="A calming technique used by Navy SEALs to reduce stress instantly.",
                duration="3-4 minutes",
                instructions=[
                    "Breathe in for 4 seconds",
                    "Hold for 4 seconds",
                    "Breathe out for 4 seconds",
                    "Hold for 4 seconds",
                    "Repeat 4-6 times"
                ],
                tone="calm"
            ),
            "grounding": WellnessSuggestion(
                module=WellnessModule.GROUNDING,
                title="5-4-3-2-1 Grounding",
                description="A grounding technique to bring you back to the present moment.",
                duration="3-5 minutes",
                instructions=[
                    "Notice 5 things you can see around you",
                    "Notice 4 things you can touch or feel",
                    "Notice 3 things you can hear",
                    "Notice 2 things you can smell",
                    "Notice 1 thing you can taste",
                    "Take a deep breath when you're done"
                ],
                tone="calm"
            ),
            "yoga": WellnessSuggestion(
                module=WellnessModule.YOGA,
                title="Gentle Stretching",
                description="Simple stretches to release tension from your body.",
                duration="5 minutes",
                instructions=[
                    "Stand or sit comfortably",
                    "Gently roll your shoulders back",
                    "Slowly turn your head side to side",
                    "Reach your arms up and stretch",
                    "Take slow, deep breaths as you move"
                ],
                tone="calm"
            ),
            "guided_meditation": WellnessSuggestion(
                module=WellnessModule.MEDITATION,
                title="Brief Meditation",
                description="A short moment of peaceful stillness.",
                duration="3-5 minutes",
                instructions=[
                    "Find a quiet, comfortable spot",
                    "Close your eyes if it feels okay",
                    "Focus on your breath, without changing it",
                    "When thoughts come, gently let them pass",
                    "Return your attention to your breath"
                ],
                tone="soft"
            ),
            "journaling": WellnessSuggestion(
                module=WellnessModule.JOURNALING,
                title="Quick Journal Prompt",
                description="Writing can help process feelings.",
                duration="5-10 minutes",
                instructions=[
                    "Find a piece of paper or open a note",
                    "Write whatever comes to mind",
                    "No need to organize or make it perfect",
                    "Just let your thoughts flow onto the page",
                    "You can keep it or let it go afterward"
                ],
                tone="gentle"
            ),
            "self_compassion": WellnessSuggestion(
                module=WellnessModule.SELF_COMPASSION,
                title="Self-Compassion Moment",
                description="A gentle reminder to be kind to yourself.",
                duration="2-3 minutes",
                instructions=[
                    "Place your hand on your heart",
                    "Say to yourself: 'This is a difficult moment'",
                    "Remember: difficulty is part of being human",
                    "Say: 'May I be kind to myself'",
                    "Take a few breaths and let that sink in"
                ],
                tone="soft"
            ),
            "mindfulness": WellnessSuggestion(
                module=WellnessModule.MINDFULNESS,
                title="Mindful Moment",
                description="A brief pause to be present.",
                duration="1-2 minutes",
                instructions=[
                    "Pause whatever you're doing",
                    "Take three slow, deep breaths",
                    "Notice how your body feels right now",
                    "Notice any thoughts without judgment",
                    "Return to your breath"
                ],
                tone="calm"
            ),
            "body_scan": WellnessSuggestion(
                module=WellnessModule.BODY_SCAN,
                title="Quick Body Check",
                description="Notice and release tension in your body.",
                duration="3-5 minutes",
                instructions=[
                    "Start by noticing your feet",
                    "Slowly move your attention up through your body",
                    "Notice any areas of tension",
                    "Breathe into those areas",
                    "Let the tension soften with each exhale"
                ],
                tone="soft"
            ),
            "reassurance": WellnessSuggestion(
                module=WellnessModule.REASSURANCE,
                title="Grounding Affirmation",
                description="Words of comfort for anxious moments.",
                duration="1-2 minutes",
                instructions=[
                    "Find a comfortable position",
                    "Say to yourself: 'I am safe in this moment'",
                    "Say: 'This feeling will pass'",
                    "Say: 'I can handle difficult things'",
                    "Take a deep breath and feel your feet on the ground"
                ],
                tone="reassuring"
            ),
            "safety_grounding": WellnessSuggestion(
                module=WellnessModule.SAFETY_GROUNDING,
                title="Safety Check",
                description="Remind yourself you are safe right now.",
                duration="1-2 minutes",
                instructions=[
                    "Look around and notice where you are",
                    "Name 3 things that show you're safe",
                    "Feel the chair/floor supporting you",
                    "Say: 'Right now, in this moment, I am okay'",
                    "Take a slow breath"
                ],
                tone="reassuring"
            ),
            "calming_exercises": WellnessSuggestion(
                module=WellnessModule.CALMING,
                title="Quick Calm",
                description="Simple techniques to reduce stress quickly.",
                duration="2-3 minutes",
                instructions=[
                    "Splash cold water on your face",
                    "Or hold something cold in your hands",
                    "Focus on the sensation",
                    "Take slow breaths",
                    "Notice how your body responds"
                ],
                tone="calm"
            ),
            "reflection": WellnessSuggestion(
                module=WellnessModule.REFLECTION,
                title="Gentle Reflection",
                description="Take a moment to check in with yourself.",
                duration="3-5 minutes",
                instructions=[
                    "Ask yourself: 'How am I really feeling?'",
                    "Don't judge the answer, just notice",
                    "Ask: 'What do I need right now?'",
                    "Consider one small thing you could do for yourself",
                    "Give yourself permission to feel what you feel"
                ],
                tone="gentle"
            ),
            "gratitude": WellnessSuggestion(
                module=WellnessModule.GRATITUDE,
                title="Gratitude Moment",
                description="Notice small things to appreciate.",
                duration="2-3 minutes",
                instructions=[
                    "Think of one thing you're grateful for today",
                    "It can be something very small",
                    "Notice how it feels to appreciate it",
                    "Think of one more thing",
                    "Let the warmth of gratitude settle in"
                ],
                tone="gentle"
            ),
            "rest": WellnessSuggestion(
                module=WellnessModule.REST,
                title="Permission to Rest",
                description="Sometimes rest is the most helpful thing.",
                duration="5-15 minutes",
                instructions=[
                    "Find a comfortable place to sit or lie down",
                    "Let your body relax completely",
                    "Close your eyes if it feels good",
                    "You don't need to do anything right now",
                    "Just rest"
                ],
                tone="soft"
            ),
            "general_wellness": WellnessSuggestion(
                module=WellnessModule.GENERAL,
                title="Wellness Check-In",
                description="A simple check-in with yourself.",
                duration="2-3 minutes",
                instructions=[
                    "Pause and take a breath",
                    "Notice how you're feeling physically",
                    "Notice how you're feeling emotionally",
                    "Ask what you might need right now",
                    "Honor whatever comes up"
                ],
                tone="calm"
            ),
            "positive_affirmation": WellnessSuggestion(
                module=WellnessModule.SELF_COMPASSION,
                title="Positive Affirmations",
                description="Gentle words to lift your spirit.",
                duration="2-3 minutes",
                instructions=[
                    "Place your hand on your heart",
                    "Say: 'I am worthy of love and kindness'",
                    "Say: 'I am doing the best I can'",
                    "Say: 'I deserve peace and happiness'",
                    "Breathe deeply and let these words sink in"
                ],
                tone="soft"
            ),
            "nature_visualization": WellnessSuggestion(
                module=WellnessModule.MEDITATION,
                title="Nature Visualization",
                description="Mentally transport yourself to a peaceful natural setting.",
                duration="3-5 minutes",
                instructions=[
                    "Close your eyes and imagine a peaceful forest",
                    "Picture sunlight filtering through leaves",
                    "Hear birds singing and water flowing",
                    "Feel a gentle breeze on your skin",
                    "Stay in this peaceful place as long as needed"
                ],
                tone="soft"
            ),
            "cold_water_reset": WellnessSuggestion(
                module=WellnessModule.CALMING,
                title="Cold Water Reset",
                description="Use cold water to quickly calm your nervous system.",
                duration="1-2 minutes",
                instructions=[
                    "Go to a sink with cold water",
                    "Splash cold water on your face",
                    "Or hold ice cubes in your hands",
                    "Focus on the cooling sensation",
                    "Take slow, deep breaths"
                ],
                tone="calm"
            ),
            "movement_break": WellnessSuggestion(
                module=WellnessModule.YOGA,
                title="Quick Movement Break",
                description="Gentle movement to release stuck energy.",
                duration="3-5 minutes",
                instructions=[
                    "Stand up and shake out your hands",
                    "Roll your shoulders forward and back",
                    "Gently twist your torso side to side",
                    "March in place for 30 seconds",
                    "End with three deep breaths"
                ],
                tone="gentle"
            ),
            "emotional_release": WellnessSuggestion(
                module=WellnessModule.JOURNALING,
                title="Emotional Release Writing",
                description="Write freely to release pent-up emotions.",
                duration="5-10 minutes",
                instructions=[
                    "Grab paper or open a notes app",
                    "Write 'I feel...' and keep going",
                    "Don't censor or edit yourself",
                    "Let all emotions flow onto the page",
                    "You can tear it up or delete it after"
                ],
                tone="gentle"
            ),
            "color_breathing": WellnessSuggestion(
                module=WellnessModule.BREATHING,
                title="Color Breathing",
                description="Combine visualization with breathing for calm.",
                duration="3-4 minutes",
                instructions=[
                    "Breathe in and imagine a calming blue light",
                    "Feel it fill your body with peace",
                    "Breathe out and imagine gray stress leaving",
                    "Watch it dissolve into the air",
                    "Repeat until you feel lighter"
                ],
                tone="soft"
            )
        }
    
    def get_all_suggestions(
        self,
        emotion_result,
        count: int = 4
    ) -> List[WellnessSuggestion]:
        """
        Get multiple wellness suggestions for the detected emotion.
        
        Args:
            emotion_result: Object with primary_emotion and intensity_level attributes
            count: Number of suggestions to return (default 4)
            
        Returns:
            List of WellnessSuggestions
        """
        # Handle both FusedEmotionResult and simple objects
        if hasattr(emotion_result, 'primary_emotion'):
            primary_emotion = emotion_result.primary_emotion
        else:
            primary_emotion = str(emotion_result)
        
        if hasattr(emotion_result, 'intensity_level'):
            intensity = emotion_result.intensity_level
        else:
            intensity = "moderate"
        
        # Normalize emotion name
        primary_emotion = primary_emotion.lower()
        
        # Get activities for this emotion
        available_activities = self.emotion_activity_map.get(
            primary_emotion,
            self.emotion_activity_map["neutral"]
        )
        
        suggestions = []
        
        # For high intensity, prioritize calming activities first
        if intensity in ["high", "crisis"]:
            priority_activities = [
                "breathing", "box_breathing", "grounding", 
                "safety_grounding", "reassurance", "cold_water_reset"
            ]
            for activity in priority_activities:
                if activity in self.activities and len(suggestions) < count:
                    suggestions.append(self.activities[activity])
        
        # Add activities specific to the emotion
        for activity in available_activities:
            if activity in self.activities:
                if self.activities[activity] not in suggestions:
                    suggestions.append(self.activities[activity])
                if len(suggestions) >= count:
                    break
        
        # If we still need more, add general ones
        general_fallbacks = ["breathing", "mindfulness", "grounding", "gratitude"]
        for activity in general_fallbacks:
            if len(suggestions) >= count:
                break
            if activity in self.activities and self.activities[activity] not in suggestions:
                suggestions.append(self.activities[activity])
        
        return suggestions[:count]
    
    def get_suggestion(
        self,
        emotion_result: FusedEmotionResult
    ) -> WellnessSuggestion:
        """
        Get a single wellness suggestion based on detected emotion.
        
        Args:
            emotion_result: Fused emotion analysis result
            
        Returns:
            Single WellnessSuggestion (never multiple)
        """
        primary_emotion = emotion_result.primary_emotion
        intensity = emotion_result.intensity_level
        
        # Get modules for this emotion
        available_modules = self.emotion_modules.get(
            primary_emotion,
            self.emotion_modules["neutral"]
        )
        
        # Prioritize based on intensity
        if intensity in ["high", "crisis"]:
            # For high intensity, prefer grounding and breathing
            priority_modules = ["breathing", "grounding", "safety_grounding", "reassurance"]
            for module in priority_modules:
                if module in available_modules:
                    return self.activities.get(module, self.activities["breathing"])
        
        # Select from available modules
        for module in available_modules:
            if module in self.activities:
                return self.activities[module]
        
        # Fallback
        return self.activities["breathing"]
    
    def get_suggestion_text(
        self,
        suggestion: WellnessSuggestion,
        emotion_result: FusedEmotionResult
    ) -> str:
        """
        Format suggestion as natural text for response.
        Framed as invitation, not command.
        """
        intensity = emotion_result.intensity_level
        
        # Soft framing based on intensity
        if intensity in ["high", "crisis"]:
            intro = "If you'd like, there's something gentle that might help"
        elif intensity == "moderate":
            intro = "If it feels right, you might try"
        else:
            intro = "You might find it helpful to try"
        
        # Build suggestion text
        text = f"{intro}: {suggestion.title.lower()}. "
        text += f"{suggestion.description} "
        
        # Add brief instruction
        if suggestion.instructions:
            text += f"You could start by {suggestion.instructions[0].lower()}."
        
        return text
    
    def should_skip_suggestion(
        self,
        emotion_result: FusedEmotionResult
    ) -> bool:
        """
        Determine if we should skip suggestion and focus on comfort.
        
        Skip suggestions when:
        - Crisis level intensity
        - Very high distress
        - User needs comfort, not advice
        """
        if emotion_result.requires_crisis_response:
            return True
        
        if emotion_result.intensity_level == "crisis":
            return True
        
        return False


# Singleton instance
wellness_engine = WellnessEngine()