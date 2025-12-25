"""
Mental Wellness Companion - Animated Landing Page
Modern, animated UI for emotion detection from voice
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
    page_title="🎭 Emotion Detector | Voice to Emotion AI",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =============================================
# Advanced Animated CSS
# =============================================
def load_animated_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #667eea, #764ba2, #6B8DD6, #8B5CF6);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating particles animation */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        overflow: hidden;
        z-index: 0;
    }
    
    /* Main container with glass effect */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 30px;
        padding: 3rem;
        margin-top: 2rem;
        box-shadow: 0 25px 80px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        animation: slideUp 0.8s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Hero Title with gradient text */
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeIn 1s ease-out;
    }
    
    .hero-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-out 0.3s both;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out both;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.15);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.25rem;
    }
    
    .feature-desc {
        font-size: 0.85rem;
        color: #64748b;
    }
    
    /* Upload area with pulse animation */
    .upload-area {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border: 3px dashed #667eea;
        border-radius: 25px;
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
        animation: pulse 2s ease infinite;
    }
    
    .upload-area:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #667eea25 0%, #764ba225 100%);
        animation: none;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4); }
        50% { box-shadow: 0 0 0 15px rgba(102, 126, 234, 0); }
    }
    
    .upload-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    /* Animated button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 1rem 3rem;
        font-size: 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.5);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Results section */
    .result-section {
        animation: slideUp 0.6s ease-out;
    }
    
    /* Transcription box with typing effect */
    .transcription-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 5px solid #667eea;
        position: relative;
        overflow: hidden;
    }
    
    .transcription-box::before {
        content: '📝 Transcription';
        position: absolute;
        top: -12px;
        left: 20px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 4px 15px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .transcription-text {
        color: #e2e8f0;
        font-size: 1.1rem;
        line-height: 1.8;
        font-style: italic;
        margin-top: 1rem;
    }
    
    /* Emotion display with bounce animation */
    .emotion-display {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 25px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.08);
        border: 2px solid rgba(102, 126, 234, 0.2);
        animation: bounceIn 0.8s ease-out;
    }
    
    @keyframes bounceIn {
        0% { transform: scale(0.8); opacity: 0; }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .emotion-emoji {
        font-size: 5rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .emotion-label {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 1rem;
    }
    
    .confidence-bar {
        background: #e2e8f0;
        border-radius: 20px;
        height: 12px;
        margin: 1rem auto;
        max-width: 200px;
        overflow: hidden;
    }
    
    .confidence-fill {
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        height: 100%;
        border-radius: 20px;
        animation: fillBar 1s ease-out;
    }
    
    @keyframes fillBar {
        from { width: 0; }
    }
    
    /* Response box with glow effect */
    .response-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 25px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 5px solid #0ea5e9;
        box-shadow: 0 10px 30px rgba(14, 165, 233, 0.1);
        position: relative;
        animation: glowPulse 3s ease infinite;
    }
    
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 10px 30px rgba(14, 165, 233, 0.1); }
        50% { box-shadow: 0 10px 40px rgba(14, 165, 233, 0.2); }
    }
    
    .response-label {
        font-weight: 700;
        color: #0369a1;
        font-size: 1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .response-text {
        color: #1e3a5f;
        font-size: 1.15rem;
        line-height: 1.8;
    }
    
    /* Wellness suggestion box */
    .wellness-box {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-radius: 25px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 5px solid #10b981;
        animation: slideInRight 0.6s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .wellness-title {
        font-weight: 700;
        color: #059669;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    .wellness-description {
        color: #065f46;
        line-height: 1.6;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 3rem;
    }
    
    .loading-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid #e2e8f0;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        margin-top: 1.5rem;
        color: #64748b;
        font-size: 1.1rem;
        animation: pulse 1.5s ease infinite;
    }
    
    /* Audio player styling */
    audio {
        width: 100%;
        border-radius: 50px;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* File uploader styling */
    .stFileUploader > div {
        padding: 0;
    }
    
    .stFileUploader label {
        display: none;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)


# =============================================
# Helper Functions
# =============================================
def get_audio_player(audio_path: str) -> str:
    """Generate HTML audio player."""
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    return f"""
    <audio controls autoplay style="width: 100%; border-radius: 50px;">
        <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
    </audio>
    """


def get_emotion_emoji(emotion: str) -> str:
    """Get emoji for emotion."""
    emojis = {
        "sadness": "😢", "sad": "😢",
        "anger": "😤", "angry": "😤",
        "fear": "😨", "fearful": "😨",
        "anxiety": "😰", "anxious": "😰",
        "joy": "😊", "happy": "😊",
        "neutral": "😐", "calm": "😌",
        "frustration": "😫", "confusion": "🤔",
        "surprise": "😲", "surprised": "😲",
        "disgust": "🤢",
    }
    return emojis.get(emotion.lower(), "🎭")


# =============================================
# Main Application
# =============================================
def main():
    load_animated_css()
    
    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Hero Section
    st.markdown("""
    <div class="hero-title">🎭 Voice Emotion AI</div>
    <p class="hero-subtitle">Upload your voice and discover the emotions within</p>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card" style="animation-delay: 0.1s;">
            <div class="feature-icon">🎤</div>
            <div class="feature-title">Upload Audio</div>
            <div class="feature-desc">MP3, WAV, M4A supported</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="animation-delay: 0.2s;">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">AI Detection</div>
            <div class="feature-desc">8 emotion categories</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card" style="animation-delay: 0.3s;">
            <div class="feature-icon">💬</div>
            <div class="feature-title">Get Response</div>
            <div class="feature-desc">Empathetic feedback</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Upload Section
    st.markdown("""
    <div class="upload-area">
        <div class="upload-icon">🎵</div>
        <p style="font-size: 1.2rem; color: #4b5563; margin: 0;">
            <strong>Drop your audio file here</strong><br>
            <span style="font-size: 0.9rem; color: #9ca3af;">or click to browse</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload audio",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
        label_visibility="collapsed"
    )
    
    audio_path = None
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded_file.getvalue())
            audio_path = tmp.name
        
        st.audio(uploaded_file)
    
    # Process Button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button(
            "✨ Analyze Emotion",
            use_container_width=True,
            disabled=audio_path is None
        )
    
    # Processing
    if process_button and audio_path:
        # Loading animation
        with st.spinner(""):
            st.markdown("""
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">🔍 Analyzing your voice...</div>
            </div>
            """, unsafe_allow_html=True)
            
            result = asyncio.run(pipeline.process(audio_path))
            st.session_state.result = result
    
    # Display Results
    if st.session_state.result:
        result = st.session_state.result
        
        st.markdown("<hr style='border: none; height: 2px; background: linear-gradient(90deg, transparent, #667eea, transparent); margin: 2rem 0;'>", unsafe_allow_html=True)
        
        # Transcription Box
        st.markdown(f"""
        <div class="transcription-box">
            <div class="transcription-text">
                "{result.transcribed_text}"
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Emotion Display
        emoji = get_emotion_emoji(result.fused_emotion)
        confidence = int(result.emotion_intensity * 100)
        
        st.markdown(f"""
        <div class="emotion-display">
            <div class="emotion-emoji">{emoji}</div>
            <div class="emotion-label">{result.fused_emotion}</div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {confidence}%;"></div>
            </div>
            <div style="color: #64748b; font-size: 0.9rem;">
                Confidence: {confidence}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Response Box
        st.markdown(f"""
        <div class="response-box">
            <div class="response-label">💙 Empathetic Response</div>
            <div class="response-text">
                {result.empathetic_response}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Audio Response
        if result.response_audio_path and os.path.exists(result.response_audio_path):
            st.markdown("#### 🔊 Listen to Response")
            st.markdown(get_audio_player(result.response_audio_path), unsafe_allow_html=True)
        
        # Wellness Suggestion
        if result.wellness_suggestion:
            suggestion = result.wellness_suggestion
            st.markdown(f"""
            <div class="wellness-box">
                <div class="wellness-title">🌱 {suggestion.title}</div>
                <div class="wellness-description">{suggestion.description}</div>
                <p style="color: #6b7280; font-size: 0.85rem; margin-top: 1rem;">
                    ⏱️ Duration: {suggestion.duration}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Reset Button
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Analyze Another", use_container_width=True):
                st.session_state.result = None
                st.rerun()


if __name__ == "__main__":
    main()
