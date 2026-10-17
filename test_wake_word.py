
import pyaudio
import numpy as np
from openwakeword.model import Model

print("Loading the Hey JARVIS model...")

model = Model(
    wakeword_models=["hey_jarvis"],
    inference_framework="onnx",
    vad_threshold=0.0
)

RATE = 16000
CHUNK = 1280

audio = pyaudio.PyAudio()
stream = audio.open(
    rate=RATE,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=CHUNK
)

print("Listening! Say: Hey JARVIS")
print("Press Ctrl+C to stop.")

try:
    while True:
        data = stream.read(
            CHUNK,
            exception_on_overflow=False
        )
        frame = np.frombuffer(data, dtype=np.int16)
        predictions = model.predict(frame)
        score = max(predictions.values(), default=0)

        if score > 0.5:
            print(f"\nHEY JARVIS DETECTED! Score: {score:.2f}")
            break

except KeyboardInterrupt:
    print("\nWake-word test stopped.")

finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
