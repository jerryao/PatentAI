@echo off
echo 正在安装专利实质审查系统所需依赖...

:: 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 未安装。请先安装 Python 3.8 或更高版本。
    exit /b 1
)

:: 创建上传文件夹
if not exist uploads (
    mkdir uploads
    echo 已创建上传文件夹。
)

:: 安装依赖
echo 安装所需的 Python 包...
pip install -r requirements.txt

echo.
echo 安装完成！
echo 可以通过运行 python run.py 启动系统。
echo. 