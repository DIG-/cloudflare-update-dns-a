from getopt import gnu_getopt
from pprint import pprint
from sys import argv, exit
from typing import Optional

from CloudFlare import CloudFlare

from .ip import get_ip as get_real_ip


def main():
    email: Optional[str] = None
    token: Optional[str] = None
    zone: Optional[str] = None
    dns_a: Optional[str] = None
    try:
        options, extras = gnu_getopt(argv[1:], "e:t:z:", ["email=", "token=", "zone=", "dns-a="])
    except BaseException as e:
        print("Failed to parse options")
        print(e)
        exit(1)

    for option, value in options:
        if option in ("-e", "--email"):
            email = value
        elif option in ("-t", "--token"):
            token = value
        elif option in ("-z", "--zone"):
            zone = value
        elif option == "--dns-a":
            dns_a = value

    if token is None:
        print("Require API Token or API Key")
        exit(2)

    if zone is None:
        print("Require zone")
        exit(2)

    if dns_a is None:
        print("Require dns-a value to update")
        exit(2)

    cf = CloudFlare(email=email, token=token)
    try:
        zones = cf.zones.get(params={"name": zone, "per_page": 1})
    except BaseException as e:
        print("Failed to get zones from CloudFlare")
        print(e)
        exit(3)
    if len(zones) <= 0:
        print("No zone found")
        exit(3)
    zone = zones[0]

    try:
        records = cf.zones.dns_records.get(zone["id"], params={"type": "A", "name": dns_a})
    except BaseException as e:
        print("Failed to get dns records from CloudFlare")
        print(e)
        exit(3)

    if len(records) <= 0:
        print("Records not found")
        exit(3)

    record = records[0]
    record_ip = record["content"]

    try:
        ip_real = get_real_ip()
    except BaseException as e:
        print("Failed to get current ip")
        print(e)
        exit(3)
    if record_ip == ip_real:
        print("IP match, do nothing")
        exit(0)

    print(f"Updating DNS ip to {ip_real}")
    try:
        cf.zones.dns_records.patch(
            zone["id"],
            record["id"],
            data={"content": ip_real},
        )
    except BaseException as e:
        print("Failed to update dns ip")
        print(e)
        exit(3)
    print("Update successfully")
    exit(0)
