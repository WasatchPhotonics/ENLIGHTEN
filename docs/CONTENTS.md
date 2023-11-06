# Contents

## Distribution

Major directories and files in the source distribution:

- dist/
    - holds 3rd-party libraries we use, if not otherwise available via Anaconda / pip etc
- docs/
    - Most of the documentation in this directory is outdated and has not been updated
      or reviewed.  It is retained for historical purposes and needs a major cleanup.
- udev/
    - needed for [Linux](README_LINUX.md)
- tests/
    - not currently used; needs refreshed
    - see [Testing](README_TESTING.md)
- enlighten/
    - \*.py 
        - Python source code for the ENLIGHTEN application, other than Wasatch.PY 
    - assets/
        - example\_data/ (could stand refactor)
            - static files copied to end-user computers by the installer
        - stylesheets/
            - more static files copied to end-user computers by the installer (used for GUI appearance)
        - uic\_qrc/
            - Qt configuration files defining GUI layout and contents
            - enlighten\_layout.ui
                - the all-important Designer layout of ENLIGHTEN screens
            - dialog\_text.ui
                - a small "info dialog" form that can be popped-up by ENLIGHTEN
            - image\_dialog.ui
                - do we use this?
            - images/
                - graphics we want to display in the GUI
- environments/
    - conda-win10.yml
        - copy this to ../environment.yml before running "conda env create"
    - need conda-linux, conda-macos etc
- scripts/ 
    - a mixture of things; could stand refactoring
    - all platforms
        - Enlighten.py
            - the actual script used to spawn and run ENLIGHTEN
        - rebuild\_resources.sh
            - calls Qt utilities to render GUI configuration into Python
            - run after modifying enlighten\_layout.ui or image files
        - environments\
            - Anaconda environment files for supported developer platforms
    - Windows-only
        - bootstrap.bat (see [Windows](README_WINDOWS.md))
            - used to configure a Windows development environment 
            - also used to build a Windows installer
        - Application\_InnoSetup.iss
            - used by bootstrap.bat and InnoSetup5 when building Windows installers
        - built-dist/
            - populated when Windows installer is built (compiled binaries)
        - windows\_installer/ 
            - populated when Windows installer is built (installer .exe)
    - used when building installers
        - support\_files/
        - work-path/

## Temporary 

Temporary files and directories which may be created:

- build/
- build-linux/
- build-mac/
    - created when building installers; may be deleted after
