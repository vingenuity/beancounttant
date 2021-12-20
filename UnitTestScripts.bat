::
:: UnitTestScripts.bat
:: 
:: Author: Vincent Kocks (engineering@vingenuity.net)
:: v1.1.0
::
:: Runs Python unit test scripts for Beancounttant.
::
@echo off


:: Static Environment Variables
set PACKAGE_REQUIREMENTS_FILE=%~dp0requirements.txt
set PYTHON=python

set OPEN_REPORT=False
set VERBOSE=True



:: Dynamic Environment Variables
if defined VERBOSE set VERBOSE_ARG=-v


:: Main Execution
echo Installing required Python packages for Beancounttant...
%PYTHON% -m pip install -r %PACKAGE_REQUIREMENTS_FILE%
if ERRORLEVEL 1 goto package_install_error
echo Installed Python packages successfully.

pushd python
echo Testing Beancounttant scripts...
%PYTHON% -m coverage run --branch -m unittest discover %VERBOSE_ARG%

echo Generating coverage reports...
%PYTHON% -m coverage report
%PYTHON% -m coverage html
popd

if defined OPEN_REPORT (
    echo Opening coverage report...
    start "Coverage Report", "python\htmlcov\index.html"
)
goto finish


:package_install_error
echo Python package installation failed!
goto finish


:finish
if /I not "%1"=="-nopause" pause
