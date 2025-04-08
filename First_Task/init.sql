CREATE TABLE logs (
    user_id INTEGER,
    action_type VARCHAR(50),
    target_id INTEGER,
    target_type VARCHAR(50),
    status VARCHAR(20),
    description TEXT,
    timestamp TIMESTAMP
);

COPY logs(user_id, action_type, target_id, target_type, status, description, timestamp)
FROM '/Users/blooomy/Desktop/08_04/logs.csv'
DELIMITER ','
CSV HEADER;
