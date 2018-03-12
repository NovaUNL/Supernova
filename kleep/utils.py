from math import log


def password_strength(password: str):
    # > 10 excellent; < 5 awful
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
