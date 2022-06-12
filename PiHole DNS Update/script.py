import requests
import json
import yaml
import sys
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


def main():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    passwd = config["PASSWD"]
    ip = config["IP"]
    sys.argv.pop(0)

    session = requests.Session()
    get_pi_session(passwd, ip, session)
    token = get_pi_token(ip, session)
    records_array = get_records(ip, session, token)
    records_array = records_array["data"]
    print(update_records(ip, session, token, records_array, sys.argv))
    print("[+] Records are now: \n\n{}".format(get_records(ip, session, token)))


if __name__ == "__main__":
    main()
