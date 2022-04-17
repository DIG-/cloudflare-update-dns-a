from getopt import gnu_getopt
from logging import basicConfig as loggingBasicConfig, getLogger
from pprint import pprint
from sys import argv, exit
from typing import Optional

from CloudFlare import CloudFlare

from .ip import get_ip as get_real_ip
from .result import Result


loggingBasicConfig(format="%(asctime)s %(levelname)7s  %(message)s")
log = getLogger()
log.setLevel("INFO")


def main():
    email: Optional[str] = None
    token: Optional[str] = None
    zone: Optional[str] = None
    dns_a: Optional[str] = None
    log.info("Starting")
    try:
        log.debug("Parse options")
        options, extras = gnu_getopt(argv[1:], "e:t:z:", ["email=", "token=", "zone=", "dns-a="])
    except BaseException as e:
        log.error("Failed to parse options", exc_info=e)
        exit(Result.FATAL)

    log.debug("Decode options")
    for option, value in options:
        if option in ("-e", "--email"):
            email = value
        elif option in ("-t", "--token"):
            token = value
        elif option in ("-z", "--zone"):
            zone = value
        elif option == "--dns-a":
            dns_a = value

    log.debug("Checking token")
    if token is None:
        log.error("Require API Token or API Key")
        exit(Result.FATAL)

    log.debug("Checking Zone")
    if zone is None:
        log.error("Require zone")
        exit(Result.FATAL)

    log.debug("Checking DNS-A")
    if dns_a is None:
        log.error("Require dns-a value to update")
        exit(Result.FATAL)

    cf = CloudFlare(email=email, token=token)
    try:
        log.debug("Getting CloudFlare Zones")
        zones = cf.zones.get(params={"name": zone, "per_page": 1})
    except BaseException as e:
        log.error("Failed to get zones from CloudFlare", exc_info=e)
        exit(Result.RETRY)
    if len(zones) <= 0:
        log.error("No zone found")
        exit(Result.FATAL)
    zone = zones[0]

    try:
        log.debug("Getting CloudFlare Records for choosen Zone")
        records = cf.zones.dns_records.get(zone["id"], params={"type": "A", "name": dns_a})
    except BaseException as e:
        log.error("Failed to get dns records from CloudFlare", exc_info=e)
        exit(Result.RETRY)

    if len(records) <= 0:
        log.error("Records not found")
        exit(Result.FATAL)

    record = records[0]
    record_ip = record["content"]

    try:
        log.debug("Getting IP from ipify")
        ip_real = get_real_ip()
    except BaseException as e:
        log.error("Failed to get current IP", exc_info=e)
        exit(Result.RETRY)
    log.debug("Compare current IP with CloudFlare IP")
    if record_ip == ip_real:
        log.info("IP match, do nothing")
        exit(Result.SUCESS)

    log.info(f"Updating DNS ip to {ip_real}")
    try:
        cf.zones.dns_records.patch(
            zone["id"],
            record["id"],
            data={"content": ip_real},
        )
    except BaseException as e:
        log.error("Failed to update dns ip", exc_info=e)
        exit(Result.FATAL)
    log.info("Update successfully")
    exit(Result.RETRY)
