from enum import Enum
from collections import deque
import subprocess, tempfile, os, sys, time, socket, ssl, threading
from protocol import send_msg, recv_msg
from config import *
from communication.clientcomms import SecureClient

# DEVICE STATUS

class Device_Status(Enum):
    READY = "ready"
    WORKING = "working"
    DONE = "done"

currentDevState = Device_Status.READY.value

def set_device_state(state: Device_Status):
    global currentDevState
    print(f"    [DEVICE_STATE] {currentDevState} -> {state.value}")
    currentDevState = state.value


# TASK STATUS

class Task_Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    CRASHED = "crashed"
    DONE = "done"

currentTaskState = Task_Status.PENDING.value

def set_task_state(state: Task_Status):
    global currentTaskState
    print(f"    [TASK_STATE] {currentTaskState} -> {state.value}")
    currentTaskState = state.value

task_queue = deque()


# TASK EXECUTION

def execute(code: str, timeout: int) -> dict:
    """
    Execute received task on client and return its result.

    Args:
        code (str): Code to execute in String type (must be written in proper Python syntax).
        timeout (int): Amount of time for task execution before timeout error.

    Returns:
        dict: Dictionary with result (stdout), errors (stderr), exit code (exit_code) [-1 if error]
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                    delete=False, dir=tempfile.gettempdir()) as f:
        f.write(code)
        tmp = f.name
    try:
        set_task_state(Task_Status.RUNNING)
        result = subprocess.run([sys.executable, tmp], capture_output=True, text=True, timeout=timeout)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Timeout", "exit_code": -1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": -1}
    finally:
        os.unlink(tmp)


def task_worker(comms: SecureClient):
    """
    Sends tasks from task queue for execution. 
    Sends task's result back to server. 
    Manages task's and device's states during tasks execution.

    Args:
        sock (socket.socket): Communication socket.
    """
    while True:
        if task_queue:
            task = task_queue.popleft()
            set_device_state(Device_Status.WORKING)
            set_task_state(Task_Status.RUNNING)
            result = execute(task["code"], task.get("timeout", 10))
            set_task_state(Task_Status.DONE)
            send_msg(comms, {
                "kind": "result",
                "task_id": task["task_id"],
                **result
            })
            time.sleep(0.2)
            set_task_state(Task_Status.PENDING)
            set_device_state(Device_Status.READY)
        else:
            time.sleep(0.1)


def heartbeat_loop(comms: SecureClient):
    """
    Send device status to the server.

    Args:
        sock (socket.socket): Communication socket.
    """
    while True:
        try:
            send_msg(comms, {
                "kind":         "status",
                "device_id":    DEVICE_ID,
                "state":        currentDevState,
                "timestamp":    time.time()
            })
        except OSError:
            break
        time.sleep(HEARTBEAT_INTERVAL)


def receive_loop(comms: SecureClient):
    """
    Check for messages from the server. Detect disconnect and received tasks. If task is detected then add it into device's task queue.

    Args:
        sock (socket.socket): Communication socket.
    """
    while True:
        try:
            msg = recv_msg(comms)
            if msg is None:
                print("\n[CLIENT] Server disconnected.")
                break

            if msg.get("kind") == "task":
                task_queue.append(msg)

        except (ConnectionResetError, BrokenPipeError, OSError):
            print("\n[CLIENT] Connection lost.")
            break


