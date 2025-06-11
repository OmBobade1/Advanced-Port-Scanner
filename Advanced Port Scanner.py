import tkinter as tk
from tkinter import messagebox, scrolledtext
import socket
import threading
import time

class PortScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Port Scanner")
        self.root.geometry("500x480")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # IP Input
        self.ip_label = tk.Label(root, text="Target IP Address:", bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 10))
        self.ip_label.pack(pady=(15, 0))
        self.ip_entry = tk.Entry(root, width=40, font=("Segoe UI", 10))
        self.ip_entry.pack(pady=5)

        # Port Range Input
        self.port_label = tk.Label(root, text="Port Range (e.g., 20-100):", bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 10))
        self.port_label.pack(pady=(10, 0))
        self.port_entry = tk.Entry(root, width=40, font=("Segoe UI", 10))
        self.port_entry.insert(0, "1-1024")
        self.port_entry.pack(pady=5)

        # Scan Button
        self.scan_btn = tk.Button(root, text="Start Scan", command=self.start_scan_thread, bg="#89b4fa", fg="black", font=("Segoe UI", 10, "bold"))
        self.scan_btn.pack(pady=10)

        # Output Area
        self.output = scrolledtext.ScrolledText(root, height=12, width=58, font=("Courier", 10))
        self.output.pack(pady=10)

        # Estimated Time Left Label (only this one!)
        self.estimate_label = tk.Label(root, text="⏳ Estimated Time Left: ...", bg="#1e1e2e", fg="#a6e3a1", font=("Segoe UI", 10, "bold"))
        self.estimate_label.pack(pady=(0, 10))

        # Timer variables
        self.start_time = None
        self.running = False
        self.total_ports = 0
        self.time_per_port = 0.3  # Adjust as needed

    def start_scan_thread(self):
        thread = threading.Thread(target=self.scan_ports)
        thread.daemon = True
        thread.start()
        self.start_timer()

    def start_timer(self):
        self.start_time = time.time()
        self.running = True
        self.update_estimate()

    def update_estimate(self):
        if self.running:
            elapsed = time.time() - self.start_time
            estimated_total = self.total_ports * self.time_per_port
            time_left = max(0, estimated_total - elapsed)
            self.estimate_label.config(text=f"⏳ Estimated Time Left: {time_left:.2f}s")
            self.root.after(100, self.update_estimate)

    def stop_timer(self):
        self.running = False
        self.estimate_label.config(text="⏳ Estimated Time Left: 0.00s")

    def scan_ports(self):
        self.output.delete("1.0", tk.END)
        target_ip = self.ip_entry.get().strip()
        port_range = self.port_entry.get().strip()

        try:
            socket.inet_aton(target_ip)
        except socket.error:
            messagebox.showerror("Invalid IP", "Please enter a valid IP address.")
            self.stop_timer()
            return

        try:
            start_port, end_port = map(int, port_range.split('-'))
            self.total_ports = end_port - start_port + 1
        except:
            messagebox.showerror("Invalid Port Range", "Please enter a valid port range (e.g., 1-1000).")
            self.stop_timer()
            return

        self.output.insert(tk.END, f"Scanning {target_ip} from port {start_port} to {end_port}...\n\n")
        open_ports = []

        for port in range(start_port, end_port + 1):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                result = s.connect_ex((target_ip, port))
                if result == 0:
                    open_ports.append(port)
                    self.output.insert(tk.END, f"[OPEN] Port {port}\n")
                s.close()
            except Exception as e:
                self.output.insert(tk.END, f"[ERROR] Port {port}: {str(e)}\n")

        if not open_ports:
            self.output.insert(tk.END, "\nNo open ports found.")
        else:
            self.output.insert(tk.END, f"\nFound {len(open_ports)} open port(s).")

        self.stop_timer()

# Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerApp(root)
    root.mainloop()
