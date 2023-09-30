@echo off

REM This is an automated script to bootstrap a previously checked-out Enlighten
REM source code distribution and prepare it for development `activate` or create
REM an installer `oneshot`.

set "rebuild_env=0"
set "clear_pyinst_appdata=0"
set "configure_conda=0"
set "install_python_deps=0"
set "update_conda=0"
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
    set "innosetup=1"
    goto args_parsed
)
if "%1" == "refreshdep" (
    set "rebuild_env=1"
    set "clear_pyinst_appdata=1"
    set "configure_conda=1"
    set "install_python_deps=1"
    set "update_conda=1"
    set "log_conf_pkg=1"
    goto args_parsed
)

if "%1" == "oneshot" (
    set "rebuild_env=1"
    set "clear_pyinst_appdata=1"
    set "configure_conda=1"
    set "install_python_deps=1"
    set "update_conda=1"
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

REM DEFINE CUSTOM ACTION HERE
if "%1" == "custom" (
    set "rebuild_env=0"
    set "clear_pyinst_appdata=0"
    set "configure_conda=0"
    set "install_python_deps=0"
    set "update_conda=0"
    set "log_conf_pkg=0"
    set "regenerate_qt=0"
    set "pyinstaller=0"
    set "innosetup=0"
    goto args_parsed
)

echo === USAGE ===
echo $ scripts\bootstrap activate
echo Do not perform any major actions. Prepare environment variables and conda for using Enlighten.
echo.
echo $ scripts\bootstrap activate virtspec
echo Prepare environment variables and conda for using Enlighten with a virtual spectrometer. (use bootstrap activate to revert to normal)
echo.
echo $ scripts\bootstrap pyinstaller
echo regenerate Qt views and run pyinstaller (to create standalone exe)
echo.
echo $ scripts\bootstrap innosetup
echo run innosetup (to create windows installer)
echo.
echo $ scripts\bootstrap refreshdep
echo This will take a while. Remove and recreate the conda environment and reinstall all dependencies from the internet.
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
REM capture start time
set TIME_START=%time%
set PYTHONUTF8=1
set PYTHONPATH=.;..\Wasatch.PY;..\SPyC_Writer\src;pluginExamples;%CONDA_PREFIX%\lib\site-packages;enlighten\assets\uic_qrc
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
set MINICONDA=%USERPROFILE%\Miniconda3
if not exist %MINICONDA% (
    echo %MINICONDA% not found.
    goto script_failure
)

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

echo.
echo %date% %time% ======================================================
echo %date% %time% Setting path
echo %date% %time% ======================================================
echo.
set PATH=%MINICONDA%;%MINICONDA%\Scripts;%MINICONDA%\Library\bin;%PROGRAM_FILES_X86%\Inno Setup 6;%PATH%
echo Path = %PATH%

echo.
echo %date% %time% ======================================================
echo %date% %time% Confirm Python version
echo %date% %time% ======================================================
echo.
which python
python --version
if %errorlevel% neq 0 goto script_failure

if "%clear_pyinst_appdata%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Delete pyinstaller appdata OPTIONAL
    echo %date% %time% ======================================================
    echo.
    echo removing %USERPROFILE%\AppData\Roaming\pyinstaller
    rd /s /q %USERPROFILE%\AppData\Roaming\pyinstaller
)
if "%rebuild_env%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Delete conda environment OPTIONAL
    echo %date% %time% ======================================================
    echo.
    echo removing %MINICONDA%\envs\conda_enlighten3
    rd /s /q %MINICONDA%\envs\conda_enlighten3
)

if "%configure_conda%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Configure Conda
    echo %date% %time% ======================================================
    echo.
    conda config --set always_yes yes --set changeps1 no
    if %errorlevel% neq 0 goto script_failure
)

if "%update_conda%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Update Conda OPTIONAL
    echo %date% %time% ======================================================
    echo.
    conda update -q conda
    if %errorlevel% neq 0 goto script_failure
)
     
if "%rebuild_env%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Remove old Conda environment OPTIONAL
    echo %date% %time% ======================================================
    echo.
    conda env remove -n conda_enlighten3
    REM SB: Do not errout if the env is already deleted, could be from 
    REM previous partial run.
)

if "%log_conf_pkg%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Logging Conda configuration
    echo %date% %time% ======================================================
    echo.
    conda info -a
    if %errorlevel% neq 0 goto script_failure
)

if "%rebuild_env%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Creating Conda Environment OPTIONAL
    echo %date% %time% ======================================================
    echo.
    del /f /q environment.yml
    copy environments\conda-win10.yml environment.yml
    conda env create -n conda_enlighten3 
)

echo.
echo %date% %time% ======================================================
echo %date% %time% Activating environment
echo %date% %time% ======================================================
echo.
REM deactivate before activate in-case user runs `scripts\bootstrap activate` multiple times
call deactivate
REM Use "source" from bash, "call" from batch and neither from Cmd
call activate conda_enlighten3
if %errorlevel% neq 0 goto script_failure

echo.
echo %date% %time% ======================================================
echo %date% %time% Reconfirming Python version
echo %date% %time% ======================================================
echo.
which python
REM this version doesn't get logged...why? (maybe goes to stderr?)
python --version
if %errorlevel% neq 0 goto script_failure

REM echo.
REM echo %date% %time% ======================================================
REM echo %date% %time% Upgrading PIP
REM echo %date% %time% ======================================================
REM echo.
REM python -m pip install --upgrade pip

if "%install_python_deps%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Installing Python pip dependencies [conda missing/bad]
    echo %date% %time% ======================================================
    echo.

    python -m pip install -r requirements.txt
    REM Bootstrap bat is meant to make a windows installer
    REM because of this separately install pywin32 since it's only meant for windows
    pip install pywin32 
    if %errorlevel% neq 0 goto script_failure

    python -m pip uninstall pyqt5
    python -m pip install --upgrade pyqt5

    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Installing pyinstaller from pip
    echo %date% %time% ======================================================
    echo.
    pip install pyinstaller
    if %errorlevel% neq 0 goto script_failure
)

if "%virtspec%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% * Appending PyUSB Virtual Spectrometer to PATH *
    echo %date% %time% ======================================================
    echo.
    set PYTHONPATH=..\pyusb-virtSpec;%PYTHONPATH%
    pip uninstall pyusb
)
if "%virtspec%" == "0" (
    pip install pyusb==1.2.1
)

if "%log_conf_pkg%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Logging Conda packages
    echo %date% %time% ======================================================
    echo.
    cmd /c "conda list --explicit" 
    if %errorlevel% neq 0 goto script_failure

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

if "%runtests%" == "1" (
    echo.
    echo %date% %time% ======================================================
    echo %date% %time% Run tests...may take some time
    echo %date% %time% ======================================================
    echo.
    py.test test
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
    echo %date% %time% Running PyInstaller OPTIONAL
    echo %date% %time% ======================================================
    echo.
    REM remove --windowed to debug the compiled .exe and see Python invocation 
    REM error messages
    REM
    REM --windowed ^
    pyinstaller ^
        --distpath="scripts/built-dist" ^
        --workpath="scripts/work-path" ^
        --noconfirm ^
        --noconsole ^
        --clean ^
        --paths="../Wasatch.PY" ^
        --hidden-import="scipy._lib.messagestream" ^
        --hidden-import="scipy.special.cython_special" ^
        --hidden-import="tensorflow" ^
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

    if "%COMPRESSION%" == "" (
        rem caller may set it to lzma/fast for speed
        set "COMPRESSION=lzma/max"
    )

    "%PROGRAM_FILES_X86%\Inno Setup 6\iscc.exe" ^
        /DENLIGHTEN_VERSION=%ENLIGHTEN_VERSION% ^
        /DCOMPRESSION=%COMPRESSION% ^
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
