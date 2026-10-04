import argparse
import logging
from pathlib import Path

from labs.lab02.task1 import Admin, AuditLog, UserAccount
from labs.lab02.task2 import check_integrity, generate_baseline


def run_demo():
    print("\n=== Демонстрація ООП (Завдання 1) ===")
    audit = AuditLog()
    admin = Admin("root_admin", "admin@domain.com", permissions=["read", "write"])
    admin.set_password("Secret123!")
    account = UserAccount(admin, audit)

    print("[*] Невдалий вхід:")
    account.login("root_admin", "WrongPass!", "192.168.0.1")

    print("\n[*] Успішний вхід:")
    if account.login("root_admin", "Secret123!", "192.168.0.1"):
        print("Вхід успішний!")

    print("\n[*] Зміна email (валідація):")
    try:
        admin.email = "invalid_email"
    except ValueError as e:
        print("Перехоплено помилку:", e)

    print("\n[*] Вихід із системи:")
    account.logout()
    print("\n=== Журнал аудиту ===")
    audit.show_all()


def run_analyze(args):
    dir_path = Path(args.dir)
    baseline_path = Path(args.baseline)
    log_path = Path(args.log_file)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if args.mode == "generate":
        generate_baseline(dir_path, baseline_path)
    elif args.mode == "check":
        check_integrity(dir_path, baseline_path)


def main():
    parser = argparse.ArgumentParser(description="Лабораторна робота №2")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("demo", help="Демонстрація Завдання 1 (OOP)")

    analyze_parser = subparsers.add_parser(
        "analyze", help="Консольна утиліта (Завдання 2)"
    )
    analyze_parser.add_argument("--dir", required=True, type=str)
    analyze_parser.add_argument("--baseline", required=True, type=str)
    analyze_parser.add_argument("--mode", required=True, choices=["generate", "check"])
    analyze_parser.add_argument("--log-file", required=True, type=str)

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()
    elif args.command == "analyze":
        run_analyze(args)


if __name__ == "__main__":
    main()
