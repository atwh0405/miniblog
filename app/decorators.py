#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_login import current_user
from functools import wraps
from flask import abort


def permission_required(permission):
    def dec(func):
        @wraps(func)
        def wrapper(**kwargs):
            if current_user.can(permission):
                return func(**kwargs)
            else:
                abort(403)
        return wrapper
    return dec

