# Add to Documentation

## Stylesheets

ENLIGHTEN allows users to customize the GUI look-and-feel to a degree.
Appearance is governed by Cascading StyleSheets (CSS), which by default
are stored in:

C:\\Program Files\\Wasatch Photonics\\ENLIGHTEN\\Enlighten\\enlighten\\assets\\stylesheets\\default

There are two ways to tweak ENLIGHTEN's appearance:

1. Edit the files in that directory directly.  This will require administrator 
   privileges, risk breaking something if you don't keep a backup, and doesn't
   support with multiple users on a shared PC (e.g. a classroom lab environment).

2. Run ENLIGHTEN with the --stylesheet-path option, pointing to a directory of 
   your choosing.  You should initially populate this directory with a copy of
   the contents from the default path listed above, then edit files within your
   own folder.  If you wish to revert a change, just re-copy a file from the 
   default path.
