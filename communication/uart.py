import serial
import threading
import queue


class SerialReader:
    def __init__(self, port="COM3", baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.ser = None
        self.queue = queue.Queue()
        self.running = False
        self.connected = False

    def connect(self, port=None, baudrate=None, bytesize=None, parity=None, stopbits=None, timeout=None):
        if self.connected:
            return True

        if port is None:
            port = self.port
        if baudrate is None:
            baudrate = self.baudrate
        if bytesize is None:
            bytesize = self.bytesize
        if parity is None:
            parity = self.parity
        if stopbits is None:
            stopbits = self.stopbits
        if timeout is None:
            timeout = self.timeout
        if self.connected:
            return True

        if port is None:
            port = self.port
        if baudrate is None:
            baudrate = self.baudrate

        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout,
            )
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

    def is_connected(self):
        return self.connected

    def stop(self):
        self.running = False
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.connected = False
        self.ser = None
