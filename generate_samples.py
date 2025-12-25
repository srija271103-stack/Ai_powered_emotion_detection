#!/usr/bin/env python3
"""Generate sample audio files with emotional speech for testing."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from modules.text_to_speech import emotion_tts

def main():
    samples_dir = Path(__file__).parent / "samples"
    samples_dir.mkdir(exist_ok=True)
    
    # Sample texts with different emotions
    samples = [
        ("sad", "I feel so sad and lonely today. Everything feels heavy and I can't find any joy."),
        ("angry", "I am so frustrated and angry! Nothing is going right and I can't take it anymore!"),
        ("happy", "I'm feeling so happy and grateful today! Everything is wonderful and life is beautiful!"),
        ("anxious", "I'm really worried and stressed about everything. I can't stop thinking about what might go wrong."),
        ("neutral", "Today I went to the store and bought some groceries. The weather was mild."),
    ]
    
    print("Generating sample audio files...")
    
    for emotion, text in samples:
        output_path = samples_dir / f"{emotion}_sample.wav"
        print(f"  Creating {emotion}_sample.wav...")
        
        try:
            result = emotion_tts.synthesize(text, emotion)
            if result:
                # Copy to samples directory
                import shutil
                shutil.copy(result, output_path)
                print(f"    ✓ Saved to {output_path}")
            else:
                print(f"    ✗ Failed to generate {emotion} sample")
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print("\nDone! Sample files are in the 'samples' directory.")
    print("You can upload these to test the emotion detection.")

if __name__ == "__main__":
    main()
