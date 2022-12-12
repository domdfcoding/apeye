# stdlib
import json
import logging
import re
import sys
import time
from datetime import datetime

# 3rd party
import pytest
import requests
from pytest_httpserver import HTTPServer
from werkzeug import Request, Response

# this package
from apeye.rate_limiter import HTTPCache, rate_limit

if sys.version_info < (3, 7):
	# 3rd party
	from backports.datetime_fromisoformat import datetime_fromisoformat

else:
	datetime_fromisoformat = datetime.fromisoformat

logging.basicConfig()


@rate_limit(3)
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

	print(caplog.record_tuples)

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


@pytest.fixture()
def timeserver(httpserver: HTTPServer):

	def time_handler(request: Request):
		time.sleep(1)

		now = datetime.utcnow()
		headers = {
				"Cache-Control": "max-age=0, private, must-revalidate",
				"Date": now.strftime("%a, %d %B %Y %H:%M:%S GMT"),
				}
		response_json = {
				"abbreviation": "GMT",
				"client_ip": "127.0.0.1",
				"datetime": now.strftime("%Y-%m-%dT%H:%M:%S%z"),
				"day_of_week": now.strftime("%w"),
				"day_of_year": now.strftime("%j"),
				}

		return Response(json.dumps(response_json, indent=4), 200, headers, None, None)

	httpserver.expect_request("/time", method="GET").respond_with_handler(time_handler)

	return httpserver


def test_cache_canary(timeserver: HTTPServer):
	# Proves that worldtimeapi.org returns a different time for two sequential requests.
	session = requests.session()

	# target_url = "http://worldtimeapi.org/api/ip"
	target_url = timeserver.url_for("/time")

	response = session.get(target_url)
	assert response.status_code == 200
	original_time = datetime_fromisoformat(response.json()["datetime"])

	response = session.get(target_url)
	assert response.status_code == 200
	current_time = datetime_fromisoformat(response.json()["datetime"])

	assert current_time > original_time


@pytest.mark.parametrize("run_number", [1, 2])
def test_http_cache(testing_http_cache, capsys, run_number: int, timeserver: HTTPServer):
	session = testing_http_cache.session

	# target_url = "http://worldtimeapi.org/api/ip"
	target_url = timeserver.url_for("/time")

	response = session.get(target_url)
	assert response.status_code == 200
	assert not response.from_cache
	original_time = datetime_fromisoformat(response.json()["datetime"])

	response = session.get(target_url)
	assert response.status_code == 200
	assert response.from_cache
	current_time = datetime_fromisoformat(response.json()["datetime"])

	# If the times have changed the cache has failed.
	assert current_time == original_time

	assert testing_http_cache.cache_dir.is_dir()
	assert testing_http_cache.clear()
	assert not testing_http_cache.cache_dir.is_dir()

	# make a new request
	response = session.get(target_url)
	assert response.status_code == 200
	assert not response.from_cache
	current_time = datetime_fromisoformat(response.json()["datetime"])

	assert current_time > original_time

	assert testing_http_cache.clear()
