# coding: utf-8

__author__ = 'asaka <lan@leancloud.rocks>'

from werkzeug.local import Local
from werkzeug.local import LocalManager

local = Local()
local_manager = LocalManager([local])
