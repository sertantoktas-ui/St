"""
OSAI CNC Control Unit Communication Module
Supports both real TCP/IP connection to OSAI unit and simulation mode.

OSAI C07 / C11 / Open7 units expose a TCP socket interface (default port 5050).
Commands follow the OSAI HOST LINK protocol (ASCII framed).
"""

import socket
import threading
import time
import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable


class MachineState(Enum):
    DISCONNECTED = "DISCONNECTED"
    IDLE         = "IDLE"
    RUNNING      = "RUNNING"
    PAUSED       = "PAUSED"
    ALARM        = "ALARM"
    HOMING       = "HOMING"


@dataclass
class AxisData:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class MachineData:
    state:           MachineState = MachineState.DISCONNECTED
    machine_pos:     AxisData     = field(default_factory=AxisData)
    work_pos:        AxisData     = field(default_factory=AxisData)
    feed_rate:       float        = 0.0      # mm/min actual
    spindle_speed:   float        = 0.0      # RPM actual
    feed_override:   int          = 100      # %
    spindle_override:int          = 100      # %
    tool_number:     int          = 1
    program_name:    str          = ""
    program_line:    int          = 0
    program_total:   int          = 0
    load_x:          float        = 0.0      # motor load %
    load_y:          float        = 0.0
    load_z:          float        = 0.0
    load_spindle:    float        = 0.0
    alarms:          list         = field(default_factory=list)
    pieces_today:    int          = 0
    power_kw:        float        = 0.0


# OSAI HOST LINK protocol constants
STX = b'\x02'
ETX = b'\x03'
ACK = b'\x06'
NAK = b'\x15'

OSAI_CMDS = {
    "GET_STATUS":   b"STS",
    "GET_POS":      b"POS",
    "GET_SPINDLE":  b"SPN",
    "GET_FEED":     b"FDR",
    "PROG_START":   b"PST",
    "PROG_STOP":    b"PSP",
    "PROG_PAUSE":   b"PPU",
    "PROG_RESET":   b"PRS",
    "HOMING":       b"HOM",
    "SET_FEED_OVR": b"FOV",
    "SET_SPN_OVR":  b"SOV",
}


class OSAIClient:
    """
    Thread-safe OSAI CNC client.
    Call start() to begin polling; stop() to clean up.
    Register callbacks via on_data_update.
    """

    def __init__(self, host: str = "192.168.1.10", port: int = 5050, simulation: bool = True):
        self.host       = host
        self.port       = port
        self.simulation = simulation
        self.data       = MachineData()
        self._lock      = threading.Lock()
        self._running   = False
        self._thread: Optional[threading.Thread] = None
        self._sock: Optional[socket.socket] = None
        self._callbacks: list[Callable] = []
        self._sim_t     = 0.0   # simulation time counter

    # ── Public API ────────────────────────────────────────────────────────────

    def on_data_update(self, cb: Callable):
        self._callbacks.append(cb)

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        self._close_socket()

    def connect(self):
        if self.simulation:
            with self._lock:
                self.data.state = MachineState.IDLE
            self._notify()
            return True
        return self._open_socket()

    def disconnect(self):
        if self.simulation:
            with self._lock:
                self.data.state = MachineState.DISCONNECTED
            self._notify()
            return
        self._close_socket()
        with self._lock:
            self.data.state = MachineState.DISCONNECTED
        self._notify()

    def program_start(self):
        if self.simulation:
            with self._lock:
                if self.data.state == MachineState.IDLE:
                    self.data.state = MachineState.RUNNING
                    self.data.program_name = "AXTEA_PART_001.NC"
                    self.data.program_total = 1200
            self._notify()
            return
        self._send_command("PROG_START")

    def program_stop(self):
        if self.simulation:
            with self._lock:
                self.data.state = MachineState.IDLE
                self.data.feed_rate = 0
                self.data.spindle_speed = 0
            self._notify()
            return
        self._send_command("PROG_STOP")

    def program_pause(self):
        if self.simulation:
            with self._lock:
                if self.data.state == MachineState.RUNNING:
                    self.data.state = MachineState.PAUSED
                elif self.data.state == MachineState.PAUSED:
                    self.data.state = MachineState.RUNNING
            self._notify()
            return
        self._send_command("PROG_PAUSE")

    def program_reset(self):
        if self.simulation:
            with self._lock:
                self.data.state = MachineState.IDLE
                self.data.program_line = 0
                self.data.feed_rate = 0
                self.data.spindle_speed = 0
            self._notify()
            return
        self._send_command("PROG_RESET")

    def homing(self):
        if self.simulation:
            with self._lock:
                self.data.state = MachineState.HOMING
            self._notify()
            return
        self._send_command("HOMING")

    def set_feed_override(self, value: int):
        value = max(0, min(200, value))
        with self._lock:
            self.data.feed_override = value
        if not self.simulation:
            self._send_command("SET_FEED_OVR", str(value).encode())

    def set_spindle_override(self, value: int):
        value = max(0, min(200, value))
        with self._lock:
            self.data.spindle_override = value
        if not self.simulation:
            self._send_command("SET_SPN_OVR", str(value).encode())

    def get_data(self) -> MachineData:
        with self._lock:
            return MachineData(**{
                k: (v.copy() if isinstance(v, list) else v)
                for k, v in self.data.__dict__.items()
                if k not in ("machine_pos", "work_pos")
            } | {
                "machine_pos": AxisData(self.data.machine_pos.x, self.data.machine_pos.y, self.data.machine_pos.z),
                "work_pos":    AxisData(self.data.work_pos.x, self.data.work_pos.y, self.data.work_pos.z),
            })

    # ── Internal loop ─────────────────────────────────────────────────────────

    def _loop(self):
        while self._running:
            if self.simulation:
                self._sim_step()
            else:
                self._poll_real()
            self._notify()
            time.sleep(0.2)

    def _sim_step(self):
        self._sim_t += 0.2
        t = self._sim_t
        with self._lock:
            st = self.data.state
            if st == MachineState.RUNNING:
                ovr = self.data.feed_override / 100.0
                sovr = self.data.spindle_override / 100.0
                self.data.machine_pos.x = 150 + 130 * math.sin(t * 0.15)
                self.data.machine_pos.y = -42  + 30  * math.cos(t * 0.12)
                self.data.machine_pos.z = -10  - 8   * abs(math.sin(t * 0.25))
                self.data.work_pos.x    = self.data.machine_pos.x - 50
                self.data.work_pos.y    = self.data.machine_pos.y + 5
                self.data.work_pos.z    = self.data.machine_pos.z + 2
                self.data.feed_rate     = round(8000 * ovr  + random.uniform(-50, 50), 1)
                self.data.spindle_speed = round(18000 * sovr + random.uniform(-20, 20), 0)
                self.data.load_x        = min(100, abs(30 + 15 * math.sin(t * 0.3) + random.uniform(-3, 3)))
                self.data.load_y        = min(100, abs(25 + 12 * math.cos(t * 0.25)))
                self.data.load_z        = min(100, abs(20 + 10 * math.sin(t * 0.4)))
                self.data.load_spindle  = min(100, abs(55 + 20 * math.sin(t * 0.1) + random.uniform(-5, 5)))
                self.data.power_kw      = round(3.5 + 1.2 * math.sin(t * 0.1) + random.uniform(-0.1, 0.1), 2)
                self.data.program_line  = min(self.data.program_total, self.data.program_line + random.randint(1, 4))
                if self.data.program_line >= self.data.program_total:
                    self.data.state = MachineState.IDLE
                    self.data.pieces_today += 1
                    self.data.program_line = 0
            elif st == MachineState.HOMING:
                self.data.machine_pos.x = max(0, self.data.machine_pos.x - 8)
                self.data.machine_pos.y = max(0, self.data.machine_pos.y + 2)
                self.data.machine_pos.z = max(0, self.data.machine_pos.z + 5)
                if (abs(self.data.machine_pos.x) < 1 and abs(self.data.machine_pos.y) < 1
                        and abs(self.data.machine_pos.z) < 1):
                    self.data.state = MachineState.IDLE
            elif st in (MachineState.IDLE, MachineState.PAUSED):
                self.data.feed_rate     = 0
                self.data.spindle_speed = 0
                self.data.power_kw      = round(0.8 + random.uniform(-0.05, 0.05), 2)

    # ── Real OSAI comms (skeleton – fill in per your unit firmware) ───────────

    def _open_socket(self) -> bool:
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(3.0)
            self._sock.connect((self.host, self.port))
            with self._lock:
                self.data.state = MachineState.IDLE
            return True
        except OSError:
            self._sock = None
            return False

    def _close_socket(self):
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def _send_command(self, cmd_key: str, payload: bytes = b"") -> Optional[bytes]:
        if not self._sock:
            return None
        raw = OSAI_CMDS.get(cmd_key, b"")
        frame = STX + raw + (b"," + payload if payload else b"") + ETX
        try:
            self._sock.sendall(frame)
            resp = self._sock.recv(256)
            return resp
        except OSError:
            return None

    def _poll_real(self):
        """Poll the real OSAI unit and update self.data."""
        resp = self._send_command("GET_STATUS")
        if resp is None:
            with self._lock:
                self.data.state = MachineState.DISCONNECTED
            return
        # Parse OSAI response frames here according to your unit's protocol version

    def _notify(self):
        snapshot = self.get_data()
        for cb in self._callbacks:
            try:
                cb(snapshot)
            except Exception:
                pass
