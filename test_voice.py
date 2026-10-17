
import pyttsx3

engine = pyttsx3.init("sapi5")
engine.setProperty("rate", 160)

print("Speaking first...")
engine.say("Hello Arshi.")
engine.runAndWait()

print("Speaking second...")
engine.say("Your JARVIS assistant is working.")
engine.runAndWait()

print("Test complete.")
