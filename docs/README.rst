How to Work on Docs
===================

- Install docutils (see, e.g., https://learnxinyminutes.com/docs/rst/)::

    % pip install docutils

- Install sphinx (see, e.g., https://www.sphinx-doc.org/en/master/usage/installation.html)::

    % pip install sphinx

- Build the docs::

    % cd h1st/docs && make html

- Run local web server to preview the docs::
  
    % cd h1st/docs && run_local_server.sh

- Edit .rst doc files