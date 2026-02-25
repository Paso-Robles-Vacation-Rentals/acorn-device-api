from dataclasses import dataclass
from datetime import datetime, timedelta
import subprocess
import time


@dataclass
class Network:
    ssid: str
    signal: int
    security: str


class Wifi:

    def __init__(self):
        self.wifi_iface: str
        self.networks: list[Network] = []
        self.last_scan: datetime = datetime.now()

        out = subprocess.run(["nmcli", "-t", "-f", "DEVICE,TYPE", "dev", "status"], capture_output=True, text=True)
        for line in out.stdout.splitlines():
            dev, dev_type = line.split(":")
            if dev_type == "wifi":
                self.wifi_iface = dev
                break
        if not self.wifi_iface:
            raise RuntimeError("No Wi-Fi interfaces found")

        self.scan()



    @staticmethod
    def status() -> dict:
        args = [
            "nmcli",
            "-t",
            "-f",
            "TYPE,STATE,CONNECTION",
            "dev",
            "status"
        ]
        out = subprocess.run(args, capture_output=True, text=True)
        for line in out.stdout.splitlines():
            dev_type, state, conn = line.split(":")
            if dev_type == "wifi":
                return {
                    "connected": state == "connected",
                    "ssid": conn if conn != "--" else None
                }
        return {
            "connected": False,
            "ssid": None
        }


    def scan(self) -> None:
        args = [
            "sudo",
            "nmcli",
            "dev",
            "wifi",
            "rescan",
            "ifname",
            self.wifi_iface
        ]
        subprocess.run(args)

        time.sleep(2)

        args = [
            "nmcli",
            "-g",
            "SSID,SIGNAL,SECURITY",
            "dev",
            "wifi",
            "list",
            "ifname",
            self.wifi_iface,
            "--rescan",
            "yes"
        ]
        out = subprocess.run(args, capture_output=True, text=True)

        self.last_scan = datetime.now()
        self.networks = []

        for line in out.stdout.splitlines():
            if not line.strip():
                continue

            ssid, signal, security = line.split(":", 2)

            self.networks.append(Network(
                ssid=ssid,
                signal=int(signal),
                security=security
            ))


    def get_networks(self) -> list[Network]:
        if self.last_scan > datetime.now() + timedelta(minutes=1):
            self.scan()

        filtered_networks = []
        seen_ssids = set()

        for net in self.networks:
            # Skip blank SSIDs
            if not net.ssid or net.ssid == "--":
                continue

            # Skip duplicates using a set
            if net.ssid in seen_ssids:
                continue

            seen_ssids.add(net.ssid)
            filtered_networks.append(net)
        return filtered_networks

    @staticmethod
    def connect(ssid, password=None) -> tuple[bool, str]:
        """
        Connect to a Wi-Fi network. If psk is None, assume open network.
        """
        args = [
            "sudo",
            "nmcli",
            "dev",
            "wifi",
            "connect",
            ssid
        ]
        if password:
            args += ["password", password]
        out = subprocess.run(args, capture_output=True, text=True)

        if out.returncode == 0:
            return True, ""

        error = (out.stderr or out.stdout).strip().lower()
        if "no network with ssid" in error:
            return False, "Network does not exist"
        elif "secrets were required" in error:
            if password:
                return False, "Incorrect password"
            return False, "Password required"
        elif "incorrect password" in error or "wrong password" in error:
            return False, "Incorrect password"
        elif "property is invalid" in error:
            return False, "Invalid password"
        elif "activation failed" in error:
            return False, "Connection activation failed"
        return False, f"Unknown error: {error}"

