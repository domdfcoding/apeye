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

			if not type(serializer) == JsonSerializer:  # pylint: disable=unidiomatic-typecheck
				raise AssertionError("content_type %s should produce a JsonSerializer")

		result = serializer.dumps(self.data)
		assert result == '{"foo": "bar"}'
		assert self.data == serializer.loads(result)

	def _test_yaml_get_serializer(self):
		s = SerializerRegistry()

		for content_type in ["text/yaml"]:
			serializer = s.get_serializer(content_type=content_type)

			if not type(serializer) == YamlSerializer:  # pylint: disable=unidiomatic-typecheck
				raise AssertionError("content_type %s should produce a YamlSerializer")

		result = serializer.dumps(self.data)
		assert result == "foo: bar\n"
		assert self.data == serializer.loads(result)

	def test_yaml_get_serializer(self):
		try:
			# 3rd party
			import yaml  # noqa: F401

			self._test_yaml_get_serializer()

		except ImportError:
			try:

				# 3rd party
				import ruamel.yaml  # type: ignore[import]  # noqa: F401

				self._test_yaml_get_serializer()

			except ImportError:

				s = SerializerRegistry()

				with pytest.raises(SerializerNotAvailable, match=f"No serializer available for 'yaml'."):
					s.get_serializer("yaml")

				with pytest.raises(SerializerNotAvailable, match=f"No serializer available for 'text/yaml'."):
					s.get_serializer(content_type="text/yaml")
