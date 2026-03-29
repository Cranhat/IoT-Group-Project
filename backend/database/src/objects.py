from pydantic import BaseModel

class User(BaseModel):
    user_id: int
    name: str
    privilege: str

class Password(BaseModel):
    user_id: int
    password: str

class Device(BaseModel):
    device_id: int
    status: str
    ip_adress: str

class Task_log(BaseModel):
    task_id: int
    user_id: int
    device_id: int
    status: str
    timestamp: int

class Task_result_log(BaseModel):
    task_id: int
    device_id: int
    result: str
    success: bool
    error_message: str
    timestamp: int

class Task_result_log(BaseModel):
    request_id: int
    user_id: int
    ip_address: str
    status: str
    timestamp: int