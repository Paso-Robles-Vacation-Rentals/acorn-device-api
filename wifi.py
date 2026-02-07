import subprocess
import time


def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def get_wifi_iface():
    """
    Return the first Wi-Fi interface detected by NetworkManager.
    """
    out = run("nmcli -t -f DEVICE,TYPE dev status")
    for line in out.splitlines():
        dev, dev_type = line.split(":")
        if dev_type == "wifi":
            return dev
    raise RuntimeError("No Wi-Fi interfaces found")


def status() -> dict:
    out = run(f"nmcli -t -f TYPE,STATE,CONNECTION dev status")
    for line in out.splitlines():
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


def scan(iface:str=None) -> list[dict]:
    if not iface:
        iface = get_wifi_iface()
    run(f"sudo nmcli dev wifi rescan ifname {iface}")

    time.sleep(1.5)

    raw = run(
        f"nmcli -g SSID,SIGNAL,SECURITY dev wifi list ifname {iface} --rescan yes")

    nets = []
    seen_ssids = set()

    for line in raw.splitlines():
        if not line.strip():
            continue

        ssid, signal, security = line.split(":", 2)

        # Skip blank SSIDs
        if not ssid or ssid == "--":
            continue

        # Skip duplicates using a set
        if ssid in seen_ssids:
            continue

        seen_ssids.add(ssid)
        nets.append({
            "ssid": ssid,
            "signal": int(signal),
            "security": security,
        })
    return nets


def connect(ssid, password=None) -> bool:
    """
    Connect to a Wi-Fi network. If psk is None, assume open network.
    """
    scan()
    try:
        if not password:
            run(f'sudo nmcli dev wifi connect "{ssid}" password "{password}"')
        else:
            run(f'sudo nmcli dev wifi connect "{ssid}"')
        return True
    except subprocess.CalledProcessError as e:
        return False