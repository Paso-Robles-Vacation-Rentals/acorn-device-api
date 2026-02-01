import subprocess

def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()

def status():
    out = run("wpa_cli -i wlp1s0 status")
    data = {}

    for line in out.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            data[k] = v

    return {
        "connected": data.get("wpa_state") == "COMPLETED",
        "ssid": data.get("ssid"),
        "ip": data.get("ip_address"),
        "state": data.get("wpa_state"),
    }

def scan():
    run("wpa_cli -i wlp1s0 scan")
    raw = run("wpa_cli -i wlp1s0 scan_results")

    nets = []
    lines = raw.splitlines()[1:]

    for l in lines:
        bssid, freq, signal, flags, ssid = l.split("\t")
        nets.append({
            "ssid": ssid,
            "signal": int(signal),
            "security": flags,
        })

    return nets

def connect(ssid, psk=None):
    net_id = run("wpa_cli -i wlp1s0 add_network")

    run(f"wpa_cli -i wlp1s0 set_network {net_id} ssid '\"{ssid}\"'")

    if psk:
        run(f"wpa_cli -i wlp1s0 set_network {net_id} psk '\"{psk}\"'")
    else:
        run(f"wpa_cli -i wlp1s0 set_network {net_id} key_mgmt NONE")

    run(f"wpa_cli -i wlp1s0 enable_network {net_id}")
    run("wpa_cli -i wlp1s0 save_config")

    return {"success": True}
