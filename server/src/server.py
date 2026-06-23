#!/usr/bin/env python3
"""
IoT Server — listens for one client (the Pi), sends tasks, receives results.
Usage: python3 server.py
Commands:
  send <code>   — send a Python one-liner
  file <path>   — send a .py file
  status        — show last known Pi state
  quit
"""

import json
import socket, ssl, threading, time, uuid, os
import urllib.request
from datetime import datetime
from protocol import send_msg, recv_msg
from config import *
from communication.comms import SecureServer

active_connections = {}
pi_statuses = {}
conn_lock  = threading.Lock()

from http.server import BaseHTTPRequestHandler, HTTPServer

class TaskHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_POST(self):
        if self.path == "/task":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                task_id = data.get("task_id")
                code = data.get("code")
                target_device = data.get("device_name")
                
                with conn_lock:
                    conn = active_connections.get(target_device) if target_device else next(iter(active_connections.values()), None)
                    if conn is not None:
                        send_msg(conn, {
                            "kind": "task",
                            "task_id": str(task_id),
                            "code": code
                        })
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"status": "success"}).encode())
                        print(f"\n[HTTP] Forwarded task {task_id} to client {target_device or 'default'}.\n> ", end="", flush=True)
                    else:
                        self.send_response(503)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": f"Client {target_device or 'default'} not connected"}).encode())
                        print(f"\n[HTTP] Failed to forward task {task_id}: Client {target_device or 'default'} not connected.\n> ", end="", flush=True)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_http_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, TaskHTTPHandler)
    print("[SERVER] HTTP Task Server started on port 8080")
    httpd.serve_forever()


def get_device_id_by_name(device_name):
    if not device_name or not isinstance(device_name, str):
        return 1
    try:
        backend_url = os.environ.get("BACKEND_API_URL", "http://backend:8000")
        url = f"{backend_url.rstrip('/')}/devices"
        with urllib.request.urlopen(url, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for dev in data.get("devices", []):
                if dev.get("ip_address") == device_name:
                    return int(dev.get("device_id"))
    except Exception as e:
        print(f"[SERVER] Error fetching device ID for name '{device_name}': {e}")
    return 1


def save_task_result_to_db(task_id, msg, device_name):
    try:
        task_id_int = int(task_id)
    except (ValueError, TypeError):
        return

    try:
        stdout = msg.get("stdout", "").strip()
        stderr = msg.get("stderr", "").strip()
        exit_code = msg.get("exit_code", 0)
        success = (exit_code == 0)

        # Resolve the database integer device_id from the client's string device_id
        device_id = get_device_id_by_name(device_name)

        result_text = stdout
        if not result_text and not success:
            result_text = f"Failed with exit code {exit_code}"

        backend_url = os.environ.get("BACKEND_API_URL", "http://backend:8000")
        url = f"{backend_url.rstrip('/')}/tasks/{task_id_int}/result"

        payload = {
            "device_id": int(device_id),
            "result": result_text,
            "success": success,
            "error_message": stderr
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            pass
        print(f"\n[SERVER] Successfully saved task result for task {task_id_int}.\n> ", end="", flush=True)
    except Exception as e:
        print(f"\n[SERVER] Failed to save task result: {e}\n> ", end="", flush=True)


def update_device_status_in_db(ip_address, status):
    try:
        backend_url = os.environ.get("BACKEND_API_URL", "http://backend:8000")
        url = f"{backend_url.rstrip('/')}/devices/status/{ip_address}"
        payload = {"status": status}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="PUT"
        )
        with urllib.request.urlopen(req, timeout=3.0) as response:
            pass
        print(f"\n[SERVER] Updated device {ip_address} status to {status} in database.\n> ", end="", flush=True)
    except Exception as e:
        print(f"\n[SERVER] Failed to update device {ip_address} status to {status}: {e}\n> ", end="", flush=True)


def heartbeat_check_loop():
    while True:
        time.sleep(5)
        now = time.time()
        stale_devices = []
        with conn_lock:
            for device_id, msg in list(pi_statuses.items()):
                if now - msg.get("received_at", 0) > 15:
                    stale_devices.append(device_id)

        for device_id in stale_devices:
            print(f"\n[SERVER] Device {device_id} heartbeat timeout. Closing socket.")
            with conn_lock:
                sock = active_connections.get(device_id)
                if sock:
                    try:
                        sock.close()
                    except Exception:
                        pass


def receive_loop(sock):
    print("[SERVER] Receive loop started")
    client_device_id = None

    while True:
        try:
            msg = recv_msg(sock)
            if msg is None:
                print(f"\n[SERVER] Client {client_device_id or 'unknown'} disconnected.")
                break

            kind = msg.get("kind")

            if kind == "status":
                device_id = msg.get("device_id")
                client_device_id = device_id
                state = msg.get("state")
                db_status = "online" if state == "ready" else "busy"

                with conn_lock:
                    prev_msg = pi_statuses.get(device_id)
                    prev_state = prev_msg.get("state") if prev_msg else None

                    active_connections[device_id] = sock
                    msg["received_at"] = time.time()
                    pi_statuses[device_id] = msg

                if prev_state != state:
                    threading.Thread(
                        target=update_device_status_in_db,
                        args=(device_id, db_status),
                        daemon=True
                    ).start()
                
                print(f"\r[PI {device_id}] state={msg.get('state')} | "
                      f"cpu={msg.get('cpu')}% | "
                      f"mem={msg.get('mem')}%        ",
                      end="", flush=True)

            elif kind == "result":
                task_id = msg.get('task_id')
                print(f"\n\n{'='*50}")
                print(f"[RESULT] device   : {client_device_id}")
                print(f"[RESULT] task_id  : {task_id}")
                print(f"         exit     : {msg.get('exit_code')}")
                print(f"         stdout   :\n{msg.get('stdout', '').strip()}")
                if msg.get("stderr"):
                    print(f"         stderr   :\n{msg.get('stderr').strip()}")
                print(f"{'='*50}\n> ", end="", flush=True)

                # Save the response in the database in a background thread
                threading.Thread(target=save_task_result_to_db, args=(task_id, msg, client_device_id), daemon=True).start()


        except (UnicodeDecodeError, json.JSONDecodeError):
            print("\n[SERVER] Received non-protocol data (transport mismatch or malformed frame).")
            break
        except (ConnectionResetError, BrokenPipeError, OSError):
            print(f"\n[SERVER] Connection lost for client {client_device_id or 'unknown'}.")
            break

    if client_device_id:
        with conn_lock:
            if active_connections.get(client_device_id) == sock:
                active_connections.pop(client_device_id, None)
                pi_statuses.pop(client_device_id, None)
                still_connected = False
            else:
                still_connected = True

        if not still_connected:
            threading.Thread(
                target=update_device_status_in_db,
                args=(client_device_id, "offline"),
                daemon=True
            ).start()


def make_server_socket() -> socket.socket:
    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    raw.bind((BIND_HOST, PORT))
    raw.listen(1)

    if USE_TLS:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(SERVER_CERT, SERVER_KEY)
        ctx.load_verify_locations(CA_CERT)
        ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx.wrap_socket(raw, server_side=True)

    return raw


def accept_connections(server_sock, comms):
    while True:
        try:
            raw_conn, addr = server_sock.accept()
            if USE_TLS:
                conn = comms.ctx.wrap_socket(raw_conn, server_side=True)
            else:
                conn = raw_conn
            print(f"\n[SERVER] Connection accepted from {addr}\n> ", end="", flush=True)
            threading.Thread(target=receive_loop, args=(conn,), daemon=True).start()
        except Exception as e:
            print(f"\n[SERVER] Accept error: {e}\n> ", end="", flush=True)
            time.sleep(1)


def main():
    threading.Thread(target=run_http_server, daemon=True).start()

    # Mark all devices offline in the database at startup
    try:
        backend_url = os.environ.get("BACKEND_API_URL", "http://backend:8000")
        url = f"{backend_url.rstrip('/')}/devices/offline-all"
        req = urllib.request.Request(url, method="POST")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            pass
        print("[SERVER] Marked all devices as offline in DB at startup.")
    except Exception as e:
        print(f"[SERVER] Failed to mark all devices offline at startup: {e}")

    # Start heartbeat check loop thread
    threading.Thread(target=heartbeat_check_loop, daemon=True).start()

    comms = SecureServer(host=BIND_HOST, port=PORT)
    server_sock = comms._create_socket()
    tls_label   = "TLS" if USE_TLS else "plain TCP (dev mode)"
    print(f"[SERVER] Listening on {BIND_HOST}:{PORT} ({tls_label})")
    print(f"[SERVER] Waiting for clients to connect...\n")

    # Start accept loop thread
    threading.Thread(target=accept_connections, args=(server_sock, comms), daemon=True).start()

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
            print(f"\n[STATUS] {pi_statuses}")
            continue
        elif raw == "quit":
            break
        else:
            print("Unknown command.")
            continue

        task = {"kind": "task", "task_id": str(uuid.uuid4())[:8], "code": code, "timeout": 10}
        
        with conn_lock:
            target_conn = next(iter(active_connections.values()), None)

        if target_conn:
            try:
                send_msg(target_conn, task)
                print(f"[SERVER] Task sent (id={task['task_id']})")
            except OSError:
                print("[ERROR] Failed to send message.")
        else:
            print("[ERROR] No clients connected.")

    print("[SERVER] Shutting down.")
    server_sock.close()


if __name__ == "__main__":
    main()
