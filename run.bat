@REM This batch file runs the main Python application and opens the web page at 127.0.0.1:5000
@echo off

REM Start the Python application in the background
start /B python main.py
REM Wait for a few seconds to ensure the server starts
timeout /t 2 /nobreak > nul
REM Open the default web browser to the specified URL
start http://127.0.0.1:5000