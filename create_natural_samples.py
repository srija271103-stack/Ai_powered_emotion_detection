#!/usr/bin/env python3
"""
Create natural-sounding emotional audio with human-like characteristics.

Emotional modifications:
- Happy: Subtle, warm, slightly higher pitch
- Angry: LOUD, sharp, fast, aggressive
- Fear: Stuttering, trembling, quiet, hesitant
- Surprised: Exclamatory, varied pitch, gasps
- Anxious: Fast, breathless, nervous, shaky
- Sad: Slow, low, quiet, heavy
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import librosa
import soundfile as sf
from scipy import signal

def add_stuttering(audio, sr, intensity=0.3):
    """Add stuttering effect for fear/anxiety."""
    output = []
    chunk_size = int(sr * 0.15)  # 150ms chunks
    
    i = 0
    while i < len(audio):
        chunk = audio[i:i+chunk_size]
        output.append(chunk)
        
        # Randomly repeat some chunks (stuttering)
        if np.random.random() < intensity:
            # Repeat with slight variation
            repeat_chunk = chunk * 0.95
            output.append(repeat_chunk[:len(repeat_chunk)//2])  # Partial repeat
        
        i += chunk_size
    
    return np.concatenate(output)

def add_tremolo(audio, sr, rate=6, depth=0.15):
    """Add trembling/shaky effect."""
    t = np.arange(len(audio)) / sr
    tremolo = 1 + depth * np.sin(2 * np.pi * rate * t)
    return audio * tremolo

def add_breath_pauses(audio, sr, frequency=0.1):
    """Add breathing pauses for anxious speech."""
    output = []
    chunk_size = int(sr * 0.5)  # 500ms chunks
    breath_sound = np.random.randn(int(sr * 0.2)) * 0.05  # Soft white noise for breath
    
    i = 0
    while i < len(audio):
        chunk = audio[i:i+chunk_size]
        output.append(chunk)
        
        if np.random.random() < frequency:
            output.append(breath_sound)
        
        i += chunk_size
    
    return np.concatenate(output)

def make_sharp(audio, sr):
    """Make audio sharp and aggressive (for anger)."""
    # Add harmonic distortion
    audio = np.tanh(audio * 2) * 0.8
    
    # Boost high frequencies
    b, a = signal.butter(2, 3000 / (sr/2), btype='high')
    high_freq = signal.filtfilt(b, a, audio)
    audio = audio + high_freq * 0.3
    
    return audio

def add_gasps(audio, sr):
    """Add gasp-like sounds for surprise."""
    output = list(audio)
    gasp = np.exp(-np.linspace(0, 5, int(sr * 0.1))) * 0.3  # Sharp attack sound
    
    # Add a gasp at the beginning
    output = list(gasp) + [0] * int(sr * 0.1) + output
    
    return np.array(output)

def main():
    samples_dir = Path(__file__).parent / "samples"
    samples_dir.mkdir(exist_ok=True)
    
    # Clean existing files
    for f in samples_dir.glob("*.wav"):
        f.unlink()
    
    from modules.text_to_speech import emotion_tts
    
    print("Creating natural emotional audio samples...")
    print("="*60)
    
    # Emotional content with natural expressions
    emotions = {
        "angry": {
            "text": (
                "I am absolutely FURIOUS about this! How DARE they do this to me! "
                "This is COMPLETELY unacceptable and I will NOT tolerate it! "
                "Someone is going to pay for this outrage! I demand answers RIGHT NOW! "
                "I've had ENOUGH of being treated like this! This is the LAST time!"
            ),
            "process": lambda y, sr: process_angry(y, sr)
        },
        "sad": {
            "text": (
                "I feel... so lost and alone... Everything seems so... pointless now... "
                "I don't know what to do anymore... The pain just won't go away... "
                "I miss how things used to be... I feel so empty inside... "
                "Sometimes I wonder if anyone even cares..."
            ),
            "process": lambda y, sr: process_sad(y, sr)
        },
        "fear": {
            "text": (
                "I... I don't know what's happening... I'm so... so scared... "
                "What was that sound? Please... please don't hurt me... "
                "I can't... I can't breathe... My heart is racing... "
                "Someone help me... I'm terrified... I don't want to be alone..."
            ),
            "process": lambda y, sr: process_fear(y, sr)
        },
        "happy": {
            "text": (
                "Oh this is wonderful! I'm so grateful for this beautiful day! "
                "Everything just feels so right, you know? I love spending time with you. "
                "Life is truly beautiful when you appreciate the little things. "
                "I feel so blessed and content right now. Thank you for being here."
            ),
            "process": lambda y, sr: process_happy(y, sr)
        },
        "surprised": {
            "text": (
                "Oh my goodness! I can't believe it! Is this really happening? "
                "Wow! I never expected this! This is incredible! "
                "Wait, what? Are you serious right now? No way! "
                "I'm completely shocked! This is amazing news!"
            ),
            "process": lambda y, sr: process_surprised(y, sr)
        },
        "anxious": {
            "text": (
                "I... I don't know if I can do this... What if something goes wrong? "
                "My mind keeps racing with all these terrible thoughts... "
                "I feel like I can't catch my breath... Everything is too much... "
                "What if I fail? What if everyone judges me? I can't stop worrying..."
            ),
            "process": lambda y, sr: process_anxious(y, sr)
        }
    }
    
    for emotion, config in emotions.items():
        print(f"\n  Creating {emotion}_natural.wav...")
        
        # Generate base audio
        temp_path = samples_dir / f"temp_{emotion}.wav"
        result = emotion_tts.synthesize(config["text"], emotion.replace("surprised", "neutral"), str(temp_path))
        
        if result:
            # Load audio
            y, sr = librosa.load(temp_path, sr=22050)
            
            # Apply emotional processing
            y = config["process"](y, sr)
            
            # Ensure 30 seconds
            target_length = 30 * sr
            if len(y) < target_length:
                y = np.pad(y, (0, target_length - len(y)), mode='constant')
            else:
                y = y[:target_length]
            
            # Normalize
            y = y / (np.max(np.abs(y)) + 1e-7) * 0.95
            
            # Save
            output_path = samples_dir / f"{emotion}_natural.wav"
            sf.write(str(output_path), y, sr)
            
            print(f"    ✓ Saved: {output_path.name}")
            
            # Clean temp
            temp_path.unlink()
        else:
            print(f"    ✗ Failed")
    
    print("\n" + "="*60)
    print("Done! Natural emotional samples created:\n")
    print("  😤 angry_natural.wav   - LOUD, sharp, aggressive")
    print("  😢 sad_natural.wav     - Slow, low, heavy")
    print("  😨 fear_natural.wav    - Stuttering, trembling")
    print("  😊 happy_natural.wav   - Subtle, warm, content")
    print("  😲 surprised_natural.wav - Exclamatory, varied pitch")
    print("  😰 anxious_natural.wav - Fast, breathless, shaky")
    print("\nUpload to http://localhost:8501 to test!")
    print("="*60)


def process_angry(y, sr):
    """ANGRY: Loud, sharp, fast, aggressive"""
    # Speed up
    y = librosa.effects.time_stretch(y, rate=1.2)
    # Raise pitch significantly
    y = librosa.effects.pitch_shift(y, sr=sr, n_steps=4)
    # Make it LOUD
    y = y * 1.8
    # Add sharpness
    y = make_sharp(y, sr)
    return y


def process_sad(y, sr):
    """SAD: Slow, low, quiet, heavy"""
    # Slow down significantly
    y = librosa.effects.time_stretch(y, rate=0.75)
    # Lower pitch
    y = librosa.effects.pitch_shift(y, sr=sr, n_steps=-3)
    # Make quieter
    y = y * 0.6
    # Add slight reverb-like effect (delay)
    delay = int(sr * 0.05)
    y_delayed = np.pad(y, (delay, 0), mode='constant')[:-delay]
    y = y * 0.8 + y_delayed * 0.2
    return y


def process_fear(y, sr):
    """FEAR: Stuttering, trembling, quiet, hesitant"""
    # Add stuttering
    y = add_stuttering(y, sr, intensity=0.25)
    # Add trembling
    y = add_tremolo(y, sr, rate=8, depth=0.2)
    # Raise pitch (fear = higher voice)
    y = librosa.effects.pitch_shift(y, sr=sr, n_steps=2)
    # Make quieter
    y = y * 0.7
    return y


def process_happy(y, sr):
    """HAPPY: Subtle, warm, slightly upbeat"""
    # Slight speed increase
    y = librosa.effects.time_stretch(y, rate=1.05)
    # Slight pitch increase
    y = librosa.effects.pitch_shift(y, sr=sr, n_steps=1)
    # Normal volume, warm tone
    # Low-pass for warmth
    b, a = signal.butter(2, 6000 / (sr/2), btype='low')
    y = signal.filtfilt(b, a, y)
    return y


def process_surprised(y, sr):
    """SURPRISED: Exclamatory, varied pitch, gasps"""
    # Add initial gasp
    y = add_gasps(y, sr)
    # Higher pitch
    y = librosa.effects.pitch_shift(y, sr=sr, n_steps=3)
    # Speed up
    y = librosa.effects.time_stretch(y, rate=1.15)
    # Add pitch variation
    chunk_size = int(sr * 0.3)
    output = []
    for i in range(0, len(y), chunk_size):
        chunk = y[i:i+chunk_size]
        # Random pitch variation for each chunk
        variation = np.random.uniform(-1, 2)
        if len(chunk) > sr * 0.1:  # Only if chunk is long enough
            chunk = librosa.effects.pitch_shift(chunk, sr=sr, n_steps=variation)
        output.append(chunk)
    y = np.concatenate(output)
    return y


def process_anxious(y, sr):
    """ANXIOUS: Fast, breathless, nervous, shaky"""
    # Speed up (rushed speech)
    y = librosa.effects.time_stretch(y, rate=1.25)
    # Add breath pauses
    y = add_breath_pauses(y, sr, frequency=0.15)
    # Add slight trembling
    y = add_tremolo(y, sr, rate=5, depth=0.1)
    # Slightly higher pitch
    y = librosa.effects.pitch_shift(y, sr=sr, n_steps=1)
    return y


if __name__ == "__main__":
    main()
