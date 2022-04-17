from getopt import gnu_getopt
from sys import argv, exit
from typing import Optional

from .ip import get_ip as get_real_ip


def main():
    email: Optional[str] = None
    token: Optional[str] = None
    dns_a: Optional[str] = None
    try:
        options, extras = gnu_getopt(argv[1:], "e:t:", ["email=", "token=", "dns-a="])
    except BaseException as e:
        print("Failed to parse options")
        print(e)
        exit(1)

    for option, value in options:
        if option in ("-e", "--email"):
            email = value
        elif option in ("-t", "--token"):
            token = value
        elif option == "--dns-a":
            dns_a = value

    if token is None:
        print("Require API Token or API Key")
        exit(2)

    try:
        ip_real = get_real_ip()
    except BaseException as e:
        print("Failed to get current ip")
        print(e)
        exit(3)
    print(ip_real)
