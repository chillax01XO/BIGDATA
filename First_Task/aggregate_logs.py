import psycopg2
import pandas as pd
from datetime import datetime, timedelta
import sys

period = input("Введите период в формате YYYY-MM-DD:YYYY-MM-DD: ").strip()
start_str, end_str = period.split(":")
start_date = datetime.strptime(start_str, "%Y-%m-%d")
end_date = datetime.strptime(end_str, "%Y-%m-%d")

conn = psycopg2.connect(
    dbname="logsdb",
    user="user",
    password="password",
    host="localhost",
    port="5432"
)

query = f"""
SELECT *
FROM logs
WHERE timestamp::date BETWEEN %s AND %s;
"""

df = pd.read_sql(query, conn, params=[start_date.date(), end_date.date()])
conn.close()

# агрегация
df['date'] = pd.to_datetime(df['timestamp']).dt.date

# кол-во рег
registrations = df[df['action_type'] == 'registration'].groupby('date').size().rename("new_accounts")

# кол-во сообщений всего и анонимных
messages = df[df['action_type'] == 'post_message']
total_messages = messages.groupby('date').size().rename("total_messages")
anon_messages = messages[messages['user_id'].isna()].groupby('date').size().rename("anon_messages")

# % анонимных сообщений
anon_pct = (anon_messages / total_messages * 100).rename("anon_message_pct").fillna(0)

# кол-во созданных тем по дням
topics_created = df[df['action_type'] == 'create_topic']
daily_topics = topics_created.groupby('date').size().rename("new_topics")

# кумулятивное количество тем
cumulative_topics = daily_topics.cumsum()

# % изменение количества тем относительно предыдущего дня
topic_change_pct = cumulative_topics.pct_change().fillna(0) * 100
topic_change_pct = topic_change_pct.rename("topic_change_pct")


result = pd.concat([registrations, anon_pct, total_messages, topic_change_pct], axis=1).fillna(0)
result = result.round(2).reset_index().rename(columns={"date": "day"})

result.to_csv("aggregated_logs.csv", index=False)
print("Отчёт сохранён в aggregated_logs.csv")
