A collection of useful utilities shared a cross a number of [Bits In Glass](https://www.bitsinglass.com) projects.

### What is this repository for? ###

This repository a collection of useful, common utilities used over and over again in a number of 
[BIG](https://www.bitsinglass.com) projects.

### How do I get set up? ###

This is a library to be included in other projects.

Dependencies should be installed automatically, but here is the `pip` command for those who like to do things manually:

    pip install --upgrade pyjwt pytest pytest-mock wheel

Alternatively, run this command:

    pip install --upgrade -r requirements.txt

To run unit tests (using `pytest`), execute the following command:

    pytest -v tests/*

### Publishing to PyPI ###

**Important Note:** The procedure is adopted from an excellent article on [Real Python](https://realpython.com/pypi-publish-python-package/).

To upload our package to PyPI, use a tool called `Twine`. We can install Twine using `pip` as usual:

    pip install twine

#### Building the Package ####

To create a source archive and a wheel for our package, run the following command:

    python setup.py sdist bdist_wheel

This will create two files in a newly created dist directory, a source archive, and a wheel:

![Dist directory Screenshot](https://d.pr/i/hfcmTI+)

Twine (1.12.0 and above) can also check that our package description will render properly on PyPI. Run twine check on the files created in `dist`:

    twine check dist/*

![twine check dist/* output screenshot](https://d.pr/i/gU8RNp+)

While it won’t catch all problems we might run into, it will for instance let us know if we are using the wrong content type.

#### Uploading the Package ####

Now we’re ready to actually upload our package to PyPI. For this, we’ll again use the `twine` tool, telling it to upload the distribution packages we have built. First, we should upload to *TestPyPI* to make sure everything works as expected:

    twine upload --repository-url https://test.pypi.org/legacy/ dist/*

Twine will ask you for our username and password, which can be found in the *LastPass*.

**NOTE:** The TestPyPI password is different from the actual PyPI.

If the upload succeeds, we can quickly head over to [TestPyPI](https://test.pypi.org/), scroll down, and look at our project being proudly displayed among the new releases! Click on our package and make sure everything looks okay.

With all the preparations taken care of, this final step is short:

    twine upload dist/*

Provide our username and password when requested. That’s it!

Head over to PyPI and look up our package - `big-utils`. We can find it either by searching, by looking at the *Your projects* page, or by going directly to the [URL of our project](https://pypi.org/project/big-utils/).