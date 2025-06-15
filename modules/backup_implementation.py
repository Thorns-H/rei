import time
import os
from datetime import datetime
from dotenv import load_dotenv
import subprocess

load_dotenv(override=True)

def perform_backup():
    try:
        db_host = os.getenv("DB_HOST")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")
        db_port = os.getenv("DB_PORT")

        backup_dir = os.path.join(os.getcwd(), "sql_source")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"{db_name}_backup_{timestamp}.sql")

        dump_command = [
            "mysqldump",
            "-h", db_host,
            "-P", str(db_port),
            "-u", db_user,
            f"--password={db_password}",
            "--databases", db_name,
            "--routines",
            "--events",
            "--single-transaction",
            "--quick",
            "--compact"
        ]

        with open(backup_file, "w") as f:
            subprocess.run(dump_command, stdout=f, check=True)

        print(f"Backup completed successfully: {backup_file}")

    except Exception as e:
        print(f"Error during backup: {e}")

def auto_backup_thread():
    backup_time = os.getenv("BACKUP_TIME", "21:00")

    try:
        target_hour, target_minute = map(int, backup_time.strip().split(":"))
    except ValueError:
        print(f"Invalid BACKUP_TIME format: '{backup_time}'. Use HH:MM in 24-hour format.")
        return

    already_ran_today = False

    while True:
        now = datetime.now()

        if now.hour == target_hour and now.minute == target_minute:
            if not already_ran_today:
                print(f"Scheduled backup started at {backup_time}")
                perform_backup()
                already_ran_today = True
            time.sleep(30)
        else:
            already_ran_today = False
            time.sleep(15)
