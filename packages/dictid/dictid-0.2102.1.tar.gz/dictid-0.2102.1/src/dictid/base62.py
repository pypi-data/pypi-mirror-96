#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the dictid project.
#  Please respect the license - more about this in the section (*) below.
#
#  dictid is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  dictid is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with dictid.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is a crime and is unethical regarding the effort and
#  time spent here.
#  Relevant employers or funding agencies will be notified accordingly.

# Initially based on https://stackoverflow.com/a/14259141/9681577

alphabet = tuple("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
rev_alphabet = dict((c, v) for v, c in enumerate(alphabet))


def b62dec(string):
    """
    >>> b62dec("AA") == 10*62 + 10
    True

    Parameters
    ----------
    string

    Returns
    -------

    """
    num = 0
    for char in string:
        num = num * 62 + rev_alphabet[char]
    return num


def b62enc(num):
    encoding = ""
    while num:
        num, rem = divmod(num, 62)
        encoding = alphabet[rem] + encoding
    return encoding
