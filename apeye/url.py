#!/usr/bin/env python
#
#  url.py
"""
:mod:`pathlib`-like approach to URLs.

.. versionchanged:: 1.0.0

	:class:`~apeye.slumber_url.SlumberURL` and :class:`~apeye.requests_url.RequestsURL`
	moved to :mod:`apeye.slumber_url` and :mod:`apeye.requests_url` respectively.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import collections
import ipaddress
import os
import pathlib
import re
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Tuple, Type, TypeVar, Union
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

# 3rd party
from domdf_python_tools.doctools import prettify_docstrings
from domdf_python_tools.typing import PathLike

# this package
from apeye import _tld

if TYPE_CHECKING:
	# stdlib
	from typing import NoReturn

__all__ = ["URL", "URLPath", "Domain", "URLType"]

#: Type variable bound to :class:`~apeye.url.URL`.
URLType = TypeVar("URLType", bound="URL")


@prettify_docstrings
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
			return self._str

	@classmethod
	def _format_parsed_parts(cls, drv, root, parts):
		if drv or root:
			return drv + root + pathlib._posix_flavour.join(parts[1:])  # type: ignore
		else:
			return pathlib._posix_flavour.join(parts)  # type: ignore

	def match(self, *args, **kwargs) -> "NoReturn":  # noqa: D102
		raise NotImplementedError

	def is_absolute(self, *args, **kwargs) -> "NoReturn":  # noqa: D102
		raise NotImplementedError

	def joinpath(self, *args, **kwargs) -> "NoReturn":  # noqa: D102
		raise NotImplementedError

	def relative_to(self, *args, **kwargs) -> "NoReturn":  # noqa: D102
		raise NotImplementedError

	@property
	def anchor(self):  # noqa: D102
		raise NotImplementedError

	@property
	def drive(self):  # noqa: D102
		raise NotImplementedError

	def __lt__(self, *args, **kwargs) -> "NoReturn":
		raise NotImplementedError

	def __le__(self, *args, **kwargs) -> "NoReturn":
		raise NotImplementedError

	def __gt__(self, *args, **kwargs) -> "NoReturn":
		raise NotImplementedError

	def __ge__(self, *args, **kwargs) -> "NoReturn":
		raise NotImplementedError

	def as_uri(self, *args, **kwargs) -> "NoReturn":  # noqa: D102
		raise NotImplementedError


class URL(os.PathLike):
	r"""
	:mod:`pathlib`-like class for URLs.

	:param url: The URL to construct the :class:`~apeye.url.URL` object from.

	.. versionchanged:: 0.3.0  The ``url`` parameter can now be a string or a :class:`~.URL`.

	.. autoclasssumm:: URL
		:autosummary-sections: Methods

	.. autosummary-widths:: 1/5

	.. autoclasssumm:: URL
		:autosummary-sections: Attributes
	"""

	#: URL scheme specifier
	scheme: str

	#: Network location part of the URL
	netloc: str

	#: The hierarchical path of the URL
	path: URLPath

	query: Dict[str, List[str]]
	"""
	The query parameters of the URL, if present.

	.. versionadded:: 0.7.0
	"""

	fragment: Optional[str]
	"""
	The URL fragment, used to identify a part of the document. :py:obj:`None` if absent from the URL.

	.. versionadded:: 0.7.0
	"""

	def __init__(self, url: Union[str, "URL"] = ''):
		if isinstance(url, URL):
			url = str(url)

		if not re.match("([A-Za-z-.]+:)?//", url):
			url = "//" + str(url)

		scheme, netloc, parts, params, query, fragment = urlparse(url)

		self.scheme: str = scheme
		self.netloc: str = netloc
		self.path = URLPath(parts)
		self.query = parse_qs(query or '')
		self.fragment = fragment or None

	@property
	def port(self) -> Optional[int]:
		"""
		The port of number of the URL as an integer, if present. Default :py:obj:`None`.

		.. versionadded:: 0.7.0
		"""

		if ':' not in self.netloc:
			return None
		else:
			return int(self.netloc.split(':')[-1])

	@classmethod
	def from_parts(
			cls: Type[URLType],
			scheme: str,
			netloc: str,
			path: PathLike,
			query: Optional[Mapping[Any, List]] = None,
			fragment: Optional[str] = None,
			) -> URLType:
		"""
		Construct a :class:`~apeye.url.URL` from a scheme, netloc and path.

		:param scheme: The scheme of the URL, e.g ``'http'``.
		:param netloc: The netloc of the URl, e.g. ``'bbc.co.uk:80'``.
		:param path: The path of the URL, e.g. ``'/news'``.
		:param query: The query parameters of the URL, if present.
		:param fragment: The URL fragment, used to identify a part of the document.
			:py:obj:`None` if absent from the URL.

		Put together, the resulting path would be ``'http://bbc.co.uk:80/news'``

		:rtype:

		.. versionchanged:: 0.7.0  Added the ``query`` and ``fragment`` arguments.
		"""

		obj = cls('')
		obj.scheme = scheme
		obj.netloc = netloc
		obj.query = dict(query or {})
		obj.fragment = fragment or None

		path = URLPath(path)

		if path.root == '/':
			obj.path = path
		else:
			obj.path = URLPath('/' + str(path))

		return obj

	def __str__(self) -> str:
		"""
		Returns the :class:`~apeye.url.URL` as a string.
		"""

		query = urlencode(self.query, doseq=True)
		url = urlunparse([self.scheme, self.netloc, str(self.path), None, query, self.fragment])

		if url.startswith("//"):
			return url[2:]
		else:
			return url

	def __repr__(self) -> str:
		"""
		Returns the string representation of the :class:`~apeye.url.URL`.
		"""

		return f"{self.__class__.__name__}({str(self)!r})"

	def __truediv__(self: URLType, key: Union[PathLike, int]) -> URLType:
		"""
		Construct a new :class:`~apeye.url.URL` object for the given child of this :class:`~apeye.url.URL`.

		:rtype:

		.. versionchanged:: 0.7.0

			* Added support for division by integers.

			* Now officially supports the new path having a URL fragment and/or query parameters.
			  Any URL fragment or query parameters from the parent URL is not inherited by its children.
		"""

		_key = key

		if isinstance(key, pathlib.PurePath):
			key = key.as_posix()
		elif isinstance(key, os.PathLike):
			key = os.fspath(key)
		elif isinstance(key, int):
			key = str(key)

		try:
			parse_result = urlparse(key)
		except AttributeError as e:
			if str(e).endswith("'decode'"):
				raise TypeError(
						f"unsupported operand type(s) for /: "
						f"'{type(self.path).__name__!r}' and {type(_key).__name__!r}",
						) from None
			else:
				raise

		try:
			new_path = self.from_parts(self.scheme, self.netloc, self.path / parse_result.path)
		except TypeError:
			return NotImplemented

		new_path.query = parse_qs(parse_result.query)
		new_path.fragment = parse_result.fragment or None

		return new_path

	def __fspath__(self) -> str:
		"""
		Returns the file system path representation of the :class:`~.URL`.
		"""

		return f"{self.netloc}{self.path}"

	def __eq__(self, other) -> bool:
		"""
		Return ``self == other``.

		.. latex:vspace:: -10px

		.. attention::

			URL fragments and query parameters are not compared.

			.. seealso:: :meth:`.URL.strict_compare`, which *does* consider those attributes.

		.. latex:vspace:: -20px
		"""

		if isinstance(other, URL):
			return self.netloc == other.netloc and self.scheme == other.scheme and self.path == other.path
		else:
			return NotImplemented

	def strict_compare(self, other) -> bool:
		"""
		Return ``self ≡ other``, comparing the scheme, netloc, path, fragment and query parameters.

		.. versionadded:: 0.7.0
		"""

		if isinstance(other, URL):
			return (
					self.netloc == other.netloc and self.scheme == other.scheme and self.path == other.path
					and self.query == other.query and self.fragment == other.fragment
					)
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

	def with_name(self: URLType, name: str, inherit: bool = True) -> URLType:
		"""
		Return a new :class:`~apeye.url.URL` with the file name changed.

		:param name:
		:param inherit: Whether the new :class:`~apeye.url.URL` should inherit the query string
			and fragment from this :class:`~apeye.url.URL`.

		:rtype:

		.. versionchanged:: 0.7.0  Added the ``inherit`` parameter.
		"""

		if inherit:
			kwargs = {"query": self.query, "fragment": self.fragment}
		else:
			kwargs = {}

		return self.from_parts(
				self.scheme,
				self.netloc,
				self.path.with_name(name),
				**kwargs,  # type: ignore
				)

	def with_suffix(self: URLType, suffix: str, inherit: bool = True) -> URLType:
		"""
		Returns a new :class:`~apeye.url.URL` with the file suffix changed.

		If the :class:`~apeye.url.URL` has no suffix, add the given suffix.

		If the given suffix is an empty string, remove the suffix from the :class:`~apeye.url.URL`.

		:param suffix:
		:param inherit: Whether the new :class:`~apeye.url.URL` should inherit the query string
			and fragment from this :class:`~apeye.url.URL`.

		:rtype:

		.. versionchanged:: 0.7.0  Added the ``inherit`` parameter.
		"""

		if inherit:
			kwargs = {"query": self.query, "fragment": self.fragment}
		else:
			kwargs = {}

		return self.from_parts(
				self.scheme,
				self.netloc,
				self.path.with_suffix(suffix),
				**kwargs,  # type: ignore
				)

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
	def parent(self: URLType) -> URLType:
		"""
		The logical parent of the :class:`~apeye.url.URL`.
		"""

		return self.from_parts(self.scheme, self.netloc, self.path.parent)

	@property
	def parents(self: URLType) -> Tuple[URLType, ...]:
		"""
		An immutable sequence providing access to the logical ancestors of the :class:`~apeye.url.URL`.
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
		Returns a :class:`apeye.url.Domain` object representing the domain part of the URL.
		"""

		return Domain._make(_tld.extract_tld(self.netloc))

	@property
	def base_url(self: URLType) -> URLType:
		"""
		Returns a :class:`apeye.url.URL` object representing the URL without query strings or URL fragments.

		.. versionadded:: 0.7.0
		"""

		return self.from_parts(
				self.scheme,
				self.netloc,
				self.path,
				)


class Domain(collections.namedtuple("Domain", "subdomain, domain, suffix")):
	"""
	:class:`typing.NamedTuple` of a URL's subdomain, domain, and suffix.
	"""

	subdomain: str
	domain: str
	suffix: str

	__slots__ = ()

	@property
	def registered_domain(self):
		"""
		Joins the domain and suffix fields with a dot, if they're both set.

		.. code-block:: python

			>>> URL('https://forums.bbc.co.uk').domain.registered_domain
			'bbc.co.uk'
			>>> URL('https://localhost:8080').domain.registered_domain
			''
		"""
		if self.domain and self.suffix:
			return self.domain + '.' + self.suffix
		return ''

	@property
	def fqdn(self):
		"""
		Returns a Fully Qualified Domain Name, if there is a proper domain/suffix.

		.. code-block:: python

			>>> URL('https://forums.bbc.co.uk/path/to/file').domain.fqdn
			'forums.bbc.co.uk'
			>>> URL('https://localhost:8080').domain.fqdn
			''
		"""
		if self.domain and self.suffix:
			# self is the namedtuple (subdomain domain suffix)
			return '.'.join(i for i in self if i)
		return ''

	@property
	def ipv4(self) -> Optional[ipaddress.IPv4Address]:
		"""
		Returns the ipv4 if that is what the presented domain/url is.

		.. code-block:: python

			>>> URL('https://127.0.0.1/path/to/file').domain.ipv4
			IPv4Address('127.0.0.1')
			>>> URL('https://127.0.0.1.1/path/to/file').domain.ipv4
			None
			>>> URL('https://256.1.1.1').domain.ipv4
			None
		"""

		if not (self.suffix or self.subdomain) and _tld.IP_RE.match(self.domain):
			return ipaddress.ip_address(self.domain)
		return None

	def __repr__(self) -> str:
		"""
		Return a string representation of the :class:`~.Domain`.
		"""

		return super().__repr__()
