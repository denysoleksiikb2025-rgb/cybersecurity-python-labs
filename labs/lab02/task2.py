import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

# Створюємо власний логер для цього файлу (виправлення LOG015)
logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    path: str
    hash: str
    size: int
    mod_date: str


def calculate_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    # Ловимо конкретну помилку читання файлів замість загальної (виправлення BLE001)
    except OSError as e:
        logger.error(f"Помилка читання файлу {file_path}: {e}")
        return ""


def scan_directory(dir_path: Path) -> dict[str, FileInfo]:
    files_data = {}
    for file_path in dir_path.rglob("*"):
        if file_path.is_file():
            rel_path = str(file_path.relative_to(dir_path).as_posix())
            file_hash = calculate_sha256(file_path)
            stat = file_path.stat()
            mod_date = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            
            fi = FileInfo(path=rel_path, hash=file_hash, size=stat.st_size, mod_date=mod_date)
            files_data[rel_path] = fi
    return files_data


def generate_baseline(dir_path: Path, baseline_path: Path) -> None:
    logger.info(f"Scanning directory: {dir_path}")
    files_data = scan_directory(dir_path)
    json_data = {path: asdict(fi) for path, fi in files_data.items()}
    
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)
        
    logger.info(f"Baseline successfully generated at: {baseline_path}")
    print(f"[INFO] Еталонний файл успішно збережено: {baseline_path}")


def check_integrity(dir_path: Path, baseline_path: Path) -> None:
    logger.info(f"Loading baseline file: {baseline_path}")
    print(f"[INFO] Loading baseline file: {baseline_path}")
    
    if not baseline_path.exists():
        print("[ERROR] Еталонний файл не знайдено! Спочатку запустіть режим generate.")
        return

    with open(baseline_path, "r", encoding="utf-8") as f:
        baseline_data = json.load(f)

    print(f"[INFO] Scanning directory: {dir_path}")
    current_data = scan_directory(dir_path)

    baseline_files = set(baseline_data.keys())
    current_files = set(current_data.keys())

    created_files = current_files - baseline_files
    deleted_files = baseline_files - current_files
    modified_files = []
    unchanged_count = 0

    for file_path in baseline_files.intersection(current_files):
        if baseline_data[file_path]["hash"] != current_data[file_path].hash:
            modified_files.append((file_path, baseline_data[file_path]["hash"], current_data[file_path].hash))
        else:
            unchanged_count += 1

    print("\n=== File Integrity Inspection Summary ===")
    print(f"Total monitored files : {len(baseline_files)}")
    print(f"Unchanged files       : {unchanged_count}")
    print(f"Modified files        : {len(modified_files)}")
    print(f"Created files         : {len(created_files)}")
    print(f"Deleted files         : {len(deleted_files)}")

    if modified_files or created_files or deleted_files:
        print("\n=== Detected Anomalies ===")
        for file_path, exp_hash, act_hash in modified_files:
            print(f"[MODIFIED] {dir_path / file_path}")
            print(f"  Expected SHA-256 : {exp_hash}")
            print(f"  Actual SHA-256   : {act_hash}")
            logger.warning(f"MODIFIED: {file_path}")
            
        for file_path in created_files:
            print(f"[CREATED]  {dir_path / file_path}")
            logger.warning(f"CREATED: {file_path}")
            
        for file_path in deleted_files:
            print(f"[DELETED]  {dir_path / file_path}")
            logger.warning(f"DELETED: {file_path}")

        print("\n[WARNING] Security alerts detected! Check audit log.")
    else:
        print("\n[INFO] No anomalies detected. Integrity verified.")