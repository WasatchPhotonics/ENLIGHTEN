# WP-ENLIGHTEN PyPi (pip) Package

ENLIGHTEN has moved into a PyPi (pip) package, allowing expedited command-line
installation and execution on compliant POSIX platforms including MacOS 
(Intel/ARM), Raspberry Pi (Linux/ARM), Linux x86/x64, and Windows (Git for 
Windows Bash and WSL).

# Instructions to _INSTALL_ and _RUN_ ENLIGHTEN from pip

These instructions show how to _install_ and _run_ ENLIGHTEN, from the PyPi 
package, in any Bash shell (Windows, MacOS, Linux or Raspberry Pi)

    $ mkdir ~/any/dir
    $ cd ~/any/dir
    $ python3 -m venv venv                  # may need to use "python" or "py" 
    $ . venv/*/activate                     # may be venv/Scripts/activate on Windows, venv/bin/activate everywhere else
    (venv) $ pip install wp-enlighten
    (venv) $ enlighten

That's it. On successive executions, it's even shorter:

    $ cd ~/any/dir
    $ . venv/*/activate
    (venv) $ enlighten

## What are each of these steps doing?

    $ python3 -m venv venv

This runs Python (version 3+), and tells it to import _and run_ the module "venv"
(virtualenv), passing the directory name `venv` as an argument. Some people 
prefer to put their virtual environments in a folder called `.env/`, so they would
run `python3 -m venv .env`. You can name your environment anything you want.

After running this command, you will have a new folder named `venv/` (or `.env/`) in
your directory. Under that folder you will have a folder named `venv/bin/` (or 
`venv/Scripts/` on Windows), which contains commands and scripts including 
`activate`. You will also have a folder called `venv/lib/` which will end up 
holding all the package dependencies you later install with `pip`.

**To emphasize:** when you run `pip` in a few minutes, you will NOT be installing
packages to your "system" Python environment; you will only be installing them
within your local "venv" virtual environment. This is incredibly important and
useful, because it means that different applications (like, ENLIGHTEN vs some
other Python application like Wasatch's FW-Util) can use different versions of
common packages like Numpy, or even different versions of Python altogether.

    $ . venv/bin/activate

Now that you've "created" your empty "venv" virtual environment, you need to
SOURCE this script to "activate" it.

NOTE THAT YOU ARE NOT "running" `venv/bin/activate`, at least not as a "command."
If you did that, it would spawn a sub-shell to run the command, and when the
command completed it would then close the sub-shell and return you to your 
original parent shell. As a result, IT IS IMPOSSIBLE for a script to modify
your ACTIVE environment, at least when "running the script as a command."

Instead, by "sourcing" the activate script using that leading `. ` (period 
followed by a space), you are running each line of that script inside your 
_current_ shell, as though you had typed it yourself. This allows the `activate`
script to modify your _current_ environment, including creating and exporting the
`$VIRTUAL_ENV` environment variable and changing your command prompt to include 
`(venv)`.

    (venv) $ pip install wp-enlighten

First of all, note that we now have an extra `(venv)` prefix in our command
prompt -- this reminds us that we have "activated" a Python virtual environment,
so any Python commands (including `pip`) will only run within, and modify, that
local environment.

In this case, the command we are running, `pip install wp-enlighten`, tells 
pip to download and install the wp-enlighten package, _along with all of its
dependencies._

The package it is downloading can be found here:

- https://pypi.org/project/wp-enlighten/

The dependencies it will install are listed in the `pyproject.toml` file in
the GitHub project you are currently reading.

As stated above, all dependencies will be installed to your 
`venv/lib/python3.14/site-packages` folder.

There is one more thing the `pip install` command does: it can install new
executable scripts in your venv/bin/ folder. In this case, it installs a new
script called `venv/bin/enlighten`. You can verify the script like this:

    (venv) $ which enlighten
    venv/bin/enlighten

    (venv) $ cat venv/bin/enlighten

In so many words, this short script essentially runs this:

    $ python3 venv/lib/python3.14/site-packages/wp_enlighten/app.py

This `venv/bin/enlighten` "command" is automatically created as part of the PyPi
packaging system by the `[project.gui-scripts]` target in pyproject.toml.

# Instructions to _MAINTAIN_ ENLIGHTEN

If you are an ENLIGHTEN maintainer, the process to update and test ENLIGHTEN
is not much different than described above.

## Run ENLIGHTEN from source (test local changes)

The most basic developer "test loop" is to be able to change some Python files, 
then immediately run ENLIGHTEN "from source" to test the changes. Fortunately we
can easily achieve this within the packaging process:

    $ git clone git@github.com:WasatchPhotonics/ENLIGHTEN.git enlighten
    $ cd enlighten
    $ python -m venv venv
    $ . venv/*/activate
    (venv) $ pip install -e .                   # install wp-enlighten package as "edittable"
    (venv) $ enlighten                          # run ENLIGHTEN from source

    # edit and test Python changes
    (venv) $ vi src/wp_enlighten/Controller.py  
    (venv) $ enlighten

    # edit and test GUI changes
    (venv) $ vi src/wp_enlighten/assets/uic_qrc/enlighten_layout.ui
    (venv) $ scripts/rebuild_resources.sh
    (venv) $ enlighten

As always, if you want to change logging level, or redirect stdout or stderr to 
files, you can do so:

    (venv) $ enlighten --log-level debug 2>enlighten.err 1>enlighten.out

## What does "pip install -e ." do?

Well, if we typed `pip install .` it would have installed all ENLIGHTEN's 
dependencies into venv/lib/python*/site-packages, and then it would have 
installed wp_enlighten itself into the same location. Then when you ran 
`enlighten`, it would have been running the "published" package under 
`venv/lib/python*/site-packages/wp_enlighten`, not the locally-modified 
`src/wp_enlighten/*` files you wanted.

So instead we run `pip install -e .` which puts _something_ into site-packages,
but a little different. Let's have a look:

    (venv) $ ls -la venv/lib/python3.14/site-packages | grep enlighten
    -rw-rw-r--   1 mzieg staff      36 Oct 20 16:30 _editable_impl_wp_enlighten.pth
    drwxrwxr-x  10 mzieg staff     320 Oct 20 16:30 wp_enlighten-4.3.1.dist-info

So you can see wp_enlighten's "dist-info" there, but not a "wp_enlighten" folder
itself. Instead, you see file offering an "editable implementation of 
wp_enlighten path". If you peek inside that file, it literally says:

    (venv) $ cat venv/lib/python3.14/site-packages/_editable_impl_wp_enlighten.pth
    /Users/mzieg/work/code/enlighten/src

So in other words, when Python tries to import or access a "wp-enlighten" package,
it will find that "editable path", and direct Python to use whatever it finds in
the cloned source code workspace.

## What if I want to test local changes to Wasatch.PY?

Standard `PYTHONPATH` manipulation is all that's needed if you want to test 
ENLIGHTEN with a locally modified Wasatch.PY.

Let's start the same as above, but adding a local clone of Wasatch.PY:

    $ git clone git@github.com:WasatchPhotonics/ENLIGHTEN.git enlighten
    $ git clone git@github.com:WasatchPhotonics/Wasatch.PY.git
    $ cd enlighten
    $ python -m venv venv
    $ . venv/*/activate
    (venv) $ pip install -e .

As before, this will download the PyPi project "wasatch" as a dependency
declared in ENLIGHTEN's `pyproject.toml`, and install the downloaded package
in `venv/lib/python/site-packages/wasatch`. We want to ignore that "downloaded"
package, and instead use our locally cloned repo:

    # insert local Wasatch.PY workspace at the front of Python's search path
    (venv) $ export PYTHONPATH=../Wasatch.PY

Now let's make some changes to "our" Wasatch.PY and test them:

    # edit and test Python changes
    (venv) $ vi ../Wasatch.PY/wasatch/FeatureIdentificationDevice.py
    (venv) $ enlighten

# Releasing new PyPi package updates

To generate a new "wheel" for upload to PyPi, just type:

    $ . venv/*/activate
    (venv) $ python -m build

This will generate two new files under dist/:

    -rw-r--r-- 1 mzieg staff 51343830 Oct 5 18:01 wp_enlighten-4.2.15-py3-none-any.whl
    -rw-r--r-- 1 mzieg staff 54653109 Oct 5 18:01 wp_enlighten-4.2.15.tar.gz

One of those is a "wheel" provided for "any" architecture (meaning it's composed
of "pure Python" and should work on "any" operating system). The other is a 
compressed tarball of the current source code snapshot. It's polite to build and
upload both.

When releasing this new wheel to the world, we should first test that our "build-
chain" is working by pushing to the "test" PyPi repository:

    $ python -m twine upload --repository testpypi dist/wp-enlighten*
    (or "make publish-test")

If that works, proceed to the actual production repository:

    $ python -m twine upload dist/wp-enlighten*
    (or "make publish")

Note that you can NEVER re-push a new wheel with an old version number; you MUST
move to new version numbers each time.

## Common Problems

### Wasatch.PY version

It is important that new ENLIGHTEN installers be built with the intended 
(presumably most-recent) Wasatch.PY version. When testing a new ENLIGHTEN
installer, you can always see the Wasatch.PY version in the very beginning
of ~/Documhents/EnlightenSpectra/enlighten.log. If that version is older
than you expect (e.g. 2.5.1 when you expected 2.5.2), make sure you have
done ALL the following:

    $ deactivate
    $ unset PYTHONPATH

    $ cd ~/work/code/Wasatch.PY
    $ rm -rf venv
    $ python -m venv
    $ . venv/*/activate
    (venv) $ rm dist/wasatch-*

    (venv) $ pip install .
    (venv) $ python -m build
    (venv) $ make publish-test
    (venv) $ make publish

    (venv) $ deactivate
    $ cd ~/work/code/enlighten
    $ rm -rf venv
    $ python -m venv
    $ . venv/*/activate
    (venv) $ rm dist/wp_enlighten-*

    (venv) $ pip install .
    (venv) $ diff -r venv/Lib/site-packages/wasatch ../Wasatch.PY/wasatch | grep -v __pycache__

    (venv) $ python -m build
    (venv) $ scripts/make_windows_installer.sh
    (venv) $ ./ENLIGHTEN*exe

    (test new installer)

    (venv) $ scripts/deploy
    (venv) $ make publish-test
    (venv) $ make publish

# Referenced Documents

- [Packaging Tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
