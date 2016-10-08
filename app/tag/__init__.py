#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint

tag = Blueprint('tag', __name__)

from . import views