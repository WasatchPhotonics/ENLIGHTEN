@echo off

REM This is an automated script to bootstrap a previously checked-out Enlighten
REM source code distribution and prepare it for development (default) or create
REM an installer.
REM
REM Examples:
REM   scripts\bootstrap.bat                                       (bootstrap development environment)
REM   scripts\bootstrap.bat installer 2>build.err | tee build.out (as above, then build installer)
REM   scripts\bootstrap.bat just-installer                        (just build installer)

set PYTHONPATH=..\Wasatch.PY;pluginExamples;.;enlighten\assets\uic_qrc

REM parse ONE cmd-line arg
if "%1" == "" (
    set "build_target=default"
) else (
    set "build_target=%1"
)

REM capture start time
set TIME_START=%time%

echo.
echo %date% %time% ======================================================
echo %date% %time% Configuring Enlighten for %build_target%
echo %date% %time% ======================================================
echo.
if not exist scripts\bootstrap.bat (
	echo Please run script as scripts\bootstrap.bat
	goto script_failure
) else (
    echo Running from %cd%
)

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

if "%build_target%" == "just-inno" (
    goto PAST_PYINSTALLER
)

REM skip ahead if we only want to do the installer (both pyinstaller and innoinstaller)
if "%build_target%" == "just-installer" (
    set "build_target=installer"
    goto JUST_INSTALLER
)

if "%build_target%" == "activate" goto ACTIVATE

echo.
echo %date% %time% ======================================================
echo %date% %time% Purging last build
echo %date% %time% ======================================================
echo.
echo removing %USERPROFILE%\AppData\Roaming\pyinstaller
rd /s /q %USERPROFILE%\AppData\Roaming\pyinstaller
echo removing %MINICONDA%\envs\conda_enlighten3
rd /s /q %MINICONDA%\envs\conda_enlighten3

echo.
echo %date% %time% ======================================================
echo %date% %time% Configure Conda
echo %date% %time% ======================================================
echo.
conda config --set always_yes yes --set changeps1 no
if %errorlevel% neq 0 goto script_failure

echo.
echo %date% %time% ======================================================
echo %date% %time% Update Conda
echo %date% %time% ======================================================
echo.
conda update -q conda
if %errorlevel% neq 0 goto script_failure
     
echo.
echo %date% %time% ======================================================
echo %date% %time% Remove old Conda environment 
echo %date% %time% ======================================================
echo.
conda env remove -n conda_enlighten3
if %errorlevel% neq 0 goto script_failure

echo.
echo %date% %time% ======================================================
echo %date% %time% Logging Conda configuration
echo %date% %time% ======================================================
echo.
conda info -a
if %errorlevel% neq 0 goto script_failure

echo.
echo %date% %time% ======================================================
echo %date% %time% Creating Conda Environment
echo %date% %time% ======================================================
echo.
del /f /q environment.yml
copy environments\conda-win10.yml environment.yml
conda env create -n conda_enlighten3 

:ACTIVATE
echo.
echo %date% %time% ======================================================
echo %date% %time% Activating environment
echo %date% %time% ======================================================
echo.
REM Use "source" from bash, "call" from batch and neither from Cmd
call activate conda_enlighten3
if %errorlevel% neq 0 goto script_failure
if "%build_target%" == "activate" goto PAST_INSTALLER

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

rem echo.
rem echo %date% %time% ======================================================
rem echo %date% %time% Installing pyinstaller from pip
rem echo %date% %time% ======================================================
rem echo.

pip install pyinstaller==4.10
if %errorlevel% neq 0 goto script_failure

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

echo.
echo %date% %time% ======================================================
echo %date% %time% Setting Python path
echo %date% %time% ======================================================
echo.
set PYTHONPATH=.;%cd%\pluginExamples;%cd%\..\Wasatch.PY;%CONDA_PREFIX%\lib\site-packages
echo PYTHONPATH = %PYTHONPATH%

echo.
echo %date% %time% ======================================================
echo %date% %time% Regenerating Qt views
echo %date% %time% ======================================================
echo.
sh scripts\rebuild_resources.sh
if %errorlevel% neq 0 goto script_failure

if "%build_target%" == "default" goto PAST_TESTS
echo.
echo %date% %time% ======================================================
echo %date% %time% Run tests...may take some time
echo %date% %time% ======================================================
echo.
REM
REM MZ: disabling this for now
REM
REM py.test tests -x
REM if %errorlevel% neq 0 goto script_failure
:PAST_TESTS

REM jump here if you don't want to bootstrap a development environment
:JUST_INSTALLER

if "%build_target%" == "installer" goto RUN_PYINSTALLER
goto PAST_PYINSTALLER

:RUN_PYINSTALLER

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

rem address bug in current pyinstaller?
rem copy enlighten\assets\uic_qrc\images\EnlightenIcon.ico .
rem set SPECPATH=%cd%/scripts

REM remove --windowed to debug the compiled .exe and see Python invocation 
REM error messages
REM
REM --windowed ^

REM pyinstaller --distpath="scripts/built-dist" --workpath="scripts/work-path" --noconfirm --clean scripts/enlighten.spec

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
    scripts/Enlighten.py

if %errorlevel% neq 0 goto script_failure

:PAST_PYINSTALLER

echo.
echo %date% %time% ======================================================
echo %date% %time% Running Inno Setup
echo %date% %time% ======================================================
echo.
"%PROGRAM_FILES_X86%\Inno Setup 6\iscc.exe" /DENLIGHTEN_VERSION=%ENLIGHTEN_VERSION% scripts\Application_InnoSetup.iss
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

:PAST_INSTALLER
echo.
echo %date% %time% All steps completed successfully.
echo %date% %time% Started at %TIME_START%
goto:eof

:script_failure
echo.
echo Boostrap script failed: errorlevel %errorlevel%
exit /b 1
