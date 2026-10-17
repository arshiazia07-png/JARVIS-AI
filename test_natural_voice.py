import asyncio
import edge_tts
import pygame

TEXT = "Hello Arshi. I am JARVIS, your personal AI assistant."
VOICE = "en-US-AriaNeural"
OUTPUT_FILE = "natural_voice_test.mp3"


async def generate_voice():
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)


asyncio.run(generate_voice())

pygame.mixer.init()
pygame.mixer.music.load(OUTPUT_FILE)
pygame.mixer.music.play()

print("Playing JARVIS's new voice...")

while pygame.mixer.music.get_busy():
    pygame.time.wait(100)

pygame.mixer.quit()
print("Voice test complete!")