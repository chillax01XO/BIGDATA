import pandas as pd
import random
from datetime import datetime, timedelta

ACTION_TYPES = [
    "first_visit", "registration", "login", "logout",
    "create_topic", "view_topic", "delete_topic", "post_message"
]

TARGET_TYPES = {
    "create_topic": "topic",
    "view_topic": "topic",
    "delete_topic": "topic",
    "post_message": "message"
}

# Параметры генерации
start_date = datetime(2025, 3, 1)
num_days = 30
min_actions_per_type = 5
num_users = 20

logs = []

for day in range(num_days):
    date = start_date + timedelta(days=day)
    for action in ACTION_TYPES:
        count = random.randint(min_actions_per_type, min_actions_per_type + 10)

        # спецобработка create_topic
        if action == "create_topic":
            # минимум 2 ошибки
            error_cases = 2
            for _ in range(error_cases):
                logs.append({
                    "user_id": None,
                    "action_type": action,
                    "target_id": random.randint(1000, 9999),
                    "target_type": TARGET_TYPES.get(action),
                    "status": "error",
                    "description": "User not logged in",
                    "timestamp": date + timedelta(minutes=random.randint(0, 1440))
                })
            count -= error_cases  # оставшиеся будут успешные

        for _ in range(count):
            is_logged_in = random.choice([True, False]) if action == "post_message" else True
            user_id = random.randint(1, num_users) if is_logged_in else None
            status = "success"

            # случайная ошибка кроме post_message
            if action != "post_message" and random.random() < 0.05:
                status = "error"

            logs.append({
                "user_id": user_id,
                "action_type": action,
                "target_id": random.randint(1000, 9999) if action in TARGET_TYPES else None,
                "target_type": TARGET_TYPES.get(action),
                "status": status,
                "description": None if status == "success" else "Random error",
                "timestamp": date + timedelta(minutes=random.randint(0, 1440))
            })


df = pd.DataFrame(logs)

df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce").astype("Int64")
df["target_id"] = pd.to_numeric(df["target_id"], errors="coerce").astype("Int64")

df = df.sort_values("timestamp")

df.to_csv("logs.csv", index=False)
print("Логи сохранены в файл logs.csv")
