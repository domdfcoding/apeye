#!/usr/bin/env python
#
#  _url.py
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
#  Based on Slumber <https://slumber.readthedocs.io>
#  Copyright (c) 2011 Donald Stufft
#  Licensed under the 2-clause BSD License
#
#  Some docstrings from Requests <https://requests.readthedocs.io>
#  Copyright 2019 Kenneth Reitz
#  Licensed under the Apache License, Version 2.0
#

# stdlib
import ipaddress
import os
import pathlib
from typing import List, NoReturn, Optional, Tuple, Type, TypeVar
from urllib.parse import urlparse

# 3rd party
import tldextract  # type: ignore
from domdf_python_tools.doctools import prettify_docstrings
from domdf_python_tools.typing import PathLike
from tldextract.remote import IP_RE  # type: ignore

__all__ = ["URL", "URLPath", "Domain", "URLType"]

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


@prettify_docstrings
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
