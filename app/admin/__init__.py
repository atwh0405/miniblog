#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint

admin = Blueprint('admin1', __name__)

from . import views
