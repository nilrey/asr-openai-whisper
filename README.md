# ASR Service

Сервис распознавания речи на основе Openai-Whisper

## Запуск окружения

```bash
.\venv\Scripts\activate

```

## Запуск

Выполнить команду:

```bash

python service_whisper.py

или 

uvicorn service_whisper:app --host 0.0.0.0 --port 8000
```

Перейти в браузере:

```code
http://<ip-server>:8000/docs
```

Перейти в endpoint POST /transcribe  

Укажите файл для распознавания в поле file
