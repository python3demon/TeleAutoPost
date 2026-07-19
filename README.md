<div align="center">
<img src="logo.png" alt="Logo" width="200">

[![Version 0.1.0](https://img.shields.io/badge/Version-0.1.0-red.svg)](https://github.com/python3demon/TeleAutoPost)
[![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram 3.30.0](https://img.shields.io/badge/aiogram-3.30.0-red.svg)](https://github.com/aiogram/aiogram/)

<h1>TeleAutoPost — Автоматическая отправка постов</h1>
</div>

## План разработки (To-Do)
- [x] Написать базовую конструкцию (/start /help)  (`v0.1.0-alpha`)
- [ ] Добавить возможность отправлять сообщения с выделениями (/send_post)  (`v0.2.0-alpha`)

## Установка
```bash
# Клонирование репозитория и переход в директорию
git clone https://github.com/python3demon/TeleAutoPost.git && cd TeleAutoPost

# Настройка конфигурации (укажите ваш токен бота)
cp .env.example .env
micro .env

# Ставим виртуальное окружение и активируем
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Запуск приложения
python main.py
```

## Стек Технологий
* **Language:** Python 3.14
* **Library:** aiogram 3.30
