import socket
import struct
import time
import random

def ping_host(host, timeout=2, count=4):
    """
    Ping a host without privileged access, using built-in modules only.
    This method constructs ICMP packets and sends them via a socket that doesn't require root/admin.
    """
    # Resolve host to IP
    try:
        dest_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print(f"Error: Could not resolve hostname {host}")
        return

    # Create a socket — SOCK_DGRAM with IPPROTO_ICMP works without privileges on many OS
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
        sock.settimeout(timeout)
    except Exception as e:
        print(f"Socket error: {e}")
        print("Note: This method works on most systems; some OS may still restrict it.")
        return

    # ICMP echo request packet structure
    def create_icmp_packet(identifier, sequence):
        # ICMP type (8=echo request), code (0), checksum, identifier, sequence
        icmp_type = 8
        icmp_code = 0
        icmp_checksum = 0
        # Create a dummy header to calculate checksum
        header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, identifier, sequence)
        # Payload: arbitrary data
        payload = b'abcdefghijklmnopqrstuvwxyz1234567890'
        # Calculate checksum
        def calculate_checksum(data):
            if len(data) % 2:
                data += b'\x00'
            checksum = 0
            for i in range(0, len(data), 2):
                word = (data[i] << 8) + data[i+1]
                checksum += word
                checksum = (checksum & 0xFFFF) + (checksum >> 16)
            return ~checksum & 0xFFFF
        icmp_checksum = calculate_checksum(header + payload)
        # Rebuild header with correct checksum
        header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, identifier, sequence)
        return header + payload

    # Send packets and measure response
    identifier = random.randint(0, 0xFFFF)
    received = 0
    total_time = 0.0

    for seq in range(count):
        packet = create_icmp_packet(identifier, seq)
        send_time = time.time()
        try:
            sock.sendto(packet, (dest_ip, 0))  # Port 0 is irrelevant for ICMP
            # Wait for reply
            data, addr = sock.recvfrom(1024)
            recv_time = time.time()
            # Verify it's an echo reply
            icmp_type_received = data[20]  # IP header is 20 bytes, ICMP type is first byte
            if icmp_type_received == 0:  # 0 = echo reply
                rtt = (recv_time - send_time) * 1000
                print(f"Reply from {addr[0]}: seq={seq} time={rtt:.2f}ms")
                received += 1
                total_time += rtt
        except socket.timeout:
            print(f"Request timed out: seq={seq}")

    # Summary
    print(f"\nPing statistics for {host} ({dest_ip}):")
    print(f"  Packets: Sent = {count}, Received = {received}, Lost = {count - received} "
          f"({((count - received)/count)*100:.1f}% loss)")
    if received > 0:
        print(f"  Approximate round trip time: Average = {total_time/received:.2f}ms")

    sock.close()

if __name__ == "__main__":
    # Example usage
    target_host = "google.com"  # Change to your target
    ping_host(target_host)
