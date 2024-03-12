@REM @echo off
title windows file system manager
color 0E
cd /d %~dp0
call .\myvenv\Scripts\activate
call python .\main.py
pause