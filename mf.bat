@echo off
REM Corplang CLI Wrapper for Windows
REM Place this file in a directory in PATH to use globally
REM
REM Usage:
REM   mf.bat run program.mp
REM   mf.bat compile main.mp
REM   mf.bat init myproject

setlocal
python "%~dp0\src\commands\main.py" %*
endlocal
