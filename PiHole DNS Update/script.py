import requests
import json
import yaml
import time
import socket
from bs4 import BeautifulSoup


def get_pi_session(passwd, ip, session):
    r = session.post(f"http://{ip}/admin/index.php?login", data={"pw": f"{passwd}"})


def get_pi_token(ip, session):
    r = session.get(f"http://{ip}/admin/index.php")
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.find(id="token").get_text()


def get_records(ip, session, token):
    r = session.post(
        f"http://{ip}/admin/scripts/pi-hole/php/customdns.php",
        data={"action": "get", "token": f"{token}"},
    )
    return json.loads(r.text)


def compare_records(
    pi_records,
    scan_records,
):
    pi_record_one = pi_records[1][1]
    pi_record_two = pi_records[2][1]
    scan_record_one = scan_records[1]
    scan_record_two = scan_records[2]

    return pi_record_one == scan_record_one and pi_record_two == scan_record_two


def update_records(ip, session, token, pi_records, scan_records):
    success_count = 0
    for i in range(len(scan_records)):
        r = session.post(
            f"http://{ip}/admin/scripts/pi-hole/php/customdns.php",
            data={
                "action": "delete",
                "domain": f"{pi_records[i+1][0]}",
                "ip": f"{pi_records[i+1][1]}",
                "token": token,
            },
        )
        if '{"success"' in r.text:
            success_count += 1
    for i in range(len(scan_records)):
        r = session.post(
            f"http://{ip}/admin/scripts/pi-hole/php/customdns.php",
            data={
                "action": "add",
                "domain": f"{pi_records[i+1][0]}",
                "ip": f"{scan_records[i]}",
                "token": token,
            },
        )
        if '{"success"' in r.text:
            success_count += 1
    if success_count < len(scan_records) * 2:
        return f"[-] Some requests failed"
    else:
        return f"[+] All requests were successful"


def scan_ips(port):
    scan_ips = ["192.168.1.231", "192.168.1.232", "192.168.1.233"]

    socket.setdefaulttimeout(1)
    for x in scan_ips:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((x, port))
        sock.close()
        if result == 0:
            return x


def main():
    while True:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)

        passwd = config["PASSWD"]
        port_one = config["P1"]
        port_two = config["P2"]
        ip = config["IP"]

        update_ips = []
        update_ips.append(scan_ips(port_one))
        update_ips.append(scan_ips(port_two))

        session = requests.Session()
        get_pi_session(passwd, ip, session)
        token = get_pi_token(ip, session)
        records_array = get_records(ip, session, token)
        records_array = records_array["data"]
        print(update_records(ip, session, token, records_array, update_ips))
        print("[+] Records are now: \n\n{}".format(get_records(ip, session, token)))
        print("[+] Program will continue again in 5 minutes")
        time.sleep(300)


if __name__ == "__main__":
    main()
