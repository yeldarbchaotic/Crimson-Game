@echo off
set current_dir=%~dp0
cd %cd:~0,3%
for /f %%i in ('dir python2* /b') do cd %%i
set python_dir=%~dp0
python --version
if %errorlevel% neq 0 (
    cd %current_dir%
    start https://www.python.org/downloads/
    start http://www.pygame.org/download.shtml
    cls
    echo Please install Python v2.7.9 and Pygame v.1.9.1
    pause
) else (
    cls
    python "%current_dir%Crimson.py"
)
cd %current_dir%