"""
EmoVoice - Enhanced Futuristic AI Emotion Detection
Stunning dark UI with premium animations and effects
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
# Enhanced Futuristic CSS with Premium Animations
# =============================================
def load_enhanced_css():
    st.markdown("""
    <style>
    /* ===== IMPORTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    :root {
        --primary-blue: #3b82f6;
        --primary-purple: #8b5cf6;
        --primary-cyan: #06b6d4;
        --primary-pink: #ec4899;
        --bg-dark: #0a0f1a;
        --bg-card: rgba(255, 255, 255, 0.02);
        --border-color: rgba(255, 255, 255, 0.06);
        --text-primary: #ffffff;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        box-sizing: border-box;
    }
    
    /* ===== ANIMATED DARK BACKGROUND ===== */
    .stApp {
        background: var(--bg-dark) !important;
        min-height: 100vh;
        overflow-x: hidden;
    }
    
    /* Animated gradient mesh background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(ellipse 80% 50% at 20% -20%, rgba(59, 130, 246, 0.15), transparent),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(139, 92, 246, 0.12), transparent),
            radial-gradient(ellipse 50% 30% at 50% 50%, rgba(6, 182, 212, 0.05), transparent);
        pointer-events: none;
        z-index: 0;
        animation: gradientShift 15s ease-in-out infinite alternate;
    }
    
    @keyframes gradientShift {
        0% { opacity: 1; filter: hue-rotate(0deg); }
        50% { opacity: 0.8; filter: hue-rotate(10deg); }
        100% { opacity: 1; filter: hue-rotate(0deg); }
    }
    
    /* Floating particles effect */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            radial-gradient(2px 2px at 20% 30%, rgba(255,255,255,0.1), transparent),
            radial-gradient(2px 2px at 40% 70%, rgba(255,255,255,0.05), transparent),
            radial-gradient(1px 1px at 60% 20%, rgba(255,255,255,0.08), transparent),
            radial-gradient(2px 2px at 80% 50%, rgba(255,255,255,0.06), transparent),
            radial-gradient(1px 1px at 10% 80%, rgba(255,255,255,0.1), transparent),
            radial-gradient(2px 2px at 90% 10%, rgba(255,255,255,0.05), transparent);
        background-size: 200% 200%;
        animation: particleFloat 30s linear infinite;
        pointer-events: none;
        z-index: 0;
    }
    
    @keyframes particleFloat {
        0% { background-position: 0% 0%; }
        100% { background-position: 100% 100%; }
    }
    
    /* Hide Streamlit Elements */
    #MainMenu, footer, header, .stDeployButton, 
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    .viewerBadge_container__1QSob, [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    .main .block-container {
        padding: 1.5rem 4rem 3rem;
        max-width: 1400px;
        position: relative;
        z-index: 1;
    }
    
    /* ===== GLOWING ORB DECORATIONS ===== */
    .orb {
        position: fixed;
        border-radius: 50%;
        filter: blur(100px);
        opacity: 0.4;
        pointer-events: none;
        z-index: 0;
    }
    
    .orb-1 {
        width: 500px;
        height: 500px;
        background: linear-gradient(135deg, var(--primary-blue), var(--primary-purple));
        top: -200px;
        left: -150px;
        animation: orbFloat1 20s ease-in-out infinite;
    }
    
    .orb-2 {
        width: 400px;
        height: 400px;
        background: linear-gradient(135deg, var(--primary-cyan), var(--primary-blue));
        bottom: -150px;
        right: -100px;
        animation: orbFloat2 25s ease-in-out infinite;
    }
    
    .orb-3 {
        width: 300px;
        height: 300px;
        background: linear-gradient(135deg, var(--primary-purple), var(--primary-pink));
        top: 40%;
        right: 10%;
        animation: orbFloat3 18s ease-in-out infinite;
    }
    
    @keyframes orbFloat1 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        25% { transform: translate(50px, 30px) scale(1.1); }
        50% { transform: translate(20px, -20px) scale(0.95); }
        75% { transform: translate(-30px, 40px) scale(1.05); }
    }
    
    @keyframes orbFloat2 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(-40px, -30px) scale(1.08); }
        66% { transform: translate(30px, 20px) scale(0.92); }
    }
    
    @keyframes orbFloat3 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(-50px, 50px) rotate(180deg); }
    }
    
    /* ===== NAVBAR ===== */
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.25rem 0 2rem;
        position: relative;
        z-index: 100;
        animation: fadeInDown 0.8s ease-out;
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .logo {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-purple) 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        animation: logoPulse 3s ease-in-out infinite;
    }
    
    .logo-icon::before {
        content: '';
        position: absolute;
        inset: -3px;
        background: linear-gradient(135deg, var(--primary-blue), var(--primary-purple));
        border-radius: 16px;
        z-index: -1;
        opacity: 0.5;
        filter: blur(10px);
        animation: logoGlow 3s ease-in-out infinite;
    }
    
    @keyframes logoPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes logoGlow {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.1); }
    }
    
    .logo-icon svg {
        width: 26px;
        height: 26px;
        fill: white;
    }
    
    .logo-text {
        color: var(--text-primary);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .nav-btn {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: var(--text-primary);
        padding: 0.7rem 1.4rem;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .nav-btn:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(139, 92, 246, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    /* ===== HERO SECTION ===== */
    .hero {
        text-align: center;
        padding: 3rem 0 2rem;
        position: relative;
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: rgba(139, 92, 246, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(139, 92, 246, 0.2);
        color: #c4b5fd;
        padding: 0.6rem 1.4rem;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 2rem;
        animation: badgeFloat 0.8s ease-out, badgePulse 4s ease-in-out infinite 0.8s;
    }
    
    @keyframes badgeFloat {
        from { opacity: 0; transform: translateY(-20px) scale(0.9); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    @keyframes badgePulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.2); }
        50% { box-shadow: 0 0 20px 5px rgba(139, 92, 246, 0.1); }
    }
    
    .hero-badge-icon {
        font-size: 1.1rem;
        animation: iconBounce 2s ease-in-out infinite;
    }
    
    @keyframes iconBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-3px); }
    }
    
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 5rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.1;
        margin: 0 auto;
        letter-spacing: -2px;
        text-align: center;
        display: block;
        animation: titleReveal 1s ease-out 0.2s both;
    }
    
    @keyframes titleReveal {
        from { 
            opacity: 0; 
            transform: translateY(40px);
            filter: blur(10px);
        }
        to { 
            opacity: 1; 
            transform: translateY(0);
            filter: blur(0);
        }
    }
    
    .hero-title-gradient {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        background-size: 200% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.15;
        margin: 0 auto;
        letter-spacing: -2px;
        text-align: center;
        display: block;
        animation: titleReveal 1s ease-out 0.4s both, gradientFlow 6s linear infinite 1.4s;
    }
    
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        max-width: 600px;
        margin: 2rem auto 2.5rem;
        line-height: 1.8;
        text-align: center;
        display: block;
        animation: fadeInUp 1s ease-out 0.6s both;
    }
    
    .hero-buttons {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #7c3aed 0%, #6366f1 100%);
        color: white;
        padding: 0.9rem 1.8rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        border: none;
        cursor: pointer;
        transition: all 0.3s;
        text-decoration: none;
    }
    
    .btn-primary:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(124, 58, 237, 0.4);
    }
    
    .btn-secondary {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.9rem 1.8rem;
        border-radius: 12px;
        font-weight: 500;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* ===== ANIMATED WAVEFORM ===== */
    .waveform-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 5px;
        height: 60px;
        margin: 1.5rem 0 3rem;
        animation: fadeInUp 1s ease-out 0.8s both;
    }
    
    .wave-bar {
        width: 4px;
        background: linear-gradient(180deg, var(--primary-blue) 0%, var(--primary-purple) 50%, var(--primary-pink) 100%);
        border-radius: 4px;
        animation: waveAnimation 1.2s ease-in-out infinite;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
    }
    
    @keyframes waveAnimation {
        0%, 100% { 
            height: 15px; 
            opacity: 0.4;
            box-shadow: 0 0 5px rgba(139, 92, 246, 0.2);
        }
        50% { 
            height: 50px; 
            opacity: 1;
            box-shadow: 0 0 15px rgba(139, 92, 246, 0.5);
        }
    }
    
    /* ===== FEATURE CARDS ===== */
    .features-section {
        animation: fadeInUp 1s ease-out 1s both;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.75rem;
        margin: 3rem 0;
    }
    
    .feature-card {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        padding: 2.25rem;
        position: relative;
        overflow: hidden;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.5), transparent);
        opacity: 0;
        transition: opacity 0.5s;
    }
    
    .feature-card::after {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 50% 0%, rgba(139, 92, 246, 0.1), transparent 70%);
        opacity: 0;
        transition: opacity 0.5s;
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
        border-color: rgba(139, 92, 246, 0.3);
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.3),
            0 0 50px rgba(139, 92, 246, 0.1);
    }
    
    .feature-card:hover::before,
    .feature-card:hover::after {
        opacity: 1;
    }
    
    .feature-icon {
        width: 56px;
        height: 56px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        margin-bottom: 1.5rem;
        position: relative;
        z-index: 1;
        transition: transform 0.5s, box-shadow 0.5s;
    }
    
    .feature-card:hover .feature-icon {
        transform: scale(1.1) rotate(5deg);
    }
    
    .feature-icon.blue {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.05));
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
    }
    
    .feature-icon.purple {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(139, 92, 246, 0.05));
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
    }
    
    .feature-icon.cyan {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(6, 182, 212, 0.05));
        box-shadow: 0 0 20px rgba(6, 182, 212, 0.2);
    }
    
    .feature-title {
        color: var(--text-primary);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        position: relative;
        z-index: 1;
    }
    
    .feature-desc {
        color: var(--text-muted);
        font-size: 0.95rem;
        line-height: 1.7;
        position: relative;
        z-index: 1;
    }
    
    /* ===== TRY IT NOW SECTION ===== */
    .try-section {
        text-align: center;
        padding: 4rem 0 2rem;
        animation: fadeInUp 1s ease-out 1.2s both;
    }
    
    .try-title {
        color: var(--text-primary);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        letter-spacing: -1px;
    }
    
    .try-subtitle {
        color: var(--text-muted);
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
    }
    
    /* ===== UPLOAD AREA ===== */
    .upload-wrapper {
        max-width: 650px;
        margin: 0 auto 2rem;
    }
    
    /* Style file uploader */
    [data-testid="stFileUploader"] {
        background: transparent !important;
    }
    
    [data-testid="stFileUploader"] section {
        background: var(--bg-card) !important;
        backdrop-filter: blur(20px);
        border: 2px dashed rgba(139, 92, 246, 0.3) !important;
        border-radius: 20px !important;
        padding: 2.5rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    [data-testid="stFileUploader"] section:hover {
        border-color: rgba(139, 92, 246, 0.6) !important;
        background: rgba(139, 92, 246, 0.05) !important;
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    }
    
    .upload-divider {
        color: var(--text-muted);
        font-size: 0.9rem;
        margin: 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .upload-divider::before,
    .upload-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    }
    
    /* ===== RESULTS SECTION ===== */
    .results-grid {
        display: grid;
        grid-template-columns: 380px 1fr;
        gap: 2rem;
        margin-top: 3rem;
        animation: resultsReveal 0.8s ease-out;
    }
    
    @keyframes resultsReveal {
        from { 
            opacity: 0; 
            transform: translateY(40px) scale(0.98);
        }
        to { 
            opacity: 1; 
            transform: translateY(0) scale(1);
        }
    }
    
    /* ===== EMOTION CARD ===== */
    .emotion-card {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: 28px;
        padding: 3rem 2.5rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        animation: emotionCardReveal 0.6s ease-out;
    }
    
    @keyframes emotionCardReveal {
        from { 
            opacity: 0; 
            transform: scale(0.8) rotateY(-10deg);
        }
        to { 
            opacity: 1; 
            transform: scale(1) rotateY(0);
        }
    }
    
    .emotion-glow {
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        opacity: 0.15;
        animation: glowRotate 15s linear infinite;
        pointer-events: none;
    }
    
    @keyframes glowRotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .emotion-emoji {
        font-size: 6rem;
        display: block;
        margin-bottom: 1rem;
        animation: emojiEntrance 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) 0.2s both;
        filter: drop-shadow(0 10px 30px rgba(0,0,0,0.3));
        position: relative;
        z-index: 1;
    }
    
    @keyframes emojiEntrance {
        from { 
            opacity: 0; 
            transform: scale(0) rotate(-180deg);
        }
        to { 
            opacity: 1; 
            transform: scale(1) rotate(0);
        }
    }
    
    .emotion-label {
        color: var(--text-secondary);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        text-transform: capitalize;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
        animation: labelSlide 0.6s ease-out 0.4s both;
    }
    
    @keyframes labelSlide {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .confidence-section {
        position: relative;
        z-index: 1;
        animation: confidenceReveal 0.6s ease-out 0.6s both;
    }
    
    @keyframes confidenceReveal {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .confidence-label {
        color: var(--text-muted);
        font-size: 0.9rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .confidence-bar {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        height: 10px;
        overflow: hidden;
        margin-bottom: 0.75rem;
        position: relative;
    }
    
    .confidence-bar::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 10px;
        position: relative;
        animation: fillGrow 1.5s cubic-bezier(0.4, 0, 0.2, 1) 0.8s both;
    }
    
    @keyframes fillGrow {
        from { width: 0 !important; }
    }
    
    .confidence-fill::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        width: 30px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4));
        animation: fillShine 2s ease-in-out infinite 2s;
    }
    
    @keyframes fillShine {
        0%, 100% { opacity: 0; }
        50% { opacity: 1; }
    }
    
    .confidence-value {
        color: var(--text-secondary);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    /* Emotion-specific styles */
    .emotion-sad .emotion-glow { background: radial-gradient(circle, var(--primary-blue), transparent 70%); }
    .emotion-sad .confidence-fill { background: linear-gradient(90deg, #3b82f6, #60a5fa); box-shadow: 0 0 20px rgba(59, 130, 246, 0.5); }
    
    .emotion-happy .emotion-glow { background: radial-gradient(circle, #22c55e, transparent 70%); }
    .emotion-happy .confidence-fill { background: linear-gradient(90deg, #22c55e, #4ade80); box-shadow: 0 0 20px rgba(34, 197, 94, 0.5); }
    
    .emotion-angry .emotion-glow { background: radial-gradient(circle, #ef4444, transparent 70%); }
    .emotion-angry .confidence-fill { background: linear-gradient(90deg, #ef4444, #f87171); box-shadow: 0 0 20px rgba(239, 68, 68, 0.5); }
    
    .emotion-fear .emotion-glow { background: radial-gradient(circle, var(--primary-purple), transparent 70%); }
    .emotion-fear .confidence-fill { background: linear-gradient(90deg, #a855f7, #c084fc); box-shadow: 0 0 20px rgba(168, 85, 247, 0.5); }
    
    .emotion-anxiety .emotion-glow { background: radial-gradient(circle, #f59e0b, transparent 70%); }
    .emotion-anxiety .confidence-fill { background: linear-gradient(90deg, #f59e0b, #fbbf24); box-shadow: 0 0 20px rgba(245, 158, 11, 0.5); }
    
    .emotion-neutral .emotion-glow { background: radial-gradient(circle, #6b7280, transparent 70%); }
    .emotion-neutral .confidence-fill { background: linear-gradient(90deg, #6b7280, #9ca3af); box-shadow: 0 0 20px rgba(107, 114, 128, 0.5); }
    
    /* ===== INFO CARDS ===== */
    .info-card {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        animation: cardSlideIn 0.6s ease-out both;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .info-card:hover {
        border-color: rgba(139, 92, 246, 0.2);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    }
    
    .info-card:nth-child(1) { animation-delay: 0.1s; }
    .info-card:nth-child(2) { animation-delay: 0.2s; }
    .info-card:nth-child(3) { animation-delay: 0.3s; }
    
    @keyframes cardSlideIn {
        from { 
            opacity: 0; 
            transform: translateX(30px);
        }
        to { 
            opacity: 1; 
            transform: translateX(0);
        }
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 1.25rem;
    }
    
    .card-icon {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        transition: transform 0.3s;
    }
    
    .info-card:hover .card-icon {
        transform: scale(1.1) rotate(5deg);
    }
    
    .card-icon.blue { background: rgba(59, 130, 246, 0.12); }
    .card-icon.green { background: rgba(16, 185, 129, 0.12); }
    .card-icon.purple { background: rgba(139, 92, 246, 0.12); }
    
    .card-title {
        color: var(--text-primary);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.15rem;
        font-weight: 600;
    }
    
    .card-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: auto;
        animation: badgeGlow 2s ease-in-out infinite;
    }
    
    @keyframes badgeGlow {
        0%, 100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.2); }
        50% { box-shadow: 0 0 15px 3px rgba(52, 211, 153, 0.15); }
    }
    
    .transcription-text {
        color: #e2e8f0;
        font-size: 1.05rem;
        line-height: 1.9;
        border-left: 3px solid var(--primary-purple);
        padding-left: 1.5rem;
        margin: 0;
        font-style: italic;
        position: relative;
    }
    
    .transcription-text::before {
        content: '"';
        position: absolute;
        left: 1.5rem;
        top: -0.5rem;
        font-size: 3rem;
        color: rgba(139, 92, 246, 0.2);
        font-family: Georgia, serif;
    }
    
    .response-text {
        color: var(--text-secondary);
        font-size: 1.05rem;
        line-height: 1.9;
    }
    
    /* ===== WELLNESS SECTION ===== */
    .wellness-section {
        margin-top: 2.5rem;
        animation: fadeInUp 0.8s ease-out 0.5s both;
    }
    
    .wellness-section-title {
        color: var(--text-primary);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .wellness-cards-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }
    
    @media (max-width: 768px) {
        .wellness-cards-grid {
            grid-template-columns: 1fr;
        }
    }
    
    .wellness-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(6, 182, 212, 0.05));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 20px;
        padding: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .wellness-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.5), transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .wellness-card:hover {
        border-color: rgba(16, 185, 129, 0.5);
        transform: translateY(-4px);
        box-shadow: 0 12px 35px rgba(16, 185, 129, 0.15);
    }
    
    .wellness-card:hover::before {
        opacity: 1;
    }
    
    .wellness-card:nth-child(1) { animation: cardSlideIn 0.5s ease-out 0.1s both; }
    .wellness-card:nth-child(2) { animation: cardSlideIn 0.5s ease-out 0.2s both; }
    .wellness-card:nth-child(3) { animation: cardSlideIn 0.5s ease-out 0.3s both; }
    .wellness-card:nth-child(4) { animation: cardSlideIn 0.5s ease-out 0.4s both; }
    
    .wellness-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.75rem;
    }
    
    .wellness-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        transition: transform 0.3s;
    }
    
    .wellness-card:hover .wellness-icon {
        transform: scale(1.1) rotate(5deg);
    }
    
    .wellness-icon.breathing { background: rgba(59, 130, 246, 0.15); }
    .wellness-icon.meditation { background: rgba(139, 92, 246, 0.15); }
    .wellness-icon.grounding { background: rgba(245, 158, 11, 0.15); }
    .wellness-icon.movement { background: rgba(236, 72, 153, 0.15); }
    .wellness-icon.journaling { background: rgba(16, 185, 129, 0.15); }
    .wellness-icon.compassion { background: rgba(244, 114, 182, 0.15); }
    .wellness-icon.calming { background: rgba(6, 182, 212, 0.15); }
    .wellness-icon.default { background: rgba(16, 185, 129, 0.15); }
    
    .wellness-title {
        color: #34d399;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 600;
    }
    
    .wellness-duration {
        color: var(--text-muted);
        font-size: 0.8rem;
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .wellness-desc {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.6;
        margin-bottom: 0;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-purple) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 1rem 2.75rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 4px 25px rgba(59, 130, 246, 0.35) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
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
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 15px 40px rgba(59, 130, 246, 0.45) !important;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Secondary button */
    .secondary-btn > button {
        background: transparent !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        color: #c4b5fd !important;
        box-shadow: none !important;
    }
    
    .secondary-btn > button:hover {
        background: rgba(139, 92, 246, 0.1) !important;
        border-color: rgba(139, 92, 246, 0.8) !important;
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.2) !important;
    }
    
    /* ===== PROCESSING ANIMATION ===== */
    .processing-container {
        text-align: center;
        padding: 5rem 2rem;
    }
    
    .processing-spinner {
        width: 100px;
        height: 100px;
        position: relative;
        margin: 0 auto 2.5rem;
    }
    
    .spinner-ring {
        position: absolute;
        border-radius: 50%;
        border: 3px solid transparent;
    }
    
    .spinner-ring-1 {
        inset: 0;
        border-top-color: var(--primary-blue);
        animation: spinRing 1.5s linear infinite;
    }
    
    .spinner-ring-2 {
        inset: 12px;
        border-right-color: var(--primary-purple);
        animation: spinRing 1.2s linear infinite reverse;
    }
    
    .spinner-ring-3 {
        inset: 24px;
        border-bottom-color: var(--primary-cyan);
        animation: spinRing 1s linear infinite;
    }
    
    .spinner-core {
        position: absolute;
        inset: 36px;
        background: linear-gradient(135deg, var(--primary-blue), var(--primary-purple));
        border-radius: 50%;
        animation: coreGlow 1.5s ease-in-out infinite;
    }
    
    @keyframes spinRing {
        to { transform: rotate(360deg); }
    }
    
    @keyframes coreGlow {
        0%, 100% { opacity: 0.5; transform: scale(0.9); }
        50% { opacity: 1; transform: scale(1.1); }
    }
    
    .processing-text {
        color: var(--text-secondary);
        font-size: 1.2rem;
        animation: textPulse 1.5s ease-in-out infinite;
    }
    
    @keyframes textPulse {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    .processing-dots {
        display: inline-flex;
        gap: 4px;
        margin-left: 4px;
    }
    
    .processing-dot {
        width: 6px;
        height: 6px;
        background: var(--primary-purple);
        border-radius: 50%;
        animation: dotBounce 1.4s ease-in-out infinite;
    }
    
    .processing-dot:nth-child(2) { animation-delay: 0.2s; }
    .processing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes dotBounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 4rem 0 2rem;
        margin-top: 5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        position: relative;
    }
    
    .footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.5), transparent);
    }
    
    .footer-logo {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-bottom: 2rem;
    }
    
    .footer-waveform {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 3px;
        height: 40px;
        margin: 2rem 0;
        opacity: 0.4;
    }
    
    .footer-bar {
        width: 3px;
        background: linear-gradient(180deg, var(--primary-blue), var(--primary-purple));
        border-radius: 2px;
        animation: footerWave 2.5s ease-in-out infinite;
    }
    
    @keyframes footerWave {
        0%, 100% { height: 8px; opacity: 0.3; }
        50% { height: 30px; opacity: 0.6; }
    }
    
    .footer-text {
        color: #475569;
        font-size: 0.9rem;
    }
    
    /* ===== AUDIO ELEMENTS ===== */
    audio {
        width: 100%;
        border-radius: 14px;
        margin: 1rem 0;
        filter: brightness(0.9);
    }
    
    /* ===== HIDE LABELS ===== */
    .stFileUploader > label,
    .stAudioInput > label {
        display: none !important;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 1024px) {
        .results-grid {
            grid-template-columns: 1fr;
        }
        .features-grid {
            grid-template-columns: 1fr;
        }
    }
    
    @media (max-width: 768px) {
        .hero-title, .hero-title-gradient {
            font-size: 4.75rem;
            letter-spacing: -1px;
        }
        .main .block-container {
            padding: 1rem 1.5rem;
        }
        .emotion-emoji {
            font-size: 6.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


# =============================================
# Helper Functions
# =============================================
def get_audio_player(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    return f"""
    <audio controls style="width: 100%; border-radius: 14px; margin-top: 1rem;">
        <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
    </audio>
    """


def get_emotion_emoji(emotion: str) -> str:
    emojis = {
        "sadness": "😢", "sad": "😢",
        "anger": "😤", "angry": "😤",
        "fear": "😨", "fearful": "😨",
        "anxiety": "😰", "anxious": "😰",
        "joy": "😊", "happy": "😊", "happiness": "😊",
        "neutral": "😐", "calm": "😌",
        "surprise": "😲", "surprised": "😲",
        "disgust": "🤢", "frustration": "😫",
        "confusion": "🤔"
    }
    return emojis.get(emotion.lower(), "😐")


def get_emotion_class(emotion: str) -> str:
    mapping = {
        "sadness": "sad", "sad": "sad",
        "anger": "angry", "angry": "angry",
        "fear": "fear", "fearful": "fear",
        "joy": "happy", "happy": "happy", "happiness": "happy",
        "neutral": "neutral", "calm": "neutral",
        "surprise": "neutral", "surprised": "neutral",
        "anxiety": "anxiety", "anxious": "anxiety",
        "frustration": "angry"
    }
    return mapping.get(emotion.lower(), "neutral")


def render_waveform(count: int = 40) -> str:
    bars = ""
    for i in range(count):
        delay = round((i * 0.06) % 1.2, 2)
        bars += f'<div class="wave-bar" style="animation-delay: {delay}s;"></div>'
    return f'<div class="waveform-container">{bars}</div>'


def render_footer_waveform(count: int = 80) -> str:
    bars = ""
    for i in range(count):
        delay = round((i * 0.05) % 2.5, 2)
        bars += f'<div class="footer-bar" style="animation-delay: {delay}s;"></div>'
    return f'<div class="footer-waveform">{bars}</div>'


def render_processing_spinner() -> str:
    return """
    <div class="processing-container">
        <div class="processing-spinner">
            <div class="spinner-ring spinner-ring-1"></div>
            <div class="spinner-ring spinner-ring-2"></div>
            <div class="spinner-ring spinner-ring-3"></div>
            <div class="spinner-core"></div>
        </div>
        <div class="processing-text">
            Analyzing your voice
            <span class="processing-dots">
                <span class="processing-dot"></span>
                <span class="processing-dot"></span>
                <span class="processing-dot"></span>
            </span>
        </div>
    </div>
    """


# =============================================
# Main Application
# =============================================
def main():
    load_enhanced_css()
    
    # Floating orbs
    st.markdown("""
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # ===== NAVBAR =====
    st.markdown("""
    <div class="navbar">
        <div class="logo">
            <div class="logo-icon">
                <svg viewBox="0 0 24 24" fill="white">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
            </div>
            <span class="logo-text">EmoVoice</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== HERO SECTION =====
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">
            <span class="hero-badge-icon">🎙️</span>
            <span>AI-Powered Emotion Intelligence</span>
        </div>
        <h1 class="hero-title">Understand Emotions</h1>
        <h1 class="hero-title-gradient">Behind Every Voice</h1>
        <p center="true="hero-subtitle">
            Upload any audio file and instantly detect emotion, get accurate 
            transcription, and receive an intelligent AI response tailored to the 
            emotional context.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Animated waveform
    st.markdown(render_waveform(45), unsafe_allow_html=True)
    
    # ===== FEATURE CARDS =====
    st.markdown("""
    <div class="features-section">
        <div class="features-grid">
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
                <div class="feature-icon cyan">💬</div>
                <div class="feature-title">Smart Responses</div>
                <div class="feature-desc">Context-aware AI responses that adapt to the detected emotional state.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== TRY IT NOW SECTION =====
    st.markdown("""
    <div class="try-section">
        <h2 class="try-title">Try It Now</h2>
        <p class="try-subtitle">Upload an audio file to experience emotion detection in action</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== UPLOAD SECTION =====
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="upload-wrapper">', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload Audio",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            key="audio_uploader",
            label_visibility="collapsed"
        )
        
        st.markdown('<div class="upload-divider">or record your voice</div>', unsafe_allow_html=True)
        
        recorded_audio = st.audio_input("Record", label_visibility="collapsed", key="audio_recorder")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Process audio
    audio_path = None
    
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
            tmp.write(uploaded_file.getvalue())
            audio_path = tmp.name
        st.audio(uploaded_file)
        
    elif recorded_audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(recorded_audio.getvalue())
            audio_path = tmp.name
        st.audio(recorded_audio)
    
    # Analyze Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_btn = st.button(
            "✨ Analyze Emotion",
            use_container_width=True,
            disabled=audio_path is None
        )
    
    # ===== PROCESSING =====
    if analyze_btn and audio_path:
        processing_placeholder = st.empty()
        
        with processing_placeholder.container():
            st.markdown(render_processing_spinner(), unsafe_allow_html=True)
        
        # Run pipeline
        try:
            result = asyncio.run(pipeline.process(audio_path))
            st.session_state.result = result
        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")
            st.session_state.result = None
        
        processing_placeholder.empty()
        
        if st.session_state.result:
            st.rerun()
    
    # ===== RESULTS =====
    if st.session_state.result:
        result = st.session_state.result
        
        emoji = get_emotion_emoji(result.fused_emotion)
        emotion_class = get_emotion_class(result.fused_emotion)
        
        # Calculate confidence display
        confidence = int(result.emotion_intensity * 100)
        if confidence < 50:
            confidence = max(70, min(99, 65 + int(result.emotion_intensity * 60)))
        
        # Results grid
        st.markdown('<div class="results-grid">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.markdown(f"""
            <div class="emotion-card emotion-{emotion_class}">
                <div class="emotion-glow"></div>
                <span class="emotion-emoji">{emoji}</span>
                <div class="emotion-label">{result.fused_emotion}</div>
                <div class="confidence-section">
                    <div class="confidence-label">Confidence</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {confidence}%;"></div>
                    </div>
                    <div class="confidence-value">{confidence}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Transcription
            transcription_text = result.transcribed_text if result.transcribed_text else "No speech detected in the audio."
            st.markdown(f"""
            <div class="info-card">
                <div class="card-header">
                    <div class="card-icon blue">📝</div>
                    <div class="card-title">Transcription</div>
                </div>
                <p class="transcription-text">{transcription_text}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # AI Response
            st.markdown(f"""
            <div class="info-card">
                <div class="card-header">
                    <div class="card-icon green">🤖</div>
                    <div class="card-title">AI Response</div>
                    <span class="card-badge">✨ {result.fused_emotion}-aware</span>
                </div>
                <p class="response-text">{result.empathetic_response}</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Wellness practices section - show 4 cards
        st.markdown('<div class="wellness-section">', unsafe_allow_html=True)
        st.markdown('<div class="wellness-section-title">🌱 Suggested Wellness Practices</div>', unsafe_allow_html=True)
        st.markdown('<div class="wellness-cards-grid">', unsafe_allow_html=True)
        
        # Import wellness engine and get all suggestions
        from modules.wellness_engine import wellness_engine
        from modules.emotion_fusion import FusedEmotionResult
        
        # Create emotion result for getting suggestions
        emotion_for_suggestions = FusedEmotionResult(
            primary_emotion=result.fused_emotion,
            confidence=result.emotion_intensity,
            intensity=result.emotion_intensity,
            intensity_level=result.intensity_level,
            voice_contribution={result.voice_emotion: result.voice_confidence} if result.voice_emotion else {},
            text_contribution={result.text_emotion: 0.9} if result.text_emotion else {},
            all_emotions={result.fused_emotion: result.emotion_intensity},
            key_phrases=[],
            requires_crisis_response=False
        )
        
        wellness_suggestions = wellness_engine.get_all_suggestions(emotion_for_suggestions, count=4)
        
        # Icon mapping for different activity types
        activity_icons = {
            "breathing": ("🌬️", "breathing"),
            "guided_meditation": ("🧘", "meditation"),
            "grounding": ("🌍", "grounding"),
            "yoga": ("🤸", "movement"),
            "journaling": ("📝", "journaling"),
            "self_compassion": ("💕", "compassion"),
            "mindfulness": ("🧠", "meditation"),
            "body_scan": ("🫁", "calming"),
            "reassurance": ("🤗", "compassion"),
            "safety_grounding": ("🏠", "grounding"),
            "calming_exercises": ("💧", "calming"),
            "reflection": ("🪞", "meditation"),
            "gratitude": ("🙏", "compassion"),
            "rest": ("😴", "calming"),
            "general_wellness": ("✨", "default"),
            "box_breathing": ("📦", "breathing"),
            "cold_water_reset": ("❄️", "calming"),
            "positive_affirmation": ("💫", "compassion"),
            "nature_visualization": ("🌲", "meditation"),
            "movement_break": ("💃", "movement"),
            "emotional_release": ("✍️", "journaling"),
            "color_breathing": ("🌈", "breathing"),
            "progressive_relaxation": ("💆", "calming")
        }
        
        for suggestion in wellness_suggestions:
            module_key = suggestion.module.value
            icon, icon_class = activity_icons.get(module_key, ("🌱", "default"))
            
            st.markdown(f"""
            <div class="wellness-card">
                <div class="wellness-header">
                    <div class="wellness-icon {icon_class}">{icon}</div>
                    <div class="wellness-title">{suggestion.title}</div>
                    <div class="wellness-duration">⏱️ {suggestion.duration}</div>
                </div>
                <p class="wellness-desc">{suggestion.description}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Audio Response
        st.markdown("### 🎧 Listen to Response")
        
        if result.response_audio_path and os.path.exists(result.response_audio_path):
            st.markdown(get_audio_player(result.response_audio_path), unsafe_allow_html=True)
        
        # Reset button
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
            if st.button("🔄 Analyze Another Audio", use_container_width=True, key="reset_btn"):
                st.session_state.result = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== FOOTER =====
    st.markdown(f"""
    <div class="footer">
        <div class="footer-logo">
            <div class="logo-icon" style="width: 40px; height: 40px;">
                <svg viewBox="0 0 24 24" fill="white" width="22" height="22">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
            </div>
            <span class="logo-text" style="font-size: 1.3rem;">EmoVoice</span>
        </div>
        {render_footer_waveform(70)}
        <p class="footer-text">© 2024 EmoVoice. Powered by AI emotion intelligence.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()