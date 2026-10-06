# wp-enlighten PyPi (pip) Package Installation

ENLIGHTEN is experimentally being moved into a PyPi (pip) package, with the goal
of an expedited installation and execution process on compliant POSIX platforms
(including MacOS Intel/ARM, Raspberry Pi, Linux x86/x64, and potentially Windows)
like this:

    $ mkdir ~/some/new/dir
    $ cd ~/some/new/dir
    $ python -m venv venv
    $ . venv/bin/activate
    (venv) $ pip install wp-enlighten
    (venv) $ enlighten

TODO:

- update scripts/deploy to validate version number between .toml and common.py, 
  then perform build and twine upload
- probably should add some kind of pre-build "hook" to the "python -m build" 
  command which runs scripts/rebuild-resources.sh if required

# PyPi Package Maintenance

Instructions to test and release new wp-enlighten package versions:

## Edit Source Code

    $ cd ~/work/code
    $ git clone git@github.com:WasatchPhotonics/ENLIGHTEN.git enlighten
    $ cd enlighten
    $ (edit files via vim, etc)

Note that in the above, we haven't created a venv, we haven't installed any 
dependencies etc; we've just checked out and editted some code.

To test changes and run ENLIGHTEN locally:

## Build Local Wheel

    $ python -m build

This will generate two new files under dist/:

    -rw-r--r-- 1 mzieg staff 51343830 Oct 5 18:01 wp_enlighten-4.2.15-py3-none-any.whl
    -rw-r--r-- 1 mzieg staff 54653109 Oct 5 18:01 wp_enlighten-4.2.15.tar.gz

In the next section we're going to install and run that new *.whl file.

## Install Local Wheel

In my test loop, I do this once:

    $ mkdir ~/testing
    $ cd ~/testing
    $ python -m venv venv
    $ . venv/bin/activate

Then I do this every time I want to test and "run" a new ENLIGHTEN:

    $ pip uninstall -y wp-enlighten
    $ pip install ~/work/code/enlighten/dist/*.whl
    $ enlighten

## Perform Internal Release Preparation

- push branch
- generate pull request
- receive sign-off
- merge to main
- ...etc

## Publish New Wheel

When you're ready to push a new production release to the world:

    $ python3 -m twine upload --repository testpypi dist/wp-enlighten*

If that works:

    $ python3 -m twine upload dist/wp-enlighten*

Note that you can NEVER re-push a new wheel with an old version number; you MUST
move to new version numbers.
