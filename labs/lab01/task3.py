import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from functools import wraps

# Додаємо шлях до папки shared
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import STUDENT_NAME, VARIANT_NUMBER

# Налаштування для алгоритму та довжини (мінімум з Завдання 1)
ALGORITHM = "sha3_224"
MIN_PASSWORD_LENGTH = 10  # Припустимо, що мінімум 10 символів

# Шляхи до файлів
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
USERS_CSV_PATH = os.path.join(DATA_DIR, "users.csv")
LOG_JSON_PATH = os.path.join(DATA_DIR, "log.json")


# --- КРОК 1: Власні винятки (Exceptions) ---
class ValidationError(Exception):
    """Власний виняток для помилок валідації пароля (короткий пароль)."""


# --- КРОК 2: Динамічна персональна сіль ---
# Створюємо рядок із 5 символів, доповнений нулями (наприклад, Варіант 17 -> "00017")
PERSONAL_SALT = str(VARIANT_NUMBER).zfill(5)


# --- КРОК 1: Функція хешування з винятками ---
def generate_hash(password: str, salt: str = "00000") -> str:
    """Генерує хеш пароля та обробляє помилки вхідних даних."""
    if password is None or password == "" or salt is None or salt == "":
        raise ValueError("Пароль або сіль не можуть бути порожніми (None або '').")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f"Пароль надто короткий. Мінімум {MIN_PASSWORD_LENGTH} символів."
        )

    salted_password = password + salt
    hasher = hashlib.sha3_224()
    hasher.update(salted_password.encode("utf-8"))
    return hasher.hexdigest()


# --- КРОК 6: Декоратор логування ---
def log_event(func):
    """Записує кожну спробу входу у файл log.json."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        username = args[0] if len(args) > 0 else kwargs.get("username", "unknown")
        result_status = "failure"

        try:
            # Виконуємо спробу входу
            result = func(*args, **kwargs)
            result_status = "success" if result else "failure"
            return result
        except Exception:
            result_status = (
                "failure"  # Якщо виникла помилка (напр. ValueError), вхід не вдався
            )
            raise
        finally:
            # Записуємо лог незалежно від того, успішний вхід чи вилетіла помилка
            log_entry = {
                "event": "login",
                "user": username,
                "result": result_status,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "args": list(args),
                "kwargs": kwargs,
            }

            os.makedirs(DATA_DIR, exist_ok=True)
            logs = []
            if os.path.exists(LOG_JSON_PATH):
                with open(LOG_JSON_PATH, "r", encoding="utf-8") as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        pass

            logs.append(log_entry)
            with open(LOG_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=4)

    return wrapper


# --- КРОК 3: Реєстрація користувачів (База даних) ---
users_to_register = (
    ("admin_root", "SuperSecr3t!22"),
    ("alex_student", "MyPass123456"),
    ("guest_01", "GuestPass!11"),
    ("moderator", "Mod3rator@123"),
    ("test_user1", "TestingPass1"),
    ("test_user2", "TestingPass2"),
    ("hacker_guy", "HackTheBox99"),
    ("cyber_ninja", "Ninj@Cyber00"),
    ("security_pro", "S3cure_Pr0!!"),
    ("developer_x", "DevX_Passw0rd"),
)


def create_user(username, password):
    """Створює кортеж (логін, хеш_пароля)."""
    hash_val = generate_hash(password, PERSONAL_SALT)
    return (username, hash_val)


def create_users(users_list):
    """Створює папку data та записує всіх користувачів у users.csv."""
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(USERS_CSV_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["username", "password_hash"])  # Опціональний заголовок

        for u, p in users_list:
            record = create_user(u, p)
            writer.writerow(record)


# --- КРОК 5: Автентифікація ---
@log_event
def login(username: str, password: str, users_db: list) -> bool:
    """Перевіряє, чи співпадає хеш пароля з тим, що в базі."""
    if not username or not password:
        raise ValueError("Помилка входу: Логін або пароль порожні.")

    attempt_hash = generate_hash(password, PERSONAL_SALT)

    # Шукаємо користувача у зчитаній базі даних (списку кортежів)
    for db_user, db_hash in users_db:
        if db_user == username and db_hash == attempt_hash:
            return True
    return False


# --- КРОК 8: Головна функція (із КРОКАМИ 4 та 7) ---
def run_task3():
    print("=" * 80)
    print(f"Студент: {STUDENT_NAME}, Варіант: {VARIANT_NUMBER}")
    print(
        f"Завдання 3: Хешування, CSV-база та JSON-логування (Сіль: '{PERSONAL_SALT}')"
    )
    print("=" * 80)

    # КРОК 7: Обгортаємо ВСЕ в блоки try...except
    try:
        # 3. Реєструємо користувачів (записуємо в CSV)
        print("[+] Створення бази даних користувачів (users.csv)...")
        create_users(users_to_register)

        # 4. Читання бази даних з CSV у список users_db
        users_db = []
        with open(USERS_CSV_PATH, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)  # Пропускаємо заголовок (перший рядок)
            for row in reader:
                if len(row) == 2:
                    users_db.append((row[0], row[1]))

        # Вивід структурованої таблиці на екран
        print("\n[ ВМІСТ БАЗИ ДАНИХ (Перші 5 записів) ]")
        print(f"{'Логін':<15} | {'Хеш (перші 30 символів)':<30}")
        print("-" * 50)
        for u, h in users_db[:5]:  # Виводимо лише 5, щоб не засмічувати консоль
            print(f"{u:<15} | {h[:30]}...")

        # Симуляція спроб входу (включаючи помилкові, щоб перевірити винятки)
        print("\n[ СИМУЛЯЦІЯ ВХОДУ (Автентифікація) ]")

        # 1. Успішний вхід
        status = login("alex_student", "MyPass123456", users_db)
        print(f"Вхід alex_student: {'Успішно' if status else 'Відмовлено'}")

        # 2. Неправильний пароль
        status = login("admin_root", "wrong_pass22", users_db)
        print(
            f"Вхід admin_root (невірний пароль): {'Успішно' if status else 'Відмовлено'}"
        )

        # 3. Перевірка ValueError (порожній пароль)
        print("\n[ ПЕРЕВІРКА ВИНЯТКІВ ]")
        login("test_user1", "", users_db)  # Це викличе ValueError!

    # Обробка винятків за вимогою Кроку 7
    except ValueError as ve:
        print(f"[!] ValueError перехоплено: {ve}")
    except ValidationError as vale:
        print(f"[!] ValidationError перехоплено: {vale}")
    except FileNotFoundError:
        print("[!] Помилка: Файл бази даних не знайдено.")
    except PermissionError:
        print("[!] Помилка: Немає прав доступу до файлу або папки data.")
    except OSError as e:
        print(f"[!] Помилка вводу/виводу: {e}")

    print("\n[+] Роботу Завдання 3 завершено. Перевірте папку data/.")


if __name__ == "__main__":
    run_task3()
