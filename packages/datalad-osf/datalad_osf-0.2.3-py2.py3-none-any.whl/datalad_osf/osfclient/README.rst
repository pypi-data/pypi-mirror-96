.. image:: LOGO/osf-cli-logo-v1-small.png
   :alt: osfclient
   :align: right

*********
osfclient
*********

|travisbadge|

The ``osfclient`` is a python library and a command-line client for up-
and downloading files to and from your `Open Science
Framework <//osf.io>`__ projects. The *Open Science Framework* (OSF) is
an open source project which facilitates the open collaboration of
researchers on the web, by sharing data and other research outputs.

As such the OSF hosts large data sets, associated with papers or
scientific projects, that can be freely downloaded. The *osfclient*
allows people to store and retrieve large datasets associated to their
scientific projects and papers on the OSF via the command line
interface. If you are completely new to the OSF you can `read their
introductory materials <https://cos.io/our-products/open-science-framework/>`__

This is a very new project, it has some rough edges.

.. |travisbadge| image:: https://travis-ci.org/osfclient/osfclient.svg?branch=master
   :target: https://travis-ci.org/osfclient/osfclient

Installing
==========

To use ``osfclient`` install it via pip:

::

    $ pip install osfclient

For details on participating in the development of ``osfclient`` check
out the `Contributing
section <https://github.com/dib-lab/osf-cli#contributing>`__.

Usage
=====

This project provides two things: a python library and a command-line
program for interacting with files stored in the
`OSF <https://osf.io/>`__.

The python library forms the basis for the command-line program. If you
want programmatic access to your files use the library, otherwise try
out the command-line program.

Read the full documentation: http://osfclient.readthedocs.io/en/latest/

Below are some examples on how to use it:

::

    # get help and see available commands, get help on a specific command
    $ osf -h
    $ osf <command> -h

    # setup a local folder for an existing project
    $ osf init

    # list all files for the project
    $ osf ls

    # fetch all files for the project
    $ osf clone
    
    # fetch an individual file from a project
    $ osf fetch remote/path.txt local/file.txt
    
    # add a new file
    $ osf upload local/file.txt remote/path.txt

    # add a new directory
    $ osf upload -r local/directory/ remote/directory

If the project is private you will need to provide authentication
details. The password will be retrieved from the ``OSF_PASSWORD``
environment variable or you will be asked directly by the tool when you
run it.

You can set default values by using a configuration file in the
current directory. This is what ``osf init`` does for you. To set the
username and project ID create ``.osfcli.config``:

::

    [osf]
    username = yourOSFaccount@example.com
    project = 9zpcy

after which you can simply run ``osf ls`` to list the contents of the
project.

Contributing
============

Contributions from everyone and anyone are welcome. Fork this
repository, make your changes, add a test to cover them and create a
Pull Request. Then one of the maintainers will review your changes. When
all comments have been addressed and all tests pass your changes will be
merged.

To setup a development version:

::

    $ git clone https://github.com/YOURNAMEHERE/osfclient
    $ git remote add upstream https://github.com/osfclient/osfclient
    $ cd osfclient
    $ pip install -r devRequirements.txt
    $ pip install -e.

There are a few secret keys relevant to this project, like passwords to
pypi.org, test.pypi.org, and the osfclient email account. We store these in an
encrypted git repo on `Keybase <//keybase.io>`__. If you need access to this
repo, contact any of the following maintainters on Keybase:

- Tim Head (@betatim)
- Ben Lindsay (@benlindsay)

For more details and instructions: `CONTRIBUTING.md <CONTRIBUTING.md>`__
