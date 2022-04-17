from urllib.request import urlopen


def get_ip() -> str:
    return str(urlopen("https://api.ipify.org", timeout=10).read())
