#  This file is managed by 'repo_helper'. Don't edit it directly.

__all__ = ["extras_require"]

extras_require = {
		"limiter": [
				"cachecontrol[filecache]>=0.12.6",
				'filelock>=3.8.0; python_version >= "3.7"',
				'lockfile>=0.12.2; python_version < "3.7"'
				],
		"all": [
				"cachecontrol[filecache]>=0.12.6",
				'filelock>=3.8.0; python_version >= "3.7"',
				'lockfile>=0.12.2; python_version < "3.7"'
				]
		}
