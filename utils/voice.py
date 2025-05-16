import os
import shutil
import uuid
import simpleaudio as sa
from gradio_client import Client, handle_file

current_dir = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(current_dir, "..", "temp")
VOICE_PATH = os.path.join(current_dir, "..", "data", "voice")

def move_file(source_path: str, destination_dir: str):
    try:
        task_id = str(uuid.uuid4())
        destination_path = os.path.join(destination_dir, task_id + os.path.splitext(source_path)[1])
        shutil.move(source_path, destination_path)
        print(f"OK: {source_path} -> {destination_path}")
        if os.path.exists(source_path):
            os.remove(source_path)
            print(f"Remove {source_path}")
        return destination_path
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_voice(prompt: str, audio_path: str, temp_dir: str = TEMP_DIR):
    try:
        audio_path = os.path.join(VOICE_PATH, "women_live.wav") if not audio_path else audio_path
        txt_path = os.path.splitext(audio_path)[0] + ".txt"
        if not os.path.exists(txt_path):
            raise FileNotFoundError(f"参考文本 {txt_path} 不存在")
        with open(txt_path, "r", encoding="utf-8") as f:
            reference_text = f.read()

        client = Client("http://127.0.0.1:7861/")
        result = client.predict(
                text=prompt,
                reference_id="",
                reference_audio=handle_file(audio_path),
                reference_text=reference_text,
                max_new_tokens=0,
                chunk_length=200,
                top_p=0.7,
                repetition_penalty=1.2,
                temperature=0.7,
                seed=0,
                use_memory_cache="on",
                api_name="/partial"
        )
        file = move_file(result[0], temp_dir)
        wave_obj = sa.WaveObject.from_wave_file(file)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        return file
    except Exception as e:
        print(f"Error: {e}")
    return None