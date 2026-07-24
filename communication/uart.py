import serial
import threading
import queue
import time


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
        self.raw_queue = queue.Queue()
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
                    raw = self.ser.read(self.ser.in_waiting)

                    if raw:
                        # Store ONLY raw bytes
                        self.raw_queue.put(raw)

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

    def get_raw_data(self):
        if not self.raw_queue.empty():
            return self.raw_queue.get()
        return None

    def probe_port(self, port=None, baudrate=None, probe_time=0.8):
        if port is None:
            port = self.port
        if baudrate is None:
            baudrate = self.baudrate

        try:
            with serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=0.2,
            ) as ser:
                start = time.time()
                while time.time() - start < probe_time:
                    if ser.in_waiting:
                        ser.readline()
                        return True
                return False
        except Exception:
            return False

    def write_line(self, data):
        if not self.connected or self.ser is None:
            return False
        try:
            self.ser.write(data.encode("utf-8"))
            return True
        except Exception as e:
            self.queue.put(f"UART Write Failed : {e}")
            return False

    def write_bytes(self, data: bytes) -> bool:
        """Write raw bytes to the serial port."""
        if not self.connected or self.ser is None:
            return False
        try:
            self.ser.write(data)
            return True
        except Exception as e:
            self.queue.put(f"UART Write Failed : {e}")
            return False

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
