How to Work on Docs
===================

- Install docutils (see, e.g., https://learnxinyminutes.com/docs/rst/)::

    % pip install docutils

- Install sphinx (see, e.g., https://www.sphinx-doc.org/en/master/usage/installation.html)::

    % pip install sphinx

(Optional, only run this step if there are changes in the api)
- Build the api::

    % cd h1st/docs && build_api.sh

- Build the docs::

    % cd h1st/docs && make html

- Run local web server to preview the docs::
  
    % cd h1st/docs && run_local_server.sh

- Edit .rst doc files