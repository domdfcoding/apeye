# stdlib
import unittest

# 3rd party
import pytest

# this package
from apeye.slumber_url import JsonSerializer, SerializerNotAvailable, SerializerRegistry, YamlSerializer


class ResourceTestCase(unittest.TestCase):

	def setUp(self):
		self.data = {"foo": "bar"}

	def test_json_get_serializer(self):
		s = SerializerRegistry()

		for content_type in [
				"application/json",
				"application/x-javascript",
				"text/javascript",
				"text/x-javascript",
				"text/x-json",
				]:
			serializer = s.get_serializer(content_type=content_type)
			assert type(serializer) == JsonSerializer, "content_type %s should produce a JsonSerializer"

		result = serializer.dumps(self.data)
		assert result == '{"foo": "bar"}'
		assert self.data == serializer.loads(result)

	def test_yaml_get_serializer(self):
		try:
			# 3rd party
			import yaml

			s = SerializerRegistry()

			for content_type in ["text/yaml"]:
				serializer = s.get_serializer(content_type=content_type)
				assert type(serializer) == YamlSerializer, "content_type %s should produce a YamlSerializer"

			result = serializer.dumps(self.data)
			assert result == "foo: bar\n"
			assert self.data == serializer.loads(result)

		except ImportError:
			s = SerializerRegistry()

			with pytest.raises(SerializerNotAvailable, match=f"No serializer available for 'yaml'."):
				s.get_serializer("yaml")

			with pytest.raises(SerializerNotAvailable, match=f"No serializer available for 'text/yaml'."):
				s.get_serializer(content_type="text/yaml")
