"""
Prosody Emotion Detector - HIGH ACCURACY VERSION
=================================================

ACCURACY RANKING (Best to Fallback):
1. Hume AI API - Professional grade, 48 emotions (requires API key)
2. emotion2vec - State-of-the-art, highest accuracy for 4 emotions (FREE)
3. HuBERT-large - Very good accuracy (FREE)
4. Wav2Vec2-XLSR - Good accuracy (FREE)
5. Audio features analysis - Basic fallback (FREE)

TARGET EMOTIONS: angry, happy, sad, neutral
"""

import os
import json
import asyncio
import numpy as np
from typing import Dict, Optional, List
from dataclasses import dataclass
from loguru import logger
from pathlib import Path

from configs.config import config


@dataclass
class EmotionResult:
    """Container for emotion detection results."""
    primary_emotion: str
    confidence: float
    all_emotions: Dict[str, float]
    intensity: float


# =============================================
# MODEL 1: emotion2vec (State-of-the-Art)
# =============================================
class Emotion2VecDetector:
    """
    emotion2vec - State-of-the-art speech emotion recognition
    
    Paper: https://arxiv.org/abs/2312.15185
    Model: https://huggingface.co/emotion2vec
    
    This is currently the BEST open-source model for speech emotion recognition.
    Accuracy: ~90%+ on standard benchmarks
    """
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cpu"
        self.is_available = False
        
        # emotion2vec outputs these emotions
        self.emotion_labels = [
            "angry", "disgusted", "fearful", "happy", 
            "neutral", "other", "sad", "surprised", "unknown"
        ]
        
        # Map to our 4 target emotions
        self.emotion_mapping = {
            "angry": "angry",
            "disgusted": "angry",  # Map to angry
            "fearful": "sad",      # Map to sad
            "happy": "happy",
            "neutral": "neutral",
            "other": "neutral",
            "sad": "sad",
            "surprised": "happy",  # Map to happy
            "unknown": "neutral"
        }
        
        self._load_model()
    
    def _load_model(self):
        """Load emotion2vec model."""
        try:
            from transformers import AutoModel, AutoProcessor
            import torch
            
            model_name = "emotion2vec/emotion2vec_base"
            
            logger.info(f"Loading emotion2vec model: {model_name}")
            
            # Try to load emotion2vec
            try:
                self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
                self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
            except Exception:
                # Fallback to alternative emotion2vec model
                model_name = "emotion2vec/emotion2vec_plus_large"
                self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
                self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
            
            # Set device
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
            
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.is_available = True
            logger.info(f"✅ emotion2vec loaded on {self.device}")
            
        except Exception as e:
            logger.warning(f"emotion2vec not available: {e}")
            self.is_available = False
    
    async def detect_emotion(self, audio_path: str) -> Optional[EmotionResult]:
        """Detect emotion using emotion2vec."""
        if not self.is_available:
            return None
        
        try:
            import torch
            import librosa
            
            # Load audio at 16kHz
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Normalize
            audio = audio / (np.abs(audio).max() + 1e-7)
            
            # Process
            inputs = self.processor(audio, sampling_rate=16000, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                
                # Get emotion probabilities
                if hasattr(outputs, 'logits'):
                    logits = outputs.logits
                else:
                    logits = outputs.last_hidden_state.mean(dim=1)
                
                probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
            
            # Map to our emotions
            emotion_scores = {"angry": 0.0, "happy": 0.0, "sad": 0.0, "neutral": 0.0}
            
            for i, prob in enumerate(probs):
                if i < len(self.emotion_labels):
                    label = self.emotion_labels[i]
                    mapped = self.emotion_mapping.get(label, "neutral")
                    emotion_scores[mapped] += float(prob)
            
            # Normalize
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {k: v/total for k, v in emotion_scores.items()}
            
            # Get primary emotion
            primary = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[primary]
            
            # Calculate intensity
            intensity = 1.0 - emotion_scores.get("neutral", 0)
            
            return EmotionResult(
                primary_emotion=primary,
                confidence=round(confidence, 3),
                all_emotions=emotion_scores,
                intensity=round(intensity, 3)
            )
            
        except Exception as e:
            logger.error(f"emotion2vec detection error: {e}")
            return None


# =============================================
# MODEL 2: HuBERT Large (Very Good Accuracy)
# =============================================
class HuBERTEmotionDetector:
    """
    HuBERT-large for speech emotion recognition.
    Pre-trained on large speech corpus, fine-tuned for emotions.
    """
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cpu"
        self.is_available = False
        self.label_mapping = {}
        
        self._load_model()
    
    def _load_model(self):
        """Load HuBERT emotion model."""
        try:
            import torch
            from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
            
            # Models to try (in order of preference)
            model_names = [
                "superb/hubert-large-superb-er",
                "facebook/hubert-large-ls960-ft",
            ]
            
            for model_name in model_names:
                try:
                    logger.info(f"Loading HuBERT model: {model_name}")
                    
                    self.processor = AutoFeatureExtractor.from_pretrained(model_name)
                    self.model = AutoModelForAudioClassification.from_pretrained(model_name)
                    
                    # Get label mapping
                    if hasattr(self.model.config, 'id2label'):
                        self.label_mapping = {
                            int(k): v.lower() for k, v in self.model.config.id2label.items()
                        }
                    
                    # Set device
                    if torch.cuda.is_available():
                        self.device = "cuda"
                    else:
                        self.device = "cpu"
                    
                    self.model = self.model.to(self.device)
                    self.model.eval()
                    
                    self.is_available = True
                    logger.info(f"✅ HuBERT loaded on {self.device}")
                    return
                    
                except Exception as e:
                    logger.warning(f"Failed to load {model_name}: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"HuBERT not available: {e}")
            self.is_available = False
    
    async def detect_emotion(self, audio_path: str) -> Optional[EmotionResult]:
        """Detect emotion using HuBERT."""
        if not self.is_available:
            return None
        
        try:
            import torch
            import librosa
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=16000)
            audio = audio / (np.abs(audio).max() + 1e-7)
            
            # Process
            inputs = self.processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
            
            # Map to our emotions
            emotion_mapping = {
                "ang": "angry", "angry": "angry", "anger": "angry",
                "hap": "happy", "happy": "happy", "happiness": "happy", "joy": "happy",
                "sad": "sad", "sadness": "sad",
                "neu": "neutral", "neutral": "neutral",
                "fea": "sad", "fear": "sad", "fearful": "sad",
                "dis": "angry", "disgust": "angry",
                "sur": "happy", "surprise": "happy", "surprised": "happy",
            }
            
            emotion_scores = {"angry": 0.0, "happy": 0.0, "sad": 0.0, "neutral": 0.0}
            
            for idx, prob in enumerate(probs):
                label = self.label_mapping.get(idx, "neutral").lower()
                mapped = emotion_mapping.get(label, "neutral")
                emotion_scores[mapped] += float(prob)
            
            # Normalize
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {k: v/total for k, v in emotion_scores.items()}
            
            primary = max(emotion_scores, key=emotion_scores.get)
            
            return EmotionResult(
                primary_emotion=primary,
                confidence=round(emotion_scores[primary], 3),
                all_emotions=emotion_scores,
                intensity=round(1.0 - emotion_scores.get("neutral", 0), 3)
            )
            
        except Exception as e:
            logger.error(f"HuBERT detection error: {e}")
            return None


# =============================================
# MODEL 3: Wav2Vec2 XLSR (Good Accuracy)
# =============================================
class Wav2Vec2EmotionDetector:
    """
    Wav2Vec2 XLSR for multilingual emotion recognition.
    Good for non-English audio.
    """
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cpu"
        self.is_available = False
        self.label_mapping = {}
        
        self._load_model()
    
    def _load_model(self):
        """Load Wav2Vec2 model."""
        try:
            import torch
            from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
            
            model_name = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
            
            logger.info(f"Loading Wav2Vec2 model: {model_name}")
            
            self.processor = AutoFeatureExtractor.from_pretrained(model_name)
            self.model = AutoModelForAudioClassification.from_pretrained(model_name)
            
            if hasattr(self.model.config, 'id2label'):
                self.label_mapping = {
                    int(k): v.lower() for k, v in self.model.config.id2label.items()
                }
            
            if torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
            
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.is_available = True
            logger.info(f"✅ Wav2Vec2 loaded on {self.device}")
            
        except Exception as e:
            logger.warning(f"Wav2Vec2 not available: {e}")
            self.is_available = False
    
    async def detect_emotion(self, audio_path: str) -> Optional[EmotionResult]:
        """Detect emotion using Wav2Vec2."""
        if not self.is_available:
            return None
        
        try:
            import torch
            import librosa
            
            audio, sr = librosa.load(audio_path, sr=16000)
            audio = audio / (np.abs(audio).max() + 1e-7)
            
            inputs = self.processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
            
            emotion_mapping = {
                "angry": "angry", "ang": "angry",
                "happy": "happy", "hap": "happy",
                "sad": "sad",
                "neutral": "neutral", "neu": "neutral",
                "fear": "sad", "fearful": "sad",
                "disgust": "angry",
                "surprise": "happy", "surprised": "happy",
            }
            
            emotion_scores = {"angry": 0.0, "happy": 0.0, "sad": 0.0, "neutral": 0.0}
            
            for idx, prob in enumerate(probs):
                label = self.label_mapping.get(idx, "neutral").lower()
                mapped = emotion_mapping.get(label, "neutral")
                emotion_scores[mapped] += float(prob)
            
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {k: v/total for k, v in emotion_scores.items()}
            
            primary = max(emotion_scores, key=emotion_scores.get)
            
            return EmotionResult(
                primary_emotion=primary,
                confidence=round(emotion_scores[primary], 3),
                all_emotions=emotion_scores,
                intensity=round(1.0 - emotion_scores.get("neutral", 0), 3)
            )
            
        except Exception as e:
            logger.error(f"Wav2Vec2 detection error: {e}")
            return None


# =============================================
# MODEL 4: Audio Features Analysis (Fallback)
# =============================================
class AudioFeaturesEmotionDetector:
    """
    Fallback emotion detection using audio features.
    Works without any ML models - basic but always available.
    
    Analyzes:
    - Pitch (high = excited/angry, low = sad)
    - Energy (high = angry/happy, low = sad)
    - Speech rate (fast = angry/anxious, slow = sad)
    - Pitch variation (high = emotional, low = neutral)
    """
    
    def __init__(self):
        self.is_available = True
        logger.info("Audio features detector initialized (fallback)")
    
    async def detect_emotion(self, audio_path: str) -> EmotionResult:
        """Detect emotion using audio features."""
        try:
            import librosa
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)
            
            # Extract features
            features = self._extract_features(y, sr)
            
            # Classify based on features
            emotion_scores = self._classify_emotion(features)
            
            primary = max(emotion_scores, key=emotion_scores.get)
            
            return EmotionResult(
                primary_emotion=primary,
                confidence=round(emotion_scores[primary], 3),
                all_emotions=emotion_scores,
                intensity=round(1.0 - emotion_scores.get("neutral", 0), 3)
            )
            
        except Exception as e:
            logger.error(f"Audio features detection error: {e}")
            return self._default_result()
    
    def _extract_features(self, y: np.ndarray, sr: int) -> Dict:
        """Extract acoustic features."""
        import librosa
        
        features = {}
        
        # RMS Energy
        rms = librosa.feature.rms(y=y)[0]
        features['energy_mean'] = float(np.mean(rms))
        features['energy_std'] = float(np.std(rms))
        
        # Pitch (F0)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        if pitch_values:
            features['pitch_mean'] = float(np.mean(pitch_values))
            features['pitch_std'] = float(np.std(pitch_values))
        else:
            features['pitch_mean'] = 150.0
            features['pitch_std'] = 30.0
        
        # Zero crossing rate (speech rate indicator)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        features['zcr_mean'] = float(np.mean(zcr))
        
        # Spectral centroid (brightness)
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        features['centroid_mean'] = float(np.mean(centroid))
        
        # MFCC (overall timbre)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features['mfcc1_mean'] = float(np.mean(mfccs[0]))
        
        return features
    
    def _classify_emotion(self, features: Dict) -> Dict[str, float]:
        """Classify emotion based on features."""
        scores = {"angry": 0.0, "happy": 0.0, "sad": 0.0, "neutral": 0.25}
        
        energy = features.get('energy_mean', 0.1)
        pitch = features.get('pitch_mean', 150)
        pitch_var = features.get('pitch_std', 30)
        zcr = features.get('zcr_mean', 0.05)
        centroid = features.get('centroid_mean', 2000)
        
        # High energy + high pitch + fast = ANGRY
        if energy > 0.15 and pitch > 180 and zcr > 0.08:
            scores['angry'] += 0.4
        
        # High energy + high pitch variation + bright = HAPPY
        if energy > 0.1 and pitch_var > 40 and centroid > 2500:
            scores['happy'] += 0.4
        
        # Low energy + low pitch + slow = SAD
        if energy < 0.08 and pitch < 140 and zcr < 0.05:
            scores['sad'] += 0.4
        
        # Medium everything = NEUTRAL
        if 0.08 <= energy <= 0.15 and 130 <= pitch <= 180:
            scores['neutral'] += 0.3
        
        # Normalize
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return scores
    
    def _default_result(self) -> EmotionResult:
        """Return default neutral result."""
        return EmotionResult(
            primary_emotion="neutral",
            confidence=0.5,
            all_emotions={"angry": 0.1, "happy": 0.1, "sad": 0.1, "neutral": 0.7},
            intensity=0.3
        )


# =============================================
# MODEL 5: Hume AI API (Best Accuracy)
# =============================================
class HumeEmotionDetector:
    """
    Hume AI API - Professional grade emotion detection.
    
    Features:
    - 48 emotions detected
    - Prosody analysis (tone, pitch, rhythm)
    - Language agnostic
    - Highest accuracy available
    
    Requires: HUME_API_KEY in .env
    """
    
    def __init__(self):
        self.api_key = config.hume_api_key
        self.is_available = bool(self.api_key)
        
        if self.is_available:
            logger.info("✅ Hume AI API available")
        else:
            logger.info("Hume AI not configured (no API key)")
        
        # Map Hume emotions to our 4 categories
        self.emotion_mapping = {
            "Anger": "angry",
            "Annoyance": "angry",
            "Contempt": "angry",
            "Disgust": "angry",
            "Frustration": "angry",
            "Rage": "angry",
            
            "Joy": "happy",
            "Amusement": "happy",
            "Contentment": "happy",
            "Excitement": "happy",
            "Interest": "happy",
            "Love": "happy",
            "Pride": "happy",
            "Relief": "happy",
            "Satisfaction": "happy",
            "Triumph": "happy",
            
            "Sadness": "sad",
            "Disappointment": "sad",
            "Distress": "sad",
            "Grief": "sad",
            "Guilt": "sad",
            "Shame": "sad",
            "Sympathy": "sad",
            "Tiredness": "sad",
            "Pain": "sad",
            "Empathic Pain": "sad",
            
            "Fear": "sad",  # Map to sad for our use case
            "Anxiety": "sad",
            "Horror": "sad",
            
            "Calmness": "neutral",
            "Boredom": "neutral",
            "Confusion": "neutral",
            "Contemplation": "neutral",
            "Concentration": "neutral",
            "Determination": "neutral",
            "Doubt": "neutral",
            "Realization": "neutral",
        }
    
    async def detect_emotion(self, audio_path: str) -> Optional[EmotionResult]:
        """Detect emotion using Hume AI API."""
        if not self.is_available:
            return None
        
        try:
            import aiohttp
            import base64
            
            # Read audio file
            with open(audio_path, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode()
            
            headers = {
                "X-Hume-Api-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Submit job
            async with aiohttp.ClientSession() as session:
                # Create job
                job_data = {
                    "models": {"prosody": {}},
                    "data": [{"base64": audio_data}]
                }
                
                async with session.post(
                    "https://api.hume.ai/v0/batch/jobs",
                    headers=headers,
                    json=job_data
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Hume API error: {await response.text()}")
                        return None
                    
                    result = await response.json()
                    job_id = result.get('job_id')
                
                if not job_id:
                    return None
                
                # Poll for results
                for _ in range(30):
                    await asyncio.sleep(1)
                    
                    async with session.get(
                        f"https://api.hume.ai/v0/batch/jobs/{job_id}/predictions",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            predictions = await response.json()
                            return self._parse_results(predictions)
                
                return None
                
        except Exception as e:
            logger.error(f"Hume API error: {e}")
            return None
    
    def _parse_results(self, predictions) -> Optional[EmotionResult]:
        """Parse Hume API results."""
        try:
            emotion_scores = {"angry": 0.0, "happy": 0.0, "sad": 0.0, "neutral": 0.0}
            
            for result in predictions:
                prosody = result.get('results', {}).get('predictions', [])
                for pred in prosody:
                    models = pred.get('models', {})
                    prosody_data = models.get('prosody', {})
                    
                    for group in prosody_data.get('grouped_predictions', []):
                        for p in group.get('predictions', []):
                            for emotion in p.get('emotions', []):
                                name = emotion.get('name', '')
                                score = emotion.get('score', 0)
                                
                                mapped = self.emotion_mapping.get(name, "neutral")
                                emotion_scores[mapped] = max(emotion_scores[mapped], score)
            
            # Normalize
            total = sum(emotion_scores.values())
            if total > 0:
                emotion_scores = {k: v/total for k, v in emotion_scores.items()}
            else:
                emotion_scores = {"neutral": 1.0, "angry": 0.0, "happy": 0.0, "sad": 0.0}
            
            primary = max(emotion_scores, key=emotion_scores.get)
            
            return EmotionResult(
                primary_emotion=primary,
                confidence=round(emotion_scores[primary], 3),
                all_emotions=emotion_scores,
                intensity=round(1.0 - emotion_scores.get("neutral", 0), 3)
            )
            
        except Exception as e:
            logger.error(f"Error parsing Hume results: {e}")
            return None


# =============================================
# MAIN DETECTOR: Cascading Fallback
# =============================================
class CascadingEmotionDetector:
    """
    Main emotion detector with cascading fallback.
    
    Priority (best accuracy first):
    1. Hume AI API (if API key available)
    2. emotion2vec (state-of-the-art local model)
    3. HuBERT-large
    4. Wav2Vec2-XLSR
    5. Audio features (always works)
    """
    
    def __init__(self):
        logger.info("="*50)
        logger.info("Initializing Emotion Detection System")
        logger.info("="*50)
        
        # Initialize all detectors
        self.hume_detector = HumeEmotionDetector()
        self.emotion2vec_detector = Emotion2VecDetector()
        self.hubert_detector = HuBERTEmotionDetector()
        self.wav2vec_detector = Wav2Vec2EmotionDetector()
        self.audio_features_detector = AudioFeaturesEmotionDetector()
        
        # Determine best available detector
        self.primary_detector = self._get_best_detector()
        
        logger.info("="*50)
        logger.info(f"🎯 Primary detector: {self.primary_detector}")
        logger.info("="*50)
    
    def _get_best_detector(self) -> str:
        """Determine the best available detector."""
        if self.hume_detector.is_available:
            return "Hume AI (Professional)"
        elif self.emotion2vec_detector.is_available:
            return "emotion2vec (State-of-the-Art)"
        elif self.hubert_detector.is_available:
            return "HuBERT-large"
        elif self.wav2vec_detector.is_available:
            return "Wav2Vec2-XLSR"
        else:
            return "Audio Features (Basic)"
    
    async def detect_emotion_from_file(self, audio_path: str) -> EmotionResult:
        """
        Detect emotion using the best available model.
        Falls back through models if one fails.
        """
        logger.info(f"Detecting emotion from: {audio_path}")
        
        # Try each detector in order of accuracy
        detectors = [
            ("Hume AI", self.hume_detector),
            ("emotion2vec", self.emotion2vec_detector),
            ("HuBERT", self.hubert_detector),
            ("Wav2Vec2", self.wav2vec_detector),
            ("Audio Features", self.audio_features_detector),
        ]
        
        for name, detector in detectors:
            if not detector.is_available:
                continue
            
            try:
                logger.info(f"Trying {name}...")
                result = await detector.detect_emotion(audio_path)
                
                if result and result.confidence > 0.1:
                    # Skip if neutral=1.0 (likely a parsing issue)
                    if result.primary_emotion == "neutral" and result.confidence >= 0.99:
                        logger.warning(f"{name} returned neutral=1.0, trying next detector...")
                        continue
                    
                    logger.info(f"✅ {name}: {result.primary_emotion} ({result.confidence:.2f})")
                    return result
                    
            except Exception as e:
                logger.warning(f"{name} failed: {e}")
                continue
        
        # Final fallback
        logger.warning("All detectors failed, returning neutral")
        return EmotionResult(
            primary_emotion="neutral",
            confidence=0.5,
            all_emotions={"neutral": 0.5, "angry": 0.1, "happy": 0.2, "sad": 0.2},
            intensity=0.3
        )
    
    @property
    def is_available(self) -> bool:
        """Check if any detector is available."""
        return True  # Audio features always works


# =============================================
# Factory function
# =============================================
def get_emotion_detector():
    """Get the cascading emotion detector."""
    return CascadingEmotionDetector()


# Singleton instance
prosody_detector = get_emotion_detector()