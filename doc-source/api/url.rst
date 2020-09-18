===================
:mod:`apeye.url`
===================

.. automodule:: apeye.url
	:no-members:
	:autosummary-members:

.. data:: apeye.url.URLType
	:annotation: = TypeVar("URLType", bound="URL")

	Type variable bound to :class:`~apeye.url.URL`.

.. autoclass:: apeye.url.URL
	:inherited-members:

.. autoclass:: apeye.url.URLPath
	:exclude-members: match,is_absolute,joinpath,relative_to,anchor,drive,__lt__,__le__,__gt__,__ge__,as_uri
	:autosummary-exclude-members: match,is_absolute,joinpath,relative_to,anchor,drive,__lt__,__le__,__gt__,__ge__,as_uri
	:inherited-members:

.. autoclass:: apeye.url.Domain
	:inherited-members:

.. autoclass:: apeye.url.RequestsURL
	:inherited-members:

.. autoclass:: apeye.url.SlumberURL
	:inherited-members:
