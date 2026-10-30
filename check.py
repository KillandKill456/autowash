import ast
import os

path = "client/main.py"
print("Проверка файла:", os.path.abspath(path))
print("Существует:", os.path.exists(path))

try:
    with open(path, encoding="utf-8") as f:
        src = f.read()
    ast.parse(src)
    print("Синтаксис: OK")
except SyntaxError as e:
    print(f"Синтаксис: ОШИБКА на строке {e.lineno}: {e.msg}")
    print(f"Строка кода: {e.text}")
except Exception as e:
    print("Ошибка:", e)

try:
    import kivy
    print("Kivy:", kivy.__version__)
except Exception as e:
    print("Kivy не установлен:", e)

try:
    import requests
    r = requests.get("http://127.0.0.1:8000", timeout=3)
    print("Сервер API:", r.status_code, r.text[:80])
except Exception as e:
    print("Сервер API: недоступен →", e)