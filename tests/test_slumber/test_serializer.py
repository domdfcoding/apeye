# stdlib
import unittest

# this package
from apeye.slumber_url import JsonSerializer, SerializerRegistry, YamlSerializer


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
		s = SerializerRegistry()

		for content_type in ["text/yaml"]:
			serializer = s.get_serializer(content_type=content_type)
			assert type(serializer) == YamlSerializer, "content_type %s should produce a YamlSerializer"

		result = serializer.dumps(self.data)
		assert result == "foo: bar\n"
		assert self.data == serializer.loads(result)
