@echo off
call python -V -V
call python -c "import platform; print(platform.architecture()[0])" | findstr "64" > nul
if %errorlevel% neq 0 (
    echo You are using a 32-bit version of Python. MagiaTimeline does not support it. Please install a 64-bit version.
    pause
    goto end
)

if not exist venv\Scripts\activate.bat (
    echo Virtual environment not found. Creating venv...
    call python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        goto end
    )
)

echo Activating virtual environment and upgrading dependencies...
call venv\Scripts\activate.bat
call python -m pip install --upgrade pip -i https://pypi.mirrors.ustc.edu.cn/simple/
if %errorlevel% neq 0 (
    echo Failed to upgrade pip.
    pause
    goto end
)

call python -m pip install --upgrade -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/
if %errorlevel% neq 0 (
    echo Failed to upgrade dependencies. Please check the error message above.
    pause
    goto end
)

call python TouchPaddle.py
if %errorlevel% neq 0 (
    echo Paddle check failed. Please check the error message above.
    pause
    goto end
)

echo Virtual environment update complete.
pause
:end
