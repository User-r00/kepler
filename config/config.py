#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configurations for Kepler.
"""
from credentials import tokens as TOKENS

PREFIX = '.'
PRESENCE = 'in the shadows.'
DESCRIPTION = 'A Discord bot for the r00m.'

emote_cache_updated = True
emote_link = ''

role_cache_updated = True
role_link = ''

ENV = 'PROD'

# Roles
if ENV == 'UAT':
    # User roles
    MOD = 472219677162995713

    # Bot Token
    TOKEN = TOKENS.UAT
else:
    # User roles
    MOD = 361827039403311106
    OPS = 564170904347869204
    MIL = 361827372863062016
    ACT = 393944070528958494

    # Bot Token
    TOKEN = TOKENS.PROD

# Global message auto-delete time.
DEL_DELAY = 20.0

# Filmoji
F_PNTS = 100


# Repository
BUG = 'https://github.com/User-r00/bravetraveler-issues/issues/new?assignees=&labels=&template=bug_report.md&title='
FEATURE = 'https://github.com/User-r00/bravetraveler-issues/issues/new?assignees=&labels=&template=feature_request.md&title='
