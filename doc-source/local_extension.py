# stdlib
from typing import Optional

# 3rd party
from docutils import nodes
from domdf_python_tools.paths import PathPlus
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import admonitionlabels
from sphinx.util.docutils import SphinxRole
from sphinx.writers.latex import LaTeXTranslator
from sphinx_toolbox import latex


def visit_seealso(translator: LaTeXTranslator, node: addnodes.seealso) -> None:
	"""
	Visit an :class:`addnodes.seealso`` node.

	:param translator:
	:param node:
	"""

	if len(node) > 1:
		LaTeXTranslator.visit_seealso(translator, node)
	else:
		translator.body.append('\n\n\\sphinxstrong{%s:} ' % admonitionlabels["seealso"])


def replace_latex(app: Sphinx, exception: Optional[Exception] = None):
	if exception:
		return

	if app.builder.name.lower() != "latex":
		return

	output_file = PathPlus(app.builder.outdir) / f"{app.builder.titles[0][1]}.tex"

	output_content = output_file.read_text()

	output_content = output_content.replace('≡', r"$\equiv$")
	output_content = output_content.replace(
			r"@\spxentry{verify}\spxextra{SlumberURL attribute}}\needspace{5\baselineskip}",
			r"@\spxentry{verify}\spxextra{SlumberURL attribute}}",
			)

	output_file.write_clean(output_content)


class RequestsXRef(SphinxRole):

	def run(self):
		return [
				nodes.reference(
						"`Requests <https://requests.readthedocs.io>`_",
						"Requests",
						refuri="https://requests.readthedocs.io"
						)
				], []


def setup(app: Sphinx):
	app.connect("build-finished", replace_latex)
	app.connect("build-finished", latex.replace_unknown_unicode)
	app.add_node(addnodes.seealso, latex=(visit_seealso, LaTeXTranslator.depart_seealso), override=True)
	app.add_role("requests", RequestsXRef())
