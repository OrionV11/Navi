from elevenlabs.client import ElevenLabs
import os
import time
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


def wake_up():
    """Activate the assistant with a greeting"""
    print("Assistant waking up...")
    speak_text("Hello! I'm ready to help you.")
    print("Listening for commands...\n")


def speak_text(text: str, voice_name: str = "elariel"):
    """Convert text to speech and play it"""
    print(f"Speaking: {text}")

    try:
        # Get voice ID from dictionary
        voice_id = VOICE_IDS.get(voice_name, VOICE_IDS["elariel"])
        
        # Convert text to speech using newer model
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_turbo_v2_5"
        )
        
        # Save audio to file
        with open("temp.mp3", "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        # Play audio
        os.system("aplay temp.mp3 2>/dev/null")
        print("Done")
        
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
    # Wake up and test
    wake_up()
    
    # Test some speech
    speak_text("This is a test of the text-to-speech system.")
    time.sleep(1)
    
    speak_text("You can use different voices for variety.", voice_name="rachel")
    time.sleep(1)
    
    speak_text("Thanks for using this assistant!", voice_name="elariel")