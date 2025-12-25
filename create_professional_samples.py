#!/usr/bin/env python3
"""
Create professional emotional audio samples using Microsoft Edge Neural TTS.
Each emotion has distinct prosody characteristics.
"""

import asyncio
import sys
from pathlib import Path

async def create_professional_samples():
    # Install edge-tts if needed
    try:
        import edge_tts
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts", "-q"])
        import edge_tts
    
    samples_dir = Path(__file__).parent / "samples"
    samples_dir.mkdir(exist_ok=True)
    
    # Clean existing files
    for f in samples_dir.glob("*.mp3"):
        f.unlink()
    
    print("=" * 60)
    print("Creating Professional Emotional Audio Samples")
    print("=" * 60)
    
    # Professional emotional samples with distinct prosody
    emotions = {
        "angry": {
            "voice": "en-US-GuyNeural",
            "text": (
                "I am absolutely FURIOUS about this situation! "
                "This is COMPLETELY unacceptable! How DARE they treat me this way! "
                "I have been waiting for HOURS and nobody cares! "
                "Someone needs to take responsibility RIGHT NOW! "
                "I am SO angry I could SCREAM! This is OUTRAGEOUS! "
                "I demand answers IMMEDIATELY! I will NOT tolerate this!"
            ),
            "rate": "+25%",  # Fast, aggressive
            "pitch": "+15Hz",  # High pitch for shouting
        },
        "anxious": {
            "voice": "en-US-AriaNeural",
            "text": (
                "I... I don't know if I can do this... "
                "What if something goes wrong? What if I fail? "
                "My mind keeps racing with all these terrible thoughts... "
                "I feel like I can't catch my breath... "
                "Everything feels overwhelming... "
                "What if everyone judges me? I can't stop worrying... "
                "The pressure is too much... I'm so stressed..."
            ),
            "rate": "+15%",  # Fast, breathless
            "pitch": "+8Hz",  # Slightly higher, nervous
        },
        "fear": {
            "voice": "en-US-JennyNeural",
            "text": (
                "I... I'm so scared right now... "
                "What... what was that sound? "
                "Please... please don't hurt me... "
                "I... I can't breathe... My heart is pounding... "
                "Someone... someone help me please... "
                "I'm... I'm terrified... I don't know what to do... "
                "I just want to feel safe again..."
            ),
            "rate": "-5%",  # Slower, hesitant
            "pitch": "+12Hz",  # Higher pitch from fear
        },
        "happy": {
            "voice": "en-US-SaraNeural",
            "text": (
                "Oh, this is such a wonderful day! "
                "I'm feeling so grateful and blessed right now. "
                "Everything just feels so right, you know? "
                "I love spending time with the people I care about. "
                "Life is truly beautiful when you appreciate the little things. "
                "I feel so content and peaceful. "
                "Thank you for being here with me!"
            ),
            "rate": "+5%",  # Slightly upbeat
            "pitch": "+3Hz",  # Warm, natural
        },
        "sad": {
            "voice": "en-US-JennyNeural",
            "text": (
                "I feel so lost and empty inside... "
                "Nothing seems to bring me joy anymore... "
                "I don't know what to do... "
                "The pain just won't go away... "
                "I miss how things used to be... "
                "Sometimes I wonder if anyone even cares... "
                "Everything feels so heavy and hopeless..."
            ),
            "rate": "-25%",  # Very slow
            "pitch": "-8Hz",  # Low pitch
        },
        "surprised": {
            "voice": "en-US-JennyNeural",
            "text": (
                "Oh my goodness! I can't believe it! "
                "Is this really happening right now? "
                "Wow! I never expected this at all! "
                "Wait, WHAT? Are you serious? "
                "This is incredible! I'm completely shocked! "
                "No way! This is amazing news! "
                "I never saw this coming!"
            ),
            "rate": "+20%",  # Excited, fast
            "pitch": "+10Hz",  # Varied, exclamatory
        },
    }
    
    for emotion, config in emotions.items():
        print(f"\n  Creating {emotion}.mp3...")
        print(f"    Voice: {config['voice']}")
        print(f"    Rate: {config['rate']}, Pitch: {config['pitch']}")
        
        output_path = samples_dir / f"{emotion}.mp3"
        
        try:
            communicate = edge_tts.Communicate(
                config["text"],
                config["voice"],
                rate=config["rate"],
                pitch=config["pitch"]
            )
            
            await communicate.save(str(output_path))
            
            # Get duration
            import librosa
            duration = librosa.get_duration(path=str(output_path))
            print(f"    ✓ Saved: {output_path.name} ({duration:.1f}s)")
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Professional Audio Samples Created!")
    print("=" * 60)
    print("\nEmotional Prosody Applied:")
    print("  😤 angry.mp3     - HIGH pitch, FAST, SHOUTING")
    print("  😰 anxious.mp3   - Fast, breathless, nervous")
    print("  😨 fear.mp3      - Hesitant, trembling, high pitch")
    print("  😊 happy.mp3     - Warm, content, natural tone")
    print("  😢 sad.mp3       - SLOW, LOW pitch, soft")
    print("  😲 surprised.mp3 - Varied pitch, exclamatory")
    print("\nTest at http://localhost:8501")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(create_professional_samples())
