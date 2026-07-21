import serial
import threading
import queue


class SerialReader:
    def __init__(self, port="COM3", baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1 ):
        self.port = port
        self.baudrate = baudrate
        self.bytesize=bytesize,
        self.parity=parity,
        self.stopbits=stopbits,
        self.timeout=timeout
        self.ser = None
        self.queue = queue.Queue()
        self.running = False
        self.connected = False

    def connect(self, port="COM3", baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1):
        if self.connected:
            return True

        if port is None:
            port = self.port
        if baudrate is None:
            baudrate = self.baudrate

        try:
            self.ser = serial.Serial(port, baudrate,bytesize, parity, stopbits, timeout)

            self.running = True
            self.connected = True

            threading.Thread(target=self.read_loop, daemon=True).start()

            self.queue.put(f"Connected to {port}")

            return True

        except Exception as e:
            self.queue.put(f"Connection Failed : {e}")
            return False

    def read_loop(self):
        while self.running:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        self.queue.put(line)
            except Exception as e:
                self.queue.put(f"UART Error : {e}")
                self.disconnect()

    def disconnect(self):
        self.running = False
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.connected = False
        self.ser = None

    def get_data(self):
        if not self.queue.empty():
            return self.queue.get()
        return None

    def stop(self):
        self.running = False
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.connected = False
        self.ser = None
