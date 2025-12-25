"""
Mental Wellness Companion - Streamlit Web Interface
Beautiful, calming UI for voice-based emotional support
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
    page_title="Mental Wellness Companion",
    page_icon="💙",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =============================================
# Custom CSS - Calming Design
# =============================================
def load_custom_css():
    st.markdown("""
    <style>
    /* Main background - calming gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #6B8DD6 100%);
        background-attachment: fixed;
    }
    
    /* Main container */
    .main .block-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 24px;
        padding: 2.5rem;
        margin-top: 1.5rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    }
    
    /* Headers */
    h1 {
        color: #2d3748;
        text-align: center;
        font-weight: 700;
        font-size: 2.2rem;
    }
    
    h2, h3 {
        color: #667eea;
        font-weight: 600;
    }
    
    /* Professional Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 0.9rem 2.5rem;
        font-size: 1.15rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* File uploader */
    .stFileUploader {
        border: 3px dashed #667eea;
        border-radius: 20px;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
    }
    
    /* Response box - Empathetic */
    .response-box {
        background: linear-gradient(135deg, #f8f9ff 0%, #eef1ff 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
    }
    
    /* Emotion Card */
    .emotion-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: transform 0.3s ease;
    }
    
    .emotion-card:hover {
        transform: translateY(-5px);
    }
    
    /* Emotion badge */
    .emotion-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-size: 1rem;
        font-weight: 600;
        margin: 0.25rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Info boxes - Transcription */
    .info-box {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8eef5 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Wellness suggestion box */
    .wellness-box {
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 5px solid #00bcd4;
        box-shadow: 0 4px 20px rgba(0, 188, 212, 0.15);
    }
    
    .wellness-box h4 {
        color: #00838f;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Crisis alert */
    .crisis-alert {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 5px solid #ff9800;
        box-shadow: 0 4px 20px rgba(255, 152, 0, 0.15);
    }
    
    /* Intensity meter */
    .intensity-circle {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 1.3rem;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Audio player */
    audio {
        width: 100%;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    /* Progress indicator */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Section dividers */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


# =============================================
# Helper Functions
# =============================================
def get_audio_player(audio_path: str) -> str:
    """Generate HTML audio player for response."""
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    return f"""
    <audio controls autoplay>
        <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
        Your browser does not support the audio element.
    </audio>
    """


def get_emotion_emoji(emotion: str) -> str:
    """Get emoji for emotion."""
    emojis = {
        "sadness": "😢",
        "sad": "😢",
        "anger": "😤",
        "angry": "😤",
        "fear": "😨",
        "fearful": "😨",
        "anxiety": "😰",
        "anxious": "😰",
        "joy": "😊",
        "happy": "😊",
        "neutral": "😐",
        "calm": "😌",
        "frustration": "😫",
        "confusion": "🤔",
        "surprise": "😲",
        "surprised": "😲",
        "disgust": "🤢",
    }
    return emojis.get(emotion.lower(), "💭")


def get_intensity_color(level: str) -> str:
    """Get color for intensity level."""
    colors = {
        "low": "#4caf50",
        "mild": "#8bc34a",
        "moderate": "#ffc107",
        "high": "#ff9800",
        "crisis": "#f44336"
    }
    return colors.get(level, "#9e9e9e")


# =============================================
# Main Application
# =============================================
def main():
    load_custom_css()
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>💙 Mental Wellness Companion</h1>
        <p style="color: #666; font-size: 1.1rem;">
            A compassionate space to share how you're feeling
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # =============================================
    # Audio Input Section
    # =============================================
    st.markdown("### 🎙️ Share Your Thoughts")
    
    input_method = st.radio(
        "Choose how to share:",
        ["📁 Upload Audio File", "🎤 Record Now"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    audio_path = None
    
    if input_method == "📁 Upload Audio File":
        uploaded_file = st.file_uploader(
            "Upload your voice recording",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            help="Supported formats: WAV, MP3, M4A, OGG, FLAC"
        )
        
        if uploaded_file:
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=f".{uploaded_file.name.split('.')[-1]}"
            )
            temp_file.write(uploaded_file.read())
            audio_path = temp_file.name
            
            # Show uploaded audio
            st.audio(uploaded_file, format=f"audio/{uploaded_file.type.split('/')[-1]}")
    
    else:  # Record Now
        st.info("🎤 Click the button below to start recording")
        
        # Note: Streamlit doesn't have native recording, but we can use st.audio_input in newer versions
        # or use a custom component. For now, showing instructions.
        st.markdown("""
        <div class="info-box">
            <p><strong>Recording Instructions:</strong></p>
            <ol>
                <li>Click the microphone button</li>
                <li>Speak naturally about how you're feeling</li>
                <li>Click stop when finished</li>
            </ol>
            <p><em>Supported languages: English, Telugu, and mixed speech</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Try to use audio input if available (Streamlit 1.28+)
        try:
            audio_input = st.audio_input("Record your message")
            if audio_input:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_file.write(audio_input.read())
                audio_path = temp_file.name
        except AttributeError:
            st.warning("Live recording requires Streamlit 1.28+. Please upload a file instead.")
    
    # =============================================
    # Process Button
    # =============================================
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button(
            "💫 Listen to Me",
            use_container_width=True,
            disabled=audio_path is None
        )
    
    # =============================================
    # Processing
    # =============================================
    if process_button and audio_path:
        st.session_state.processing = True
        
        # Progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step-by-step progress
            status_text.text("🔊 Cleaning audio...")
            progress_bar.progress(10)
            
            status_text.text("🎭 Detecting emotions from your voice...")
            progress_bar.progress(30)
            
            status_text.text("📝 Understanding your words...")
            progress_bar.progress(50)
            
            status_text.text("💭 Processing your feelings...")
            progress_bar.progress(70)
            
            status_text.text("💙 Preparing a caring response...")
            progress_bar.progress(90)
            
            # Run pipeline
            result = asyncio.run(pipeline.process(audio_path))
            st.session_state.result = result
            
            progress_bar.progress(100)
            status_text.text("✨ Complete!")
            time.sleep(0.5)
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
            st.session_state.processing = False
            return
        
        st.session_state.processing = False
    
    # =============================================
    # Display Results
    # =============================================
    if st.session_state.result:
        result = st.session_state.result
        
        st.markdown("---")
        
        # What we heard
        st.markdown("### 📝 What I Heard")
        st.markdown(f"""
        <div class="info-box">
            <p style="font-style: italic; color: #555;">"{result.transcribed_text}"</p>
            <p style="font-size: 0.8rem; color: #888;">Language: {result.detected_language.upper()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Emotion Analysis
        st.markdown("### 🎭 How You're Feeling")
        
        col1, col2 = st.columns(2)
        
        with col1:
            emoji = get_emotion_emoji(result.fused_emotion)
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <span style="font-size: 3rem;">{emoji}</span>
                <h3 style="margin: 0.5rem 0; text-transform: capitalize;">{result.fused_emotion}</h3>
                <p style="color: #666;">Primary emotion detected</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            intensity_color = get_intensity_color(result.intensity_level)
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <div style="
                    width: 80px; height: 80px; 
                    border-radius: 50%; 
                    background: {intensity_color};
                    margin: 0 auto;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 1.2rem;
                ">{int(result.emotion_intensity * 100)}%</div>
                <h3 style="margin: 0.5rem 0; text-transform: capitalize;">{result.intensity_level}</h3>
                <p style="color: #666;">Emotional intensity</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Safety Alert if needed
        if result.safety_result.is_crisis:
            st.markdown(f"""
            <div class="crisis-alert">
                <h4>💙 You Matter</h4>
                <p>{result.safety_result.priority_message}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Empathetic Response
        st.markdown("### 💬 Response")
        st.markdown(f"""
        <div class="response-box">
            <p style="font-size: 1.1rem; line-height: 1.8; color: #333;">
                {result.empathetic_response}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Audio response
        if result.response_audio_path and os.path.exists(result.response_audio_path):
            st.markdown("#### 🔊 Listen to Response")
            st.markdown(get_audio_player(result.response_audio_path), unsafe_allow_html=True)
        
        # Wellness Suggestion
        if result.wellness_suggestion:
            suggestion = result.wellness_suggestion
            st.markdown(f"""
            <div class="wellness-box">
                <h4>🌱 {suggestion.title}</h4>
                <p>{suggestion.description}</p>
                <p style="font-size: 0.9rem; color: #666;">
                    ⏱️ Duration: {suggestion.duration}
                </p>
                <details>
                    <summary style="cursor: pointer; color: #26c6da;">Show steps</summary>
                    <ol style="margin-top: 0.5rem;">
                        {"".join(f"<li>{step}</li>" for step in suggestion.instructions)}
                    </ol>
                </details>
            </div>
            """, unsafe_allow_html=True)
        
        # Processing time
        st.markdown(f"""
        <p style="text-align: center; color: #888; font-size: 0.8rem; margin-top: 2rem;">
            Processed in {result.processing_time:.2f} seconds
        </p>
        """, unsafe_allow_html=True)
        
        # Reset button
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Start Over", use_container_width=True):
                st.session_state.result = None
                st.rerun()
    
    # =============================================
    # Footer
    # =============================================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.8rem; padding: 1rem;">
        <p>💙 Remember: You're not alone. It's okay to seek help.</p>
        <p>This is a supportive tool, not a replacement for professional care.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
