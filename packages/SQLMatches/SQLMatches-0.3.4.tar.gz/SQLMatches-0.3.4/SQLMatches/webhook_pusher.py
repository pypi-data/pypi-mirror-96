# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2021 WardPearce
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


from typing import Any
from sqlalchemy.sql import select, and_
from aiohttp import BasicAuth, ClientConnectionError

from .tables import (
    community_table,
    api_key_table
)
from .resources import Sessions, Config


class WebhookPusher:
    def __init__(self, community_name: str, data: dict) -> None:
        """Used to push webhook.

        Parameters
        ----------
        community_name : str
            Community name.
        data : dict
            Data to push.
        """

        self.community_name = community_name
        self.data = data

    async def __post(self, url: str, key: str) -> None:
        try:
            await Sessions.aiohttp.post(
                url,
                timeout=Config.webhook_timeout,
                json=self.data,
                auth=BasicAuth("", key)
            )
        except ClientConnectionError:
            pass

    async def __send(self, col: Any, global_webhook: str = None) -> None:
        """Sends webhook request.

        Parameters
        ----------
        col : Any
            Column to select.
        global_webhook : str, optional
            by default None
        """

        query = select([
            col, api_key_table.c.api_key
        ]).select_from(
            community_table.join(
                api_key_table,
                api_key_table.c.community_name ==
                community_table.c.community_name
            )
        ).where(
            and_(
                community_table.c.community_name == self.community_name,
                api_key_table.c.master == True  # noqa: E712
            )
        )

        row = await Sessions.database.fetch_one(query)
        if row and row[0]:
            await self.__post(row[0], row[1])

        if global_webhook:
            await self.__post(global_webhook, Config.webhook_key)

    async def round_end(self) -> None:
        """Used to push round end webhook.
        """

        await self.__send(
            community_table.c.round_end_webhook,
            Config.webhook_round_end
        )

    async def match_end(self) -> None:
        """Used to push match end webhook.
        """

        await self.__send(
            community_table.c.match_end_webhook,
            Config.webhook_match_end
        )

    async def match_start(self) -> None:
        """Used to push match start webhook.
        """

        await self.__send(
            community_table.c.match_start_webhook,
            Config.webhook_match_start
        )
