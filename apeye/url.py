#!/usr/bin/env python
#
#  url.py
"""
Pathlib-like approach to URLs.
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

# stdlib
import copy
import ipaddress
import os
import pathlib
from typing import (
		IO,
		Any,
		Dict,
		Iterable,
		List,
		Mapping,
		MutableMapping,
		NoReturn,
		Optional,
		Sequence,
		Tuple,
		Type,
		TypeVar,
		Union
		)
from urllib.parse import urlparse

# 3rd party
import requests
import slumber  # type: ignore
import tldextract  # type: ignore
from domdf_python_tools.typing import PathLike
from requests.structures import CaseInsensitiveDict
from slumber import Serializer
from tldextract.remote import IP_RE  # type: ignore

__all__ = ["URL", "URLPath", "Domain", "RequestsURL", "SlumberURL"]

#: Type variable bound to :class:`~apeye.url.URL`.
URLType = TypeVar("URLType", bound="URL")


class URLPath(pathlib.PurePosixPath):
	"""
	Represents the path part of a URL.

	Subclass of :class:`pathlib.PurePosixPath` that provides a subset of its methods.
	"""

	def __str__(self) -> str:
		"""
		Return the string representation of the path, suitable for passing to system calls.
		"""

		try:
			return self._str  # type: ignore
		except AttributeError:
			self._str = self._format_parsed_parts(self._drv, self._root, self._parts) or ''  # type: ignore
			return self._str  # type: ignore

	@classmethod
	def _format_parsed_parts(cls, drv, root, parts):
		if drv or root:
			return drv + root + pathlib._posix_flavour.join(parts[1:])  # type: ignore
		else:
			return pathlib._posix_flavour.join(parts)  # type: ignore

	def match(self, *args, **kwargs) -> NoReturn:
		raise NotImplementedError

	def is_absolute(self, *args, **kwargs) -> NoReturn:
		raise NotImplementedError

	def joinpath(self, *args, **kwargs) -> NoReturn:
		raise NotImplementedError

	def relative_to(self, *args, **kwargs) -> NoReturn:
		raise NotImplementedError

	@property
	def anchor(self):
		raise NotImplementedError

	@property
	def drive(self):
		raise NotImplementedError

	def __lt__(self, *args, **kwargs) -> NoReturn:
		raise NotImplementedError

	def __le__(self, *args, **kwargs) -> NoReturn:
		raise NotImplementedError

	def __gt__(self, *args, **kwargs) -> NoReturn:
		raise NotImplementedError

	def __ge__(self, *args, **kwargs) -> NoReturn:
		raise NotImplementedError

	def as_uri(self, *args, **kwargs) -> NoReturn:
		raise NotImplementedError


class URL(os.PathLike):
	"""
	Pathlib-like class for URLs.

	:param url: The url to construct the :class:`~apeye.url.URL` object from.
	"""

	def __init__(self, url: str = ''):
		scheme, netloc, parts, *_ = urlparse(url)

		if not scheme and not str(url).startswith("//"):
			scheme, netloc, parts, *_ = urlparse("//" + str(url))

		self.scheme: str = scheme
		self.netloc: str = netloc
		self.path = URLPath(parts)

	@classmethod
	def from_parts(cls: Type[URLType], scheme: str, netloc: str, path: PathLike) -> URLType:
		"""
		Construct a :class:`~apeye.url.URL` from a scheme, netloc and path.

		:param scheme: The scheme of the URL, e.g ``'http'``.
		:param netloc: The netloc of the URl, e.g. ``'bbc.co.uk:80'``.
		:param path: The path of the URL, e.g. ``'/news'``.

		Put together, the resulting path would be ``'http://bbc.co.uk:80/news'``
		"""

		obj = cls('')
		obj.scheme = scheme
		obj.netloc = netloc

		path = URLPath(path)

		if path.root == "/":
			obj.path = path
		else:
			obj.path = URLPath("/" + str(path))

		return obj

	def __str__(self) -> str:
		"""
		Returns the :class:`~apeye.url.URL` as a string.
		"""

		if self.scheme:
			return f"{self.scheme}://{self.netloc}{self.path}"
		else:
			return f"{self.netloc}{self.path}"

	def __repr__(self) -> str:
		"""
		Returns the string representation of the :class:`~apeye.url.URL`.
		"""

		return f"{self.__class__.__name__}({str(self)!r})"

	def __truediv__(self: URLType, key: PathLike) -> URLType:
		"""
		Construct a new :class:`~apeye.url.URL` object for the given child of this :class:`~apeye.url.URL`.
		"""

		# TODO: division by int

		try:
			return self.from_parts(self.scheme, self.netloc, self.path / key)
		except TypeError:
			return NotImplemented

	def __fspath__(self) -> str:
		return f"{self.netloc}{self.path}"

	def __eq__(self, other) -> bool:
		"""
		Return ``self == other``
		"""

		if isinstance(other, URL):
			return self.netloc == other.netloc and self.scheme == other.scheme and self.path == other.path
		else:
			return NotImplemented

	def __hash__(self) -> int:
		"""
		Returns the has of the :class:`~apeye.url.URL` .
		"""

		return hash((self.scheme, self.netloc, self.path))

	@property
	def name(self) -> str:
		"""
		The final path component, if any.
		"""

		return self.path.name

	@property
	def suffix(self) -> str:
		"""
		The final component's last suffix, if any.

		This includes the leading period. For example: ``'.txt'``.
		"""
		return self.path.suffix

	@property
	def suffixes(self) -> List[str]:
		"""
		A list of the final component's suffixes, if any.

		These include the leading periods. For example: ``['.tar', '.gz']``.
		"""
		return self.path.suffixes

	@property
	def stem(self):
		"""
		The final path component, minus its last suffix.
		"""

		return self.path.stem

	def with_name(self, name: str) -> "URL":
		"""
		Return a new :class:`~apeye.url.URL` with the file name changed.
		"""

		return self.from_parts(self.scheme, self.netloc, self.path.with_name(name))

	def with_suffix(self, suffix: str) -> "URL":
		"""
		Returns a new :class:`~apeye.url.URL` with the file suffix changed.

		If the :class:`~apeye.url.URL` has no suffix, add the given suffix.

		If the given suffix is an empty string, remove the suffix from the :class:`~apeye.url.URL`.
		"""

		return self.from_parts(self.scheme, self.netloc, self.path.with_suffix(suffix))

	@property
	def parts(self) -> Tuple[str, ...]:
		"""
		An object providing sequence-like access to the components in the URL.

		To retrieve only the parts of the path, use :meth:`URL.path.parts <URLPath.parts>`.
		"""

		return (
				self.scheme,
				self.domain.subdomain,
				self.domain.domain,
				self.domain.suffix,
				*self.path.parts[1:],
				)

	@property
	def parent(self) -> "URL":
		"""
		The logical parent of the :class:`~apeye.url.URL`.
		"""

		return self.from_parts(self.scheme, self.netloc, self.path.parent)

	@property
	def parents(self) -> Tuple["URL", ...]:
		"""
		An immutable sequence providing access to the logical ancestors of the :class:`~apeye.url.URL` :
		"""

		return tuple(self.from_parts(self.scheme, self.netloc, path) for path in self.path.parents)

	@property
	def fqdn(self) -> str:
		"""
		Returns the Fully Qualified Domain Name of the :class:`~apeye.url.URL` .
		"""

		return self.domain.fqdn

	@property
	def domain(self) -> "Domain":
		"""
		Returns a :class:`apeye.url.Domain` object representing the domain part of the url.
		"""

		extract: tldextract.tldextract.ExtractResult = tldextract.extract(self.netloc)
		return Domain(extract.subdomain, extract.domain, extract.suffix)


_ParamsType = Optional[Union[Mapping[Union[str, bytes, int, float], "_ParamsMappingValueType"],
								Union[str, bytes],
								Tuple[Union[str, bytes, int, float], "_ParamsMappingValueType"], ]]


class RequestsURL(URL):
	"""
	Extension of :class:`~apeye.url.URL` with support for interacting with the website using the
	`Requests <https://requests.readthedocs.io>`__ library.

	The :class:`requests.Session` used for this object, and all objects created using the
	``/`` or ``.parent`` operations, can be accessed using the ``.session`` attribute.
	If desired, this can be replaced with a different session object, such as one using caching.

	:param url: The url to construct the :class:`~apeye.url.URL` object from.
	"""

	def __init__(self, url: str = ''):
		super().__init__(url)
		self.session = requests.Session()

	def get(self, params: _ParamsType = None, **kwargs) -> requests.Response:
		"""
		Perform a GET request using `Requests <https://requests.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET

		:param params: (optional) Dictionary, list of tuples or bytes to send
			in the query string for the :class:`requests.Request`.
		:param kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.get(str(self), params=params, **kwargs)

	def options(self, **kwargs) -> requests.Response:
		"""
		Send an OPTIONS request using `Requests <https://requests.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS

		:param kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.options(str(self), **kwargs)

	def head(self, **kwargs) -> requests.Response:
		"""
		Send a HEAD request using `Requests <https://requests.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/HEAD

		:param kwargs: Optional arguments that :func:`requests.request` takes.
			If `allow_redirects` is not provided, it will be set to `False`
			(as opposed to the default :func:`requests.request` behavior).
		"""

		return self.session.head(str(self), **kwargs)

	def post(self, data: "_Data" = None, json=None, **kwargs) -> requests.Response:
		"""
		Send a POST request using `Requests <https://requests.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST

		:param data: (optional) Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param json: (optional) json data to send in the body of the :class:`requests.Request`.
		:param kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.post(str(self), data=data, json=json, **kwargs)

	def put(self, data: "_Data" = None, json=None, **kwargs) -> requests.Response:
		"""
		Send a PUT request using `Requests <https://requests.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PUT

		:param data: (optional) Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param json: (optional) json data to send in the body of the :class:`requests.Request`.
		:param kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.put(str(self), data=data, json=json, **kwargs)

	def patch(self, data: "_Data" = None, json=None, **kwargs) -> requests.Response:
		"""
		Send a PATCH request using `Requests <https://requests.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PATCH

		:param data: (optional) Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param json: (optional) json data to send in the body of the :class:`requests.Request`.
		:param kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.patch(str(self), data=data, json=json, **kwargs)

	def delete(self, **kwargs) -> requests.Response:
		"""
		Send a DELETE request using `Requests <https://requests.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/DELETE

		:param kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.delete(str(self), **kwargs)

	def __del__(self):
		"""
		Attempt to close session when garbage collected to avoid leaving connections open.
		"""

		self.session.close()

	def __truediv__(self, other):
		"""
		Construct a new :class:`~apeye.url.URL` object for the given child of this :class:`~apeye.url.URL`.
		"""

		new_obj = super().__truediv__(other)

		if new_obj is not NotImplemented:
			new_obj.session = self.session

		return new_obj


_ParamsMappingValueType = Union[str, bytes, int, float, Iterable[Union[str, bytes, int, float]]]
_Data = Union[None, str, bytes, MutableMapping[str, Any], Iterable[Tuple[str, Optional[str]]], IO]


class Domain(tldextract.tldextract.ExtractResult):
	subdomain: str
	domain: str
	suffix: str

	@property
	def ipv4(self) -> Optional[ipaddress.IPv4Address]:
		"""
		Returns the ipv4 if that is what the presented domain/url is

		>>> URL('http://127.0.0.1/path/to/file').domain.ipv4
		IPv4Address('127.0.0.1')
		>>> URL('http://127.0.0.1.1/path/to/file').domain.ipv4
		None
		>>> URL('http://256.1.1.1').domain.ipv4
		None
		"""

		if not (self.suffix or self.subdomain) and IP_RE.match(self.domain):
			return ipaddress.ip_address(self.domain)
		return None


class SlumberURL(URL):
	"""
	Subclass of :class:`~apeye.url.URL` with support for interacting with
	REST APIs with `Slumber <https://slumber.readthedocs.io>`__ and `Requests <https://requests.readthedocs.io>`__.

	:param url: The url to construct the :class:`~.SlumberURL` object from.
	:param auth:
	:param format:
	:param append_slash:
	:param session:
	:param serializer:
	"""

	def __init__(self, url: str = '', auth=None, format=None, append_slash=True, session=None, serializer=None):
		super().__init__(url)

		if serializer is None:
			serializer = Serializer(default=format)

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

	def url(self):
		url = str(self)

		if self._store["append_slash"] and not url.endswith("/"):
			url = url + "/"

		return url

	_request = slumber.Resource._request
	_try_to_serialize_response = slumber.Resource._try_to_serialize_response
	_process_response = slumber.Resource._process_response

	def get(self, **params) -> Dict:
		"""
		Perform a GET request using `Slumber <https://slumber.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET

		:param params: Parameters to send in the query string of the :class:`requests.Request`.
		"""

		resp = self._request("GET", params=params)
		return self._process_response(resp)

	def post(self, data: "_Data" = None, files=None, **params) -> Dict:
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

		return new_obj
