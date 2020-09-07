#!usr/bin/env python3
# -*- coding: utf-8 -*-


"""Paste class for Kepler."""

import aiohttp
import json


class Paste_it():
    """Creates a new paste on a hastebin server."""

    async def new_paste(self, content):
        async with aiohttp.ClientSession() as session:
            async with session.post('https://hastebin.com/documents',
                                    data=content.encode('utf-8')) as response:
                json_data = await response.json()
                link = json_data['key']

                return f'Results: <http://hastebin.com/{link}>'
