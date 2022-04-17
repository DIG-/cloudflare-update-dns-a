from sys import exit

from .ip import get_ip as get_real_ip


def main():
    try:
        ip_real = get_real_ip()
    except BaseException as e:
        print("Failed to get current ip")
        print(e)
        exit(1)
    print(ip_real)
