@echo off

echo.
echo %date% %time% ======================================================
echo %date% %time% Setting environment variables
echo %date% %time% ======================================================
echo.

set start_time=%time%

set "PYTHONPATH=%cd%/../Wasatch.PY;%cd%/../jcamp;%cd%/plugins;%cd%;%cd%/enlighten/assets/uic_qrc"
echo PYTHONPATH %PYTHONPATH%

if exist "C:\Program Files (x86)" (
    set "PROGRAM_FILES_X86=C:\Program Files (x86)"
) else (
    set "PROGRAM_FILES_X86=C:\Program Files"
)
echo using PROGRAM_FILES_X86 = %PROGRAM_FILES_X86%
set inno_exe="%PROGRAM_FILES_X86%\Inno Setup 6\iscc.exe"

if not exist %inno_exe% (
    echo %inno_exe% not found
    goto script_failure
)

echo.
echo %date% %time% ======================================================
echo %date% %time% Activating environment
echo %date% %time% ======================================================
echo.

set enlighten_venv=".env\enlighten"
set venv_python=%enlighten_venv%\Scripts\python
set activate=%enlighten_venv%\Scripts\activate
echo "running %activate%"
call %enlighten_venv%\Scripts\activate
if %errorlevel% neq 0 goto script_failure

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
REM --hide-console hide-early worked on Win10 but not Win11
REM --hide-console hide-late doesn't work on Win10
REM 
pyinstaller ^
    --distpath="scripts/built-dist" ^
    --workpath="scripts/work-path" ^
    --noconfirm ^
    --python-option "X utf8" ^
    --noconsole ^
    --clean ^
    --paths="../enlighten/assets/uic_qrc" ^
    --hidden-import="numpy.core._multiarray_umath" ^
    --hidden-import="scipy._lib.messagestream" ^
    --hidden-import="scipy._lib.array_api_compat.numpy.fft" ^
    --hidden-import="scipy.special._special_ufuncs" ^
    --hidden-import="scipy.special.cython_special" ^
    --hidden-import="colour" ^
    --hidden-import="tensorflow" ^
    --hidden-import="tensorflow.python.data.ops.shuffle_op" ^
    --add-data="support_files/libusb_drivers/amd64/libusb0.dll:." ^
    --icon "../enlighten/assets/uic_qrc/images/EnlightenIcon.ico" ^
    --specpath="%cd%/scripts" ^
    --exclude-module _bootlocale ^
    scripts/Enlighten.py

REM @see https://stackoverflow.com/a/69521558 re: _bootlocale

if %errorlevel% neq 0 goto script_failure

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

echo Running %inno_exe%
%inno_exe% /DENLIGHTEN_VERSION=%ENLIGHTEN_VERSION% /DCOMPRESSION=%COMPRESSION% scripts\Application_InnoSetup.iss

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

%RING_BELL%
echo Script complete -- started at %start_time%
goto:eof

:script_failure
%RING_BELL%
echo.
echo script failed: errorlevel %errorlevel%
exit /b 1
