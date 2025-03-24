from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import logging
import time
from dotenv import load_dotenv
from app.utils.docx_processor import extract_text_from_docx
from app.api.siliconflow_client import SiliconFlowClient
from werkzeug.utils import secure_filename

# 配置日志
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# 记录API密钥前几位字符，用于调试
api_key = os.getenv('SILICONFLOW_API_KEY', '')
logger.debug(f"API密钥前5位: {api_key[:5]}...")
logger.debug(f"API基础URL: {os.getenv('SILICONFLOW_API_BASE')}")

app = Flask(__name__, 
           template_folder='app/templates',
           static_folder='app/static')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'docx'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize SiliconFlow client
silicon_flow_client = SiliconFlowClient(
    api_key=os.getenv('SILICONFLOW_API_KEY'),
    api_base=os.getenv('SILICONFLOW_API_BASE')
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    logger.debug("访问首页")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_patent():
    logger.debug("接收到上传请求")
    logger.debug(f"请求方法: {request.method}")
    logger.debug(f"表单数据: {request.form}")
    logger.debug(f"文件: {request.files}")
    
    if 'patent_file' not in request.files:
        logger.error("未找到patent_file字段")
        flash('No file part', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['patent_file']
    logger.debug(f"文件名: {file.filename}")
    
    if file.filename == '':
        logger.error("未选择文件")
        flash('No selected file', 'danger')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        logger.debug("文件验证通过")
        
        # 使用时间戳确保文件名唯一，避免中文文件名问题
        timestamp = int(time.time())
        # 获取原始扩展名
        _, ext = os.path.splitext(file.filename)
        # 创建新文件名
        filename = f"patent_{timestamp}{ext}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.debug(f"保存路径: {filepath}")
        try:
            file.save(filepath)
            logger.debug(f"文件已保存: {filepath}")
            
            # Process the DOCX and get patent text
            logger.debug("开始处理DOCX文件")
            patent_text = extract_text_from_docx(filepath)
            logger.debug(f"提取的文本长度: {len(patent_text)}")
            
            # 记录一小部分文本用于调试
            text_sample = patent_text[:200] + "..." if len(patent_text) > 200 else patent_text
            logger.debug(f"文本样本: {text_sample}")
            
            # Send to SiliconFlow API for analysis
            logger.debug("开始调用API分析专利")
            try:
                analysis_result = silicon_flow_client.analyze_patent(patent_text)
                logger.debug("API分析完成")
                logger.debug(f"API返回类型: {type(analysis_result)}")
                # 安全地记录部分API响应
                if isinstance(analysis_result, dict):
                    keys = list(analysis_result.keys())
                    logger.debug(f"API响应包含的键: {keys}")
                
                original_filename = file.filename  # 保存原始文件名用于显示
                return render_template('results.html', 
                                    filename=original_filename,
                                    analysis=analysis_result)
            except Exception as api_error:
                logger.exception(f"API调用失败: {str(api_error)}")
                flash(f'API analysis failed: {str(api_error)}', 'danger')
                return redirect(url_for('index'))
        except Exception as e:
            logger.exception(f"处理文件时出错: {str(e)}")
            flash(f'Error processing file: {str(e)}', 'danger')
            return redirect(url_for('index'))
    
    logger.error("不支持的文件格式")
    flash('Only DOCX files are allowed', 'danger')
    return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze_patent():
    if 'patent_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['patent_file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the DOCX and get patent text
        patent_text = extract_text_from_docx(filepath)
        
        # Send to SiliconFlow API for analysis
        analysis_result = silicon_flow_client.analyze_patent(patent_text)
        
        return jsonify(analysis_result)
    
    return jsonify({'error': 'Only DOCX files are allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True) 