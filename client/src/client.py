from task_exec import *


def main():
    retry_delay = 2

    while True:
        try:
            sock = None     # CHANGE TO SOCKET RECEIVED FROM COMMUNICATION SECTION !!!!!!!!!
            sock.connect((SERVER_HOST, PORT))
            retry_delay = 2

            threads = [
                threading.Thread(target=heartbeat_loop, args=(sock,), daemon=True),
                threading.Thread(target=task_worker,    args=(sock,), daemon=True),
                threading.Thread(target=receive_loop,   args=(sock,), daemon=True),
            ]

            for t in threads:
                t.start()

            threads[2].join()
            sock.close()

        except (ConnectionRefusedError, OSError) as e:
            print(f"[CLIENT] Could not connect: {e}")

        print(f"[CLIENT] Reconnecting in {retry_delay}s...")
        time.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CLIENT] Exiting.")
