CREATE TABLE IF NOT EXISTS sensor_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TEXT,
        payload INTEGER
    );

    CREATE TABLE IF NOT EXISTS to_manipulator_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TEXT,
        status TEXT
    );