users_initialization = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INT PRIMARY KEY,
        name TEXT,
        privilege_type TEXT
    );
    """

passwords_initialization = """
    CREATE TABLE IF NOT EXISTS passwords (
        user_id INT,
        password TEXT
); """

devices_initialization = """
    CREATE TABLE IF NOT EXISTS devices (
        device_id INT PRIMARY KEY,
        status TEXT,
        ip_address TEXT
); """

task_logs_initialization = """
    CREATE TABLE IF NOT EXISTS task_logs (
        task_id INT PRIMARY KEY,
        user_id INT,
        device_id INT,
        status TEXT,
        timestamp TIMESTAMP DEFAULT NOW()
); """

task_result_logs_initialization = """
    CREATE TABLE IF NOT EXISTS task_result_logs (
        task_id INT,
        device_id INT,
        result TEXT,
        success BOOLEAN,
        error_message TEXT,
        timestamp TIMESTAMP DEFAULT NOW()
); """

http_logs_initialization = """
    CREATE TABLE IF NOT EXISTS http_logs (
        request_id INT PRIMARY KEY,
        user_id INT,
        ip_address TEXT,
        status TEXT,
        timestamp TIMESTAMP DEFAULT NOW()
); """