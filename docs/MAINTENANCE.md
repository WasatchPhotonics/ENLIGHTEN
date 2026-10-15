# Maintenance

Miscellaneous notes, advice and history on how to maintain and extend ENLIGHTEN.

If you haven't already, see [Architecture](ARCHITECTURE.md) for an 
introduction to key classes.

## Release Process

- update version number 
    - update in src/wp_enlighten/common.py
    - update in pyproject.toml
- update CHANGELOG.md 
- build a Windows installer (see [Windows](BUILD_WINDOWS.md))
- git tag x.y.z
- git push --tags
- run scripts/deploy --win

## Graphics

(see [Qt](QT.md) and [CSS](CSS.md) notes)

When adding images to uic_qrc/images/devices or ./grey_images, remember 
to update uic_qrc/devices.qrc or ./grey_icons.qrc, then do `scripts\rebuild_resources.sh`.

At one point there was a Qt-CSS bug where you can't have whitespace in 
"qlineargradient(spread:pad"...I do not know if this has been resolved:

- https: // www.qtcentre.org/threads/46371-QSS-qlineargradient-not-working-when-inserting-whitespaces
  (note, link currently marked "unsafe"!)

## FAQ

### Why "enlighten.Authentication.Authentication" vs just "enlighten.Authentication"?

In Python, a directory is a _package_ and a .py/c file is a _module_.  If you 
want to seperate each class in its own file (which is my preference), then by
definition each class will exist within its own module.

According to [PEP8](https://www.python.org/dev/peps/pep-0008/#package-and-module-names),
module names should be lowercase, so technically the Authentication class should
be defined in authentication.py.  But I came from C++ and Java, where we like to
name the file after the class for consistency.

