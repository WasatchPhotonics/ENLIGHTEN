# ENLIGHTEN Documentation System

ENLIGHTEN's internal developer documentation is rendered here:

- https://mco.wasatchphotonics.com/doc/Enlighten/

# Rendering

You can render the Doxygen to HTML (or RTF -> Word) using "make docs".

Note that image generation requires that you have dot/graphviz installed.

# Doxygen Syntax

ENLIGHTEN's documentation is auto-rendered using Doxygen:

- http://www.doxygen.nl/
- http://www.doxygen.nl/manual/commands.html

Internal Python documentation therefore uses Doxygen's "##" syntax rather than 
the unofficial grab-bag of competing "Pythonic" approaches growing out of PEP256:

- https://www.python.org/dev/peps/pep-0256/

# Dot syntax

If you want to make dynamic clickable diagrams like on the [Architecture](README_ARCHITECTURE.md)
page, see:

- https://www.graphviz.org/pdf/dotguide.pdf

# Warnings

## Too Many READMEs

Doxygen gets confused if it processes more than one README.md, which it is
configured to use as the "mainpage" in the Doxyfile.  Therefore either name
per-folder README's something else, or exclude those directories from 
processing in the Doxyfile.
