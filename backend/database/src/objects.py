from datetime import datetime
from pydantic import BaseModel, Field

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
    ip_address: str
    container_name: str | None = None
    device_name: str | None = None

class Task_log(BaseModel):
    task_id: int
    user_id: int
    device_id: int
    status: str
    timestamp: datetime

class Task_result_log(BaseModel):
    task_id: int
    device_id: int
    result: str
    success: bool
    error_message: str
    timestamp: datetime

class HTTP_log(BaseModel):
    request_id: int
    user_id: int
    ip_address: str
    status: str
    timestamp: datetime

class Packet_sniffer_log(BaseModel):
    sniffer_name: str
    port: int
    log: str
    timestamp: datetime

    def __init__(self, **data):
        if isinstance(data.get("log"), str):
            data["log"] = data["log"].replace("\x00", "")

        super().__init__(**data)

