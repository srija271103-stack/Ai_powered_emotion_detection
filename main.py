#!/usr/bin/env python3
"""
EmoVoice - AI-Powered Emotion Intelligence
Main Entry Point

Run this script to start the application.
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.helpers import setup_logging
from loguru import logger


def run_streamlit():
    """Launch the Streamlit web interface."""
    import subprocess
    
    # Use the EmoVoice UI (with exact design match)
    app_path = project_root / "app" / "emovoice_ui.py"
    
    if not app_path.exists():
        # Fallback to futuristic_ui if emovoice_ui doesn't exist
        app_path = project_root / "app" / "futuristic_ui.py"
    
    logger.info(f"Starting EmoVoice UI: {app_path}")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false"
    ])


def run_cli(audio_path: str):
    """Run pipeline on a single audio file from command line."""
    from app.pipeline import process_audio
    
    logger.info(f"Processing audio file: {audio_path}")
    
    if not os.path.exists(audio_path):
        logger.error(f"File not found: {audio_path}")
        sys.exit(1)
    
    result = process_audio(audio_path)
    
    print("\n" + "="*60)
    print("MENTAL WELLNESS COMPANION - ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n📝 TRANSCRIPTION:")
    print(f"   {result.transcribed_text}")
    print(f"   Language: {result.detected_language}")
    
    print(f"\n🎭 EMOTION ANALYSIS:")
    print(f"   Voice Emotion: {result.voice_emotion} ({result.voice_confidence:.2f})")
    print(f"   Text Emotion: {result.text_emotion}")
    print(f"   Fused Emotion: {result.fused_emotion}")
    print(f"   Intensity: {result.intensity_level} ({result.emotion_intensity:.2f})")
    
    if result.safety_result.is_crisis:
        print(f"\n⚠️  SAFETY ALERT:")
        print(f"   {result.safety_result.priority_message}")
    
    print(f"\n💬 EMPATHETIC RESPONSE:")
    print(f"   {result.empathetic_response}")
    
    if result.wellness_suggestion:
        print(f"\n🌱 WELLNESS SUGGESTION:")
        print(f"   {result.wellness_suggestion.title}")
        print(f"   {result.wellness_suggestion.description}")
    
    if result.response_audio_path:
        print(f"\n🔊 Audio Response: {result.response_audio_path}")
    
    print(f"\n⏱️  Processing Time: {result.processing_time:.2f}s")
    print("="*60)


def run_demo():
    """Run a demonstration with sample text."""
    import asyncio
    from modules.text_emotion import text_analyzer
    from modules.emotion_fusion import emotion_fusion
    from modules.prosody_emotion import EmotionResult
    from modules.wellness_engine import wellness_engine
    from modules.response_generator import response_generator
    
    print("\n" + "="*60)
    print("MENTAL WELLNESS COMPANION - DEMO MODE")
    print("="*60)
    
    # Simulate user input
    sample_texts = [
        "I've been feeling so sad lately. Everything feels heavy and I can't seem to find joy in anything anymore.",
        "I'm so frustrated with everything! Nothing is working out and I just want to scream!",
        "I'm worried about the future. What if things don't get better? I feel so anxious all the time."
    ]
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\n--- Demo {i} ---")
        print(f"Input: \"{text}\"")
        
        # Analyze text emotion
        text_emotion = asyncio.run(text_analyzer.analyze_text(text))
        
        # Simulate voice emotion (in real use, this comes from Hume AI)
        voice_emotion = EmotionResult(
            primary_emotion=text_emotion.primary_emotion,
            confidence=0.75,
            all_emotions=text_emotion.all_emotions,
            intensity=0.6
        )
        
        # Fuse emotions
        fused = emotion_fusion.fuse_emotions(voice_emotion, text_emotion)
        
        print(f"Detected Emotion: {fused.primary_emotion} (intensity: {fused.intensity_level})")
        
        # Get wellness suggestion
        if not wellness_engine.should_skip_suggestion(fused):
            suggestion = wellness_engine.get_suggestion(fused)
            print(f"Wellness Suggestion: {suggestion.title}")
        
        # Generate response
        context = response_generator.create_context(text, fused)
        response = asyncio.run(response_generator.generate_response(context))
        
        print(f"Response: {response}")
        print()
    
    print("="*60)
    print("Demo complete! Run with --streamlit for the full web interface.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Mental Wellness Companion - Voice-based emotional support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --streamlit          Launch web interface
  python main.py --audio input.wav    Process single audio file
  python main.py --demo               Run demonstration mode
        """
    )
    
    parser.add_argument(
        "--streamlit",
        action="store_true",
        help="Launch the Streamlit web interface"
    )
    
    parser.add_argument(
        "--audio",
        type=str,
        help="Path to audio file to process"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demonstration mode with sample inputs"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Check for .env file
    env_file = project_root / ".env"
    if not env_file.exists():
        logger.warning("No .env file found. Copy .env.example to .env and add your API keys.")
    
    # Route to appropriate function
    if args.streamlit:
        logger.info("Starting Streamlit web interface...")
        run_streamlit()
    elif args.audio:
        run_cli(args.audio)
    elif args.demo:
        run_demo()
    else:
        # Default to Streamlit
        print("\nMental Wellness Companion")
        print("=" * 40)
        print("\nUsage options:")
        print("  python main.py --streamlit    Launch web interface")
        print("  python main.py --audio FILE   Process audio file")
        print("  python main.py --demo         Run demo mode")
        print("\nRun 'python main.py --help' for more options.")
        print("\nStarting web interface by default...")
        run_streamlit()


if __name__ == "__main__":
    main()