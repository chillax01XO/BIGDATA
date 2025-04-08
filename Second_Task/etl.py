import psycopg2
import pandas as pd
from datetime import datetime, timedelta

# Расчёт периода: последние 30 дней 
end_date = datetime.today()
start_date = end_date - timedelta(days=30)


conn = psycopg2.connect(
    dbname="logsdb",
    user="user",
    password="password",
    host="host.docker.internal",
    port="5432"
)



query = """
SELECT *
FROM logs
WHERE timestamp::date BETWEEN %s AND %s;
"""

df = pd.read_sql(query, conn, params=[start_date.date(), end_date.date()])
conn.close()

df['date'] = pd.to_datetime(df['timestamp']).dt.date

# Регистрации
registrations = df[df['action_type'] == 'registration'].groupby('date').size().rename("new_accounts")

# Сообщения
messages = df[df['action_type'] == 'post_message']
total_messages = messages.groupby('date').size().rename("total_messages")
anon_messages = messages[messages['user_id'].isna()].groupby('date').size().rename("anon_messages")
anon_pct = (anon_messages / total_messages * 100).rename("anon_message_pct").fillna(0)

# Создание тем
topics_created = df[df['action_type'] == 'create_topic']
daily_topics = topics_created.groupby('date').size().rename("new_topics")
cumulative_topics = daily_topics.cumsum()
topic_change_pct = cumulative_topics.pct_change().fillna(0) * 100
topic_change_pct = topic_change_pct.rename("topic_change_pct")


result = pd.concat([registrations, anon_pct, total_messages, topic_change_pct], axis=1).fillna(0)
result = result.round(2).reset_index().rename(columns={"date": "day"})

result.to_csv("/workspace/aggregated_logs.csv", index=False)
print("Файл aggregated_logs.csv создан.")
