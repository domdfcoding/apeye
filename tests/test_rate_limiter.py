# stdlib
import logging
import re
import sys
import time
from datetime import datetime

# 3rd party
import pytest
import requests

# this package
from apeye.rate_limiter import HTTPCache, rate_limit

if sys.version_info < (3, 7):
	# 3rd party
	from backports.datetime_fromisoformat import MonkeyPatch
	MonkeyPatch.patch_fromisoformat()

logging.basicConfig()


@rate_limit(1)  # logger=logger
def rate_limited_function():
	print("Inside function")
	return 42


def test_rate_limit(capsys, caplog):
	assert rate_limited_function() == 42
	assert rate_limited_function() == 42
	assert rate_limited_function() == 42

	assert capsys.readouterr().out.splitlines() == ["Inside function"] * 3
	caplog.set_level(logging.DEBUG)

	assert rate_limited_function() == 42
	assert rate_limited_function() == 42
	time.sleep(2)
	assert rate_limited_function() == 42

	assert capsys.readouterr().out.splitlines() == ["Inside function"] * 3

	last_ran_re = re.compile(r"rate_limited_function: Last ran (\d+(\.\d+)?|\d+e-\d+) seconds ago\.")

	assert last_ran_re.match(caplog.record_tuples[0][2])
	assert re.match(r"rate_limited_function: Waiting (\d+(\.\d+)?|\d+e-\d+) seconds\.", caplog.record_tuples[1][2])
	assert last_ran_re.match(caplog.record_tuples[2][2])
	assert last_ran_re.match(caplog.record_tuples[3][2])


@pytest.fixture(scope="session")
def testing_http_cache():
	cache = HTTPCache("testing_apeye_http")
	assert cache.clear()
	yield cache

	cache.clear()


@pytest.mark.flaky(reruns=2, reruns_delay=20)
def test_cache_canary():
	# Proves that worldtimeapi.org returns a different time for two sequential requests.
	session = requests.session()

	target_url = "http://worldtimeapi.org/api/ip"

	response = session.get(target_url)
	assert response.status_code == 200
	original_time = datetime.fromisoformat(response.json()["datetime"])  # type: ignore

	response = session.get(target_url)
	assert response.status_code == 200
	current_time = datetime.fromisoformat(response.json()["datetime"])  # type: ignore

	assert current_time > original_time


@pytest.mark.flaky(reruns=2, reruns_delay=20)
@pytest.mark.parametrize("run_number", [1, 2])
def test_http_cache(testing_http_cache, capsys, run_number):
	session = testing_http_cache.session

	target_url = "http://worldtimeapi.org/api/ip"

	response = session.get(target_url)
	assert response.status_code == 200
	assert not response.from_cache
	original_time = datetime.fromisoformat(response.json()["datetime"])  # type: ignore

	response = session.get(target_url)
	assert response.status_code == 200
	assert response.from_cache
	current_time = datetime.fromisoformat(response.json()["datetime"])  # type: ignore

	# If the times have changed the cache has failed.
	assert current_time == original_time

	assert testing_http_cache.cache_dir.is_dir()
	assert testing_http_cache.clear()
	assert not testing_http_cache.cache_dir.is_dir()

	# make a new request
	response = session.get(target_url)
	assert response.status_code == 200
	assert not response.from_cache
	current_time = datetime.fromisoformat(response.json()["datetime"])  # type: ignore

	assert current_time > original_time

	assert testing_http_cache.clear()
