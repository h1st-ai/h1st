# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
PYTHON        = python3

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Build the api
api:
	sphinx-apidoc \
  		--force \
  		--implicit-namespaces \
  		--maxdepth 9 \
  		--separate \
  		--module-first \
		--output-dir source/api \
		../h1st
	# Removing package suffix from module names
	@echo "Cleaning up."
	(cd source/api ; $(PYTHON) clean-up.py)
	@echo "API documentation finished."

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

