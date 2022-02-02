How to Work on Docs
===================

- Install docutils (see, e.g., https://learnxinyminutes.com/docs/rst/)::

    % pip install docutils
    % sudo apt install python3-docutils # on Ubuntu

- Install sphinx (see, e.g., https://www.sphinx-doc.org/en/master/usage/installation.html)::

    % pip install sphinx sphinx-rtd-theme
    % sudo apt install python3-sphinx python3-sphinx-rtd-theme # on Ubuntu

- Install auto api 
    % pip install sphinx-autoapi

- Build the Concepts & Tutorials docs::

    % cd h1st/docs && make html

- Run local web server to preview the docs::
  
    % cd h1st/docs && run-local-server.sh

- Edit .rst doc files
