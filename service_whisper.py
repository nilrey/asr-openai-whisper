# service_whisper.py
import os
os.environ["PATH"] = r"C:\ffmpeg\bin" + os.pathsep + os.environ["PATH"]

import shutil
import subprocess
import tempfile
import time
from contextlib import asynccontextmanager
from typing import Optional

print("Проверка ffmpeg")
print(f"Путь к ffmpeg: {shutil.which('ffmpeg')}")

try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
    print("ffmpeg работает")
    print(result.stdout[:200])
except Exception as e:
    print(f"Ошибка: {e}")

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import whisper
from pydub import AudioSegment

model = None
model_load_time = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, model_load_time
    
    print("Загрузка модели Whisper Tiny")
    start = time.time()
    
    model = whisper.load_model("tiny", download_root="./models/")
    
    model_load_time = time.time() - start
    print(f"Модель загружена за {model_load_time:.2f} секунд")
    
    yield
    
    print("Сервис завершает работу")


app = FastAPI(
    title="Whisper ASR Service",
    description="API для распознавания речи на основе Whisper Tiny",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "service": "Whisper ASR Service",
        "status": "running",
        "model": "Whisper Tiny",
        "load_time_seconds": model_load_time,
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "load_time_seconds": model_load_time
    }


@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(, description="Аудиофайл для распознавания"),
    language: Optional[str] = None,
    task: str = "transcribe"
):
    if model is None:
        raise HTTPException(status_code=503, detail="Модель еще не загружена")
    
    # Сохраняем загруженный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Конвертируем в WAV, если это не WAV
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext != '.wav':
            print(f"Конвертация {file_ext} в WAV")
            audio = AudioSegment.from_file(tmp_path)
            wav_path = tmp_path + ".wav"
            audio.export(wav_path, format="wav")
            audio_path = wav_path
        else:
            audio_path = tmp_path
        
        start_time = time.time()
        
        options = {
            "task": task,
            "fp16": False,
            "verbose": False,
            "condition_on_previous_text": False
        }
        
        if language:
            options["language"] = language
        
        result = model.transcribe(audio_path, **options)
        
        processing_time = time.time() - start_time
        
        return JSONResponse(content={
            "success": True,
            "text": result["text"].strip(),
            "language": result.get("language", language or "auto"),
            "processing_time_seconds": round(processing_time, 3),
            "file_name": file.filename,
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "file_name": file.filename
            }
        )
    finally:
        # Удаляем временные файлы
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(tmp_path + ".wav"):
            os.remove(tmp_path + ".wav")


if __name__ == "__main__":
    uvicorn.run(
        "service_whisper:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )