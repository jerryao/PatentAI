from app import app

if __name__ == "__main__":
    print("启动专利实质审查系统...")
    print("请访问 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 