#!/usr/bin/env python3
#
#  __init__.py
"""
Handy tools for working with URLs and APIs.
"""
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# this package
from apeye import cache
from apeye.requests_url import RequestsURL, TrailingRequestsURL
from apeye.slumber_url import SlumberURL
from apeye.url import URL, Domain, URLPath

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"
__license__: str = "GNU Lesser General Public License v3 or later (LGPLv3+)"
__version__: str = "0.9.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = [
		"URL",
		"Domain",
		"URLPath",
		"RequestsURL",
		"TrailingRequestsURL",
		"SlumberURL",
		"cache",
		]

try:
	# this package
	from apeye import rate_limiter
	__all__.append("rate_limiter")

except ImportError:
	pass
