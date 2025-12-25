"""
Empathetic Response Generator
Uses Ollama (local), OpenAI, or Claude to generate compassionate, emotionally-aware responses
"""

import os
from typing import Optional, Dict
from dataclasses import dataclass
from loguru import logger
import anthropic
import requests
import json

from configs.config import config
from modules.emotion_fusion import FusedEmotionResult
from modules.wellness_engine import WellnessSuggestion


@dataclass
class ResponseContext:
    """Context for generating empathetic response."""
    transcribed_text: str
    primary_emotion: str
    confidence: float
    intensity: float
    intensity_level: str
    key_phrases: list
    requires_crisis: bool
    wellness_suggestion: Optional[WellnessSuggestion]


class OllamaClient:
    """Simple Ollama HTTP client for local LLM."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.2"
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, system: str = "", max_tokens: int = 300) -> str:
        """Generate response using Ollama."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return ""


class OpenAIClient:
    """OpenAI client for cloud LLM."""
    
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.client = None
        
        if self.api_key and self.api_key != "your_openai_api_key_here":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.error(f"OpenAI init failed: {e}")
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def generate(self, prompt: str, system: str = "", max_tokens: int = 300) -> str:
        """Generate response using OpenAI GPT-4."""
        if not self.client:
            return ""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI request failed: {e}")
            return ""


class EmpathyResponseGenerator:
    """
    Generates compassionate, emotionally-aware responses.
    Priority: OpenAI > Ollama > Anthropic > Fallback
    
    Core principles:
    - Validate feelings without judgment
    - Never diagnose or minimize
    - Keep responses calm and human
    - Suggest ONE small supportive action
    - Encourage self-care, not dependency
    """
    
    def __init__(self):
        self.anthropic_client = None
        self.ollama = OllamaClient()
        self.openai = OpenAIClient()
        
        # Priority: OpenAI > Ollama > Anthropic (OpenAI works on cloud + local)
        if self.openai.is_available():
            self.llm_provider = "openai"
            logger.info("✅ Using OpenAI (GPT-4o-mini) for response generation")
        elif self.ollama.is_available():
            self.llm_provider = "ollama"
            logger.info("✅ Using Ollama (local LLM) for response generation")
        else:
            self.llm_provider = "anthropic"
            logger.info("Using Anthropic Claude as fallback...")
            self._init_anthropic()
        
        # System prompt - THE MOST IMPORTANT PART
        self.system_prompt = self._build_system_prompt()
    
    def _init_anthropic(self):
        """Initialize Anthropic client as fallback."""
        if config.anthropic_api_key:
            self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        else:
            logger.warning("Anthropic API key not set")
    
    def _build_system_prompt(self) -> str:
        """Build the core system prompt for empathetic responses."""
        return """You are a compassionate, emotionally intelligent mental wellness companion.

Your role:
- Listen to the user's spoken thoughts and emotional struggles.
- Validate their feelings without judgment.
- Never diagnose medical or mental conditions.
- Never minimize or dismiss emotional pain.
- Never provide harmful, extreme, or absolute advice.

Your goals:
1. Make the user feel heard and understood.
2. Reflect their emotion in a gentle, empathetic way.
3. Offer exactly ONE small, supportive suggestion (breathing, grounding, yoga, reflection, or rest).
4. Keep responses calm, human, and soothing.
5. Encourage self-care, not dependency.

Tone rules:
- If the user is sad or anxious → soft, warm, slow.
- If the user is angry → calm, grounding, steady.
- If the user is fearful → reassuring and protective.
- If the user is neutral → supportive and reflective.
- Never sound robotic, cheerful, or preachy.

Safety rules:
- If emotional intensity is high, prioritize comfort over advice.
- If self-harm or hopelessness is implied, gently encourage seeking human support.
- Never mention AI, models, scores, or analysis.

Response length:
- 2 to 4 short sentences maximum."""
    
    def _build_emotion_addon(self, emotion: str) -> str:
        """Get emotion-specific prompt addition."""
        addons = {
            "sadness": """
The user is feeling sadness or emotional heaviness.
Respond gently, with warmth and emotional validation.
Avoid positivity pressure or forced motivation.""",
            
            "sad": """
The user is feeling sadness or emotional heaviness.
Respond gently, with warmth and emotional validation.
Avoid positivity pressure or forced motivation.""",
            
            "anger": """
The user is feeling anger or frustration.
Respond calmly and grounding.
Do not match their intensity.
Help them slow down emotionally.""",
            
            "angry": """
The user is feeling anger or frustration.
Respond calmly and grounding.
Do not match their intensity.
Help them slow down emotionally.""",
            
            "fear": """
The user is feeling anxious or fearful.
Respond reassuringly and gently.
Focus on safety and grounding.""",
            
            "anxiety": """
The user is feeling anxious or fearful.
Respond reassuringly and gently.
Focus on safety and grounding.""",
            
            "frustration": """
The user is feeling frustrated or stuck.
Respond with understanding and patience.
Acknowledge the difficulty without dismissing it.""",
            
            "neutral": """
The user is emotionally neutral or uncertain.
Respond reflectively and supportively.
Encourage gentle self-awareness.""",
            
            "confusion": """
The user seems confused or uncertain.
Respond with patience and clarity.
Help them feel less alone in their uncertainty.""",
            
            "happy": """
The user is expressing happiness or positive emotions.
Respond warmly and supportively.
Celebrate with them gently and encourage gratitude.""",
            
            "joy": """
The user is expressing positive emotions.
Respond warmly and supportively.
Celebrate with them gently."""
        }
        
        return addons.get(emotion.lower(), addons["neutral"])
    
    def _build_crisis_addon(self) -> str:
        """Prompt addition for crisis situations."""
        return """
IMPORTANT - The user may be experiencing intense emotional pain.

Your response must:
- Express care and concern.
- Encourage reaching out to trusted people.
- Avoid panic or alarmist language.
- Never provide medical or legal instructions.
- Emphasize that they are not alone.

End with a gentle mention that talking to someone they trust, like a friend, family member, or counselor, can help."""
    
    def _build_wellness_addon(self) -> str:
        """Prompt for framing wellness suggestions."""
        return """
When suggesting a wellness activity:
- Suggest only ONE activity.
- Keep it optional, not commanding.
- Frame it as an invitation, not a solution.
- Avoid phrases like "you must" or "you should"."""
    
    def _build_user_prompt(self, context: ResponseContext) -> str:
        """Build the dynamic user prompt with context."""
        prompt = f"""User spoken text:
"{context.transcribed_text}"

Detected primary emotion: {context.primary_emotion}
Emotion confidence: {context.confidence}
Emotional intensity: {context.intensity_level}

Please respond empathetically following your role."""
        
        return prompt
    
    async def generate_response(
        self,
        context: ResponseContext
    ) -> str:
        """
        Generate an empathetic response based on emotional context.
        
        Priority:
        1. Ollama (local, free)
        2. Anthropic (paid)
        3. Fallback responses
        
        Args:
            context: ResponseContext with all emotional analysis
            
        Returns:
            Empathetic response string
        """
        # Build complete system prompt with addons
        full_system = self.system_prompt
        full_system += "\n" + self._build_emotion_addon(context.primary_emotion)
        
        if context.requires_crisis:
            full_system += "\n" + self._build_crisis_addon()
        else:
            full_system += "\n" + self._build_wellness_addon()
        
        # Build user prompt
        user_prompt = self._build_user_prompt(context)
        
        # Try based on provider
        if self.llm_provider == "openai":
            try:
                logger.info("Generating response with OpenAI (GPT-4o-mini)...")
                response = self.openai.generate(
                    prompt=user_prompt,
                    system=full_system,
                    max_tokens=300
                )
                
                if response:
                    logger.info(f"✅ OpenAI response generated: {len(response)} chars")
                    return response
                else:
                    logger.warning("OpenAI returned empty, trying fallback...")
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
        
        elif self.llm_provider == "ollama":
            try:
                logger.info("Generating response with Ollama (local LLM)...")
                response = self.ollama.generate(
                    prompt=user_prompt,
                    system=full_system,
                    max_tokens=300
                )
                
                if response:
                    logger.info(f"✅ Ollama response generated: {len(response)} chars")
                    return response
                else:
                    logger.warning("Ollama returned empty, trying fallback...")
            except Exception as e:
                logger.error(f"Ollama error: {e}")
        
        # Try Anthropic as fallback
        if self.anthropic_client:
            try:
                response = self.anthropic_client.messages.create(
                    model=config.llm.model,
                    max_tokens=config.llm.max_tokens,
                    temperature=config.llm.temperature,
                    system=full_system,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                
                generated_text = response.content[0].text.strip()
                logger.info(f"Generated empathetic response via Anthropic: {len(generated_text)} chars")
                return generated_text
                
            except Exception as e:
                logger.error(f"Anthropic error: {e}")
        
        # Fall back to hardcoded responses
        return self._fallback_response(context)
    
    def _fallback_response(self, context: ResponseContext) -> str:
        """
        Fallback responses when API is unavailable.
        """
        emotion = context.primary_emotion
        intensity = context.intensity_level
        
        # Crisis response
        if context.requires_crisis or intensity == "crisis":
            return (
                "I hear you, and I'm really glad you're sharing this with me. "
                "What you're feeling sounds really heavy. "
                "Please know you don't have to carry this alone — "
                "reaching out to someone you trust, like a friend or counselor, can help."
            )
        
        # Emotion-specific fallbacks
        fallbacks = {
            "sadness": (
                "I can hear how hard things are feeling right now. "
                "It's okay to feel this sadness. "
                "If it feels right, you might try taking a few slow, deep breaths."
            ),
            "sad": (
                "I can hear how hard things are feeling right now. "
                "It's okay to feel this sadness. "
                "If it feels right, you might try taking a few slow, deep breaths."
            ),
            "anger": (
                "I understand you're feeling frustrated. "
                "Those feelings are valid. "
                "Would it help to step away for a moment and take some slow breaths?"
            ),
            "angry": (
                "I understand you're feeling frustrated. "
                "Those feelings are valid. "
                "Would it help to step away for a moment and take some slow breaths?"
            ),
            "fear": (
                "That sounds scary, and it makes sense you're feeling afraid. "
                "You're safe in this moment. "
                "Try feeling your feet on the ground — you're here, right now."
            ),
            "anxiety": (
                "I hear that things feel overwhelming right now. "
                "That anxious feeling is hard to carry. "
                "If you can, try breathing out slowly — longer than you breathe in."
            ),
            "frustration": (
                "It sounds like you're feeling stuck and frustrated. "
                "That's a really difficult place to be. "
                "Sometimes stepping back for a moment can help things feel clearer."
            ),
            "happy": (
                "It's wonderful to hear that positive energy in your voice! "
                "These moments of happiness are precious. "
                "Take a moment to really savor this feeling."
            ),
            "joy": (
                "It's wonderful to hear that positive energy in your voice! "
                "These moments of happiness are precious. "
                "Take a moment to really savor this feeling."
            ),
            "neutral": (
                "Thank you for sharing what's on your mind. "
                "I'm here to listen whenever you need. "
                "How are you feeling in this moment?"
            )
        }
        
        return fallbacks.get(emotion, fallbacks["neutral"])
    
    def create_context(
        self,
        transcribed_text: str,
        emotion_result: FusedEmotionResult,
        suggestion: Optional[WellnessSuggestion] = None
    ) -> ResponseContext:
        """
        Create ResponseContext from analysis results.
        """
        return ResponseContext(
            transcribed_text=transcribed_text,
            primary_emotion=emotion_result.primary_emotion,
            confidence=emotion_result.confidence,
            intensity=emotion_result.intensity,
            intensity_level=emotion_result.intensity_level,
            key_phrases=emotion_result.key_phrases,
            requires_crisis=emotion_result.requires_crisis_response,
            wellness_suggestion=suggestion
        )


# Singleton instance
response_generator = EmpathyResponseGenerator()
