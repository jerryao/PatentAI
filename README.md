# 专利实质审查系统

基于SiliconFlow API的专利实质审查系统，能对提交的专利文档（docx格式）进行实质性审查，并提供审查意见。

## 功能特点

- **专利文档解析**：支持上传docx格式的专利文档，并解析其内容
- **新颖性分析**：评估专利是否与现有技术相同或相似
- **创造性分析**：评估专利是否对本领域技术人员而言显而易见
- **实用性分析**：判断专利技术是否能够实现并产生积极效果
- **充分公开分析**：检查说明书是否清楚、完整地公开了发明
- **权利要求分析**：评估权利要求是否清楚、简要，是否得到说明书支持
- **审查结论与修改建议**：给出综合评估意见和具体修改建议

## 技术架构

- 前端：HTML, CSS, JavaScript, Bootstrap 5
- 后端：Python, Flask
- API：SiliconFlow大模型API
- 文件处理：python-docx

## 安装部署

1. 克隆代码库
```
git clone [repository-url]
cd patent-ai
```

2. 安装依赖
```
pip install -r requirements.txt
```

3. 配置环境变量
在项目根目录创建`.env`文件，添加以下内容：
```
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_API_BASE=https://api.siliconflow.cn/v1
```

4. 创建上传目录
```
mkdir uploads
```

5. 运行应用
```
python app.py
```

应用将在 http://localhost:5000 启动

## API接口

除了Web界面，系统还提供了API接口供集成使用：

- `POST /api/analyze`：上传并分析专利文档
  - 参数：`patent_file`（文件，docx格式）
  - 返回：JSON格式的分析结果

## 系统要求

- Python 3.8+
- 网络连接（用于访问SiliconFlow API）
- 50MB以上的可用存储空间

## 注意事项

- 请确保上传的文档符合标准专利申请格式
- API密钥需要从SiliconFlow官方获取
- 本系统仅提供技术性分析，不构成法律意见

## 许可证

MIT License 