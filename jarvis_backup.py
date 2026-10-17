
import datetime
import json
import urllib.request
import urllib.error
import speech_recognition as sr
import pyttsx3
import subprocess
import webbrowser

# Ollama local AI settings
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:1b"


# Initialize voice systems
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

# Select a likely female Windows voice if available
voices = engine.getProperty("voices")
for voice in voices:
    details = f"{voice.name} {voice.id}".lower()
    if any(word in details for word in ["zira", "female", "woman"]):
        engine.setProperty("voice", voice.id)
        break


def speak(text):
    """Print and speak a response."""
    print(f"\nJARVIS: {text}")
    engine.say(text)
    engine.runAndWait()


def listen():
    """Capture a spoken command."""
    try:
        with sr.Microphone() as source:
            print("\nListening...")
            recognizer.adjust_for_ambient_noise(
                source, duration=0.4
            )
            audio = recognizer.listen(
                source, timeout=6, phrase_time_limit=12
            )

        command = recognizer.recognize_google(audio)
        print(f"YOU: {command}")
        return command.lower().strip()

    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        print("Speech wasn't clear.")
        return ""
    except sr.RequestError:
        speak("Speech recognition is unavailable.")
        return ""
    except OSError as error:
        print(f"Microphone error: {error}")
        speak("I cannot access the microphone.")
        return ""


def ask_ai(question):
    """Send a question to the local Ollama AI."""
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are JARVIS, a helpful voice assistant. "
                    "Answer directly in 2-4 short sentences. "
                    "Use simple, natural language suitable for speaking aloud." 
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "stream": False,
"keep_alive": "10m",
"options": {
    "num_predict": 100
}
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["message"]["content"].strip()

    except urllib.error.URLError as error:
        print(f"Ollama connection error: {error}")
        return (
            "I cannot connect to my local AI brain. "
            "Please make sure Ollama is running."
        )
    except (KeyError, ValueError, TimeoutError) as error:
        print(f"AI response error: {error}")
        return "I had trouble processing that request."


def process_command(command):
    """Handle built-in commands or ask the AI."""

    if not command:
        return True

    if command in [
        "exit", "quit", "stop jarvis", "shut down"
    ]:
        speak("Shutting down. See you soon!")
        return False

    if "what time" in command or command == "time":
        current_time = datetime.datetime.now().strftime(
            "%I:%M %p"
        )
        speak(f"It is {current_time}.")
        return True

    if command in ["hello", "hello jarvis", "hi jarvis"]:
        speak("Hello! My Tony Stark. What can I help you with?")
        return True
        # Open Windows applications
    if command in ["open notepad", "start notepad"]:
        subprocess.Popen(["notepad.exe"])
        speak("Opening Notepad.")
        return True

    if command in ["open calculator", "start calculator"]:
        subprocess.Popen(["calc.exe"])
        speak("Opening Calculator.")
        return True

    # Open websites
    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")
        return True

    if "open google" in command:
        webbrowser.open("https://www.google.com")
        speak("Opening Google.")
        return True

    answer = ask_ai(command)
    speak(answer)
    return True


def main():
    speak("JARVIS is starting. Connecting to my local AI brain.")

    # Test the AI connection before listening for commands
    answer = ask_ai("Say hello and introduce yourself briefly.")
    speak(answer)

    while True:
        command = listen()
        if not process_command(command):
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nJARVIS stopped safely.")
    finally:
        engine.stop()
