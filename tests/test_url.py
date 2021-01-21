# stdlib
import json
import os
import pathlib
import sys
from abc import ABC, abstractmethod
from ipaddress import IPv4Address
from textwrap import dedent
from typing import Type
from urllib.parse import parse_qs

# 3rd party
import pytest
import pytest_httpserver.pytest_plugin  # type: ignore
import requests
import werkzeug
from coincidence import count
from pytest_httpserver.httpserver import QueryMatcher  # type: ignore

# this package
from apeye.requests_url import TrailingRequestsURL
from apeye.url import URL, Domain, RequestsURL, SlumberURL, URLPath


class TestUrlPath:

	@pytest.mark.parametrize(
			"value", [
					"/watch?v=NG21KWZSiok",
					"watch?v=NG21KWZSiok",
					'',
					"/programmes/b006qtlx/episodes/player",
					]
			)
	def test_str(self, value):
		assert str(URLPath(value)) == value

	@pytest.mark.parametrize(
			"value, expects",
			[
					("/watch?v=NG21KWZSiok", "URLPath('/watch?v=NG21KWZSiok')"),
					("watch?v=NG21KWZSiok", "URLPath('watch?v=NG21KWZSiok')"),
					('', "URLPath('')"),
					("/programmes/b006qtlx/episodes/player", "URLPath('/programmes/b006qtlx/episodes/player')"),
					]
			)
	def test_repr(self, value, expects):
		assert repr(URLPath(value)) == expects

	@pytest.mark.parametrize(
			"method",
			[
					URLPath().match,
					URLPath().is_absolute,
					URLPath().joinpath,
					URLPath().relative_to,
					URLPath().as_uri,
					URLPath().__lt__,
					URLPath().__le__,
					URLPath().__gt__,
					URLPath().__ge__,
					]
			)
	def test_notimplemented(self, method):
		with pytest.raises(NotImplementedError):
			method()

	def test_notimplemented_properties(self):
		with pytest.raises(NotImplementedError):
			URLPath().anchor  # pylint: disable=expression-not-assigned
		with pytest.raises(NotImplementedError):
			URLPath().drive  # pylint: disable=expression-not-assigned

	@pytest.mark.parametrize(
			"value, expects",
			[
					(URLPath() / "news", URLPath("news")),
					(URLPath('/') / "news", URLPath("/news")),
					(URLPath("/programmes") / "b006qtlx", URLPath("/programmes/b006qtlx")),
					("/programmes" / URLPath("b006qtlx"), URLPath("/programmes/b006qtlx")),
					]
			)
	def test_division(self, value, expects):
		assert value == expects

	@count(100)
	def test_division_errors_number(self, count: int):
		if sys.version_info < (3, 8):
			with pytest.raises(TypeError, match=r"expected str, bytes or os.PathLike object, not int"):
				URLPath() / count  # type: ignore  # pylint: disable=expression-not-assigned
			with pytest.raises(TypeError, match=r"expected str, bytes or os.PathLike object, not float"):
				URLPath() / float(count)  # type: ignore  # pylint: disable=expression-not-assigned
		else:
			with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: 'URLPath' and 'int'"):
				URLPath() / count  # pylint: disable=expression-not-assigned
			with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: 'URLPath' and 'float'"):
				URLPath() / float(count)  # pylint: disable=expression-not-assigned

	@pytest.mark.parametrize("obj", [[], (), {}, set(), pytest.raises, ABC])
	def test_division_errors(self, obj):
		if sys.version_info < (3, 8):
			with pytest.raises(TypeError, match=r"expected str, bytes or os.PathLike object, not .*"):
				URLPath() / obj  # pylint: disable=expression-not-assigned
		else:
			with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: 'URLPath' and .*"):
				URLPath() / obj  # pylint: disable=expression-not-assigned

	@pytest.mark.parametrize("obj", [1234, 12.34, [], (), {}, set(), pytest.raises, ABC])
	def test_rtruediv_typerror(self, obj):
		if sys.version_info < (3, 8):
			with pytest.raises(TypeError, match=r"expected str, bytes or os.PathLike object, not .*"):
				obj / URLPath()  # pylint: disable=expression-not-assigned
		else:
			with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: .* and 'URLPath'"):
				obj / URLPath()  # pylint: disable=expression-not-assigned


class _TestURL(ABC):

	@property
	@abstractmethod
	def _class(self) -> Type:
		pass

	@pytest.mark.parametrize(
			"url, scheme, netloc, path",
			[
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes/player",
							"https",
							"www.bbc.co.uk",
							URLPath("/programmes/b006qtlx/episodes/player"),
							),
					(
							"www.bbc.co.uk/programmes/b006qtlx/episodes/player",
							'',
							"www.bbc.co.uk",
							URLPath("/programmes/b006qtlx/episodes/player"),
							),
					(
							"/programmes/b006qtlx/episodes/player",
							'',
							'',
							URLPath("/programmes/b006qtlx/episodes/player"),
							),
					(
							"//www.bbc.co.uk/programmes/b006qtlx/episodes/player",
							'',
							"www.bbc.co.uk",
							URLPath("/programmes/b006qtlx/episodes/player"),
							),
					]
			)
	def test_creation(self, url, scheme, netloc, path):
		url = self._class(url)
		assert url.scheme == scheme
		assert url.netloc == netloc
		assert url.path == path

	@pytest.mark.parametrize(
			"url",
			[
					"https://www.bbc.co.uk/programmes/b006qtlx/episodes/player",
					"www.bbc.co.uk/programmes/b006qtlx/episodes/player",
					"www.bbc.co.uk",
					"/programmes/b006qtlx/episodes/player",
					"programmes/b006qtlx/episodes/player",
					"https://127.0.0.1/programmes/b006qtlx/episodes/player",
					"ftp://127.0.0.1/programmes/b006qtlx/episodes/player",
					]
			)
	def test_str(self, url):
		assert str(self._class(url)) == url

	def test_division(self):
		value = self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes") / "player"
		assert value == self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes/player")

		value = self._class("/programmes/b006qtlx/episodes") / "player"
		assert value == self._class("/programmes/b006qtlx/episodes/player")

		assert self._class("www.bbc.co.uk") / "news" == self._class("www.bbc.co.uk/news")
		assert self._class() / "news" == self._class("/news")

	@count(100)
	def test_division_number(self, count: int):
		assert (self._class() / count).parts[-1] == str(count)

		with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: '.*' and 'float'"):
			self._class() / float(count)  # pylint: disable=expression-not-assigned

	@pytest.mark.parametrize("obj", [[], (), {}, set(), pytest.raises, ABC])
	def test_division_errors(self, obj):
		with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: '.*' and .*"):
			self._class() / obj  # pylint: disable=expression-not-assigned

	@pytest.mark.parametrize("obj", [1234, 12.34, "abcdefg", [], (), {}, set(), pytest.raises, ABC])
	def test_rtruediv_typerror(self, obj):
		with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: .* and '.*'"):
			obj / self._class()  # pylint: disable=expression-not-assigned

	def test_empty_url_operations(self):
		assert self._class().name == ''
		assert self._class().suffix == ''
		assert self._class().fqdn == ''
		assert self._class().stem == ''
		assert self._class().suffixes == []

	@pytest.mark.parametrize(
			"url, name",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", "episodes"),
					("www.bbc.co.uk", ''),
					("/programmes/b006qtlx/episodes", "episodes"),
					]
			)
	def test_name(self, url, name):
		assert self._class(url).name == name

	@pytest.mark.parametrize(
			"url, suffix",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", ''),
					("www.bbc.co.uk", ''),
					("/programmes/b006qtlx/episodes", ''),
					("https://imgs.xkcd.com/comics/workflow.png", ".png"),
					]
			)
	def test_suffix(self, url, suffix):
		assert self._class(url).suffix == suffix

	@pytest.mark.parametrize(
			"url, suffixes",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", []),
					("www.bbc.co.uk", []),
					("/programmes/b006qtlx/episodes", []),
					("https://imgs.xkcd.com/comics/workflow.png", [".png"]),
					(
							"https://github.com/domdfcoding/domdf_python_tools/releases/download/"
							"v0.4.8/domdf_python_tools-0.4.8.tar.gz", [".4", ".8", ".tar", ".gz"]
							),
					]
			)
	def test_suffixes(self, url, suffixes):
		assert self._class(url).suffixes == suffixes

	@pytest.mark.parametrize(
			"url, stem",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", "episodes"),
					("www.bbc.co.uk", ''),
					("/programmes/b006qtlx/episodes", "episodes"),
					("https://imgs.xkcd.com/comics/workflow.png", "workflow"),
					(
							"https://github.com/domdfcoding/domdf_python_tools/releases/download/v0.4.8/domdf_python_tools-0.4.8.tar.gz",
							"domdf_python_tools-0.4.8.tar"
							),
					]
			)
	def test_stem(self, url, stem):
		assert self._class(url).stem == stem

	def test_with_name(self):
		value = self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes").with_name("foo")
		assert value == self._class("https://www.bbc.co.uk/programmes/b006qtlx/foo")

		value = self._class("/programmes/b006qtlx/episodes").with_name("foo")
		assert value == self._class("/programmes/b006qtlx/foo")

		value = self._class("https://imgs.xkcd.com/comics/workflow.png").with_name("baz")
		assert value == self._class("https://imgs.xkcd.com/comics/baz")

		with pytest.raises(ValueError, match=r"URLPath\(''\) has an empty name"):
			self._class("www.bbc.co.uk").with_name("bar")
		with pytest.raises(ValueError, match=r"URLPath\(''\) has an empty name"):
			self._class().with_name("bar")

	def test_with_suffix(self):
		value = self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes").with_suffix(".foo")
		assert value == self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes.foo")

		value = self._class("/programmes/b006qtlx/episodes").with_suffix(".foo")
		assert value == self._class("/programmes/b006qtlx/episodes.foo")

		value = self._class("https://imgs.xkcd.com/comics/workflow.png").with_suffix(".baz")
		assert value == self._class("https://imgs.xkcd.com/comics/workflow.baz")

	@pytest.mark.parametrize(
			"url, parent",
			[
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes",
							"https://www.bbc.co.uk/programmes/b006qtlx"
							),
					("/programmes/b006qtlx/episodes", "/programmes/b006qtlx"),
					("https://imgs.xkcd.com/comics/workflow.png", "https://imgs.xkcd.com/comics"),
					]
			)
	def test_parent(self, url, parent):
		assert self._class(url).parent == self._class(parent)

	@pytest.mark.parametrize(
			"url, fqdn",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", "www.bbc.co.uk"),
					("www.bbc.co.uk", "www.bbc.co.uk"),
					("/programmes/b006qtlx/episodes", ''),
					("https://imgs.xkcd.com/comics/workflow.png", "imgs.xkcd.com"),
					]
			)
	def test_fqdn(self, url, fqdn):
		assert self._class(url).fqdn == fqdn

	@pytest.mark.parametrize(
			"url, subdomain, domain, suffix, ipv4",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", "www", "bbc", "co.uk", None),
					("/programmes/b006qtlx/episodes", '', '', '', None),
					("https://www.bbc.co.uk", "www", "bbc", "co.uk", None),
					("ftp://127.0.0.1/download.zip", '', "127.0.0.1", '', IPv4Address("127.0.0.1")),
					]
			)
	def test_domain(self, url, subdomain, domain, suffix, ipv4):
		assert isinstance(self._class(url).domain, Domain)
		assert self._class(url).domain.subdomain == subdomain
		assert self._class(url).domain.domain == domain
		assert self._class(url).domain.suffix == suffix
		assert self._class(url).domain.ipv4 == ipv4

	@pytest.mark.parametrize(
			"url, expects",
			[
					("bbc.co.uk/news", "bbc.co.uk/news"),
					("https://bbc.co.uk/news", "bbc.co.uk/news"),
					("https://www.bbc.co.uk/news", "www.bbc.co.uk/news"),
					]
			)
	def test_cast_to_pathlib(self, url, expects):
		assert pathlib.Path(self._class(url)) == pathlib.Path(expects)

	@pytest.mark.parametrize(
			"url, expects",
			[
					("bbc.co.uk/news", "bbc.co.uk/news"),
					("https://bbc.co.uk/news", "bbc.co.uk/news"),
					("https://www.bbc.co.uk/news", "www.bbc.co.uk/news"),
					]
			)
	def test_fspath(self, url, expects):
		assert self._class(url).__fspath__() == expects
		assert os.fspath(self._class(url)) == expects

	def test_hash(self):
		assert hash(self._class("bbc.co.uk")) == hash(self._class("bbc.co.uk"))
		assert hash(self._class("bbc.co.uk/news")) != hash(self._class("bbc.co.uk"))
		assert {self._class("bbc.co.uk"), hash(self._class("bbc.co.uk/news"))}

	@pytest.mark.parametrize(
			"url, parts",
			[
					(
							"https://hub.docker.com/r/tobix/pywine/dockerfile",
							("https", "hub", "docker", "com", 'r', "tobix", "pywine", "dockerfile")
							),
					]
			)
	def test_parts(self, url, parts):
		assert self._class(url).parts == parts

	def test_parents(self):
		assert self._class("https://hub.docker.com/r/tobix/pywine/dockerfile").parents == (
				self._class("https://hub.docker.com/r/tobix/pywine"),
				self._class("https://hub.docker.com/r/tobix"),
				self._class("https://hub.docker.com/r"),
				self._class("https://hub.docker.com/"),
				)

	def test_notimplemented_eq(self):
		assert URL() != 7
		assert URL() != 3.14142
		assert URL() != 'a'
		assert URL() != [7, 'a', 3.14142]
		assert URL() != (7, 'a', 3.14142)
		assert URL() != {7, 'a', 3.14142}
		assert URL() != {"int": 7, "str": 'a', "float": 3.14142}

	def test_from_url(self):
		url = URL("bbc.co.uk")
		assert self._class(url) == url

	def test_with_query(self):
		url = self._class("https://api.github.com/user/domdfcoding/repos?page=2&per_page=50")
		assert url.query == {"page": ['2'], "per_page": ["50"]}

		url = self._class("https://api.github.com/user/domdfcoding/repos?name=bob")
		assert url.query == {"name": ["bob"]}

		url = self._class("https://api.github.com/user/domdfcoding/repos")
		assert url.query == {}

		url = self._class("https://api.github.com?foo=bar")
		assert url.query == {"foo": ["bar"]}
		assert (url / "users").query == {}

	def test_with_fragment(self):
		url = self._class("https://api.github.com/user/domdfcoding/repos#footer")
		assert url.fragment == "footer"

		url = self._class("https://api.github.com/user/domdfcoding/repos")
		assert url.fragment is None

		url = self._class("https://api.github.com#footer")
		assert url.fragment == "footer"
		assert (url / "users").fragment is None


class TestUrl(_TestURL):

	_class = URL

	@pytest.mark.parametrize(
			"url, expects",
			[
					(
							URL("https://www.bbc.co.uk/programmes/b006qtlx/episodes/player"),
							"URL('https://www.bbc.co.uk/programmes/b006qtlx/episodes/player')"
							),
					(
							URL("www.bbc.co.uk/programmes/b006qtlx/episodes/player"),
							"URL('www.bbc.co.uk/programmes/b006qtlx/episodes/player')"
							),
					(URL("www.bbc.co.uk"), "URL('www.bbc.co.uk')"),
					(URL("/programmes/b006qtlx/episodes/player"), "URL('/programmes/b006qtlx/episodes/player')"),
					(URL("programmes/b006qtlx/episodes/player"), "URL('programmes/b006qtlx/episodes/player')"),
					(
							URL("https://127.0.0.1/programmes/b006qtlx/episodes/player"),
							"URL('https://127.0.0.1/programmes/b006qtlx/episodes/player')"
							),
					(
							URL("ftp://127.0.0.1/programmes/b006qtlx/episodes/player"),
							"URL('ftp://127.0.0.1/programmes/b006qtlx/episodes/player')"
							),
					]
			)
	def test_repr(self, url, expects):
		assert repr(url) == expects

	def test_isinstance(self):
		assert isinstance(URL(), URL)
		assert isinstance(URL(), os.PathLike)  # type: ignore

	def test_equality(self):
		assert URL() == URL()
		assert URL("bbc.co.uk") == URL("bbc.co.uk")
		assert URL("https://bbc.co.uk") == URL("https://bbc.co.uk")
		assert URL("bbc.co.uk/news") == URL("bbc.co.uk/news")

		assert URL("bbc.co.uk") != URL("bbc.co.uk/news")
		assert URL("bbc.co.uk") != URL("http://bbc.co.uk/news")
		assert URL("bbc.co.uk") != URL("http://bbc.co.uk")


class TestSlumberURL(_TestURL):

	_class = SlumberURL

	def test_isinstance(self):
		assert isinstance(SlumberURL(), SlumberURL)
		assert isinstance(SlumberURL(), URL)
		assert isinstance(SlumberURL(), os.PathLike)  # type: ignore

	base = SlumberURL("https://jsonplaceholder.typicode.com")

	def test_get(self):
		assert self.base / "todos" / '1' == URL("https://jsonplaceholder.typicode.com/todos/1")
		assert (self.base / "todos" / '1').get() == {
				"userId": 1,
				"id": 1,
				"title": "delectus aut autem",
				"completed": False,
				}
		assert isinstance((self.base / "todos").get(userID=1), list)

	def test_head(self):
		assert self.base / "todos" / '1' == URL("https://jsonplaceholder.typicode.com/todos/1")
		headers = (self.base / "todos" / '1').head()

		assert "Date" in headers
		assert headers["Content-Type"] == "application/json; charset=utf-8"
		assert headers["Server"] == "cloudflare"
		assert headers["Content-Encoding"] == "gzip"

	def test_options(self):
		options = SlumberURL("https://readthedocs.org").options()
		assert options == "GET, HEAD, OPTIONS"

	def test_post(self):
		assert self.base / "posts" == URL("https://jsonplaceholder.typicode.com/posts")
		expected = {"body": "bar", "userId": 1, "id": 101, "title": "foo"}
		assert (self.base / "posts").post({"title": "foo", "body": "bar", "userId": 1}) == expected

	def test_put(self):
		assert self.base / "posts" / '1' == URL("https://jsonplaceholder.typicode.com/posts/1")
		expected = {"body": "bar", "userId": 1, "id": 1, "title": "foo"}
		assert (self.base / "posts" / '1').put({"title": "foo", "body": "bar", "userId": 1}) == expected

	def test_patch(self):
		body = dedent(
				"""\
		quia et suscipit
		suscipit recusandae consequuntur expedita et cum
		reprehenderit molestiae ut ut quas totam
		nostrum rerum est autem sunt rem eveniet architecto"""
				)

		expected = {"body": body, "userId": 1, "id": 1, "title": "foo"}
		assert (self.base / "posts" / '1').patch({"title": "foo"}) == expected

	def test_delete(self):
		assert (self.base / "posts" / '1').delete()

	def test_equality(self):
		assert SlumberURL() == SlumberURL()
		assert URL() == SlumberURL()

		assert SlumberURL("bbc.co.uk") == SlumberURL("bbc.co.uk")
		assert URL("bbc.co.uk") == SlumberURL("bbc.co.uk")

		assert SlumberURL("https://bbc.co.uk") == SlumberURL("https://bbc.co.uk")
		assert URL("https://bbc.co.uk") == SlumberURL("https://bbc.co.uk")

		assert SlumberURL("bbc.co.uk/news") == SlumberURL("bbc.co.uk/news")
		assert URL("bbc.co.uk/news") == SlumberURL("bbc.co.uk/news")

		assert SlumberURL("bbc.co.uk") != SlumberURL("bbc.co.uk/news")
		assert SlumberURL("bbc.co.uk") != SlumberURL("http://bbc.co.uk/news")
		assert SlumberURL("bbc.co.uk") != SlumberURL("http://bbc.co.uk")

	def test_division__store(self):
		sess = requests.Session()
		l_url = SlumberURL(
				"http://bbc.co.uk",
				format="XML",
				auth=("username", "password"),
				append_slash=False,
				session=sess,
				)
		l_url.timeout = 42
		l_url.cert = "cert"
		l_url.proxies = "proxies"  # type: ignore
		l_url.allow_redirects = False
		l_url.verify = "verify"
		new_url = l_url / "news"
		assert new_url._store == l_url._store
		assert new_url.session is sess is l_url.session is l_url._store["session"]
		assert new_url.session.auth == l_url.session.auth == ("username", "password")
		assert new_url._store["format"] == l_url._store["format"] == "XML"
		assert new_url.timeout == 42
		assert new_url.cert == "cert"
		assert new_url.proxies == "proxies"
		assert new_url.allow_redirects is False
		assert new_url.verify == "verify"


class TestRequestsURL(_TestURL):

	_class = RequestsURL

	def test_isinstance(self):
		assert isinstance(RequestsURL(), RequestsURL)
		assert isinstance(RequestsURL(), URL)
		assert isinstance(RequestsURL(), os.PathLike)  # type: ignore

	base = RequestsURL("https://raw.githubusercontent.com")

	def test_get(self):
		target_url = self.base / "domdfcoding" / "domdf_python_tools" / "master" / "LICENSE"

		assert target_url == URL("https://raw.githubusercontent.com/domdfcoding/domdf_python_tools/master/LICENSE")
		assert target_url.get().text.splitlines()[:11] == [
				"                   GNU LESSER GENERAL PUBLIC LICENSE",
				"                       Version 3, 29 June 2007",
				'',
				" Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>",
				" Everyone is permitted to copy and distribute verbatim copies",
				" of this license document, but changing it is not allowed.",
				'',
				'',
				"  This version of the GNU Lesser General Public License incorporates",
				"the terms and conditions of version 3 of the GNU General Public",
				"License, supplemented by the additional permissions listed below.",
				]

	def test_get_default_params(self, httpserver: pytest_httpserver.pytest_plugin.PluginHTTPServer):

		class QM(QueryMatcher):

			def get_comparing_values(self, request_query_string: bytes) -> tuple:
				return '', ''

			def match(self, request_query_string: bytes) -> bool:
				return True

		def handler(request: werkzeug.Request):
			headers = {"Content-Type": "application/json"}
			body = json.dumps(parse_qs(request.query_string.decode("UTF-8")))
			return werkzeug.Response(body, 200, headers, None, None)

		httpserver.expect_request("/query", method="GET", query_string=QM()).respond_with_handler(handler)

		url = RequestsURL(httpserver.url_for("/query?foo=bar&fizz=buzz"))
		assert url.get().json() == {"foo": ["bar"], "fizz": ["buzz"]}

		url = RequestsURL(httpserver.url_for("/query"))
		assert url.get(params={"bdfl": "Guido"}).json() == {"bdfl": ["Guido"]}

	def test_requests_integration(self, httpserver: pytest_httpserver.pytest_plugin.PluginHTTPServer):
		# We only need to test the wrapper; the actual implementations are tested by requests themselves.

		httpserver.expect_request("/testing_get", method="GET").respond_with_json("GET request succeeded")
		assert RequestsURL(httpserver.url_for("/testing_get")).get().json() == "GET request succeeded"

		def setup_response(method):
			route = f"/testing_{method.lower()}"
			data = f"This is a {method} request"
			response = f"{method} request succeeded"
			expect_request = httpserver.expect_request(route, method=method, data=data)
			expect_request.respond_with_json(response)
			return httpserver.url_for(route), data, response

		route, data, response = setup_response("POST")
		assert RequestsURL(route).post(data=data).json() == response

		route, data, response = setup_response("PUT")
		assert RequestsURL(route).put(data=data).json() == response

		route, data, response = setup_response("PATCH")
		assert RequestsURL(route).patch(data=data).json() == response

		route, data, response = setup_response("OPTIONS")
		assert RequestsURL(route).options(data=data).json() == response

		method = "DELETE"
		route = f"/testing_{method.lower()}"
		data = f"This is a {method} request"
		response = f"{method} failed successfully"
		expect_request = httpserver.expect_request(route, method=method, data=data)
		expect_request.respond_with_json(response)
		assert RequestsURL(httpserver.url_for(route)).delete(data=data).json() == response

		method = "HEAD"
		route = f"/testing_{method.lower()}"
		data = f"This is a {method} request"
		test_string = "HEAD request succeeded"
		httpserver.expect_request(route, method=method, data=data).respond_with_json(test_string)
		headers = RequestsURL(httpserver.url_for(route)).head(data=data).headers
		assert headers["Content-Type"] == "application/json"
		assert headers["Content-Length"] == str(len(repr(test_string)))
		assert headers["Server"].startswith("Werkzeug")
		assert "Date" in headers

	def test_equality(self):

		assert RequestsURL() == RequestsURL()
		assert URL() == RequestsURL()

		assert RequestsURL("bbc.co.uk") == RequestsURL("bbc.co.uk")
		assert URL("bbc.co.uk") == RequestsURL("bbc.co.uk")

		assert RequestsURL("https://bbc.co.uk") == RequestsURL("https://bbc.co.uk")
		assert URL("https://bbc.co.uk") == RequestsURL("https://bbc.co.uk")

		assert RequestsURL("bbc.co.uk/news") == RequestsURL("bbc.co.uk/news")
		assert URL("bbc.co.uk/news") == RequestsURL("bbc.co.uk/news")

		assert RequestsURL("bbc.co.uk") != RequestsURL("bbc.co.uk/news")
		assert RequestsURL("bbc.co.uk") != RequestsURL("http://bbc.co.uk/news")
		assert RequestsURL("bbc.co.uk") != RequestsURL("http://bbc.co.uk")

	def test_division_session(self):
		sess = requests.Session()
		l_url = RequestsURL("http://bbc.co.uk")
		l_url.session = sess
		new_url = l_url / "news"
		assert new_url.session is sess

		sess = requests.Session()
		l_url = RequestsURL("http://bbc.co.uk")
		new_url = l_url / "news"
		assert new_url.session is not sess


def test_subclass__eq__():

	assert RequestsURL() == SlumberURL()
	assert RequestsURL("bbc.co.uk") == SlumberURL("bbc.co.uk")
	assert RequestsURL("https://bbc.co.uk") == SlumberURL("https://bbc.co.uk")
	assert RequestsURL("bbc.co.uk/news") == SlumberURL("bbc.co.uk/news")


class TestTrailingRequestsURL(TestRequestsURL):

	_class = TrailingRequestsURL

	@pytest.mark.parametrize(
			"url, expects",
			[
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes/player/",
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes/player/"
							),
					(
							"www.bbc.co.uk/programmes/b006qtlx/episodes/player/",
							"www.bbc.co.uk/programmes/b006qtlx/episodes/player/"
							),
					("www.bbc.co.uk", "www.bbc.co.uk/"),
					("/programmes/b006qtlx/episodes/player", "/programmes/b006qtlx/episodes/player/"),
					("programmes/b006qtlx/episodes/player", "programmes/b006qtlx/episodes/player/"),
					(
							"https://127.0.0.1/programmes/b006qtlx/episodes/player",
							"https://127.0.0.1/programmes/b006qtlx/episodes/player/"
							),
					(
							"ftp://127.0.0.1/programmes/b006qtlx/episodes/player",
							"ftp://127.0.0.1/programmes/b006qtlx/episodes/player/"
							),
					]
			)
	def test_str(self, url, expects):
		assert str(self._class(url)) == expects
