#!/usr/bin/env python3
"""
IoT Server — accepts multiple peripheral clients, sends tasks, receives results.
Usage: python3 server.py
Commands:
  send <code>             — send a Python one-liner to first connected device
  send <device_id> <code> — send to a specific device
  file <path>             — send a .py file
  clients                 — list connected devices
  status                  — show last known device states
  quit
"""

import socket
import ssl
import threading
import uuid

from protocol import send_msg, recv_msg
from config import *

clients: dict[str, dict] = {}
clients_lock = threading.Lock()


def receive_loop(sock, addr):
    device_key = f"{addr[0]}:{addr[1]}"

    print(f"[SERVER] Receive loop started for {device_key}")

    while True:
        try:
            msg = recv_msg(sock)
            if msg is None:
                print(f"\n[SERVER] Client disconnected: {device_key}")
                break

            kind = msg.get("kind")

            if kind == "status":
                device_id = msg.get("device_id") or device_key
                with clients_lock:
                    clients[device_id] = {
                        "sock": sock,
                        "addr": addr,
                        "status": msg,
                    }
                print(
                    f"\r[PI:{device_id}] state={msg.get('state')} | "
                    f"cpu={msg.get('cpu')}% | "
                    f"mem={msg.get('mem')}%        ",
                    end="",
                    flush=True,
                )

            elif kind == "result":
                print(f"\n\n{'='*50}")
                print(f"[RESULT] device  : {msg.get('device_id', device_key)}")
                print(f"         task_id : {msg.get('task_id')}")
                print(f"         exit    : {msg.get('exit_code')}")
                print(f"         stdout  :\n{msg.get('stdout', '').strip()}")
                if msg.get("stderr"):
                    print(f"         stderr  :\n{msg.get('stderr').strip()}")
                print(f"{'='*50}\n> ", end="", flush=True)

        except (ConnectionResetError, BrokenPipeError, OSError):
            print(f"\n[SERVER] Connection lost: {device_key}")
            break

    with clients_lock:
        stale = [key for key, value in clients.items() if value.get("sock") is sock]
        for key in stale:
            clients.pop(key, None)


def accept_loop(server_sock):
    while True:
        try:
            conn, addr = server_sock.accept()
            print(f"[SERVER] Client connected from {addr}")
            threading.Thread(
                target=receive_loop,
                args=(conn, addr),
                daemon=True,
            ).start()
        except OSError as exc:
            print(f"[SERVER] Accept loop stopped: {exc}")
            break


def make_server_socket() -> socket.socket:
    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    raw.bind((BIND_HOST, PORT))
    raw.listen(32)

    if USE_TLS:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(SERVER_CERT, SERVER_KEY)
        ctx.load_verify_locations(CA_CERT)
        ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx.wrap_socket(raw, server_side=True)

    return raw


def get_target_socket(device_id: str | None):
    with clients_lock:
        if not clients:
            return None, None

        if device_id:
            entry = clients.get(device_id)
            if not entry:
                return None, None
            return device_id, entry["sock"]

        first_id = next(iter(clients))
        return first_id, clients[first_id]["sock"]


def main():
    server_sock = make_server_socket()
    tls_label = "TLS" if USE_TLS else "plain TCP (dev mode)"
    print(f"[SERVER] Listening on {BIND_HOST}:{PORT} ({tls_label})")
    print("[SERVER] Waiting for peripheral devices...\n")

    threading.Thread(target=accept_loop, args=(server_sock,), daemon=True).start()

    print(
        "Commands: send <code> | send <device_id> <code> | file <path> | "
        "clients | status | quit\n"
    )
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not raw:
            continue

        if raw == "clients":
            with clients_lock:
                if not clients:
                    print("[CLIENTS] none connected")
                else:
                    for device_id, entry in clients.items():
                        status = entry.get("status", {})
                        print(
                            f"  - {device_id} @ {entry.get('addr')} "
                            f"state={status.get('state', 'unknown')}"
                        )
            continue

        if raw == "status":
            with clients_lock:
                print(f"\n[STATUS] { {k: v.get('status') for k, v in clients.items()} }")
            continue

        if raw == "quit":
            break

        target_device_id = None
        code = None

        if raw.startswith("send "):
            parts = raw[5:].strip().split(" ", 1)
            with clients_lock:
                known_ids = set(clients.keys())
            if len(parts) == 2 and parts[0] in known_ids:
                target_device_id, code = parts[0], parts[1]
            else:
                code = raw[5:]
        elif raw.startswith("file "):
            try:
                with open(raw[5:].strip()) as file_handle:
                    code = file_handle.read()
            except FileNotFoundError:
                print("[ERROR] File not found")
                continue
        else:
            print("Unknown command.")
            continue

        device_id, sock = get_target_socket(target_device_id)
        if sock is None:
            print("[ERROR] No matching connected device.")
            continue

        task = {
            "kind": "task",
            "task_id": str(uuid.uuid4())[:8],
            "code": code,
            "timeout": 10,
        }
        try:
            send_msg(sock, task)
            print(f"[SERVER] Task sent to {device_id} (id={task['task_id']})")
        except OSError:
            print("[ERROR] Not connected.")

    print("[SERVER] Shutting down.")
    server_sock.close()


if __name__ == "__main__":
    main()
