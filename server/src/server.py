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

pi_status  = {"state": "unknown"}
connection = None
conn_lock  = threading.Lock()

from http.server import BaseHTTPRequestHandler, HTTPServer

class TaskHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_POST(self):
        global connection
        if self.path == "/task":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                task_id = data.get("task_id")
                code = data.get("code")
                
                with conn_lock:
                    if connection is not None:
                        send_msg(connection, {
                            "kind": "task",
                            "task_id": str(task_id),
                            "code": code
                        })
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"status": "success"}).encode())
                        print(f"\n[HTTP] Forwarded task {task_id} to client.\n> ", end="", flush=True)
                    else:
                        self.send_response(503)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "No client connected"}).encode())
                        print(f"\n[HTTP] Failed to forward task {task_id}: No client connected.\n> ", end="", flush=True)
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
                if dev.get("name") == device_name:
                    return int(dev.get("device_id"))
    except Exception as e:
        print(f"[SERVER] Error fetching device ID for name '{device_name}': {e}")
    return 1


def save_task_result_to_db(task_id, msg):
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
        device_name = pi_status.get("device_id")
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


def save_response_to_db(task_id, msg):
    try:
        # Format the response from client stdout and stderr
        stdout = msg.get("stdout", "").strip()
        stderr = msg.get("stderr", "").strip()
        
        response_text = stdout
        if stderr:
            if response_text:
                response_text += f"\nError: {stderr}"
            else:
                response_text = f"Error: {stderr}"
                
        if not response_text:
            response_text = f"Exit code: {msg.get('exit_code', 0)}"

        # Default backend URL is http://backend:8000
        backend_url = os.environ.get("BACKEND_API_URL", "http://backend:8000")
        url = f"{backend_url.rstrip('/')}/tables/communication_responses"
        
        payload = {
            "task_id": str(task_id),
            "response": response_text,
            "timestamp": datetime.now().isoformat()
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
        print(f"\n[SERVER] Successfully saved response for task {task_id} to database.\n> ", end="", flush=True)
    except Exception as e:
        print(f"\n[SERVER] Failed to save response to database: {e}\n> ", end="", flush=True)


def receive_loop(sock):
    global pi_status
    print("[SERVER] Receive loop started")

    while True:
        try:
            msg = recv_msg(sock)
            if msg is None:
                print("\n[SERVER] Client disconnected.")
                break

            kind = msg.get("kind")

            if kind == "status":
                pi_status = msg
                print(f"\r[PI] state={msg.get('state')} | "
                      f"cpu={msg.get('cpu')}% | "
                      f"mem={msg.get('mem')}%        ",
                      end="", flush=True)

            elif kind == "result":
                task_id = msg.get('task_id')
                print(f"\n\n{'='*50}")
                print(f"[RESULT] task_id : {task_id}")
                print(f"         exit    : {msg.get('exit_code')}")
                print(f"         stdout  :\n{msg.get('stdout', '').strip()}")
                if msg.get("stderr"):
                    print(f"         stderr  :\n{msg.get('stderr').strip()}")
                print(f"{'='*50}\n> ", end="", flush=True)

                # Save the response in the database in a background thread
                threading.Thread(target=save_response_to_db, args=(task_id, msg), daemon=True).start()
                threading.Thread(target=save_task_result_to_db, args=(task_id, msg), daemon=True).start()


        except (UnicodeDecodeError, json.JSONDecodeError):
            print("\n[SERVER] Received non-protocol data (transport mismatch or malformed frame).")
            break
        except (ConnectionResetError, BrokenPipeError, OSError):
            print("\n[SERVER] Connection lost.")
            break


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


def main():
    global connection
    threading.Thread(target=run_http_server, daemon=True).start()

    comms = SecureServer(host=BIND_HOST, port=PORT)
    server_sock = comms._create_socket()
    tls_label   = "TLS" if USE_TLS else "plain TCP (dev mode)"
    print(f"[SERVER] Listening on {BIND_HOST}:{PORT} ({tls_label})")
    print(f"[SERVER] Waiting for Pi to connect...\n")

    raw_conn, addr = server_sock.accept()
    if USE_TLS:
        conn = comms.ctx.wrap_socket(raw_conn, server_side=True)
    else:
        conn = raw_conn

    connection = conn
    print(f"[SERVER] Pi connected from {addr}\n")

    threading.Thread(target=receive_loop, args=(conn,), daemon=True).start()

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
            print(f"\n[STATUS] {pi_status}")
            continue
        elif raw == "quit":
            break
        else:
            print("Unknown command.")
            continue

        task = {"kind": "task", "task_id": str(uuid.uuid4())[:8], "code": code, "timeout": 10}
        try:
            send_msg(connection, task)
            print(f"[SERVER] Task sent (id={task['task_id']})")
        except OSError:
            print("[ERROR] Not connected.")

    print("[SERVER] Shutting down.")
    conn.close()
    server_sock.close()


if __name__ == "__main__":
    main()
