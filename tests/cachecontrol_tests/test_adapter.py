# SPDX-FileCopyrightText: 2015 Eric Larson
#
# SPDX-License-Identifier: Apache-2.0
#
# From https://github.com/ionrock/cachecontrol

# stdlib
from typing import Iterator

# 3rd party
import pytest
from cachecontrol.wrapper import CacheControl
from requests import Session

# this package
from apeye.rate_limiter import RateLimitAdapter


def use_wrapper() -> Session:
	print("Using helper")
	sess = CacheControl(Session())
	return sess


def use_adapter() -> Session:
	print("Using adapter")
	sess = Session()
	sess.mount("http://", RateLimitAdapter())
	return sess


@pytest.fixture(params=[use_adapter, use_wrapper])
def sess(url: str, request) -> Iterator[Session]:
	sess = request.param()
	sess.get(url)
	yield sess

	# closing session object
	sess.close()


class TestSessionActions:

	def test_get_caches(self, url: str, sess: Session):
		r2 = sess.get(url)
		assert r2.from_cache is True  # type: ignore[attr-defined]

	def test_get_with_no_cache_does_not_cache(self, url: str, sess: Session):
		r2 = sess.get(url, headers={"Cache-Control": "no-cache"})
		assert not r2.from_cache  # type: ignore[attr-defined]

	def test_put_invalidates_cache(self, url: str, sess: Session):
		r2 = sess.put(url, data={"foo": "bar"})
		sess.get(url)
		assert not r2.from_cache  # type: ignore[attr-defined]

	def test_patch_invalidates_cache(self, url: str, sess: Session):
		r2 = sess.patch(url, data={"foo": "bar"})
		sess.get(url)
		assert not r2.from_cache  # type: ignore[attr-defined]

	def test_delete_invalidates_cache(self, url: str, sess: Session):
		r2 = sess.delete(url)
		sess.get(url)
		assert not r2.from_cache  # type: ignore[attr-defined]
