#!/usr/bin/env python
#
#  url.py
"""
:mod:`pathlib`-like approach to URLs.

.. versionchanged:: 0.2.0

	:class:`~apeye.slumber_url.SlumberURL` and :class:`~apeye.requests_url.RequestsURL`
	moved to :mod:`apeye.slumber_url` and :mod:`apeye.requests_url` respectively,
	but can still be imported from this module.
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
import sys

# this package
from apeye._url import URL, Domain, URLPath, URLType
from apeye.requests_url import RequestsURL
from apeye.slumber_url import SlumberURL

__all__ = ["URL", "URLPath", "Domain", "RequestsURL", "SlumberURL", "URLType"]

#: Fiddle __module__ so these *look* like they were defined in this file.
URL.__module__ = "apeye.url"
Domain.__module__ = "apeye.url"
URLPath.__module__ = "apeye.url"

if sys.version_info >= (3, 7):  # pragma: no cover (<py37)
	URLType.__module__ = "apeye.url"
