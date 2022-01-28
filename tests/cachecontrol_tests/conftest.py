# SPDX-FileCopyrightText: 2015 Eric Larson
#
# SPDX-License-Identifier: Apache-2.0
#
# From https://github.com/ionrock/cachecontrol

# stdlib
import os
import socket
from contextlib import suppress
from pprint import pformat

# 3rd party
import cherrypy  # type: ignore[import]
import pytest


class SimpleApp:

	def __init__(self):
		self.etag_count = 0
		self.update_etag_string()

	def dispatch(self, env):
		path = env["PATH_INFO"][1:].split('/')
		segment = path.pop(0)
		if segment and hasattr(self, segment):
			return getattr(self, segment)

		return None

	def update_etag_string(self):
		self.etag_count += 1
		self.etag_string = f'"ETAG-{self.etag_count}"'

	def __call__(self, env, start_response):
		func = self.dispatch(env)

		if func:
			return func(env, start_response)

		headers = [("Cache-Control", "max-age=5000"), ("Content-Type", "text/plain")]
		start_response("200 OK", headers)
		return [pformat(env).encode("utf8")]


@pytest.fixture(scope="session")
def server():
	return cherrypy.server


@pytest.fixture()
def url(server):
	return "http://%s:%s/" % server.bind_addr


def get_free_port():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 0))
	ip, port = s.getsockname()
	s.close()
	ip = os.environ.get("WEBTEST_SERVER_BIND", "127.0.0.1")
	return ip, port


def pytest_configure(config):
	cherrypy.tree.graft(SimpleApp(), '/')

	ip, port = get_free_port()

	cherrypy.config.update({"server.socket_host": ip, "server.socket_port": port})

	# turn off logging
	logger = cherrypy.log.access_log
	logger.removeHandler(logger.handlers[0])

	cherrypy.server.start()


def pytest_unconfigure(config):
	with suppress(Exception):
		cherrypy.server.stop()
