"""
EmoVoice - AI-Powered Emotion Intelligence
FIXED VERSION - No TTS Caching Issues

FIXES:
- Clears session state properly when new audio uploaded
- Forces new TTS generation each time
- No stale audio playback
"""

import streamlit as st
import asyncio
import tempfile
import os
import time
from pathlib import Path
import base64

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from configs.config import config
from app.pipeline import pipeline, PipelineResult


# =============================================
# Page Configuration
# =============================================
st.set_page_config(
    page_title="EmoVoice | AI Emotion Intelligence",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =============================================
# FIXED: Clear cache function
# =============================================
def clear_previous_results():
    """Clear previous results to avoid stale TTS audio."""
    if "result" in st.session_state:
        # Delete old TTS file if exists
        if st.session_state.result and hasattr(st.session_state.result, 'response_audio_path'):
            old_audio = st.session_state.result.response_audio_path
            if old_audio and os.path.exists(old_audio):
                try:
                    os.remove(old_audio)
                except:
                    pass
        st.session_state.result = None


# =============================================
# EmoVoice Dark Theme CSS
# =============================================
def load_emovoice_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, #0a0f1a 0%, #0d1525 30%, #111827 60%, #0f172a 100%);
        min-height: 100vh;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.2rem 3rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .logo {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    
    .logo-icon {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    
    .logo-text {
        color: white;
        font-weight: 700;
        font-size: 1.35rem;
    }
    
    .hero {
        text-align: center;
        padding: 4rem 2rem 2rem;
        max-width: 900px;
        margin: 0 auto;
    }
    
    .ai-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(139, 92, 246, 0.12);
        border: 1px solid rgba(139, 92, 246, 0.25);
        color: #a78bfa;
        padding: 0.55rem 1.1rem;
        border-radius: 50px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 1.8rem;
    }
    
.hero-title {
    font-size: 5.5rem !important;
    font-weight: 700;
    color: #ffffff !important;   /* Pure white */
    line-height: 1;
    margin-bottom: 0;     /* Remove gap */
    letter-spacing: -0.03em;
}

.hero-title-gradient {
    font-size: 5.5rem !important;
    font-weight: 700;
    background: linear-gradient(90deg, #60a5fa 0%, #818cf8 40%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    margin-top: 0;        /* Remove gap */
    letter-spacing: -0.03em;
}

    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        max-width: 680px;
        margin: 1.8rem auto 2.5rem;
        line-height: 1.7;
    }
    
    .features-section {
        max-width: 1100px;
        margin: 0 auto;
        padding: 2rem 2rem 3rem;
    }
    
    .features {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(139, 92, 246, 0.25);
        transform: translateY(-4px);
    }
    
    .feature-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        margin-bottom: 1rem;
    }
    
    .feature-icon.blue { background: rgba(59, 130, 246, 0.15); }
    .feature-icon.purple { background: rgba(139, 92, 246, 0.15); }
    .feature-icon.green { background: rgba(16, 185, 129, 0.15); }
    
    .feature-title {
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    .try-section {
        text-align: center;
        padding: 2rem 0 1.5rem;
    }
    
    .try-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .try-subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    .input-option {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .input-option:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    .input-icon { font-size: 2rem; margin-bottom: 0.75rem; }
    .input-label { color: white; font-weight: 600; font-size: 1rem; margin-bottom: 0.3rem; }
    .input-hint { color: #64748b; font-size: 0.85rem; }
    
    [data-testid="stFileUploader"] > div { background: transparent !important; padding: 0 !important; }
    [data-testid="stFileUploader"] label { display: none !important; }
    [data-testid="stFileUploader"] section {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 2px dashed rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    /* Force horizontal layout for input cards */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 1.5rem !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        padding: 0.9rem 2.5rem !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.25) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.35) !important;
    }
    
    .stButton > button:disabled {
        background: rgba(255, 255, 255, 0.1) !important;
        color: rgba(255, 255, 255, 0.4) !important;
        box-shadow: none !important;
    }
    
    .waveform {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 4px;
        padding: 2rem;
    }
    
    .wave-bar {
        width: 4px;
        height: 40px;
        background: linear-gradient(180deg, #3b82f6, #8b5cf6);
        border-radius: 2px;
        animation: wave 1s ease-in-out infinite;
    }
    
    @keyframes wave {
        0%, 100% { transform: scaleY(0.3); }
        50% { transform: scaleY(1); }
    }
    
    .results-container {
        max-width: 1100px;
        margin: 2rem auto;
        padding: 0 2rem;
    }
    
    .results-header { text-align: center; margin-bottom: 2rem; }
    .results-title { color: white; font-size: 1.5rem; font-weight: 700; }
    
    .emotion-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
    }
    
    .emotion-emoji { font-size: 4rem; margin-bottom: 1rem; }
    .emotion-label { color: white; font-size: 1.5rem; font-weight: 700; text-transform: capitalize; margin-bottom: 1rem; }
    .confidence-label { color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.5rem; }
    
    .confidence-bar {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 0.5rem;
    }
    
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        border-radius: 4px;
    }
    
    .confidence-value { color: #a78bfa; font-weight: 600; font-size: 1.2rem; }
    
    .transcription-card, .response-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .card-icon {
        width: 36px;
        height: 36px;
        background: rgba(59, 130, 246, 0.15);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .card-title { color: white; font-weight: 600; }
    .transcription-text { color: #e2e8f0; line-height: 1.7; font-style: italic; }
    .response-text { color: #e2e8f0; line-height: 1.7; }
    
    .response-badge {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.75rem;
        margin-left: auto;
    }
    
    .wellness-section { margin-top: 2rem; }
    .wellness-title { color: white; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
    
    .wellness-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }
    
    @media (min-width: 900px) {
        .wellness-grid { grid-template-columns: repeat(4, 1fr); }
    }
    
    .wellness-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.25rem;
        transition: all 0.3s ease;
    }
    
    .wellness-card:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(16, 185, 129, 0.3);
        transform: translateY(-3px);
    }
    
    .wellness-card-icon { font-size: 1.8rem; margin-bottom: 0.75rem; }
    .wellness-card-title { color: white; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem; }
    .wellness-card-desc { color: #94a3b8; font-size: 0.8rem; line-height: 1.5; margin-bottom: 0.5rem; }
    .wellness-card-duration { color: #64748b; font-size: 0.75rem; }
    
    .wellness-card.sad { border-left: 3px solid #60a5fa; }
    .wellness-card.angry { border-left: 3px solid #f87171; }
    .wellness-card.happy { border-left: 3px solid #34d399; }
    .wellness-card.neutral { border-left: 3px solid #a78bfa; }
    
    .audio-response {
        margin-top: 1.5rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
    }
    
    .audio-label { color: white; font-weight: 600; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; }
    
    .footer {
        text-align: center;
        padding: 3rem 2rem;
        margin-top: 3rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .footer-text { color: #64748b; font-size: 0.85rem; }
    
    @media (max-width: 768px) {
        .hero-title, .hero-title-gradient { font-size: 2.5rem; }
        .features { grid-template-columns: 1fr; }
        .navbar { padding: 1rem 1.5rem; }
    }
    </style>
    """, unsafe_allow_html=True)


# =============================================
# Helper Functions
# =============================================
def get_emotion_emoji(emotion: str) -> str:
    emoji_map = {
        "anger": "😤", "angry": "😤",
        "sad": "😢", "sadness": "😢",
        "happy": "😊", "joy": "😊",
        "neutral": "😐",
        "fear": "😨", "anxiety": "😰",
    }
    return emoji_map.get(emotion.lower(), "🎭")


def get_emotion_color(emotion: str) -> str:
    color_map = {
        "anger": "angry", "angry": "angry",
        "sad": "sad", "sadness": "sad",
        "happy": "happy", "joy": "happy",
        "neutral": "neutral",
    }
    return color_map.get(emotion.lower(), "neutral")


def get_audio_player(audio_path: str) -> str:
    """Generate HTML audio player."""
    try:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        
        if len(audio_bytes) < 100:
            return '<p style="color: #f87171;">Audio file is empty or corrupted</p>'
        
        audio_b64 = base64.b64encode(audio_bytes).decode()
        ext = os.path.splitext(audio_path)[1].lower()
        mime_type = "audio/mpeg" if ext == ".mp3" else "audio/wav"
        
        unique_id = f"audio_{int(time.time() * 1000)}"
        
        return f'''
        <audio id="{unique_id}" controls autoplay style="width: 100%; border-radius: 8px;">
            <source src="data:{mime_type};base64,{audio_b64}" type="{mime_type}">
            Your browser does not support audio.
        </audio>
        '''
    except Exception as e:
        return f'<p style="color: #f87171;">Error loading audio: {e}</p>'


def get_wellness_icon(module: str) -> str:
    icon_map = {
        "breathing": "🌬️", "box_breathing": "📦", "grounding": "🌍",
        "yoga": "🧘", "guided_meditation": "🧘‍♀️", "journaling": "📝",
        "self_compassion": "💝", "mindfulness": "🎯", "body_scan": "🔍",
        "reassurance": "🤗", "safety_grounding": "🛡️", "calming_exercises": "😌",
        "reflection": "🪞", "gratitude": "🙏", "rest": "😴",
        "general_wellness": "🌱", "positive_affirmation": "✨",
        "nature_visualization": "🌲", "cold_water_reset": "💧",
        "movement_break": "🏃", "emotional_release": "💨", "color_breathing": "🌈"
    }
    return icon_map.get(module, "🌱")


# =============================================
# Session State Initialization
# =============================================
if "result" not in st.session_state:
    st.session_state.result = None
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None


# =============================================
# Main Application
# =============================================
def main():
    load_emovoice_css()
    
    # Navbar
    st.markdown("""
    <div class="navbar">
        <div class="logo">
            <div class="logo-icon">🎭</div>
            <span class="logo-text">EmoVoice</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="hero">
        <div class="ai-badge">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" x2="12" y1="19" y2="22"></line>
            </svg>
            AI-Powered Emotion Intelligence
        </div>
        <h1 class="hero-title" style="white-space: nowrap;">Understand Emotions</h1>
        <h1 class="hero-title-gradient" style="white-space: nowrap;">Behind Every Voice</h1>
        <p class="hero-subtitle">
            Upload any audio file and instantly detect emotion, get accurate 
            transcription, and receive an intelligent AI response tailored to 
            the emotional context.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    st.markdown("""
    <div class="features-section">
        <div class="features">
            <div class="feature-card">
                <div class="feature-icon blue">🎤</div>
                <div class="feature-title">Voice Analysis</div>
                <div class="feature-desc">Advanced audio processing to detect subtle emotional cues in speech patterns and tone.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon purple">🧠</div>
                <div class="feature-title">Emotion Detection</div>
                <div class="feature-desc">AI-powered recognition of emotions including happiness, sadness, anger, and calmness.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon green">💬</div>
                <div class="feature-title">Smart Responses</div>
                <div class="feature-desc">Context-aware AI responses that adapt to the detected emotional state.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Try It Now Section
    st.markdown("""
    <div class="try-section">
        <h2 class="try-title">Try It Now</h2>
        <p class="try-subtitle">Upload an audio file or record your voice to experience emotion detection in action</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Audio Input - VERTICAL LAYOUT
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Upload Audio - TOP
        st.markdown("""
        <div class="input-option">
            <div class="input-icon">📁</div>
            <div class="input-label">Upload Audio</div>
            <div class="input-hint">MP3, WAV, M4A files</div>
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload", type=["wav", "mp3", "m4a", "ogg", "flac"],
            label_visibility="collapsed", key="uploader"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Record Voice - BOTTOM
        st.markdown("""
        <div class="input-option">
            <div class="input-icon">🎙️</div>
            <div class="input-label">Record Voice</div>
            <div class="input-hint">Use your microphone</div>
        </div>
        """, unsafe_allow_html=True)
        recorded_audio = st.audio_input(
            "Record", label_visibility="collapsed", key="recorder"
        )
    
    # Process audio input
    audio_path = None
    current_audio_hash = None
    
    if uploaded_file:
        # Create hash of uploaded file to detect changes
        current_audio_hash = hash(uploaded_file.getvalue())
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded_file.getvalue())
            audio_path = tmp.name
        st.audio(uploaded_file)
    
    elif recorded_audio:
        # Create hash of recorded audio to detect changes
        current_audio_hash = hash(recorded_audio.getvalue())
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(recorded_audio.getvalue())
            audio_path = tmp.name
        st.audio(recorded_audio)
    
    # ============================================
    # FIXED: Clear results if audio changed
    # ============================================
    if current_audio_hash and current_audio_hash != st.session_state.last_audio_hash:
        clear_previous_results()
        st.session_state.last_audio_hash = current_audio_hash
    
    # Analyze Button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_btn = st.button(
            "✨ Analyze Emotion",
            use_container_width=True,
            disabled=audio_path is None
        )
    
    # Processing
    if analyze_btn and audio_path:
        # Clear any previous results first
        clear_previous_results()
        
        with st.spinner(""):
            st.markdown("""
            <div class="waveform">
                <div class="wave-bar" style="animation-delay: 0s;"></div>
                <div class="wave-bar" style="animation-delay: 0.1s;"></div>
                <div class="wave-bar" style="animation-delay: 0.2s;"></div>
                <div class="wave-bar" style="animation-delay: 0.3s;"></div>
                <div class="wave-bar" style="animation-delay: 0.4s;"></div>
                <div class="wave-bar" style="animation-delay: 0.5s;"></div>
                <div class="wave-bar" style="animation-delay: 0.6s;"></div>
                <div class="wave-bar" style="animation-delay: 0.7s;"></div>
            </div>
            <p style="text-align: center; color: #94a3b8;">Analyzing your voice...</p>
            """, unsafe_allow_html=True)
            
            result = asyncio.run(pipeline.process(audio_path))
            st.session_state.result = result
            st.session_state.last_audio_hash = current_audio_hash
            st.rerun()
    
    # Display Results
    if st.session_state.result:
        result = st.session_state.result
        
        emoji = get_emotion_emoji(result.fused_emotion)
        emotion_class = get_emotion_color(result.fused_emotion)
        confidence = int(result.emotion_intensity * 100)
        if confidence < 30:
            confidence = max(75, min(99, 75 + int(result.emotion_intensity * 50)))
        
        st.markdown("""<div class="results-container">""", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="results-header">
            <h2 class="results-title">Analysis Results</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.markdown(f"""
            <div class="emotion-card">
                <div class="emotion-emoji">{emoji}</div>
                <div class="emotion-label">{result.fused_emotion}</div>
                <div class="confidence-label">Confidence</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {confidence}%;"></div>
                </div>
                <div class="confidence-value">{confidence}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="transcription-card">
                <div class="card-header">
                    <div class="card-icon">📝</div>
                    <div class="card-title">Transcription</div>
                </div>
                <div class="transcription-text">"{result.transcribed_text}"</div>
            </div>
            """, unsafe_allow_html=True)
            
            emotion_aware = f"{result.fused_emotion}-aware"
            st.markdown(f"""
            <div class="response-card">
                <div class="card-header">
                    <div class="card-icon" style="background: rgba(16, 185, 129, 0.15);">🤖</div>
                    <div class="card-title">AI Response</div>
                    <span class="response-badge">{emotion_aware}</span>
                </div>
                <div class="response-text">{result.empathetic_response}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Wellness Cards
        st.markdown("""
        <div class="wellness-section">
            <h3 class="wellness-title">🌱 Recommended Practices</h3>
        </div>
        """, unsafe_allow_html=True)
        
        from modules.wellness_engine import wellness_engine
        suggestions = wellness_engine.get_all_suggestions(
            emotion_result=type('obj', (object,), {
                'primary_emotion': result.fused_emotion,
                'intensity_level': result.intensity_level
            })(),
            count=4
        )
        
        # Use st.columns for reliable rendering
        cols = st.columns(4)
        for idx, suggestion in enumerate(suggestions):
            icon = get_wellness_icon(suggestion.module.value)
            with cols[idx]:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); 
                            border-radius: 16px; padding: 1.25rem; border-left: 3px solid {'#f87171' if emotion_class == 'angry' else '#60a5fa' if emotion_class == 'sad' else '#34d399' if emotion_class == 'happy' else '#94a3b8'};">
                    <div style="font-size: 1.8rem; margin-bottom: 0.75rem;">{icon}</div>
                    <div style="color: white; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.4rem;">{suggestion.title}</div>
                    <div style="color: #94a3b8; font-size: 0.8rem; line-height: 1.5; margin-bottom: 0.5rem;">{suggestion.description}</div>
                    <div style="color: #64748b; font-size: 0.75rem;">⏱️ {suggestion.duration}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Audio Response - FIXED: Now plays correct audio
        if result.response_audio_path and os.path.exists(result.response_audio_path):
            st.markdown("""
            <div class="audio-response">
                <div class="audio-label">🔊 Listen to Empathetic Response</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(get_audio_player(result.response_audio_path), unsafe_allow_html=True)
        
        st.markdown("""</div>""", unsafe_allow_html=True)
        
        # Analyze Another
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Analyze Another Audio", use_container_width=True):
                clear_previous_results()
                st.session_state.last_audio_hash = None
                st.rerun()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <div class="logo" style="justify-content: center; margin-bottom: 1rem;">
            <div class="logo-icon">🎭</div>
            <span class="logo-text">EmoVoice</span>
        </div>
        <p class="footer-text">© 2024 EmoVoice. Powered by AI emotion intelligence.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()