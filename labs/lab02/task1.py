import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

ITERATIONS = 100000
SESSION_TIMEOUT_SEC = 900


class User:
    def __init__(self, username: str, email: str, role: str, active: bool = True):
        self.username = username
        self.role = role
        self.active = active
        self.__password_hash = b""
        self.__password_salt = b""
        self.email = email  # Викличе setter

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        # Валідація: латинська літера, 3-64 символи, @ і домен
        if not re.match(
            r"^[A-Za-z][A-Za-z0-9_\-\.]{2,63}@[A-Za-z0-9\-\.]+\.[A-Za-z]{2,}$", value
        ):
            raise ValueError("Невірний формат email")
        self._email = value

    def set_password(self, password: str):
        self.__password_salt = os.urandom(16)
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), self.__password_salt, ITERATIONS
        )

    def check_password(self, password: str) -> bool:
        if not self.__password_salt:
            return False
        test_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), self.__password_salt, ITERATIONS
        )
        return hmac.compare_digest(self.__password_hash, test_hash)

    def deactivate(self):
        self.active = False

    def __str__(self):
        return f"User(username={self.username}, email={self.email}, role={self.role}, active={self.active})"


class Admin(User):
    def __init__(
        self,
        username: str,
        email: str,
        role: str = "admin",
        active: bool = True,
        permissions=None,
    ):
        super().__init__(username, email, role, active)
        self.permissions = set(permissions) if permissions else set()

    def grant_permission(self, permission: str):
        self.permissions.add(permission)

    def revoke_permission(self, permission: str):
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self):
        return f"Admin(username={self.username}, email={self.email}, permissions={self.permissions})"


class Session:
    def __init__(self, ip: str):
        self.ip = ip
        now = datetime.now(timezone.utc)
        self.login_time = now
        self.last_activity = now

    def touch(self):
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            return False
        diff = datetime.now(timezone.utc) - self.last_activity
        return diff <= timedelta(seconds=timeout_sec)


@dataclass
class LogEntry:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self):
        self.logs = []

    def add_log(self, username: str, action: str):
        self.logs.append(LogEntry(datetime.now(timezone.utc), username, action))

    def show_all(self):
        for log in self.logs:
            print(
                f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}] {log.username} - {log.action}"
            )


class UserAccount:
    def __init__(self, user: User, audit_log: AuditLog):
        self.user = user
        self.session = None
        self.audit_log = audit_log

    def login(self, username, password, ip):
        if (
            username == self.user.username
            and self.user.active
            and self.user.check_password(password)
        ):
            self.session = Session(ip)
            self.audit_log.add_log(username, "login_success")
            return True
        self.audit_log.add_log(username, "login_failure")
        return False

    def is_authenticated(self) -> bool:
        if self.session and self.session.is_active(SESSION_TIMEOUT_SEC):
            self.session.touch()
            return True
        return False

    def logout(self):
        if self.session:
            self.session = None
            self.audit_log.add_log(self.user.username, "logout")

    def __getitem__(self, key):
        if key == "user":
            return self.user
        elif key == "session":
            return self.session
        raise KeyError(f"Невідомий ключ: {key}")

    def __setitem__(self, key, value):
        if key == "user":
            if not isinstance(value, User):
                raise TypeError("Значення має бути об'єктом User")
            self.user = value
        elif key == "session":
            if value is not None and not isinstance(value, Session):
                raise TypeError("Значення має бути об'єктом Session")
            self.session = value
        else:
            raise KeyError(f"Встановлення ключа {key} заборонено")
