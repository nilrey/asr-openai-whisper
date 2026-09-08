# Настройка сервера и окружения проекта

### Disclaimer

Положительный результат на серверах timeweb.cloud с расположением сервера - Нидерланды

Установка проверялась на серверах с Ubuntu (версий 22 и 24), Windows 11

Проект разрабатывался на python3.12

Описание установки на сервер дано для **Ubuntu (версий 22 и 24)**

## Установка (при необходимости) python3-pip python3-venv
```bash
apt update && apt upgrade -y

apt install python3-pip python3-venv -y
```


## Настройки сети

#### Проверьте статус UFW

Сервис предлагается ставить на порту 8000 (можно указать любой другой, но прописать изменения в конфиге)

```bash
sudo ufw status
```

#### Если UFW активен, разрешите порт 8000

```bash
sudo ufw allow 8000/tcp
```
#### Для iptables (не понадобилось)
```bash
sudo iptables -L -n | grep 8000
```
#### Разрешить порт в iptables (не понадобилось)
```bash
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```
## Установка nginx
```bash
apt update && apt upgrade -y

apt install nginx -y
```

### Создать пользователя для веб-проекта 

#### Создаем пользователя 
```bash
adduser fastapi_user
```

Укажите "Name", любое имя для галочки - Albert Einstain

Остальные вопросы - по дефолту, жмем Enter

При получении запроса на пароль - придумываем пароль

#### Добавляем в группу админов

```bash
usermod -aG sudo fastapi_user
```

#### Проверяем группы пользователя, наличие в группе sudo
```bash
groups fastapi_user

Ответ примерно такой:

fastapi_user : fastapi_user sudo users
```

#### Переключаемся на созданного пользователя
```bash
su - fastapi_user
```

## Установка FFmpeg
```bash
sudo apt update

sudo apt install ffmpeg -y

ffmpeg -version
```

## Установка окружения проекта

```bash
# Перейти в корень проекта

cd /home/fastapi_user/tts-openai-whisper

# Создать окружение проекта:

python3 -m venv venv

# Активировать окружение:

source ./venv/bin/activate

# Установить зависимости:

pip install -r requirements.txt

# Установка CPU-версии PyTorch (легкая, без CUDA):

pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Установка Whisper

pip install --no-cache-dir openai-whisper

```
### Запустить сервис

Запуск сервиса из корневой директории проекта

```bash
uvicorn service_whisper:app --host 0.0.0.0 --port 8000

или

python service_whisper.py
```