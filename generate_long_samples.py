#!/usr/bin/env python3
"""Generate longer sample audio files (25-30 seconds) for comprehensive testing."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from modules.text_to_speech import emotion_tts

def main():
    samples_dir = Path(__file__).parent / "samples"
    samples_dir.mkdir(exist_ok=True)
    
    # Longer sample texts (25-30 seconds when spoken) with different emotions
    samples = [
        ("sad_long", """
            I've been feeling really down lately. It's like there's this heavy weight on my chest 
            that I can't shake off. I used to enjoy going out with friends, but now I just want 
            to stay in bed all day. Everything feels so meaningless. I don't know what's wrong 
            with me. I miss feeling happy. I miss feeling like myself. Sometimes I wonder if 
            things will ever get better. The days just blend together and I feel so alone.
        """),
        
        ("angry_long", """
            I am so frustrated right now! Nothing is working out the way it should. I've been 
            trying so hard at work, but nobody appreciates anything I do. My boss is always 
            criticizing me for the smallest things. And then I come home and there's more stress 
            waiting for me. I feel like screaming! Why does everything have to be so difficult? 
            I can't take this anymore. I'm tired of being treated like I don't matter. This is 
            absolutely ridiculous and I've had enough of it!
        """),
        
        ("anxious_long", """
            I can't stop worrying about everything. What if I fail my exam? What if I lose my job? 
            What if something bad happens to my family? My mind just keeps racing with all these 
            terrible scenarios. I couldn't sleep last night because I kept thinking about all the 
            things that could go wrong. My heart is pounding even now. I feel so overwhelmed and 
            stressed. I don't know how to calm down. Every little thing makes me nervous. I just 
            want to feel peaceful again but I don't know how to stop these anxious thoughts.
        """),
        
        ("happy_long", """
            Today was such an amazing day! I woke up feeling grateful and everything just fell 
            into place. I got some really good news at work and my family surprised me with a 
            lovely dinner. I feel so blessed to have such wonderful people in my life. The sun 
            was shining, the weather was perfect, and I felt so alive and happy. I want to spread 
            this positivity to everyone around me. Life is beautiful when you take a moment to 
            appreciate all the little things. I'm feeling hopeful about the future!
        """),
        
        ("depressed_long", """
            I don't know how to explain this feeling. It's like I'm numb to everything. I used 
            to have dreams and goals, but now I can't even remember what they were. Getting out 
            of bed feels impossible some days. I've been pretending to be okay around others, 
            but inside I'm struggling so much. I feel disconnected from everyone, even myself. 
            Food doesn't taste good anymore. Music doesn't make me feel anything. I'm just going 
            through the motions. I really need help but I don't know where to start.
        """),
    ]
    
    print("Generating longer sample audio files (25-30 seconds each)...")
    print("This may take a minute...\n")
    
    for emotion, text in samples:
        output_path = samples_dir / f"{emotion}.wav"
        print(f"  Creating {emotion}.wav...")
        
        # Clean up the text
        clean_text = " ".join(text.split())
        
        try:
            # Extract base emotion for TTS
            base_emotion = emotion.split("_")[0]
            if base_emotion == "depressed":
                base_emotion = "sad"
            
            result = emotion_tts.synthesize(clean_text, base_emotion)
            if result:
                import shutil
                shutil.copy(result, output_path)
                
                # Get duration
                import librosa
                duration = librosa.get_duration(path=str(output_path))
                print(f"    ✓ Saved: {output_path.name} ({duration:.1f} seconds)")
            else:
                print(f"    ✗ Failed to generate {emotion}")
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Done! Extended sample files are in the 'samples' directory.")
    print("\nThese files will test:")
    print("  ✓ Speech-to-Text (STT) transcription")
    print("  ✓ Emotion detection from voice")
    print("  ✓ Empathetic response generation")
    print("  ✓ Wellness suggestions")
    print("\nUpload any of these to http://localhost:8501 to test!")
    print("="*60)

if __name__ == "__main__":
    main()
