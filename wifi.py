import subprocess

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


def status(iface:str|None=None) -> dict:
    if not iface:
        iface = get_wifi_iface()
    out = run(f"nmcli -t -f DEVICE,STATE,CONNECTION,IP4.ADDRESS dev status")
    for line in out.splitlines():
        dev, state, conn, ip = line.split(":")
        if dev == iface:
            return {
                "connected": state == "connected",
                "ssid": conn if conn != "--" else None,
                "ip": ip if ip != "--" else None,
                "state": state,
            }
    return {
        "connected": False,
        "ssid": None,
        "ip": None,
        "state": "unknown",
    }


def scan(iface:str=None) -> list[dict]:
    if not iface:
        iface = get_wifi_iface()
    run(f"nmcli dev wifi rescan ifname {iface}")
    raw = run(
        f"nmcli -f SSID,SIGNAL,SECURITY dev wifi list ifname {iface} --rescan yes --terse --fields SSID,SIGNAL,SECURITY")

    nets = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        ssid, signal, security = line.split(":")
        nets.append({
            "ssid": ssid,
            "signal": int(signal),
            "security": security,
        })
    return nets

def connect(ssid, psk=None, iface="wlp1s0") -> bool:
    """
    Connect to a Wi-Fi network. If psk is None, assume open network.
    """
    try:
        if psk:
            run(f'nmcli dev wifi connect "{ssid}" password "{psk}" ifname {iface}')
        else:
            run(f'nmcli dev wifi connect "{ssid}" ifname {iface}')
        return True
    except subprocess.CalledProcessError:
        return False
