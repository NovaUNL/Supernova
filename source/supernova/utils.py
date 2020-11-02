from difflib import SequenceMatcher
import diff_match_patch as dmp_module
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


def correlation(a: str, b: str):
    """
    Checks two strings correlation
    :param a: First string
    :param b: Second string
    :return: Correlation ratio
    """
    return SequenceMatcher(None, a, b).ratio()


class _diff_match_patch(dmp_module.diff_match_patch):

    def diff_prettyHtml(self, diffs):
        """Convert a diff array into a pretty HTML report.

        Args:
          diffs: Array of diff tuples.

        Returns:
          HTML representation.
        """
        html = []
        for (op, data) in diffs:
            text = (
                data.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "&para;<br>")
            )
            if op == self.DIFF_INSERT:
                html.append('<span class="insert">%s</span>' % text)
            elif op == self.DIFF_DELETE:
                html.append('<span class="delete">%s</span>' % text)
            elif op == self.DIFF_EQUAL:
                html.append("<span>%s</span>" % text)
        return "".join(html)


def comparison_html(a, b):
    dmp = _diff_match_patch()
    diff = dmp.diff_main(a, b)
    dmp.diff_cleanupSemantic(diff)
    return dmp.diff_prettyHtml(diff)
