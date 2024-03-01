@echo off

REM This is an automated script to bootstrap a previously checked-out Enlighten
REM source code distribution and prepare it for development `activate` or create
REM an installer `oneshot`.

set "rebuild_env=0"
set "clear_pyinst_appdata=0"
set "configure_venv=0"
set "install_python_deps=0"
set "update_venv=0"
set "log_conf_pkg=0"
set "regenerate_qt=0"
set "pyinstaller=0"
set "innosetup=0"
set "runtests=0"
set "virtspec=0"

REM Convoluted but safe way to generate an audible bell from a .bat
REM without inserting control characters which confuse unix2dos etc.
REM https://stackoverflow.com/a/64515648
set "RING_BELL=echo x|choice /n 2>nul"

set ENLIGHTEN_VENV=%HOME%\enlighten_py311
echo Using ENLIGHTEN_VENV at %ENLIGHTEN_VENV%

if "%2" == "virtspec" (
    set "virtspec=1"
)

if "%1" == "activate" (
    goto args_parsed
)

if "%1" == "pyinstaller" (
    set "regenerate_qt=1"
    set "pyinstaller=1"
    goto args_parsed
)

if "%1" == "innosetup" (
    set "regenerate_qt=1"
    set "pyinstaller=1"
    set "innosetup=1"
    goto args_parsed
)

if "%1" == "refreshdep" (
    set "rebuild_env=1"
    set "clear_pyinst_appdata=1"
    set "configure_venv=1"
    set "install_python_deps=1"
    set "update_venv=1"
    set "log_conf_pkg=1"
    goto args_parsed
)

if "%1" == "oneshot" (
    set "rebuild_env=1"
    set "clear_pyinst_appdata=1"
    set "configure_venv=1"
    set "install_python_deps=1"
    set "update_venv=1"
    set "log_conf_pkg=1"
    set "regenerate_qt=1"
    set "pyinstaller=1"
    set "innosetup=1"
    goto args_parsed
)

if "%1" == "test" (
    set "runtests=1"
    goto args_parsed
)

if "%1" == "ui" (
    set "regenerate_qt=1"
    goto args_parsed
)

if "%1" == "help" (
    echo options are:
    echo   activate
    echo   innosetup
    echo   pyinstaller
    echo   refreshdep
    echo   oneshot
    echo   ui
    echo   test
    goto:eof
)

REM DEFINE CUSTOM ACTION HERE
if "%1" == "custom" (
    set "rebuild_env=0"
    set "clear_pyinst_appdata=0"
    set "configure_venv=0"
    set "install_python_deps=0"
    set "update_venv=0"
    set "log_conf_pkg=0"
    set "regenerate_qt=0"
    set "pyinstaller=0"
    set "innosetup=0"
    goto args_parsed
)

echo === USAGE ===
echo $ scripts\bootstrap activate
echo Do not perform any major actions. Prepare environment variables and venv for using Enlighten.
echo.
echo $ scripts\bootstrap activate virtspec
echo Prepare environment variables and venv for using Enlighten with a virtual spectrometer. (use bootstrap activate to revert to normal)
echo.
echo $ scripts\bootstrap pyinstaller
echo regenerate Qt views and run pyinstaller (to create standalone exe)
echo.
echo $ scripts\bootstrap innosetup
echo run innosetup (to create windows installer)
echo.
echo $ scripts\bootstrap refreshdep
echo This will take a while. Remove and recreate the venv environment and reinstall all dependencies from the internet.
echo.
echo $ scripts\bootstrap oneshot
echo This will take a while. Perform all steps (except for testing) and produce an installer.
echo.
echo $ scripts\bootstrap test
echo This will take a while. Performs tests.
echo.
echo $ scripts\bootstrap ui
echo Rebuild UI only.
echo.
echo $ scripts\bootstrap custom
echo If you need a very particular action sequence (for example run pyinstaller without regenerating Qt views), edit this file, search for DEFINE CUSTOM ACTION HERE, and change flags as desired.
goto:eof

:args_parsed

if not exist scripts\bootstrap.bat (
    echo Please run script as scripts\bootstrap.bat
    goto script_failure
) else (
    echo Running from %cd%
)

echo.
echo %date% %time% ======================================================
echo %date% %time% Setting environment variables
echo %date% %time% ======================================================
echo.
set TIME_START=%time%
set PYTHONPATH=.;..\Wasatch.PY;..\jcamp;plugins;enlighten\assets\uic_qrc
echo PYTHONPATH = %PYTHONPATH%

if exist "C:\Program Files (x86)" (
    set "PROGRAM_FILES_X86=C:\Program Files (x86)"
) else (
    set "PROGRAM_FILES_X86=C:\Program Files"
)
echo using PROGRAM_FILES_X86 = %PROGRAM_FILES_X86%

echo.
echo %date% %time% ======================================================
echo %date% %time% Checking dependencies
echo %date% %time% ======================================================
echo.

if not exist "%PROGRAM_FILES_X86%\Inno Setup 6" (
    echo Warning: Inno Setup 6 not installed
    goto script_failure
)

if not exist "..\Wasatch.PY" (
    echo Warning: Wasatch.PY not found
    goto script_failure
)

echo.
echo %date% %time% ======================================================
echo %date% %time% Extracting Enlighten version
echo %date% %time% ======================================================
echo.

grep '^VERSION' enlighten/common.py | grep -E -o '([0-9]\.?)+' > version.txt
set /p ENLIGHTEN_VERSION=<version.txt
echo ENLIGHTEN_VERSION = %ENLIGHTEN_VERSION%
del /f /q version.txt

echo.
echo %date% %time% ======================================================
echo %date% %time% Setting path
echo %date% %time% ======================================================
echo.

REM set PATH=%PROGRAM_FILES_X86%\Inno Setup 6;%PATH%
REM echo Path = %PATH%

echo.
echo %date% %time% ======================================================
echo %date% %time% Confirm Python version
echo %date% %time% ======================================================
echo.

where python
python --version
if %errorlevel% neq 0 goto script_failure

if "%clear_pyinst_appdata%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Delete pyinstaller appdata 
    echo %date% %time% ======================================================
    echo.
    echo removing %USERPROFILE%\AppData\Roaming\pyinstaller
    rd /s /q %USERPROFILE%\AppData\Roaming\pyinstaller
)

if "%rebuild_env%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Delete venv 
    echo %date% %time% ======================================================
    echo.
    echo removing %ENLIGHTEN_VENV%
    rd /s /q %ENLIGHTEN_VENV%
)

if "%configure_venv%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Create venv
    echo %date% %time% ======================================================
    echo.
    python3.11 -m venv %ENLIGHTEN_VENV%
    if %errorlevel% neq 0 goto script_failure
)

echo.
echo %date% %time% ======================================================
echo %date% %time% Activating environment
echo %date% %time% ======================================================
echo.

call %ENLIGHTEN_VENV%\Scripts\activate
if %errorlevel% neq 0 goto script_failure

echo.
echo %date% %time% ======================================================
echo %date% %time% Reconfirming Python version
echo %date% %time% ======================================================
echo.

where python
python --version
if %errorlevel% neq 0 goto script_failure

if "%install_python_deps%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Installing Python pip dependencies 
    echo %date% %time% ======================================================
    echo.

    python -m pip install -r requirements.txt

    REM Bootstrap bat is meant to make a windows installer
    REM because of this separately install pywin32 since it's only meant for windows
    pip install pywin32 

    REM not sure why this doesn't work from requirements.txt
    pip install spc_spectra
    if %errorlevel% neq 0 goto script_failure
)

if "%log_conf_pkg%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Logging Pip packages
    echo %date% %time% ======================================================
    echo.
    pip freeze
    if %errorlevel% neq 0 goto script_failure
)

if "%regenerate_qt%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Regenerating Qt views
    echo %date% %time% ======================================================
    echo.
    sh scripts\rebuild_resources.sh
    if %errorlevel% neq 0 goto script_failure
)

if "%pyinstaller%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Purging old build artifacts
    echo %date% %time% ======================================================
    echo.
    rmdir /Q /S scripts\built-dist\Enlighten
    rmdir /Q /S scripts\work-path\Enlighten

    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Running PyInstaller
    echo %date% %time% ======================================================
    echo.
    REM hide-early worked on Win10 but not Win11
    REM hide-late doesn't work on Win10
    pyinstaller ^
        --distpath="scripts/built-dist" ^
        --workpath="scripts/work-path" ^
        --noconfirm ^
        --python-option "X utf8" ^
        --hide-console hide-late ^
        --clean ^
        --paths="../Wasatch.PY" ^
        --hidden-import="scipy._lib.messagestream" ^
        --hidden-import="scipy.special.cython_special" ^
        --hidden-import="tensorflow" ^
        --hidden-import="tensorflow.python.data.ops.shuffle_op" ^
        --add-data="support_files/libusb_drivers/amd64/libusb0.dll:." ^
        --icon "../enlighten/assets/uic_qrc/images/EnlightenIcon.ico" ^
        --specpath="%cd%/scripts" ^
        --exclude-module _bootlocale ^
        scripts/Enlighten.py

    REM @see https://stackoverflow.com/a/69521558

    if %errorlevel% neq 0 goto script_failure
)

if "%innosetup%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Running Inno Setup
    echo %date% %time% ======================================================
    echo.

    if not exist "scripts\windows_installer\" mkdir scripts\windows_installer

    rem see https://jrsoftware.org/ishelp/index.php?topic=setup_compression
    if "%COMPRESSION%" == "" (
        rem caller may set it to lzma/fast for speed
        set "COMPRESSION=lzma/max"
    )

    "%PROGRAM_FILES_X86%\Inno Setup 6\iscc.exe" ^
        /DENLIGHTEN_VERSION=%ENLIGHTEN_VERSION% ^
        scripts\Application_InnoSetup.iss
    if %errorlevel% neq 0 goto script_failure

    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Reviewing installer artifacts [built-dist]
    echo %date% %time% ======================================================
    echo.

    dir scripts\built-dist\Enlighten\*.exe
    if %errorlevel% neq 0 goto script_failure

    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Reviewing installer artifacts [windows_installer]
    echo %date% %time% ======================================================
    echo.

    dir scripts\windows_installer\*.exe
    if %errorlevel% neq 0 goto script_failure

    copy scripts\windows_installer\Enlighten-Setup64-%ENLIGHTEN_VERSION%.exe .
    if %errorlevel% neq 0 goto script_failure
)

echo.
echo %date% %time% All steps completed successfully.
echo %date% %time% Started at %TIME_START%
%RING_BELL%

goto:eof

:script_failure
echo.
echo Boostrap script failed: errorlevel %errorlevel%
%RING_BELL%
exit /b 1
