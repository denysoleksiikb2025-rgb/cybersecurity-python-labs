import os
import sys

# Додаємо шлях до папки shared
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from shared.student import STUDENT_NAME, VARIANT_NUMBER

# =====================================================================
# КРОК 1: Вхідні дані варіанту
# =====================================================================
users = {
    "sysadmin02": {"role": "system_admin", "clearance": 4, "department": "Infrastructure", "active": True},
    "analyst234": {"role": "security_analyst", "clearance": 3, "department": "SOC", "active": True},
    "developer567": {"role": "developer", "clearance": 2, "department": "Development", "active": True},
    "intern890": {"role": "intern", "clearance": 1, "department": "HR", "active": True},
    "external123": {"role": "external", "clearance": 1, "department": "Vendor", "active": False}
}

resources = [
    ("prod_database", 4), ("dev_environment", 2), ("documentation", 1),
    ("source_code", 3), ("server_configs", 4), ("test_data", 2),
    ("compliance_docs", 3), ("system_logs", 4), ("project_files", 2),
    ("public_wiki", 1)
]

security_levels = ("Open", "Internal", "Restricted", "Top Secret")

blocked_users = {"external123", "old_account", "test_user"}


# =====================================================================
# КРОК 3: Алгоритм перевірки доступу
# =====================================================================
def check_access(username: str, resource_level: int) -> str:
    """Перевіряє доступ користувача до ресурсу за суворим алгоритмом."""
    
    # 1. Якщо користувача немає в системі (словнику users)
    if username not in users:
        return "DENY (User not found)"
    
    # 2. Якщо користувач є у списку заблокованих blocked_users
    if username in blocked_users:
        return "DENY (User is blocked)"
    
    user_info = users[username]
    
    # 3. Якщо обліковий запис неактивний (active == False)
    if not user_info.get("active"):
        return "DENY (Account inactive)"
    
    # 4 & 5. Порівняння рівня допуску користувача з рівнем ресурсу
    user_clearance = user_info.get("clearance", 0)
    if user_clearance >= resource_level:
        return "ALLOW"
    else:
        return "DENY (Insufficient clearance)"


# =====================================================================
# ГОЛОВНА ФУНКЦІЯ (КРОКИ 2 ТА 4)
# =====================================================================
def run_task2():
    print("=" * 80)
    print(f"Студент: {STUDENT_NAME}, Варіант: {VARIANT_NUMBER}")
    print("Завдання 2: Багаторівнева система контролю доступу")
    print("=" * 80)

    # КРОК 2: Виведення списку усіх ресурсів системи
    print("\n[ СПИСОК РЕСУРСІВ СИСТЕМИ ]")
    print("-" * 60)
    for res_name, res_level in resources:
        # Віднімаємо 1, бо рівні йдуть від 1 до 4, а індекси кортежу від 0 до 3
        level_text = security_levels[res_level - 1]
        print(f"Ресурс: {res_name:<20} | Рівень безпеки: {res_level} ({level_text})")

    # КРОК 4: Виведення результатів перевірки
    print("\n[ РЕЗУЛЬТАТИ ПЕРЕВІРКИ ДОСТУПУ ]")
    print("-" * 80)
    
    # Формуємо список користувачів для перевірки: всі, хто є в словнику + один невідомий хакер
    test_users = list(users.keys()) + ["unknown_hacker"]
    
    # Перевіряємо кожного користувача до кожного ресурсу
    for u_name in test_users:
        for res_name, res_level in resources:
            result = check_access(u_name, res_level)
            # Точний формат за методичкою
            print(f"user=[{u_name}] resource=[{res_name}] -> {result}")
        print("-" * 80) # Розділювач між користувачами

if __name__ == "__main__":
    run_task2()