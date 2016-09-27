#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint

main = Blueprint('main', __name__)
from . import errors, views
from ..models import Permissions


@main.app_context_processor
def inject_permissions():
    return dict(Permissions=Permissions)