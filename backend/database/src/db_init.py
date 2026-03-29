users_initialization = """
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        privilege_type TEXT NOT NULL
    );
    """

passwords_initialization = """
    CREATE TABLE IF NOT EXISTS passwords (
        user_id INT,
        password TEXT NOT NULL,

        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
    ); """

devices_initialization = """
    CREATE TABLE IF NOT EXISTS devices (
        device_id SERIAL PRIMARY KEY,
        status TEXT NOT NULL,
        ip_address TEXT UNIQUE
    ); """

task_logs_initialization = """
    CREATE TABLE IF NOT EXISTS task_logs (
        task_id SERIAL PRIMARY KEY,
        user_id INT,
        device_id INT,
        status TEXT,
        timestamp TIMESTAMP DEFAULT NOW(),

        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
        FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE SET NULL
        ); """

task_result_logs_initialization = """
    CREATE TABLE IF NOT EXISTS task_result_logs (
        task_id INT,
        device_id INT,
        result TEXT,
        success BOOLEAN NOT NULL DEFAULT FALSE,
        error_message TEXT,
        timestamp TIMESTAMP DEFAULT NOW(),

        FOREIGN KEY (task_id) REFERENCES task_logs(task_id) ON DELETE SET NULL,
        FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE SET NULL
    ); """

http_logs_initialization = """
    CREATE TABLE IF NOT EXISTS http_logs (
        request_id SERIAL PRIMARY KEY,
        user_id INT,
        ip_address TEXT,
        status TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT NOW(),
        
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
    ); """