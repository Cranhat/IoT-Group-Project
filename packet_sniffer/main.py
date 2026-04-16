import logging
import time
import signal
import sys
import os
from scapy.all import sniff, IP, TCP, Raw

MONITORED_PORT = int(os.getenv("MONITORED_PORT"))
SNIFFER_TIMEOUT = int(os.getenv("SNIFFER_TIMEOUT"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    logger.info("Signal received - stopping sniffer...")
    sys.exit(0)


def check_permissions():
    if os.geteuid() != 0:
        logger.warning("Root privileges missing - packet sniffer may not function correctly")
        logger.warning("Run with sudo or ensure CAP_NET_RAW is set")
        return False
    return True


def process_packet(packet):
    try:
        if packet.haslayer(TCP) and packet.haslayer(IP):
            ip_src = packet[IP].src
            ip_dst = packet[IP].dst
            sport = packet[TCP].sport
            dport = packet[TCP].dport

            if sport == MONITORED_PORT or dport == MONITORED_PORT:
                if packet.haslayer(Raw):
                    raw_data = packet[Raw].load

                    try:
                        decoded_data = raw_data.decode('utf-8', errors='ignore')

                        if decoded_data.strip():
                            logger.info(f"CAPTURED: [{ip_src}:{sport} -> {ip_dst}:{dport}]")

                            lines = decoded_data.split('\n')
                            for line in lines[:5]:
                                logger.info(f"   {line.strip()}")
                            logger.info("-" * 40)

                    except Exception as e:
                        logger.warning(f"UTF-8 decoding error: {e}")
                        logger.info(f"CAPTURED (Binary): [{ip_src}:{sport} -> {ip_dst}:{dport}]")
                        logger.info(f"   {raw_data[:50]}...")
                        logger.info("-" * 40)
    except Exception as e:
        logger.error(f"Packet processing error: {e}", exc_info=True)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("-" * 50)
    print("IoT Packet Sniffer")
    print(f"Monitoring Port: {MONITORED_PORT}")
    print(f"Timeout: {'infinite' if SNIFFER_TIMEOUT == 0 else f'{SNIFFER_TIMEOUT}s'}")
    print("-" * 50)

    if not check_permissions():
        logger.warning("Continuing despite missing full privileges...")

    logger.info("Waiting 2 seconds for backend to initialize...")
    time.sleep(2)

    try:
        logger.info(f"Started listening on port {MONITORED_PORT}...")
        sniff(
            prn=process_packet,
            store=False,
            filter=f"tcp port {MONITORED_PORT}",
            timeout=SNIFFER_TIMEOUT if SNIFFER_TIMEOUT > 0 else None
        )
        logger.info("Sniffer stopped normally")
    except PermissionError:
        logger.error("Error: Access denied to network interface")
        logger.error("Try running with sudo or set CAP_NET_RAW")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during sniffing: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()