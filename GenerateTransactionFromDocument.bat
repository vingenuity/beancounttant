::
:: GenerateTransactionFromDocument.bat
:: 
:: Author: Vincent Kocks (engineering@vingenuity.net)
:: v1.0.0
::
:: Generates a Beancount transaction from a document file given via the command line.
::
@echo off


:: --------------------------------------------------------------
:: FILE PARAMETERS
:: --------------------------------------------------------------
set GENERATE_TRANSACTION_SCRIPT=%~dp0python\generate_transaction_from_document.py
set PYTHON=python


:: --------------------------------------------------------------
:: MAIN SCRIPT FLOW
:: --------------------------------------------------------------
set /P DOCUMENT=Please enter the path to a document:
set CONFIG_FILE=.\config.json

%PYTHON% %GENERATE_TRANSACTION_SCRIPT% -c "%CONFIG_FILE%" -d "%DOCUMENT%"

pause
