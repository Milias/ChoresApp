import sys
import os
import re
import enum
import uuid
import argparse
import itertools
from datetime import datetime, date, timedelta
from urllib.parse import urlparse, urljoin

import requests

from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey, Binary, Boolean, Float, types, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, exists, and_, func, literal

import jinja2
from jinja2 import Template

from flask import g, request, jsonify, redirect, render_template, flash, send_from_directory
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect

from wtforms import StringField, PasswordField, HiddenField, TextAreaField, IntegerField, SelectField, SelectMultipleField, BooleanField, DecimalField, FieldList, FormField
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import InputRequired, Email, Optional, Length, EqualTo

from .. import app

csrf = CSRFProtect()
csrf.init_app(app)

Base = declarative_base()

def tex_escape(text):
  """
    :param text: a plain text message
    :return: the message escaped to appear correctly in LaTeX
  """
  conv = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\^{}',
    '\\': r'\textbackslash{}',
    '<': r'\textless',
    '>': r'\textgreater',
  }
  regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
  return regex.sub(lambda match: conv[match.group()], text)

class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

def is_safe_url(target):
  ref_url = urlparse(request.host_url)
  test_url = urlparse(urljoin(request.host_url, target))
  return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def get_redirect_target():
  for target in request.args.get('next'), request.referrer:
    if not target:
      continue
    if is_safe_url(target):
      return target

class RedirectForm(FlaskForm):
  next = HiddenField()

  def __init__(self, *args, **kwargs):
    FlaskForm.__init__(self, *args, **kwargs)
    if not self.next.data:
      self.next.data = get_redirect_target() or ''

  def redirect(self, endpoint='/', **values):
    if is_safe_url(self.next.data):
      return redirect(self.next.data)
    target = get_redirect_target()
    return redirect(target or url_for(endpoint, **values))

