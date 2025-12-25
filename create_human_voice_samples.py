#!/usr/bin/env python3
"""
Download REAL human emotional speech recordings.
Uses edge-tts (Microsoft Edge TTS) which sounds much more natural.
"""

import asyncio
import sys
from pathlib import Path

# Install edge-tts if needed
try:
    import edge_tts
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts", "-q"])
    import edge_tts


async def create_emotional_audio():
    samples_dir = Path(__file__).parent / "samples"
    samples_dir.mkdir(exist_ok=True)
    
    # Clean existing files
    for f in samples_dir.glob("*.wav"):
        f.unlink()
    for f in samples_dir.glob("*.mp3"):
        f.unlink()
    
    print("Creating natural emotional audio with Microsoft Edge TTS...")
    print("This voice sounds much more human-like!\n")
    
    # Using different voices for different emotions (natural sounding)
    # Microsoft Edge has very natural voices
    emotions = {
        "angry": {
            "voice": "en-US-GuyNeural",  # Male voice, good for angry
            "text": (
                "I am absolutely furious right now! This is completely unacceptable! "
                "I've been waiting for hours and nobody cares! How dare they treat me like this! "
                "I demand an explanation immediately! This is outrageous! "
                "Someone is going to pay for this! I've had enough of being treated like this! "
                "This is the last time I put up with this nonsense!"
            ),
            "style": "angry",
            "rate": "+15%",
            "pitch": "+10Hz"
        },
        "sad": {
            "voice": "en-US-JennyNeural",  # Female voice, emotional
            "text": (
                "I feel so lost and alone... Everything seems so pointless now... "
                "I don't know what to do anymore... The pain just won't go away... "
                "I miss how things used to be... I feel so empty inside... "
                "Sometimes I wonder if anyone even cares about me... "
                "The days just blend together and nothing brings me joy anymore..."
            ),
            "style": "sad",
            "rate": "-20%",
            "pitch": "-5Hz"
        },
        "fear": {
            "voice": "en-US-AriaNeural",  # Female voice, expressive
            "text": (
                "I... I don't know what's happening... I'm so scared right now... "
                "What was that sound? Please... please don't hurt me... "
                "I can't breathe... My heart is racing so fast... "
                "Someone help me please... I'm terrified... "
                "I don't want to be alone... Please, I need help..."
            ),
            "style": "fearful",
            "rate": "+5%",
            "pitch": "+15Hz"
        },
        "happy": {
            "voice": "en-US-SaraNeural",  # Female voice, cheerful
            "text": (
                "Oh this is wonderful! I'm so incredibly happy right now! "
                "Everything is going so well and I feel so blessed! "
                "I love spending time with the people I care about! "
                "Life is truly beautiful when you appreciate the little things! "
                "Thank you so much for being here! This is just perfect!"
            ),
            "style": "cheerful",
            "rate": "+10%",
            "pitch": "+5Hz"
        },
        "surprised": {
            "voice": "en-US-JennyNeural",
            "text": (
                "Oh my goodness! I can't believe it! Is this really happening? "
                "Wow! I never expected this at all! This is incredible! "
                "Wait, what? Are you serious right now? No way! "
                "I'm completely shocked! This is amazing news! "
                "I never saw this coming! This is unbelievable!"
            ),
            "style": "excited",
            "rate": "+20%",
            "pitch": "+10Hz"
        },
        "anxious": {
            "voice": "en-US-AriaNeural",
            "text": (
                "I... I don't know if I can do this... What if something goes wrong? "
                "My mind keeps racing with all these terrible thoughts... "
                "I feel like I can't catch my breath... Everything is too much... "
                "What if I fail? What if everyone judges me? "
                "I can't stop worrying about every little thing..."
            ),
            "style": "nervous",  # Not all styles are supported, will fall back
            "rate": "+8%",
            "pitch": "+8Hz"
        }
    }
    
    for emotion, config in emotions.items():
        print(f"  Creating {emotion}.mp3 with {config['voice']}...")
        
        output_path = samples_dir / f"{emotion}.mp3"
        
        try:
            # Create communicate object with SSML for better control
            communicate = edge_tts.Communicate(
                config["text"],
                config["voice"],
                rate=config["rate"],
                pitch=config["pitch"]
            )
            
            await communicate.save(str(output_path))
            print(f"    ✓ Saved: {output_path.name}")
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Done! Natural human-like voice samples created:")
    print("\n  😤 angry.mp3     - Male voice, angry tone")
    print("  😢 sad.mp3       - Female voice, sad tone")
    print("  😨 fear.mp3      - Female voice, fearful tone")
    print("  😊 happy.mp3     - Female voice, cheerful tone")
    print("  😲 surprised.mp3 - Female voice, excited tone")
    print("  😰 anxious.mp3   - Female voice, nervous tone")
    print("\nThese use Microsoft Edge Neural TTS - very human-like!")
    print("Upload to http://localhost:8501 to test!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(create_emotional_audio())
