# Wiley KnowItAll 

Notes about ENLIGHTEN's integration with KnowItAll.

Basic dataflow:

    Controller <--> KIA.Feature <--> KIA.Wrapper <--> KIAConsole.exe <--> KnowItAll
    \_____________Enlighten_(Python)___________/      \_____C++____/

## Dependencies

You can download KnowItAll here:

- https://get.knowitall.com

## Implementation

See these Python classes:

- \ref enlighten.KnowItAll.Feature.Feature
- \ref enlighten.KnowItAll.Wrapper.Wrapper
- \ref enlighten.KnowItAll.Config.Config

KIAConsole.exe is built from this C++ project: 

- https://github.com/WasatchPhotonics/KnowItAllWrapper

## Installation

Although KIAConsole.exe is built in 'Release', KnowItAll itself seems to need the 
"Debug" version of various Visual C++ Redistributable libraries, which don't come
with Microsoft's standard vc\_redist.exe installer (although that is now included
and executed by ENLIGHTEN's installer...see scripts/Application\_InnoSetup.iss).

Specifically, these three DLLs are required at runtime:

- msvcp140d.dll
- vcruntime140d.dll
- ucrtbased.dll

If you have Visual Studio installed, these files can be found in places like:

- Program Files (x86)/Microsoft SDKs/Windows Kits/10/ExtensionSDKs/Microsoft.UniversalCRT.Debug
- Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Redist/MSVC
- Program Files (x86)/Windows Kits/10/bin

More specifically, there are both 32- and 64-bit versions of each file, which
need to be installed into System32 (64-bit) and SysWOW64 (32-bit) respectively.
Appropriate versions of each file are provided in dist/Windows in the appropriate
subdirectories, and are installed by InnoSetup.

## Reference

- [KnowItAll Homepage](https://sciencesolutions.wiley.com/knowitall-spectroscopy-software/)
- [KnowItAll SDK](https://sciencesolutions.wiley.com/knowitall-sdk/)
- [KnowItAll Brochure](https://sciencesolutions.wiley.com/wp-content/uploads/2021/10/210413-Wiley_KnowItAll_Software_Spectroscopy_Edition_Brochure.pdf)
- [Wiley Logo Usage](https://www.wiley.com/en-us/thewileylogo)
