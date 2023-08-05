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


from typing import AsyncGenerator, List, Tuple
from uuid import uuid4
from datetime import datetime
from secrets import token_urlsafe
from email.mime.text import MIMEText

from sqlalchemy.sql import select, and_, or_, func

from ..resources import Sessions, Config, DemoQueue

from ..decorators import (
    validate_community_type,
    validate_webhooks,
    validate_email
)


from ..templates import render_html

from ..tables import (
    community_table,
    scoreboard_total_table,
    scoreboard_table,
    user_table,
    api_key_table,
    statistic_table,
    server_table
)

from ..exceptions import (
    InvalidCommunity,
    InvalidSteamID,
    UserExists,
    ServerExists
)

from .models import (
    CommunityModel,
    MatchModel,
    ProfileModel,
    CommunityStatsModel, ProfileOverviewModel,
    PublicCommunityModel,
    ServerModel
)

from ..user import create_user

from .key import Key
from .match import Match
from .server import Server


class Community:
    def __init__(self, community_name: str) -> str:
        """Handles community interactions.

        Paramters
        ---------
        community_name: str
            ID of community.
        """

        self.community_name = community_name

    async def create_server(self, ip: str, port: int,
                            name: str) -> Tuple[ServerModel, Server]:
        """Used to create server.

        Parameters
        ----------
        ip : str
        port : int
        name : str

        Returns
        -------
        ServerModel
        Server

        Raises
        ------
        ServerExists
        """

        values = dict(
            community_name=self.community_name,
            ip=ip,
            port=port,
            name=name,
            players=0,
            max_players=0,
            map=None
        )

        try:
            await Sessions.database.execute(
                server_table.insert().values(
                    **values
                )
            )
        except Exception:
            raise ServerExists()
        else:
            return ServerModel(**values), self.server(ip, port)

    async def servers(self) -> AsyncGenerator[ServerModel, Server]:
        """Used to list servers.

        Yields
        -------
        ServerModel
        Server
        """

        query = server_table.select().where(
            server_table.c.community_name == self.community_name
        )

        async for row in Sessions.database.iterate(query):
            yield ServerModel(**row), self.server(row["ip"], row["port"])

    def server(self, ip: str, port: int) -> Server:
        """Used to interact with a server.

        Parameters
        ----------
        ip : str
        port : int

        Returns
        -------
        Server
        """

        return Server(ip, port, self.community_name)

    async def email(self, title: str, content: str,
                    link_href: str, link_text: str) -> None:
        """Used to send email to community owner.

        Parameters
        ----------
        title : str
        content : str
        link_href : str
        link_text : str
        """

        community = await self.get()

        message = MIMEText(render_html(
            "email.html",
            {
                "title": title,
                "content": content,
                "link": {
                    "href": link_href,
                    "text": link_text
                }
            }
        ), "html", "utf-8")

        message["From"] = Config.system_email
        message["To"] = community.email
        message["Subject"] = "{} - {}".format(
            title,
            (datetime.now()).strftime(Config.timestamp_format)
        )

        await Sessions.smtp.send_message(message)

    async def update_subscription_expire(self) -> None:
        await Sessions.database.execute(
            community_table.update().values(
                subscription_expires=datetime.now() +
                Config.subscription_length
            ).where(
                community_table.c.community_name == self.community_name
            )
        )

    async def billing_session(self) -> str:
        """Used to get a billing session.

        Returns
        -------
        str
        """

        league = await self.get()

        billing = await (
            Sessions.stripe.customer(league.customer_id)
        ).create_billing_session(
            "{}c/{}/owner".format(
                Config.frontend_url,
                league.community_name
            )
        )

        return billing.url

    async def checkout_session(self) -> str:
        """Used to get a checkout session.

        Returns
        -------
        str
            Session ID.
        """

        league = await self.get()

        owner_url = "{}c/{}/owner/".format(
            Config.frontend_url,
            league.community_name
        )

        return await (
            Sessions.stripe.customer(league.customer_id)
        ).create_checkout_session(
            cancel_url=owner_url + "cancel",
            success_url=owner_url + "success",
            price_id=Config.price_id
        )

    @validate_webhooks
    @validate_community_type
    @validate_email
    async def update(self, demos: bool = None,
                     community_type: str = None,
                     match_start_webhook: str = None,
                     round_end_webhook: str = None,
                     match_end_webhook: str = None,
                     allow_api_access: bool = None,
                     email: str = None) -> CommunityModel:
        """Used to update a community.

        Parameters
        ----------
        demos : bool, optional
            by default None
        community_type : str, optional
            by default None
        match_start_webhook : str, optional
            by default None
        round_end_webhook : str, optional
            by default None
        match_end_webhook : str, optional
            by default None
        allow_api_access : bool, optional
            by default None
        email : str, optional
            by default None

        Returns
        -------
        CommunityModel
        """

        values = {}

        if community_type is not None:
            values["community_type_id"] = Config.community_types[
                community_type
            ]

        if demos is not None:
            values["demos"] = demos

        if allow_api_access is not None:
            values["allow_api_access"] = allow_api_access

        if match_start_webhook:
            values["match_start_webhook"] = match_start_webhook

        if round_end_webhook:
            values["round_end_webhook"] = round_end_webhook

        if match_end_webhook:
            values["match_end_webhook"] = match_end_webhook

        if email:
            values["email"] = email

        if values:
            query = community_table.update().values(
                **values
            ).where(
                community_table.c.community_name == self.community_name
            )

            await Sessions.database.execute(query)

        return await self.get()

    async def stats(self) -> CommunityStatsModel:
        """Gets basic stats about community.

        Returns
        -------
        CommunityStatsModel
        """

        sub_active_matches = select([
            func.count().label("active_matches")
        ]).select_from(
            scoreboard_total_table
        ).where(
            and_(
                scoreboard_total_table.c.community_name == self.community_name,
                scoreboard_total_table.c.status == 1
            )
        ).alias("sub_active_matches")

        sub_stored_demos = select([
            func.count().label("stored_demos")
        ]).select_from(
            scoreboard_total_table
        ).where(
            and_(
                scoreboard_total_table.c.community_name == self.community_name,
                scoreboard_total_table.c.demo_status == 2
            )
        ).alias("sub_stored_demos")

        sub_total_matches = select([
            func.count().label("total_matches"),
        ]).select_from(
            scoreboard_total_table
        ).where(
            and_(
                scoreboard_total_table.c.community_name == self.community_name,
                scoreboard_total_table.c.status == 0
            )
        ).alias("sub_total_matches")

        sub_total_users = select([
            func.count().label("total_users"),
        ]).select_from(
            statistic_table
        ).where(
            statistic_table.c.community_name == self.community_name
        ).alias("sub_total_users")

        query = select([
            sub_total_users.c.total_users,
            sub_active_matches.c.active_matches,
            sub_stored_demos.c.stored_demos,
            sub_total_matches.c.total_matches
        ])

        return CommunityStatsModel(
            **await Sessions.database.fetch_one(query)
        )

    async def profile(self, steam_id: str) -> ProfileModel:
        """Get user profile.

        Parameters
        ----------
        steam_id : str

        Returns
        -------
        ProfileModel

        Raises
        ------
        InvalidSteamID
        """

        query = select([
            user_table.c.name,
            user_table.c.timestamp,
            statistic_table.c.steam_id,
            statistic_table.c.kills,
            statistic_table.c.headshots,
            statistic_table.c.assists,
            statistic_table.c.deaths,
            statistic_table.c.shots_fired,
            statistic_table.c.shots_hit,
            statistic_table.c.mvps
        ]).select_from(
            statistic_table.join(
                user_table,
                user_table.c.steam_id == statistic_table.c.steam_id
            )
        ).where(
            and_(
                statistic_table.c.steam_id == steam_id,
                statistic_table.c.community_name == self.community_name
            )
        )

        row = await Sessions.database.fetch_one(query=query)
        if row:
            return ProfileModel(**row)
        else:
            raise InvalidSteamID()

    async def players(self, search: str = None, page: int = 1,
                      limit: int = 10, desc: bool = True
                      ) -> AsyncGenerator[ProfileOverviewModel, None]:
        """Used to list community players.

        Parameters
        ----------
        search : str, optional
            by default None
        page : int, optional
            by default 1
        limit : int, optional
            by default 10
        desc : bool, optional
            by default True

        Yields
        ------
        ProfileOverviewModel
        """

        query = select([
            user_table.c.name,
            statistic_table.c.steam_id,
            statistic_table.c.kills,
            statistic_table.c.headshots,
            statistic_table.c.assists,
            statistic_table.c.deaths
        ]).select_from(
            statistic_table.join(
                user_table,
                user_table.c.steam_id == statistic_table.c.steam_id
            )
        ).where(
            statistic_table.c.community_name == self.community_name
        )

        if search:
            query = query.where(
                or_(
                    statistic_table.c.steamid == search,
                    statistic_table.c.name.like("%{}%".format(search))
                )
            )

        query = query.order_by(
            statistic_table.c.kills.desc() if desc
            else statistic_table.c.kills.asc()
        ).limit(limit).offset((page - 1) * limit if page > 1 else 0)

        async for row in Sessions.database.iterate(query):
            yield ProfileOverviewModel(**row)

    async def delete_matches(self, matches: List[str]) -> None:
        """Used to bulk delete matches.

        Parameters
        ----------
        matches : List[str]
            List of match IDs to delete.
        """

        await Sessions.database.execute(
            scoreboard_total_table.delete().where(
                scoreboard_total_table.c.match_id ==
                scoreboard_table.c.match_id
            ).where(
                and_(
                    scoreboard_total_table.c.community_name ==
                    self.community_name,
                    scoreboard_total_table.c.match_id.in_(matches)
                )
            )
        )

        # Todo
        # Work out sqlalchemy left joining delete,
        # so i don't need this ugly mess.
        await Sessions.database.execute(
            scoreboard_total_table.delete().where(
                and_(
                    scoreboard_total_table.c.community_name
                    == self.community_name,
                    scoreboard_total_table.c.match_id.in_(matches)
                )
            )
        )

        if Config.upload_type:
            if self.community_name not in DemoQueue.matches:
                DemoQueue.matches[self.community_name] = matches
            else:
                DemoQueue.matches[self.community_name] += matches

    async def create_match(self, team_1_name: str, team_2_name: str,
                           team_1_side: int, team_2_side: int,
                           team_1_score: int, team_2_score: int,
                           map_name: str) -> Tuple[MatchModel, Match]:
        """Creates a match.

        Returns
        -------
        Match
            Used for interacting with matches.
        """

        match_id = str(uuid4())
        now = datetime.now()
        status = 1
        demo_status = 0

        query = scoreboard_total_table.insert().values(
            match_id=match_id,
            team_1_name=team_1_name,
            team_2_name=team_2_name,
            team_1_side=team_1_side,
            team_2_side=team_2_side,
            map=map_name,
            community_name=self.community_name,
            team_1_score=team_1_score,
            team_2_score=team_2_score,
            status=status,
            demo_status=demo_status,
            timestamp=now
        )

        await Sessions.database.execute(query=query)

        return MatchModel(
            match_id=match_id, timestamp=now, status=status,
            demo_status=demo_status, map=map_name, team_1_name=team_1_name,
            team_2_name=team_2_name, team_1_score=team_1_score,
            team_2_score=team_2_score, team_1_side=team_1_side,
            team_2_side=team_2_side, community_name=self.community_name
        ), self.match(match_id)

    def match(self, match_id) -> Match:
        """Handles interactions with a match

        Paramters
        ---------
        match_id: str
            ID of match
        """

        return Match(match_id, self.community_name)

    def key(self, api_key: str) -> Key:
        """Used to interact with key.

        Parameters
        ----------
        api_key : str

        Returns
        -------
        Key
        """

        return Key(api_key, self.community_name)

    async def user_to_key(self, steam_id: str) -> Tuple[str, Key]:
        """Used to get a API key from a steam ID.

        Parameters
        ----------
        steam_id : str

        Returns
        -------
        str
            The API key.
        Key
        """

        key = await Sessions.database.fetch_val(
            select([api_key_table.c.api_key]).select_from(
                api_key_table
            ).where(
                and_(
                    api_key_table.c.community_name == self.community_name,
                    api_key_table.c.owner_id == steam_id,
                    api_key_table.c.master == False  # noqa: E712
                )
            )
        )

        return key, self.key(key)

    async def create_key(self, steam_id: str) -> Tuple[str, Key]:
        """Used to create a API key for a user.

        Parameters
        ----------
        steam_id : str

        Returns
        -------
        str
            The API key.
        Key
        """

        key = token_urlsafe(24)

        try:
            await create_user(steam_id, "Unknown")
        except UserExists:
            pass

        await Sessions.database.execute(
            api_key_table.insert().values(
                api_key=key,
                owner_id=steam_id,
                timestamp=datetime.now(),
                community_name=self.community_name,
                master=False
            )
        )

        return key, self.key(key)

    async def regenerate_master(self) -> str:
        """Regenerates the master API key.
        """

        key = token_urlsafe(24)

        query = api_key_table.update().values(
            api_key=key,
            timestamp=datetime.now()
        ).where(
            and_(
                api_key_table.c.community_name == self.community_name,
                api_key_table.c.master == 1
            )
        )

        await Sessions.database.execute(query=query)

        return key

    async def exists(self) -> bool:
        """Checks if community exists with name.
        """

        query = select([func.count()]).select_from(community_table).where(
            community_table.c.community_name == self.community_name
        )

        return await Sessions.database.fetch_val(query=query) > 0

    async def matches(self, search: str = None,
                      page: int = 1, limit: int = 10, desc: bool = True,
                      require_scoreboard: bool = True
                      ) -> AsyncGenerator[MatchModel, Match]:
        """Lists matches.

        Paramters
        ---------
        search: str
        page: int
        limit: int
        desc: bool, optional
            by default True
        require_scoreboard : bool, optional
            If enabled scoreboard will need to be ready
            to pull match, by default True

        Yields
        ------
        MatchModel
            Holds basic match details.
        Match
            Used for interacting with a match.
        """

        query = select([
            scoreboard_total_table.c.match_id,
            scoreboard_total_table.c.timestamp,
            scoreboard_total_table.c.status,
            scoreboard_total_table.c.demo_status,
            scoreboard_total_table.c.map,
            scoreboard_total_table.c.team_1_name,
            scoreboard_total_table.c.team_2_name,
            scoreboard_total_table.c.team_1_score,
            scoreboard_total_table.c.team_2_score,
            scoreboard_total_table.c.team_1_side,
            scoreboard_total_table.c.team_2_side,
            scoreboard_total_table.c.community_name
        ])

        if search:
            like_search = "%{}%".format(search)

            query = query.select_from(
                scoreboard_total_table.join(
                    scoreboard_table,
                    scoreboard_table.c.match_id ==
                    scoreboard_total_table.c.match_id
                ).join(
                    user_table,
                    user_table.c.steam_id == scoreboard_table.c.steam_id
                )
            ).where(
                and_(
                    scoreboard_total_table.c.community_name ==
                    self.community_name,
                    or_(
                        scoreboard_total_table.c.match_id == search,
                        scoreboard_total_table.c.map.like(like_search),
                        scoreboard_total_table.c.team_1_name.like(
                            like_search),
                        scoreboard_total_table.c.team_2_name.like(
                            like_search),
                        user_table.c.name.like(like_search),
                        user_table.c.steam_id == search
                    )
                )
            )
        elif require_scoreboard:
            query = query.select_from(
                scoreboard_total_table.join(
                    scoreboard_table,
                    scoreboard_table.c.match_id ==
                    scoreboard_total_table.c.match_id
                )
            ).where(
                scoreboard_total_table.c.community_name
                == self.community_name,
            )
        else:
            query = query.select_from(
                scoreboard_total_table
            ).where(
                scoreboard_total_table.c.community_name
                == self.community_name,
            )

        query = query.distinct().order_by(
            scoreboard_total_table.c.timestamp.desc() if desc
            else scoreboard_total_table.c.timestamp.asc()
        ).limit(limit).offset((page - 1) * limit if page > 1 else 0)

        async for row in Sessions.database.iterate(query=query):
            yield MatchModel(**row), self.match(row["match_id"])

    async def public(self) -> PublicCommunityModel:
        """Used to get public data on a community.

        Returns
        -------
        PublicCommunityModel

        Raises
        ------
        InvalidCommunity
            Raised when community ID doesn't exist.
        """

        query = select([
            community_table.c.owner_id,
            community_table.c.disabled,
            community_table.c.community_name,
            community_table.c.timestamp,
            community_table.c.banned,
            community_table.c.allow_api_access
        ]).select_from(community_table).where(
            community_table.c.community_name == self.community_name
        )

        row = await Sessions.database.fetch_one(query)
        if row:
            return PublicCommunityModel(**row)
        else:
            raise InvalidCommunity()

    async def get(self) -> CommunityModel:
        """Gets base community details.

        Returns
        -------
        CommunityModel
            Holds community data.

        Raises
        ------
        InvalidCommunity
            Raised when community ID doesn't exist.
        """

        query = select([
            api_key_table.c.api_key,
            api_key_table.c.owner_id,
            community_table.c.disabled,
            community_table.c.banned,
            community_table.c.community_name,
            community_table.c.timestamp,
            community_table.c.allow_api_access,
            community_table.c.match_start_webhook,
            community_table.c.round_end_webhook,
            community_table.c.match_end_webhook,
            community_table.c.customer_id,
            community_table.c.email,
            community_table.c.subscription_expires
        ]).select_from(
            community_table.join(
                api_key_table,
                community_table.c.community_name ==
                api_key_table.c.community_name
            )
        ).where(
            and_(
                community_table.c.community_name == self.community_name,
                api_key_table.c.master == True  # noqa: E712
            )
        )

        row = await Sessions.database.fetch_one(query)
        if row:
            return CommunityModel(**row)
        else:
            raise InvalidCommunity()

    async def disable(self) -> None:
        """Disables a community.
        """

        query = community_table.update().where(
            community_table.c.community_name == self.community_name
        ).values(disabled=True)

        await Sessions.database.execute(query)
