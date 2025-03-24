from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from dotenv import load_dotenv
from app.utils.docx_processor import extract_text_from_docx
from app.api.siliconflow_client import SiliconFlowClient
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
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
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_patent():
    if 'patent_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['patent_file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the DOCX and get patent text
        patent_text = extract_text_from_docx(filepath)
        
        # Send to SiliconFlow API for analysis
        analysis_result = silicon_flow_client.analyze_patent(patent_text)
        
        return render_template('results.html', 
                              filename=filename,
                              analysis=analysis_result)
    
    flash('Only DOCX files are allowed')
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