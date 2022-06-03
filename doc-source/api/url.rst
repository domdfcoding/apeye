===================
:mod:`apeye.url`
===================

.. rst-class:: source-link

	**Source code:** :source:`apeye_core/__init__.py`

--------------------

.. autosummary-widths:: 35/100

.. automodule:: apeye.url
	:no-members:
	:autosummary-members:

.. autotypevar:: apeye.url.URLType
.. autotypevar:: apeye.url.URLPathType

.. latex:clearpage::

.. autoclass:: apeye.url.URL
	:autoclass-alias: apeye_core.URL
	:exclude-members: __lt__,__le__,__gt__,__ge__
	:inherited-members:

.. latex:vspace:: 20px
.. autosummary-widths:: 1/4

.. autoclass:: apeye.url.URLPath
	:autoclass-alias: apeye_core.URLPath
	:exclude-members: match,as_posix,anchor,drive,__lt__,__le__,__gt__,__ge__,as_uri,__reduce__
	:autosummary-exclude-members: match,as_posix,anchor,drive,__lt__,__le__,__gt__,__ge__,as_uri,__hash__,__new__,__weakref__,__reduce__
	:inherited-members:

.. autonamedtuple:: apeye.url.Domain
	:inherited-members: tuple
	:special-members:
	:no-show-inheritance:
