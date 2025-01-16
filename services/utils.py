import random
import re
import string


def generate_shortname():
    return "".join(random.choices(string.ascii_letters + string.digits, k=4)).lower()


def is_valid_url(url):
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # IPv4
        r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"  # IPv6
        r"(?::\d+)?"  # port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return re.match(regex, url) is not None