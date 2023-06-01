# SPDX-FileCopyrightText: 2015 Eric Larson
#
# SPDX-License-Identifier: Apache-2.0
#
# From https://github.com/ionrock/cachecontrol

# 3rd party
import pytest
from cachecontrol.cache import DictCache
from requests import Session

# this package
from apeye.rate_limiter import RateLimitAdapter


class NullSerializer:

	def dumps(self, request, response, body=None):
		return response

	def loads(self, request, data, body_file=None):
		if data and getattr(data, "chunked", False):
			data.chunked = False
		return data


class TestMaxAge:

	@pytest.fixture()
	def sess(self, url):
		self.url = url
		self.cache = DictCache()
		sess = Session()
		adapter = RateLimitAdapter(
				self.cache,
				serializer=NullSerializer()  # type: ignore[arg-type]  # NullSerializer is not the right type
				)
		sess.mount("http://", adapter)
		return sess

	def test_client_max_age_0(self, sess):
		"""
		Making sure when the client uses max-age=0 we don't get a
		cached copy even though we're still fresh.
		"""
		print("first request")
		r = sess.get(self.url)
		assert self.cache.get(self.url) == r.raw

		print("second request")
		r = sess.get(self.url, headers={"Cache-Control": "max-age=0"})

		# don't remove from the cache
		assert self.cache.get(self.url)
		assert not r.from_cache

	def test_client_max_age_3600(self, sess):
		"""
		Verify we get a cached value when the client has a
		reasonable max-age value.
		"""
		r = sess.get(self.url)
		assert self.cache.get(self.url) == r.raw

		# request that we don't want a new one unless
		r = sess.get(self.url, headers={"Cache-Control": "max-age=3600"})
		assert r.from_cache is True

		# now lets grab one that forces a new request b/c the cache
		# has expired. To do that we'll inject a new time value.
		resp = self.cache.get(self.url)
		assert resp is not None
		resp.headers[  # type: ignore[attr-defined]  # something is wrong in CacheControl's new type hints
				"date"] = "Tue, 15 Nov 1994 08:12:31 GMT"
		r = sess.get(self.url)
		assert not r.from_cache
