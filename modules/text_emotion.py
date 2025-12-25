"""
Text Emotion Analyzer Module
Secondary emotion source - analyzes WHAT the user said
Complements prosody analysis which captures HOW they said it
"""

import os
import re
from typing import Dict, Optional, List
from dataclasses import dataclass
from loguru import logger

from configs.config import config


@dataclass
class TextEmotionResult:
    """Container for text-based emotion analysis."""
    primary_emotion: str
    confidence: float
    all_emotions: Dict[str, float]
    sentiment: str  # positive, negative, neutral
    key_phrases: List[str]


class TextEmotionAnalyzer:
    """
    LLM-based text emotion analysis using OpenAI GPT-4o.
    
    Why use text emotion:
    - Captures the WHY behind emotions
    - Identifies specific concerns and triggers
    - Provides context for prosody-detected emotions
    - Handles cases where voice alone is ambiguous
    """
    
    def __init__(self):
        self.openai_client = None
        self._init_client()
        
        # Emotion keywords for fallback analysis
        self.emotion_keywords = {
            "sadness": [
                "sad", "depressed", "unhappy", "crying", "tears", "grief",
                "lonely", "alone", "hopeless", "empty", "loss", "hurt",
                "pain", "suffering", "miserable", "devastated"
            ],
            "anger": [
                "angry", "furious", "mad", "annoyed", "frustrated", "irritated",
                "hate", "resent", "bitter", "rage", "upset", "livid"
            ],
            "fear": [
                "afraid", "scared", "terrified", "frightened", "panic",
                "worried", "nervous", "anxious", "dread", "terror"
            ],
            "anxiety": [
                "anxious", "stressed", "overwhelmed", "worried", "tense",
                "restless", "uneasy", "nervous", "pressure", "can't cope"
            ],
            "joy": [
                "happy", "joyful", "excited", "grateful", "thankful",
                "blessed", "content", "peaceful", "relieved", "hopeful"
            ],
            "confusion": [
                "confused", "lost", "uncertain", "don't know", "unclear",
                "puzzled", "bewildered", "unsure"
            ],
            "frustration": [
                "frustrated", "stuck", "blocked", "impossible", "give up",
                "can't do", "failing", "struggle"
            ]
        }
    
    def _init_client(self):
        """Initialize OpenAI client for accurate emotion detection."""
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if api_key and api_key != "your_openai_api_key_here":
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized for text emotion analysis")
            except Exception as e:
                logger.error(f"OpenAI init failed: {e}")
        else:
            logger.warning("OpenAI API key not set - using keyword analysis")
    
    async def analyze_text(self, text: str) -> TextEmotionResult:
        """
        Analyze text for emotional content.
        
        Args:
            text: Transcribed user speech
            
        Returns:
            TextEmotionResult with detected emotions
        """
        if not text or not text.strip():
            return self._empty_result()
        
        # Try OpenAI analysis first (most accurate)
        if self.openai_client:
            try:
                return await self._openai_analyze(text)
            except Exception as e:
                logger.warning(f"OpenAI analysis failed: {e}, falling back to keywords")
        
        # Fallback to keyword analysis
        return self._keyword_analyze(text)
    
    async def _openai_analyze(self, text: str) -> TextEmotionResult:
        """
        Use OpenAI GPT-4o for highly accurate emotion analysis.
        """
        prompt = f"""Analyze the emotional content of this text from someone expressing their feelings.

Text: "{text}"

Respond ONLY with a JSON object (no markdown, no explanation):
{{
    "primary_emotion": "one of: sadness, anger, fear, anxiety, joy, confusion, frustration, neutral",
    "confidence": 0.0 to 1.0,
    "all_emotions": {{
        "sadness": 0.0 to 1.0,
        "anger": 0.0 to 1.0,
        "fear": 0.0 to 1.0,
        "anxiety": 0.0 to 1.0,
        "joy": 0.0 to 1.0,
        "neutral": 0.0 to 1.0
    }},
    "sentiment": "positive, negative, or neutral",
    "key_phrases": ["phrase1", "phrase2"]
}}

Focus on emotional indicators, not just keywords. Consider context and implied feelings."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Clean JSON if wrapped in markdown
        if response_text.startswith("```"):
            response_text = re.sub(r"```json?\n?", "", response_text)
            response_text = response_text.replace("```", "").strip()
        
        import json
        data = json.loads(response_text)
        
        logger.info(f"✅ OpenAI emotion analysis: {data.get('primary_emotion')} (confidence: {data.get('confidence', 0.5):.2f})")
        
        return TextEmotionResult(
            primary_emotion=data.get("primary_emotion", "neutral"),
            confidence=data.get("confidence", 0.5),
            all_emotions=data.get("all_emotions", {"neutral": 0.5}),
            sentiment=data.get("sentiment", "neutral"),
            key_phrases=data.get("key_phrases", [])
        )
    
    def _keyword_analyze(self, text: str) -> TextEmotionResult:
        """
        Enhanced keyword-based emotion analysis as fallback.
        Handles intensity modifiers and negation patterns.
        """
        text_lower = text.lower()
        emotion_scores = {}
        
        # Intensity modifiers
        intensifiers = ["very", "really", "so", "extremely", "incredibly", "terribly", "absolutely", "completely"]
        diminishers = ["a bit", "slightly", "somewhat", "a little", "kind of", "sort of"]
        
        # Check for intensifiers
        intensity_boost = 1.0
        for word in intensifiers:
            if word in text_lower:
                intensity_boost = 1.3
                break
        for phrase in diminishers:
            if phrase in text_lower:
                intensity_boost = 0.7
                break
        
        # Negation patterns
        negation_words = ["not", "never", "no", "don't", "doesn't", "didn't", "won't", "wouldn't", "can't", "couldn't", "isn't", "aren't"]
        has_negation = any(neg in text_lower for neg in negation_words)
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in text_lower:
                    # Check if negated
                    is_negated = False
                    if has_negation:
                        # Simple check: negation word within 3 words before keyword
                        pos = text_lower.find(keyword)
                        if pos > 0:
                            prefix = text_lower[max(0, pos-25):pos]
                            is_negated = any(neg in prefix for neg in negation_words)
                    
                    if is_negated:
                        # Negated emotion - flip to opposite
                        if emotion == "joy":
                            emotion_scores["sadness"] = emotion_scores.get("sadness", 0) + 0.3
                        elif emotion in ["sadness", "anger", "fear", "anxiety"]:
                            emotion_scores["neutral"] = emotion_scores.get("neutral", 0) + 0.2
                    else:
                        # Weight by keyword position (earlier = stronger)
                        pos = text_lower.find(keyword)
                        weight = 1.0 - (pos / max(len(text_lower), 1)) * 0.3
                        score += weight * intensity_boost
                        matched_keywords.append(keyword)
            
            # Normalize score
            if score > 0:
                emotion_scores[emotion] = min(1.0, score / 2.5)
        
        # Ensure all emotions have a score
        for emotion in ["sadness", "anger", "fear", "anxiety", "joy", "neutral"]:
            if emotion not in emotion_scores:
                emotion_scores[emotion] = 0.05
        
        # Find primary emotion
        if not emotion_scores or max(emotion_scores.values()) < 0.15:
            emotion_scores["neutral"] = 0.5
        
        primary = max(emotion_scores, key=emotion_scores.get)
        
        # Adjust confidence based on keyword matches
        confidence = min(0.9, emotion_scores[primary] * 1.2)
        
        # Determine sentiment
        positive_emotions = ["joy"]
        negative_emotions = ["sadness", "anger", "fear", "anxiety", "frustration"]
        
        if primary in positive_emotions:
            sentiment = "positive"
        elif primary in negative_emotions:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Extract key phrases (simple extraction)
        key_phrases = self._extract_key_phrases(text)
        
        logger.info(f"Keyword analysis: {primary} (confidence: {confidence:.2f})")
        
        return TextEmotionResult(
            primary_emotion=primary,
            confidence=round(confidence, 3),
            all_emotions=emotion_scores,
            sentiment=sentiment,
            key_phrases=key_phrases
        )
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract emotionally significant phrases."""
        phrases = []
        
        # Look for "I feel" statements
        feel_pattern = r"i (?:feel|am|'m) (\w+(?:\s+\w+)?)"
        matches = re.findall(feel_pattern, text.lower())
        phrases.extend(matches[:3])
        
        # Look for "so" intensifiers
        so_pattern = r"so (\w+)"
        matches = re.findall(so_pattern, text.lower())
        phrases.extend(matches[:2])
        
        return list(set(phrases))[:5]
    
    def _empty_result(self) -> TextEmotionResult:
        """Return empty result for no text."""
        return TextEmotionResult(
            primary_emotion="neutral",
            confidence=0.3,
            all_emotions={"neutral": 0.5},
            sentiment="neutral",
            key_phrases=[]
        )


# Singleton instance
text_analyzer = TextEmotionAnalyzer()
