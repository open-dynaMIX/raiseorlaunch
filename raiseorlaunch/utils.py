# -*- coding: utf-8 -*-


def check_positive(value):
    try:
        fvalue = float(value)
    except ValueError:
        return False
    else:
        if fvalue <= 0:
            return False
        return True
