# Contributing guidelines

## Pull Request Checklist

Before sending your pull requests, make sure you followed this list.

- Read [contributing guidelines](CONTRIBUTING.md).
- Read [Code of Conduct] [TBD]
- Check if my changes are consistent with the [guidelines]: TBD
- Changes are consistent with the [Coding Style] (TBD)
- Run [Unit Tests]: ``nose2``

## How to become a contributor and submit your own code


### Contributing code

If you have improvements to graphengine, send us your pull requests! For those
just getting started, Github has a
[how to](https://help.github.com/articles/using-pull-requests/).

Before sending your pull request for
[review](https://https://github.com/adatao/graphengine/pulls),
make sure your changes are consistent with the guidelines and follow the
graphengine coding style (TBD).

#### General guidelines and philosophy for contribution

*   Include unit tests when you contribute new features, as they help to a)
    prove that your code works correctly, and b) guard against future breaking
    changes to lower the maintenance cost.
*   Bug fixes also generally require unit tests, because the presence of bugs
    usually indicates insufficient test coverage.
*   Keep API compatibility in mind when you change code in core GraphEngine. 
*   Tests should follow the basic principles:
**  Only depend on what you use in your requirements. 
**  All code should have unit tests.
**  Each class should have its own unit test file. 
**  Smaller tests are better. 
**  Always use seed if you're using any stochasticity functions. 
**  Avoid using sleep in multi thread tests.
**  Avoid using external resource in tests e.g: S3, requests to external services: download model from repos etc. 

#### License

TBD

#### Python coding style

Changes to code should conform to
[Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md)

Use `pylint` to check your Python changes. To install `pylint` and check a file
with `pylint` against graphengine custom style definition TBD

#### Running unit tests
Using tools and libraries installed directly on your system.
    For example, to run all tests under graphengine, do:

    ```bash
    nose2
    ```
