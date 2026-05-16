import socket
import time

def ping_host_tcp(host, port=80, timeout=2, count=4):
    """
    Ping a host using TCP stream sockets (SOCK_STREAM).
    No privileged access required; uses only built‑in modules.
    Measures connection time as the "ping" metric.
    """
    # Resolve hostname to IP
    try:
        dest_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print(f"Error: Could not resolve hostname '{host}'")
        return

    received = 0
    total_time = 0.0

    print(f"TCP ping to {host} ({dest_ip}):{port}, timeout={timeout}s\n")

    for seq in range(count):
        # Create TCP stream socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                start_time = time.perf_counter()
                # Attempt to establish connection
                result = sock.connect_ex((dest_ip, port))
                end_time = time.perf_counter()

            if result == 0:  # Connection succeeded
                rtt = (end_time - start_time) * 1000
                print(f"Success: seq={seq} time={rtt:.2f}ms")
                received += 1
                total_time += rtt
            else:
                print(f"Failed: seq={seq} (error code: {result})")

        except socket.timeout:
            print(f"Timeout: seq={seq}")
        except OSError as e:
            print(f"Error seq={seq}: {e}")

    # Summary statistics
    print(f"\nPing statistics for {host} ({dest_ip}):{port}")
    print(f"  Packets: Sent = {count}, Received = {received}, Lost = {count - received} "
          f"({((count - received)/count)*100:.1f}% loss)")
    if received > 0:
        print(f"  Approximate round trip time: Average = {total_time/received:.2f}ms")

if __name__ == "__main__":
    # Example: ping google.com on common web port 80
    ping_host_tcp("google.com", port=80, timeout=2, count=4)
