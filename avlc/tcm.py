"""
Module Information
------------------
**Time Converter Module v1.3 (24/Feb/2021)**
\n**Author:** Kevin Putra Satrianto github.com/negated-py
\nOriginal Revision: 19/Jan/2021

Module Description
------------------
This module is for time conversion between
Milliseconds, Seconds, Minutes and Hours
"""


def ms2min(int_milliseconds: int):  # convert ms (int) to mm:ss (str)
    """
    Milliseconds to Minute Converter
    \n=============================

    Parameter: Milliseconds (int)
    \nReturn: MM:SS (str)
    """

    if not type(int_milliseconds).__name__ == 'int':
        raise TypeError("Invalid parameter: " + type(int_milliseconds).__name__ + " \nParameter should be: int")
    else:
        time = str(int((int_milliseconds / 1000) / 60)) + ":" + str(
            '%02d' % int((int_milliseconds / 1000) % 60))
        return time


def ms2hr(int_milliseconds: int):  # convert ms (int) to hh:mm:ss (str)
    """
    Milliseconds to Hour Converter
    \n===========================

    Parameter: Milliseconds (int)
    \nReturn: HH:MM:SS (str)
    """

    if not type(int_milliseconds).__name__ == 'int':
        raise TypeError("Invalid parameter: " + type(int_milliseconds).__name__ + " \nParameter should be: int")
    else:
        time = str(int((int_milliseconds / (1000 * 60 * 60) % 24))) + ":" + str(
            '%02d' % int((int_milliseconds / (1000 * 60)) % 60)) + ":" + str(
            '%02d' % int((int_milliseconds / 1000) % 60))
        return time


def min2ms(int_minutes: int):  # convert minutes (int) to milliseconds (int)
    """
    Minute to Milliseconds Converter
    \n==============================

    Parameter: Minute (int)
    \nReturn: Milliseconds (int)
    """

    if not type(int_minutes).__name__ == 'int':
        raise TypeError("Invalid parameter: " + type(int_minutes).__name__ + " \nParameter should be: int")
    else:
        time = int_minutes * 60000
        return time


def ms2sec(int_ms: int):
    """
    Milliseconds to Seconds Converter
    \n==============================

    Parameter: Milliseconds (int)
    \nReturn: Seconds (float)
    """

    if not type(int_ms).__name__ == 'int' and not type(int_ms).__name__ == 'float':
        raise TypeError("Invalid parameter: " + type(int_ms).__name__ + " \nParameter should be: int")
    else:
        time = int_ms / 1000

        return float(time)


if __name__ == '__main__':  # if the script being run directly, print the following messages:
    print("Module: Time Converter Module"
          "\nVersion: 1.3 (21/Feb/2021)"
          "\nOriginal Revision: 4/2/2021"
          "\nAuthor: Kevin Putra (github.com/negated-py) \n.\n.\n.\n.\n.\n.\n.\n.")
    input("This script isn't meant to be ran directly."
          "\nPress enter to close")
