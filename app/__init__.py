# Patent AI Examination System
# Package initialization

# Import app from app.py
import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入app.py中的Flask应用
from app_main import app 