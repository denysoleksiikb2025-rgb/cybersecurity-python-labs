import os
import random
import sys

# Додаємо шлях до папки shared, щоб імпортувати дані
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared.student import STUDENT_NAME, VARIANT_NUMBER

# Вхідні дані для 2 варіанту
passwords = ["Hello123!", "simple", "CompL3x@Pass", "password", "Strong#2023", 
             "weak", "MySecur3!", "12345", "Advanced@1", "basic"]
criteria = {"min_length": 10, "require_digits": True, "require_upper": True, "require_special": True}
forbidden_passwords = {"password", "simple", "weak", "basic", "12345", "hello"}

def analyze_passwords():
    print("=" * 40)
    print(f"Студент: {STUDENT_NAME}, Варіант: {VARIANT_NUMBER}")
    print("=" * 40)

    # 3. Генеруємо 3 випадкові індекси та додаємо дублікати паролів
    duplicates = [passwords[random.randint(0, len(passwords)-1)] for _ in range(3)]
    passwords.extend(duplicates)

    min_len = criteria["min_length"]

    print(f"{'Пароль':<18} | {'Статус':<15}")
    print("-" * 40)

    # 4. Оцінюємо надійність кожного пароля
    for pwd in passwords:
        # Перевірка на входження до заборонених або занадто коротких
        is_forbidden = pwd.lower() in forbidden_passwords or pwd in forbidden_passwords or len(pwd) < min_len
        
        # Перевірка наявності різних типів символів
        has_digit = any(c.isdigit() for c in pwd)
        has_upper = any(c.isupper() for c in pwd)
        has_lower = any(c.islower() for c in pwd)
        has_special = any(not c.isalnum() for c in pwd)

        criteria_met = sum([has_digit, has_upper, has_lower, has_special])
        is_unique = passwords.count(pwd) == 1

        # Алгоритм визначення статусу
        if is_forbidden:
            status = "Заборонений"
        elif criteria_met == 4 and len(pwd) >= min_len + 4 and is_unique:
            status = "Дуже сильний"
        elif criteria_met == 4 and len(pwd) >= min_len:
            status = "Сильний"
        elif len(pwd) >= min_len and criteria_met > 1:
            status = "Середній"
        else:
            status = "Слабкий"

        print(f"{pwd:<18} | {status:<15}")

if __name__ == "__main__":
    analyze_passwords()