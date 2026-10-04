import os
import sys

# Додаємо шлях до головної папки проєкту
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from labs.lab01.task1 import analyze_passwords
from labs.lab01.task2 import run_task2
from labs.lab01.task3 import run_task3
from shared.student import STUDENT_NAME, VARIANT_NUMBER


def main():
    print("*" * 65)
    print(f" ЛАБОРАТОРНА РОБОТА 1 | Виконав: {STUDENT_NAME} | Варіант: {VARIANT_NUMBER}")
    print("*" * 65)
    
    print("\n\n>>> ЗАПУСК ЗАВДАННЯ 1: Аналізатор паролів <<<")
    analyze_passwords()
    
    print("\n\n>>> ЗАПУСК ЗАВДАННЯ 2: Система контролю доступу (RBAC) <<<")
    run_task2()
    
    print("\n\n>>> ЗАПУСК ЗАВДАННЯ 3: Хешування (sha3_224) <<<")
    run_task3()
    
    print("\n" + "*" * 65)
    print(" Усі завдання успішно виконано!")
    print("*" * 65)

if __name__ == "__main__":
    main()