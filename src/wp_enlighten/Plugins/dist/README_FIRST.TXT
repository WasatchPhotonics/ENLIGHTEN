--------------------------------------------------------------------------------
!!!         READ THIS BEFORE EDITING OR ADDING FILES IN THIS DIRECTORY       !!!
--------------------------------------------------------------------------------

This directory is copied to EnlightenSpectra/plugins in the user's "Documents" 
directory during installation.

This directory is also UNINSTALLED when you uninstall ENLIGHTEN -- with a few
important caveats:

1. If you have ADDED new files in this directory (which the ENLIGHTEN installer
   knows nothing about), those files will be LEFT UNCHANGED when you uninstall
   ENLIGHTEN.

2. If you then re-install ENLIGHTEN, it will re-create this directory and copy
   its own "default" plug-ins to this folder.  HOWEVER, it will NOT delete or
   change files which YOU had added in previous ENLIGHTEN versions (as long as
   default ENLIGHTEN plugins don't have the same name as yours).

3. If you EDIT or CHANGE an EXISTING plugin, without renaming it, YOUR WORK MAY 
   BE DELETED when you uninstall ENLIGHTEN.

4. If you EDIT or CHANGE an EXISTING plugin, without renaming it, YOUR WORK MAY 
   BE OVERWRITTEN when you re-install ENLIGHTEN.

We recommend you put all your custom plugins into the "User" folder,
(EnlightenSpectra/plugins/User), or that you create a new folder with your
company name (i.e. EnlightenSpectra/plugins/ACME). This way, your new or 
modified plugins will never be overwritten by future ENLIGHTEN updates.

Obviously, we also recommend that you put your own plugins under revision-control
(GitHub / GitLab are free!) to avoid any "unfortunate mishaps."

Please see "README_PLUGINS.md" for additional information.
