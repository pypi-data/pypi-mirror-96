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

from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.requests import Request

from webargs import fields
from webargs_starlette import use_args

from ...responses import response
from ...caches import ServerCache, ServersCache
from ...resources import Sessions


class ServersAPI(HTTPEndpoint):
    @requires("community")
    async def get(self, request: Request) -> response:
        """Used to list servers.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        cache = ServersCache(request.state.community.community_name)
        cache_get = await cache.get()

        if cache_get:
            return response(cache_get)

        data = [
            server.api_schema async for server, _
            in request.state.community.servers()
        ]

        await cache.set(data)

        return response(data)

    @use_args({"ip": fields.String(min=1, max=15, required=True),
               "port": fields.Integer(required=True),
               "name": fields.String(min=3, max=64, required=True)})
    @requires("is_owner")
    async def post(self, request: Request, parameters: dict) -> response:
        model, _ = await request.state.community.create_server(**parameters)

        await ServerCache(
            parameters["ip"], parameters["port"]
        ).set(model.api_schema)

        await ServersCache(request.state.community.community_name).expire()

        await Sessions.websocket.emit(
            request.state.community.community_name,
            {
                "ip": parameters["ip"],
                "port": parameters["port"],
                "data": model.api_schema,
                "state": "add"
            },
            room="ws_room"
        )

        return response(model.api_schema)


class ServerAPI(HTTPEndpoint):
    @requires("community")
    async def get(self, request: Request) -> response:
        """Used to get info on server.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        ip, port = request.path_params["ip"], request.path_params["port"]

        cache = ServerCache(ip, port)
        cache_get = await cache.get()

        if cache_get:
            return response(cache_get)

        data = (
            await (request.state.community.server(ip, port)).get()
        ).api_schema

        await cache.set(data)

        await ServersCache(request.state.community.community_name).expire()

        return response(data)

    @use_args({"players": fields.Integer(), "max_players": fields.Integer(),
               "ip": fields.String(min=1, max=15), "port": fields.Integer(),
               "name": fields.String(min=3, max=64),
               "map_name": fields.String(max=24)})
    @requires("master")
    async def post(self, request: Request, parameters: dict) -> response:
        """Used to update server.

        Parameters
        ----------
        request : Request
        parameters : dict

        Returns
        -------
        response
        """

        ip, port = request.path_params["ip"], request.path_params["port"]
        server = request.state.community.server(ip, port)

        await server.update(**parameters)
        data = (await server.get()).api_schema

        await ServerCache(ip, port).set(data)
        await ServersCache(request.state.community.community_name).expire()

        await Sessions.websocket.emit(
            request.state.community.community_name,
            {
                "ip": ip,
                "port": port,
                "data": data,
                "state": "update"
            },
            room="ws_room"
        )

        return response()

    @requires("is_owner")
    async def delete(self, request: Request) -> response:
        """Used to delete a server.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        ip, port = request.path_params["ip"], request.path_params["port"]

        await (request.state.community.server(ip, port)).delete()

        await ServerCache(ip, port).expire()
        await ServersCache(request.state.community.community_name).expire()

        await Sessions.websocket.emit(
            request.state.community.community_name,
            {
                "ip": ip,
                "port": port,
                "state": "delete"
            },
            room="ws_room"
        )

        return response()
