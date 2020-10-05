#!/usr/bin/env python
#
#  slumber_url.py
"""
Subclass of :class:`~apeye.url.URL` with support for interacting with
REST APIs with `Slumber <https://slumber.readthedocs.io>`__ and
`Requests <https://requests.readthedocs.io>`__.

.. versionadded:: 0.2.0
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Based on the "pathlib" module from CPython.
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com. All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives. All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum. All rights reserved.
#
#  Based on Slumber <https://slumber.readthedocs.io>
#  Copyright (c) 2011 Donald Stufft
#  Licensed under the 2-clause BSD License
#
#  Some docstrings from Requests <https://requests.readthedocs.io>
#  Copyright 2019 Kenneth Reitz
#  Licensed under the Apache License, Version 2.0
#

# stdlib
import copy
import json
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Mapping, MutableMapping, Optional, Tuple, Type, Union
from urllib.parse import unquote

# 3rd party
import requests
from requests import Request
from requests.auth import AuthBase
from requests.structures import CaseInsensitiveDict
from requests.utils import guess_json_utf

# this package
from apeye._url import URL
from apeye.requests_url import _Data

__all__ = [
		"SlumberURL",
		"SerializerRegistry",
		"YamlSerializer",
		"Serializer",
		"JsonSerializer",
		"SlumberBaseException",
		"SlumberHttpBaseException",
		"HttpClientError",
		"HttpNotFoundError",
		"HttpServerError",
		"SerializerNotAvailable",
		]


class Serializer(ABC):
	"""
	Base class for serializers.
	"""

	@property
	@abstractmethod
	def content_types(self) -> List[str]:
		"""
		List of supported content types.
		"""

		return NotImplemented

	@property
	@abstractmethod
	def key(self) -> str:
		return NotImplemented

	def get_content_type(self) -> str:
		"""
		Returns the first value from :attr:`~.Serializer.content_types`.
		"""

		return self.content_types[0]

	@abstractmethod
	def loads(self, data: str) -> MutableMapping[str, Any]:
		"""
		Deserialize data using this :class:`~.Serializer`.

		:param data:
		"""

		raise NotImplementedError()

	@abstractmethod
	def dumps(self, data: Mapping[str, Any]) -> str:
		"""
		Serialize data using this :class:`~.Serializer`.

		:param data:
		"""

		raise NotImplementedError()


class JsonSerializer(Serializer):
	"""
	Serializer for JSON data.
	"""

	content_types = [
			"application/json",
			"application/x-javascript",
			"text/javascript",
			"text/x-javascript",
			"text/x-json",
			]
	key = "json"

	def loads(self, data: str) -> MutableMapping[str, Any]:
		return json.loads(data)

	def dumps(self, data: Mapping[str, Any]) -> str:
		return json.dumps(data)


_SERIALIZERS: List[Type[Serializer]] = [JsonSerializer]

try:
	# 3rd party
	import yaml

	class YamlSerializer(Serializer):
		"""
		Serializer for YAML data.
		"""

		content_types = ["text/yaml"]
		key = "yaml"

		def loads(self, data: str) -> MutableMapping[str, Any]:
			return yaml.safe_load(str(data))

		def dumps(self, data: Mapping[str, Any]) -> str:
			return yaml.dump(data)

	_SERIALIZERS.append(YamlSerializer)

except ImportError:

	class YamlSerializer(Serializer):  # type: ignore
		"""
		Serializer for YAML data.
		"""

		content_types = ["text/yaml"]
		key = "yaml"

		def __init__(self):
			raise NotImplementedError("'yaml' package not available.")


class SerializerRegistry:
	"""
	Serializes and deserializes data for transfer to and from a REST API.

	:param default: The default serializer to use if none is specified.
		Corresponds to the :attr:`~.Serializer.key` of a :class:`~.Serializer`.
	:param serializers: List of :class:`~.Serializer` objects to use.
	"""

	def __init__(self, default: str = "json", serializers: Optional[List[Serializer]] = None):

		#: Mapping of formats to :class:`~.Serializer` objects.
		self.serializers: Dict[str, Serializer] = {}

		for serializer in serializers or [x() for x in _SERIALIZERS]:
			self.serializers[serializer.key] = serializer

		#: The default serializer to use if none is specified.
		self.default: str = default

	def get_serializer(self, name: Optional[str] = None, content_type: Optional[str] = None):
		"""
		Returns the first :class:`~.Serializer` that supports either the given
		format or the given content type.

		:param name:
		:param content_type:
		"""

		if name is None and content_type is None:
			return self.serializers[self.default]

		elif name is not None and content_type is None:
			if name not in self.serializers:
				raise SerializerNotAvailable(f"{name} is not an available serializer")
			return self.serializers[name]

		else:
			for x in self.serializers.values():
				for ctype in x.content_types:
					if content_type == ctype:
						return x

			raise SerializerNotAvailable(f"{content_type} is not an available serializer")

	def loads(self, data: str, format: Optional[str] = None) -> MutableMapping[str, Any]:
		"""
		Deserialize data of the given format.

		:param data:
		:param format: The serialization format to use.
		"""

		s = self.get_serializer(format)
		return s.loads(data)

	def dumps(self, data: Mapping[str, Any], format: Optional[str] = None) -> str:
		"""
		Serialize data of the given format.

		:param data:
		:param format: The serialization format to use.
		"""

		s = self.get_serializer(format)
		return s.dumps(data)

	def get_content_type(self, format: Optional[str] = None):
		"""
		Returns the content type for the serializer that supports the given format.

		:param format: The desired serialization format.
		"""

		s = self.get_serializer(format)
		return s.get_content_type()


class SlumberURL(URL):
	"""
	Subclass of :class:`~apeye.url.URL` with support for interacting with
	REST APIs with `Slumber <https://slumber.readthedocs.io>`__ and
	`Requests <https://requests.readthedocs.io>`__.

	:param url: The url to construct the :class:`~.SlumberURL` object from.
	:param auth:
	:param format:
	:param append_slash:
	:param session:
	:param serializer: (optional) An instance of :class:`apeye.url.SerializerRegistry`.
	:param timeout: (optional) How long to wait for the server to send
		data before giving up.
	:param allow_redirects: Whether to allow redirects. .
	:param proxies: (optional) Dictionary mapping protocol or protocol and
		hostname to the URL of the proxy.
	:param verify: (optional) Either a boolean, in which case it controls whether we verify
		the server's TLS certificate, or a string, in which case it must be a path
		to a CA bundle to use.
	:param cert: (optional) if String, path to ssl client cert file (.pem).
		If Tuple, ('cert', 'key') pair.

	``timeout``, ``allow_redirects``, ``proxies``, ``verify`` and ``cert`` are
	passed to Requests when making any HTTP requests, and are inherited by all children
	created from this URL.
	"""

	serializer: SerializerRegistry
	session: requests.Session

	#: How long to wait for the server to send data before giving up.
	timeout: Union[None, float, Tuple[float, float], Tuple[float, None]]

	#: Whether to allow redirects.
	allow_redirects: Optional[bool]

	#: Dictionary mapping protocol or protocol and hostname to the URL of the proxy.
	proxies: Optional[MutableMapping[str, str]]

	verify: Union[None, bool, str]
	"""
	Either a boolean, in which case it controls whether we verify
	the server's TLS certificate, or a string, in which case it must be a path
	to a CA bundle to use.
	"""

	#: The path to ssl client cert file or a ('cert', 'key') pair.
	cert: Union[str, Tuple[str, str], None]

	def __init__(
			self,
			url: str = '',
			auth: Union[None, Tuple[str, str], AuthBase, Callable[[Request], Request]] = None,
			format: str = "json",
			append_slash=True,
			session=None,
			serializer: Optional[SerializerRegistry] = None,
			*,
			timeout: Union[None, float, Tuple[float, float], Tuple[float, None]] = None,
			allow_redirects: Optional[bool] = True,
			proxies: Optional[MutableMapping[str, str]] = None,
			verify: Union[None, bool, str] = None,
			cert: Union[str, Tuple[str, str], None] = None,
			):
		super().__init__(url)

		if serializer is None:
			serializer = SerializerRegistry(default=format)

		if session is None:
			session = requests.session()

		if auth is not None:
			session.auth = auth

		self._store = {
				"format": format if format is not None else "json",
				"append_slash": append_slash,
				"session": session,
				"serializer": serializer,
				}

		self.timeout = timeout
		self.allow_redirects = allow_redirects
		self.proxies = proxies
		self.verify = verify
		self.cert = cert

	def url(self):
		url = str(self)

		if self._store["append_slash"] and not url.endswith("/"):
			url = url + "/"

		return url

	def _request(self, method, data=None, files=None, params=None):
		serializer = self._store["serializer"]
		url = self.url()

		headers = {"accept": serializer.get_content_type()}

		if not files:
			headers["content-type"] = serializer.get_content_type()
			if data is not None:
				data = serializer.dumps(data)

		resp = self._store["session"].request(
				method,
				url,
				data=data,
				params=params,
				files=files,
				headers=headers,
				timeout=self.timeout,
				allow_redirects=self.allow_redirects,
				proxies=self.proxies,
				verify=self.verify,
				cert=self.cert,
				)

		if 400 <= resp.status_code <= 499:
			exception_class = HttpNotFoundError if resp.status_code == 404 else HttpClientError
			raise exception_class(
					f"Client Error {resp.status_code}: {unquote(resp.url)}",
					response=resp,
					content=resp.content,
					)

		elif 500 <= resp.status_code <= 599:
			raise HttpServerError(
					f"Server Error {resp.status_code}: {unquote(resp.url)}",
					response=resp,
					content=resp.content,
					)

		self._ = resp

		return resp

	def _try_to_serialize_response(self, resp):
		s = self._store["serializer"]
		if resp.status_code in [204, 205]:
			return

		if resp.headers.get("content-type", None) and resp.content:
			content_type = resp.headers.get("content-type").split(";")[0].strip()

			try:
				stype = s.get_serializer(content_type=content_type)
			except SerializerNotAvailable:
				return resp.content

			if type(resp.content) == bytes:
				try:
					encoding = guess_json_utf(resp.content)
					return stype.loads(resp.content.decode(encoding))
				except:
					return resp.content
			return stype.loads(resp.content)
		else:
			return resp.content

	def _process_response(self, resp):
		# TODO: something to expose headers and status

		if 200 <= resp.status_code <= 299:
			return self._try_to_serialize_response(resp)
		else:
			return  # @@@ We should probably do some sort of error here? (Is this even possible?)

	def get(self, **params) -> Dict:
		"""
		Perform a GET request using `Slumber <https://slumber.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET

		:param params: Parameters to send in the query string of the :class:`requests.Request`.
		"""

		resp = self._request("GET", params=params)
		return self._process_response(resp)

	def post(self, data: _Data = None, files=None, **params) -> Dict:
		"""
		Perform a POST request using `Slumber <https://slumber.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST

		:param data: (optional) Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param files: (optional) Dictionary of ``'name': file-like-objects``
			(or ``{'name': file-tuple}``) for multipart encoding upload.
			``file-tuple`` can be a 2-tuple ``('filename', fileobj)``,
			3-tuple ``('filename', fileobj, 'content_type')``
			or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``,
			where ``'content-type'`` is a string defining the content type of the
			given file and ``custom_headers`` a dict-like object containing additional
			headers to add for the file.
		:param params: Parameters to send in the query string of the :class:`requests.Request`.
		"""

		resp = self._request("POST", data=data, files=files, params=params)
		return self._process_response(resp)

	def patch(self, data=None, files=None, **params) -> Dict:
		"""
		Perform a PATCH request using `Slumber <https://slumber.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PATCH

		:param data: (optional) Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param files: (optional) Dictionary of ``'name': file-like-objects``
			(or ``{'name': file-tuple}``) for multipart encoding upload.
			``file-tuple`` can be a 2-tuple ``('filename', fileobj)``,
			3-tuple ``('filename', fileobj, 'content_type')``
			or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``,
			where ``'content-type'`` is a string defining the content type of the
			given file and ``custom_headers`` a dict-like object containing additional
			headers to add for the file.
		:param params: Parameters to send in the query string of the :class:`requests.Request`.
		"""

		resp = self._request("PATCH", data=data, files=files, params=params)
		return self._process_response(resp)

	def put(self, data=None, files=None, **params) -> Dict:
		"""
		Perform a PUT request using `Slumber <https://slumber.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PUT

		:param data: (optional) Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param files: (optional) Dictionary of ``'name': file-like-objects``
			(or ``{'name': file-tuple}``) for multipart encoding upload.
			``file-tuple`` can be a 2-tuple ``('filename', fileobj)``,
			3-tuple ``('filename', fileobj, 'content_type')``
			or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``,
			where ``'content-type'`` is a string defining the content type of the
			given file and ``custom_headers`` a dict-like object containing additional
			headers to add for the file.
		:param params: Parameters to send in the query string of the :class:`requests.Request`.
		"""

		resp = self._request("PUT", data=data, files=files, params=params)
		return self._process_response(resp)

	def delete(self, **params) -> bool:
		"""
		Perform a DELETE request using `Slumber <https://slumber.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/DELETE

		:param params: Parameters to send in the query string of the :class:`requests.Request`.

		:returns: :py:obj:`True` if the DELETE request succeeded. :py:obj:`False` otherwise.
		"""

		resp = self._request("DELETE", params=params)
		if 200 <= resp.status_code <= 299:
			if resp.status_code == 204:
				return True
			else:
				return True
		else:
			return False

	def __del__(self):
		self._store["session"].close()

	def options(self, **kwargs) -> str:
		"""
		Send an OPTIONS request using `Requests <https://requests.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS

		:param kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self._store["session"].options(str(self), **kwargs).headers.get("Allow", '')

	def head(self, **kwargs) -> CaseInsensitiveDict:
		"""
		Send a HEAD request using `Requests <https://requests.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/HEAD

		:param kwargs: Optional arguments that :func:`requests.request` takes.
			If `allow_redirects` is not provided, it will be set to :py:obj:`False`
			(as opposed to the default :func:`requests.request` behavior).
		"""

		return self._store["session"].head(str(self), **kwargs).headers

	def __truediv__(self, other):
		"""
		Construct a new :class:`~apeye.url.URL` object for the given child of this :class:`~apeye.url.URL`.
		"""

		new_obj = super().__truediv__(other)

		if new_obj is not NotImplemented:
			new_obj._store = copy.copy(self._store)
			new_obj.timeout = self.timeout
			new_obj.allow_redirects = self.allow_redirects
			new_obj.proxies = self.proxies
			new_obj.verify = self.verify
			new_obj.cert = self.cert

		return new_obj


class SlumberBaseException(Exception):
	"""
	All Slumber exceptions inherit from this exception.
	"""


class SlumberHttpBaseException(SlumberBaseException):
	"""
	All Slumber HTTP Exceptions inherit from this exception.
	"""

	def __init__(self, *args, **kwargs):
		for key, value in kwargs.items():
			setattr(self, key, value)
		super().__init__(*args)


class HttpClientError(SlumberHttpBaseException):
	"""
	Called when the server tells us there was a client error (4xx).
	"""


class HttpNotFoundError(HttpClientError):
	"""
	Called when the server sends a 404 error.
	"""


class HttpServerError(SlumberHttpBaseException):
	"""
	Called when the server tells us there was a server error (5xx).
	"""


class SerializerNotAvailable(SlumberBaseException):
	"""
	The chosen Serializer is not available.
	"""
