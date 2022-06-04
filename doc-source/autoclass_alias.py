# stdlib
import inspect
from typing import Any, Callable, Dict, List

# 3rd party
from sphinx.application import Sphinx
from sphinx_toolbox.more_autodoc import generic_bases
from sphinx_toolbox.more_autodoc.overloads import FunctionDocumenter
from sphinx_toolbox.more_autosummary import PatchedAutoSummClassDocumenter
from sphinx_toolbox.utils import SphinxExtMetadata


def alias_option(arg: Any) -> List[str]:
	"""
	Used to convert the :members: option to auto directives.
	"""

	if arg is None:
		return []
	else:
		return [x.strip() for x in arg.split(',') if x.strip()]


class AliasedClassDocumenter(generic_bases.GenericBasesClassDocumenter):

	option_spec: Dict[str, Callable] = {
			**PatchedAutoSummClassDocumenter.option_spec,
			"autoclass-alias": alias_option,
			}

	def add_directive_header(self, sig: str) -> None:
		"""
		Add the directive's header, and the inheritance information if the ``:show-inheritance:`` flag set.

		:param sig: The NamedTuple's signature.
		"""

		if "autoclass-alias" not in self.options:
			return super().add_directive_header(sig)

		if self.doc_as_attr:
			self.directivetype = "attribute"

		domain = getattr(self, "domain", "py")
		directive = getattr(self, "directivetype", self.objtype)
		name = self.format_name()
		sourcename = self.get_sourcename()

		if '\n' in sig:
			raise NotImplementedError(sig)

		# one signature per line, indented by column
		prefix = f'.. {domain}:{directive}:: '
		for i, sig_line in enumerate(sig.split('\n')):
			self.add_line(f'{prefix}{name}{sig_line}', sourcename)
			if i == 0:
				prefix = ' ' * len(prefix)

		# for i, alias in enumerate(self.options["autoclass-alias"]):
		# 	self.add_line(f'{prefix}{alias}{sig}', sourcename)
		# 	if i == 0:
		# 		prefix = ' ' * len(prefix)
		#
		# if self.objpath:
		# 	self.add_line(f'{prefix}{name}{sig}', sourcename)

		if self.options.noindex:
			self.add_line("   :noindex:", sourcename)

		if self.objpath:
			# Be explicit about the module, this is necessary since .. class::
			# etc. don't support a prepended module name
			self.add_line(f"   :module: {self.modname}", sourcename)

		self.add_line(f"   :canonical: {self.options['autoclass-alias'][0]}", sourcename)

		if self.analyzer and '.'.join(self.objpath) in self.analyzer.finals:
			self.add_line("   :final:", sourcename)

		# add inheritance info, if wanted
		if not self.doc_as_attr and self.options.show_inheritance:
			generic_bases._add_generic_bases(self)


class AliasedFunctionDocumenter(FunctionDocumenter):

	option_spec: Dict[str, Callable] = {
			**FunctionDocumenter.option_spec,
			"autofunction-alias": alias_option,
			}

	def add_directive_header(self, sig: str) -> None:
		"""
		Add the directive's header.

		:param sig:
		"""

		if "autofunction-alias" not in self.options:
			return super().add_directive_header(sig)

		domain = getattr(self, "domain", "py")
		directive = getattr(self, "directivetype", self.objtype)
		name = self.format_name()
		sourcename = self.get_sourcename()

		if '\n' in sig:
			raise NotImplementedError(sig)

		# one signature per line, indented by column
		prefix = f".. {domain}:{directive}:: "
		for i, sig_line in enumerate(sig.split('\n')):
			self.add_line(f'{prefix}{name}{sig_line}', sourcename)
			if i == 0:
				prefix = ' ' * len(prefix)

		# for i, alias in enumerate(self.options["autofunction-alias"]):
		# 	self.add_line(f'{prefix}{alias}{sig}', sourcename)
		# 	if i == 0:
		# 		prefix = ' ' * len(prefix)
		#
		# if self.objpath:
		# 	self.add_line(f'{prefix}{name}{sig}', sourcename)

		if self.options.noindex:
			self.add_line("   :noindex:", sourcename)

		if self.objpath:
			# Be explicit about the module, this is necessary since .. class::
			# etc. don't support a prepended module name
			self.add_line(f"   :module: {self.modname}", sourcename)

		self.add_line(f"   :canonical: {self.options['autofunction-alias'][0]}", sourcename)

		if inspect.iscoroutinefunction(self.object):
			self.add_line("   :async:", sourcename)

		if self.env.config.overloads_location == "top":
			for line in self.create_body_overloads():
				self.add_line(f"{self.content_indent}{line}", self.get_sourcename())


def setup(app: Sphinx) -> SphinxExtMetadata:
	app.add_autodocumenter(AliasedClassDocumenter, override=True)
	app.add_autodocumenter(AliasedFunctionDocumenter, override=True)
	return {"parallel_read_safe": True}
