from elevenlabs.client import ElevenLabs
import os
import time
import subprocess
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

VOICE_IDS = {
    "rachel": "EXAVITQu4vr4xnSDxMaL",
    "bella": "EXAVITQu4vr4xnSDxMaL",
    "antoni": "zcAOhNBS3c14rBihAFp1",
    "josh": "TxGEqnHWrfWFTfGW9XjX",
    "elariel": "ksryVoNAGZT8GxWCTiVm"
}


def find_audio_player():
    """Find available audio player on the system"""
    players = ["mpv", "ffplay", "paplay", "aplay"]
    
    for player in players:
        result = subprocess.run(["which", player], capture_output=True)
        if result.returncode == 0:
            return player
    
    return None


def play_audio_file(filepath: str):
    """Play audio file using available player"""
    player = find_audio_player()
    
    if not player:
        print("No audio player found. Install: pacman -S mpv")
        return False
    
    try:
        if player == "mpv":
            subprocess.run(
                ["mpv", "--no-video", "--really-quiet", filepath],
                check=True
            )
        elif player == "ffplay":
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filepath],
                check=True
            )
        elif player == "paplay":
            subprocess.run(["paplay", filepath], check=True)
        elif player == "aplay":
            subprocess.run(["aplay", filepath], check=True)
        
        return True
    except subprocess.CalledProcessError:
        return False


def wake_up():
    """Activate the assistant with a greeting"""
    print("Assistant waking up...")
    speak_text("Hello! I'm ready to help you.")
    print("Listening for commands...\n")


def speak_text(text: str, voice_name: str = "elariel"):
    """Convert text to speech and play it"""

    try:
        voice_id = VOICE_IDS.get(voice_name, VOICE_IDS["elariel"])
        
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_turbo_v2_5"
        )
        
        with open("temp.mp3", "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        if play_audio_file("temp.mp3"):
            print("-" * 40)
        else:
            print("Warning: Audio created but playback failed")
        
    except Exception as e:
        print(f"Error: {e}")


def set_voice(voice_name: str):
    """Set which voice to use"""
    if voice_name in VOICE_IDS:
        print(f"Voice set to: {voice_name}")
        return voice_name
    else:
        print(f"Available voices: {', '.join(VOICE_IDS.keys())}")
        return "elariel"


# Example usage
if __name__ == "__main__":
    player = find_audio_player()
    if player:
        print(f"Using: {player}\n")
    else:
        print("No audio player found!\n")
    
    # Wake up and test
    wake_up()
    
    # Test some speech
    speak_text("This is a test of the text-to-speech system.")
    time.sleep(1)
    
    speak_text("You can use different voices for variety.", voice_name="rachel")
    time.sleep(1)
    
    speak_text("Thanks for using this assistant!", voice_name="elariel")