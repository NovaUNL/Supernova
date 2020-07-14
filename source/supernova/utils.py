from difflib import SequenceMatcher
from math import log


def password_strength(password: str):
    """
    | Checks for variety and strong elements in a password and gives a strength index.
    | The index can be read as: > 10 excellent; < 5 awful

    :param password: The password to evaluate
    :return: password strength value.
    """
    uppercase = 0
    lowercase = 0
    number = 0
    special = 0
    for char in password:
        if char.isupper():
            uppercase += 1
        elif char.islower():
            lowercase += 1
        elif char.isdigit():
            number += 1
        else:
            special += 1
    # The logarithms are there to award variety. A single group is *BAD*
    return int(log(uppercase + 1) + uppercase * 0.5
               # Lowercase has the same keyspace as uppercase, but they are more common
               + log(lowercase + 1) + lowercase * 0.4
               # There are fewer numbers than letters, they are not as secure, but they are rarer
               + log(number + 1) + number * 0.2
               # Specials are great, but a special only password would be silly
               + log(special + 1) * 2 + special * 0.5)


def correlated(a: str, b: str, threshold=0.5):
    """
    Checks if two strings are above a correlation threshold
    :param a: First string
    :param b: Second string
    :param threshold: Minimum correlation
    :return: Related
    """
    return SequenceMatcher(a, b).ratio() > threshold


def correlation(a: str, b: str):  # TODO redundant, merge with above
    """
    Checks two strings correlation
    :param a: First string
    :param b: Second string
    :return: Correlation ratio
    """
    return SequenceMatcher(a, b).ratio()
