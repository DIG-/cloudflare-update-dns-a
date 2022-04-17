from urllib.request import urlopen


def get_ip() -> str:
    return urlopen("https://api.ipify.org", timeout=10).read().decode("utf-8")
