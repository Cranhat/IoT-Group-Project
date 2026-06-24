#!/usr/bin/env python3
"""
IoT Server — listens for clients (Pi devices), sends tasks, receives results.
Integrates with the backend API to register devices and relay task results.

Usage: python3 server.py
Console commands (while a client is connected):
  send <code>   — send a Python one-liner
  file <path>   — send a .py file
  status        — show last known Pi state
  quit
"""

import json
import os
import socket
import ssl
import threading
import time
import uuid

import urllib.request
import urllib.error

from protocol import send_msg, recv_msg
from config import *
from communication.comms import SecureServer

# ── Backend integration ───────────────────────────────────────────────────────

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")

def _api(method: str, path: str, body: dict | None = None) -> dict | None:
    """Minimal HTTP client using only stdlib. Returns parsed JSON or None on error."""
    url = BACKEND_URL.rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"[BACKEND] {method} {path} → HTTP {e.code}: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"[BACKEND] {method} {path} → {e}")
        return None


# ── Per-client state ──────────────────────────────────────────────────────────

# Maps addr (str) → {"conn": socket, "device_id": int|None, "status": dict}
clients: dict[str, dict] = {}
clients_lock = threading.Lock()


# ── Backend reporting helpers ─────────────────────────────────────────────────

def backend_register(ip: str, device_name: str) -> int | None:
    result = _api("POST", "/devices/register", {
        "status": "online",
        "ip_address": ip,
        "device_name": device_name,
    })
    if result:
        return result.get("device_id")
    return None


def backend_set_status(ip: str, status: str):
    _api("PATCH", f"/devices/by-ip/{ip}/status", {"status": status})


def backend_submit_result(task_id: str, stdout: str, stderr: str, exit_code: int):
    """task_id from the backend is an int; from the client it's a short UUID string.
    We store the backend int task_id in pending_tasks keyed by short UUID."""
    # task_id here is already the backend integer, passed in by receive_loop
    success = (exit_code == 0)
    result_text = stdout.strip() if stdout else None
    error_text  = stderr.strip() if stderr else None
    _api("PUT", f"/tasks/{task_id}/result", {
        "result":        result_text,
        "success":       success,
        "exit_code":     exit_code,
        "error_message": error_text,
    })


# ── Task polling ──────────────────────────────────────────────────────────────

# pending_tasks: maps backend task_id (int) → short UUID sent to the client
pending_tasks: dict[int, str] = {}
# reverse: short client UUID → backend task_id
pending_reverse: dict[str, int] = {}
pending_lock = threading.Lock()


def task_poll_loop(addr: str):
    """Polls the backend for pending tasks for this device and forwards them."""
    while True:
        time.sleep(2)
        with clients_lock:
            entry = clients.get(addr)
        if entry is None:
            break

        device_id = entry.get("device_id")
        conn      = entry.get("conn")
        if device_id is None or conn is None:
            continue

        result = _api("GET", f"/tasks/pending?device_id={device_id}")
        if not result:
            continue

        for task in result.get("tasks", []):
            backend_id = task["task_id"]
            with pending_lock:
                if backend_id in pending_tasks:
                    continue  # already dispatched
                short_id = str(uuid.uuid4())[:8]
                pending_tasks[backend_id]  = short_id
                pending_reverse[short_id]  = backend_id

            msg = {
                "kind":    "task",
                "task_id": short_id,
                "code":    task["problem"],
                "timeout": 10,
            }
            try:
                send_msg(conn, msg)
                print(f"[SERVER] Dispatched backend task {backend_id} → client UUID {short_id}")
            except OSError:
                with pending_lock:
                    pending_tasks.pop(backend_id, None)
                    pending_reverse.pop(short_id, None)


# ── Per-connection receive loop ───────────────────────────────────────────────

def receive_loop(conn: socket.socket, addr: str):
    print(f"[SERVER] Receive loop started for {addr}")

    while True:
        try:
            msg = recv_msg(conn)
            if msg is None:
                print(f"\n[SERVER] Client {addr} disconnected.")
                break

            kind = msg.get("kind")

            if kind == "status":
                with clients_lock:
                    if addr in clients:
                        clients[addr]["status"] = msg
                print(f"\r[PI:{addr}] state={msg.get('state')} | "
                      f"cpu={msg.get('cpu')}% | "
                      f"mem={msg.get('mem')}%        ",
                      end="", flush=True)

            elif kind == "result":
                short_id  = msg.get("task_id")
                stdout    = msg.get("stdout", "")
                stderr    = msg.get("stderr", "")
                exit_code = msg.get("exit_code", -1)

                print(f"\n\n{'='*50}")
                print(f"[RESULT] task_id : {short_id}")
                print(f"         exit    : {exit_code}")
                print(f"         stdout  :\n{stdout.strip()}")
                if stderr:
                    print(f"         stderr  :\n{stderr.strip()}")
                print(f"{'='*50}\n> ", end="", flush=True)

                with pending_lock:
                    backend_id = pending_reverse.pop(short_id, None)
                    if backend_id is not None:
                        pending_tasks.pop(backend_id, None)

                if backend_id is not None:
                    backend_submit_result(backend_id, stdout, stderr, exit_code)
                else:
                    print(f"[SERVER] Warning: result for unknown task_id {short_id}")

        except (UnicodeDecodeError, json.JSONDecodeError):
            print(f"\n[SERVER] Malformed data from {addr}.")
            break
        except (ConnectionResetError, BrokenPipeError, OSError):
            print(f"\n[SERVER] Connection lost from {addr}.")
            break

    # Cleanup
    with clients_lock:
        entry = clients.pop(addr, None)
    if entry and entry.get("device_id") is not None:
        backend_set_status(addr, "offline")
        print(f"[SERVER] Device {addr} marked offline in backend.")


# ── Accept loop ───────────────────────────────────────────────────────────────

def accept_loop(server_sock: socket.socket, comms: SecureServer):
    while True:
        try:
            raw_conn, addr_tuple = server_sock.accept()
        except OSError:
            break

        ip = addr_tuple[0]
        if USE_TLS:
            try:
                conn = comms.ctx.wrap_socket(raw_conn, server_side=True)
            except ssl.SSLError as e:
                print(f"[SERVER] TLS handshake failed from {ip}: {e}")
                raw_conn.close()
                continue
        else:
            conn = raw_conn

        print(f"[SERVER] Client connected from {ip}")

        # Extract device name from TLS client cert CN if available
        device_name = ip
        if USE_TLS:
            try:
                cert = conn.getpeercert()
                for rdn in cert.get("subject", []):
                    for key, val in rdn:
                        if key == "commonName":
                            device_name = val
            except Exception:
                pass

        device_id = backend_register(ip, device_name)
        if device_id:
            print(f"[SERVER] Registered device {device_name} ({ip}) as device_id={device_id}")
        else:
            print(f"[SERVER] Backend unavailable — device {ip} not registered")

        with clients_lock:
            clients[ip] = {"conn": conn, "device_id": device_id, "status": {}}

        threading.Thread(target=receive_loop, args=(conn, ip), daemon=True).start()
        threading.Thread(target=task_poll_loop, args=(ip,), daemon=True).start()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    comms = SecureServer(host=BIND_HOST, port=PORT)
    server_sock = comms._create_socket()
    tls_label = "TLS" if USE_TLS else "plain TCP (dev mode)"
    print(f"[SERVER] Listening on {BIND_HOST}:{PORT} ({tls_label})")
    print(f"[SERVER] Backend: {BACKEND_URL}")
    print(f"[SERVER] Waiting for clients...\n")

    threading.Thread(target=accept_loop, args=(server_sock, comms), daemon=True).start()

    print("Commands: send <code> | file <path> | status | quit\n")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not raw:
            continue

        if raw.startswith("send "):
            code = raw[5:]
        elif raw.startswith("file "):
            try:
                with open(raw[5:].strip()) as f:
                    code = f.read()
            except FileNotFoundError:
                print("[ERROR] File not found")
                continue
        elif raw == "status":
            with clients_lock:
                if not clients:
                    print("[STATUS] No clients connected.")
                else:
                    for ip, entry in clients.items():
                        print(f"  {ip} (device_id={entry['device_id']}): {entry['status']}")
            continue
        elif raw == "quit":
            break
        else:
            print("Unknown command.")
            continue

        # Send to all connected clients
        with clients_lock:
            targets = list(clients.items())

        if not targets:
            print("[ERROR] No clients connected.")
            continue

        for ip, entry in targets:
            conn = entry.get("conn")
            if conn is None:
                continue
            short_id = str(uuid.uuid4())[:8]
            task = {"kind": "task", "task_id": short_id, "code": code, "timeout": 10}
            try:
                send_msg(conn, task)
                print(f"[SERVER] Task sent to {ip} (id={short_id})")
            except OSError:
                print(f"[ERROR] Could not send to {ip}")

    print("[SERVER] Shutting down.")
    server_sock.close()


if __name__ == "__main__":
    main()
