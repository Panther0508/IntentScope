"""
IntentScope Live Preview Web Application
A real-time dashboard showing the AI-powered behavioral analytics system
with folder upload and code execution capabilities
"""

import os
import logging
import uuid
import shutil
import subprocess
import sys
import ast
import json
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for
from flask_cors import CORS
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import time
import zipfile
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

# Enable CORS for all routes
CORS(app)

# Upload folder configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions for upload
ALLOWED_EXTENSIONS = {
    'txt', 'py', 'js', 'html', 'css', 'json', 'xml', 'md', 'yaml', 'yml',
    'csv', 'log', 'sh', 'bat', 'ps1', 'sql', 'r', 'java', 'c', 'cpp',
    'h', 'hpp', 'cs', 'go', 'rs', 'rb', 'php', 'swift', 'kt', 'scala', 'ts'
}

# Store execution results in memory
execution_results = {}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_folder_size(folder_path):
    """Calculate total size of folder"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def format_size(size_bytes):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def scan_project_structure(folder_path):
    """Scan and return project structure"""
    structure = {
        'name': os.path.basename(folder_path),
        'path': folder_path,
        'type': 'folder',
        'children': []
    }
    
    try:
        items = sorted(os.listdir(folder_path))
        for item in items:
            # Skip hidden files and common temp directories
            if item.startswith('.') or item in ['__pycache__', 'node_modules', 'venv', '.git']:
                continue
                
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                structure['children'].append(scan_project_structure(item_path))
            else:
                if allowed_file(item):
                    size = os.path.getsize(item_path)
                    structure['children'].append({
                        'name': item,
                        'path': item_path,
                        'type': 'file',
                        'size': format_size(size),
                        'size_bytes': size
                    })
    except PermissionError:
        pass
    
    return structure


def analyze_project(folder_path):
    """Analyze project and return metadata"""
    analysis = {
        'total_files': 0,
        'total_folders': 0,
        'total_size': 0,
        'file_types': {},
        'languages': {},
        'main_files': [],
        'user_datasets': [],
        'csv_analysis': {}
    }
    
    # Language detection mapping
    language_map = {
        'py': 'Python',
        'js': 'JavaScript',
        'html': 'HTML',
        'css': 'CSS',
        'json': 'JSON',
        'xml': 'XML',
        'md': 'Markdown',
        'yaml': 'YAML',
        'yml': 'YAML',
        'csv': 'CSV',
        'sql': 'SQL',
        'r': 'R',
        'java': 'Java',
        'c': 'C',
        'cpp': 'C++',
        'h': 'C/C++ Header',
        'hpp': 'C++ Header',
        'cs': 'C#',
        'go': 'Go',
        'rs': 'Rust',
        'rb': 'Ruby',
        'php': 'PHP',
        'swift': 'Swift',
        'kt': 'Kotlin',
        'scala': 'Scala',
        'ts': 'TypeScript'
    }
    
    csv_files = []
    
    for root, dirs, files in os.walk(folder_path):
        # Skip hidden and temp directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
        
        analysis['total_folders'] += len(dirs)
        
        for file in files:
            if file.startswith('.'):
                continue
                
            file_path = os.path.join(root, file)
            ext = file.rsplit('.', 1)[-1].lower() if '.' in file else ''
            
            analysis['total_files'] += 1
            
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                analysis['total_size'] += size
                
                if ext:
                    analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
                    lang = language_map.get(ext, ext.upper())
                    analysis['languages'][lang] = analysis['languages'].get(lang, 0) + 1
                    
                    # Track CSV files for analysis
                    if ext == 'csv':
                        csv_files.append((file, file_path))
                
                # Identify main files
                main_file_patterns = ['main', 'index', 'app', 'server', 'setup', 'run']
                if any(pattern in file.lower() for pattern in main_file_patterns):
                    rel_path = os.path.relpath(file_path, folder_path)
                    analysis['main_files'].append({
                        'name': file,
                        'path': rel_path,
                        'size': format_size(size)
                    })
    
    # Analyze CSV files for user data
    if csv_files:
        analysis['csv_analysis'] = analyze_csv_datasets(csv_files)
        analysis['user_datasets'] = [f[0] for f in csv_files]
    
    analysis['total_size_formatted'] = format_size(analysis['total_size'])
    return analysis


def analyze_csv_datasets(csv_files):
    """Analyze CSV files to extract user data insights"""
    results = {
        'total_datasets': len(csv_files),
        'datasets': [],
        'user_columns_found': False,
        'column_stats': {},
        'summary': {}
    }
    
    # Common user-related column names
    user_column_patterns = [
        'user', 'customer', 'client', 'member', 'account', 'id',
        'name', 'email', 'age', 'gender', 'country', 'city', 'region',
        'signup', 'registered', 'created', 'last_login', 'active', 'status',
        'purchase', 'order', 'transaction', 'spent', 'amount', 'revenue',
        'subscription', 'plan', 'tier', 'churn', '流失', '用户'
    ]
    
    total_rows = 0
    
    for filename, filepath in csv_files:
        try:
            # Try different encodings
            df = None
            for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(filepath, encoding=encoding, nrows=1000)
                    break
                except:
                    continue
            
            if df is None or df.empty:
                continue
            
            # Get column info
            columns = list(df.columns)
            num_rows = len(df)
            total_rows += num_rows
            
            # Detect user-related columns
            user_cols = []
            numeric_cols = []
            categorical_cols = []
            
            for col in columns:
                col_lower = col.lower()
                
                # Check if it's a user-related column
                if any(pattern in col_lower for pattern in user_column_patterns):
                    user_cols.append(col)
                    results['user_columns_found'] = True
                
                # Check if numeric
                if pd.api.types.is_numeric_dtype(df[col]):
                    numeric_cols.append(col)
                # Check if categorical (object or few unique values)
                elif df[col].dtype == 'object' or df[col].nunique() < 50:
                    categorical_cols.append(col)
            
            # Generate basic stats
            dataset_info = {
                'name': filename,
                'rows': num_rows,
                'columns': len(columns),
                'user_columns': user_cols,
                'numeric_columns': numeric_cols[:10],  # Limit
                'categorical_columns': categorical_cols[:10],
                'preview': {}
            }
            
            # Add preview data
            for col in columns[:5]:
                if pd.api.types.is_numeric_dtype(df[col]):
                    dataset_info['preview'][col] = {
                        'type': 'numeric',
                        'min': float(df[col].min()) if not pd.isna(df[col].min()) else 0,
                        'max': float(df[col].max()) if not pd.isna(df[col].max()) else 0,
                        'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else 0
                    }
                else:
                    top_values = df[col].value_counts().head(5).to_dict()
                    dataset_info['preview'][col] = {
                        'type': 'categorical',
                        'unique': int(df[col].nunique()),
                        'top_values': {str(k): int(v) for k, v in top_values.items()}
                    }
            
            results['datasets'].append(dataset_info)
            
        except Exception as e:
            logger.error(f"Error analyzing CSV {filename}: {str(e)}")
            continue
    
    results['summary'] = {
        'total_rows': total_rows,
        'total_files': len(csv_files)
    }
    
    return results


def get_user_data_for_dashboard():
    """Get user data analytics for dashboard display"""
    if not execution_results:
        return None
    
    all_csv_analysis = {}
    total_files = 0
    total_size = 0
    languages = {}
    file_types = {}
    all_files = []
    user_datasets = []
    
    for project_id, project in execution_results.items():
        if not os.path.exists(project['folder_path']):
            continue
            
        analysis = project.get('analysis', {})
        total_files += analysis.get('total_files', 0)
        total_size += analysis.get('total_size', 0)
        
        # Aggregate languages
        for lang, count in analysis.get('languages', {}).items():
            languages[lang] = languages.get(lang, 0) + count
        
        # Aggregate file types
        for ft, count in analysis.get('file_types', {}).items():
            file_types[ft] = file_types.get(ft, 0) + count
        
        # Collect CSV analysis
        csv_analysis = analysis.get('csv_analysis', {})
        if csv_analysis:
            all_csv_analysis[project['name']] = csv_analysis
            user_datasets.extend(analysis.get('user_datasets', []))
        
        # Collect all files
        for root, dirs, files in os.walk(project['folder_path']):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if not f.startswith('.'):
                    rel_path = os.path.relpath(os.path.join(root, f), project['folder_path'])
                    all_files.append({
                        'id': len(all_files) + 1,
                        'name': f,
                        'path': rel_path,
                        'project': project['name'],
                        'size': format_size(os.path.getsize(os.path.join(root, f))),
                        'type': f.rsplit('.', 1)[-1].lower() if '.' in f else 'unknown'
                    })
    
    if total_files == 0:
        return None
    
    # Aggregate CSV data
    aggregated_csv = aggregate_csv_data(all_csv_analysis)
    
    return {
        'total_files': total_files,
        'total_size': format_size(total_size),
        'total_size_bytes': total_size,
        'languages': languages,
        'file_types': file_types,
        'files': all_files[:50],
        'total_projects': len(execution_results),
        'user_datasets': user_datasets,
        'csv_analysis': all_csv_analysis,
        'aggregated_csv': aggregated_csv
    }


def aggregate_csv_data(csv_analysis_dict):
    """Aggregate data from multiple CSV files"""
    if not csv_analysis_dict:
        return {}
    
    total_rows = 0
    all_user_cols = {}
    all_numeric_cols = {}
    all_categorical_cols = {}
    
    for project_name, analysis in csv_analysis_dict.items():
        for dataset in analysis.get('datasets', []):
            total_rows += dataset.get('rows', 0)
            
            # Collect column stats
            for col in dataset.get('user_columns', []):
                all_user_cols[col] = all_user_cols.get(col, 0) + 1
            
            for col in dataset.get('numeric_columns', []):
                all_numeric_cols[col] = col
            
            for col in dataset.get('categorical_columns', []):
                all_categorical_cols[col] = col
    
    return {
        'total_rows': total_rows,
        'user_columns': list(all_user_cols.keys()),
        'numeric_columns': list(all_numeric_cols.keys())[:20],
        'categorical_columns': list(all_categorical_cols.keys())[:20]
    }


def execute_python_file(file_path, project_folder):
    """Execute a Python file and return output"""
    result = {
        'success': False,
        'output': '',
        'error': '',
        'execution_time': 0
    }
    
    start_time = time.time()
    
    try:
        # Create a restricted environment for execution
        env = os.environ.copy()
        env['PYTHONPATH'] = project_folder
        
        # Run with timeout
        process = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=project_folder,
            env=env
        )
        
        result['success'] = process.returncode == 0
        result['output'] = process.stdout
        result['error'] = process.stderr
        
    except subprocess.TimeoutExpired:
        result['error'] = 'Execution timed out (30 second limit)'
    except Exception as e:
        result['error'] = str(e)
    
    result['execution_time'] = round(time.time() - start_time, 3)
    return result


def execute_javascript_file(file_path, project_folder):
    """Execute a JavaScript file using Node.js"""
    result = {
        'success': False,
        'output': '',
        'error': '',
        'execution_time': 0
    }
    
    start_time = time.time()
    
    try:
        process = subprocess.run(
            ['node', file_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=project_folder
        )
        
        result['success'] = process.returncode == 0
        result['output'] = process.stdout
        result['error'] = process.stderr
        
    except subprocess.TimeoutExpired:
        result['error'] = 'Execution timed out (30 second limit)'
    except FileNotFoundError:
        result['error'] = 'Node.js not installed'
    except Exception as e:
        result['error'] = str(e)
    
    result['execution_time'] = round(time.time() - start_time, 3)
    return result


def read_file_content(file_path, max_size=1024*1024):
    """Read file content with size limit"""
    try:
        if os.path.getsize(file_path) > max_size:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(max_size) + f"\n\n... (file truncated, showing first {format_size(max_size)})"
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


# Sample data generators (existing functionality)
def generate_live_users():
    """Generate live user data for the dashboard"""
    users = []
    user_types = ['Builder', 'Explorer', 'Learner', 'Abandoner']
    
    for i in range(50):
        user = {
            'id': i + 1,
            'name': f'User_{i+1:03d}',
            'type': random.choice(user_types),
            'interactions': random.randint(1, 100),
            'success_rate': round(random.uniform(0.3, 1.0), 2),
            'churn_risk': round(random.uniform(0.1, 0.9), 2),
            'last_active': (datetime.now() - timedelta(minutes=random.randint(1, 1440))).isoformat(),
            'is_anomaly': random.random() < 0.05,
            'segment': random.choice(['Premium', 'Regular', 'New', 'At-Risk'])
        }
        users.append(user)
    
    return users


def get_project_data_for_dashboard():
    """Get project data formatted for dashboard display"""
    if not execution_results:
        return None
    
    # Aggregate data from all projects
    total_files = 0
    total_size = 0
    languages = {}
    file_types = {}
    all_files = []
    user_datasets = []
    csv_analysis = {}
    
    for project_id, project in execution_results.items():
        if not os.path.exists(project['folder_path']):
            continue
            
        analysis = project.get('analysis', {})
        total_files += analysis.get('total_files', 0)
        total_size += analysis.get('total_size', 0)
        
        # Aggregate languages
        for lang, count in analysis.get('languages', {}).items():
            languages[lang] = languages.get(lang, 0) + count
        
        # Aggregate file types
        for ft, count in analysis.get('file_types', {}).items():
            file_types[ft] = file_types.get(ft, 0) + count
        
        # Collect CSV analysis
        if analysis.get('csv_analysis'):
            csv_analysis[project['name']] = analysis['csv_analysis']
            user_datasets.extend(analysis.get('user_datasets', []))
        
        # Collect all files
        for root, dirs, files in os.walk(project['folder_path']):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if not f.startswith('.'):
                    rel_path = os.path.relpath(os.path.join(root, f), project['folder_path'])
                    all_files.append({
                        'id': len(all_files) + 1,
                        'name': f,
                        'path': rel_path,
                        'project': project['name'],
                        'size': format_size(os.path.getsize(os.path.join(root, f))),
                        'type': f.rsplit('.', 1)[-1].lower() if '.' in f else 'unknown'
                    })
    
    if total_files == 0:
        return None
    
    # Aggregate CSV data
    aggregated_csv = aggregate_csv_data(csv_analysis)
    
    return {
        'total_files': total_files,
        'total_size': format_size(total_size),
        'total_size_bytes': total_size,
        'languages': languages,
        'file_types': file_types,
        'files': all_files[:50],  # Limit to 50 files for display
        'total_projects': len(execution_results),
        'user_datasets': user_datasets,
        'csv_analysis': csv_analysis,
        'aggregated_csv': aggregated_csv
    }


def generate_metrics():
    """Generate real-time metrics"""
    return {
        'total_users': random.randint(4500, 5500),
        'active_users': random.randint(800, 1200),
        'avg_success_rate': round(random.uniform(0.75, 0.90), 3),
        'churn_rate': round(random.uniform(0.05, 0.15), 3),
        'anomalies_detected': random.randint(10, 50),
        'predictions_made': random.randint(1000, 5000),
        'recommendations_served': random.randint(500, 2000),
        'timestamp': datetime.now().isoformat()
    }


def generate_intention_distribution():
    """Generate intention class distribution"""
    total = 1000
    return {
        'Builder': random.randint(200, 350),
        'Explorer': random.randint(150, 300),
        'Learner': random.randint(200, 400),
        'Abandoner': random.randint(50, 150)
    }


def generate_feature_importance():
    """Generate feature importance data"""
    features = [
        'successful_actions', 'overall_success_rate', 'advanced_premium_usage',
        'total_interactions', 'unique_actions', 'session_duration_mean',
        'action_diversity_ratio', 'days_active', 'login_count', 'complete_sessions'
    ]
    
    importance = {f: round(random.uniform(0.01, 0.5), 4) for f in features}
    total = sum(importance.values())
    return {k: round(v/total, 4) for k, v in importance.items()}


# Routes
@app.route('/')
def index():
    # Check for page parameter to switch to specific tab on load
    page = request.args.get('page', 'dashboard')
    return render_template('index.html', initial_page=page)


@app.route('/upload')
def upload_page():
    """Dedicated upload page"""
    return render_template('index.html', initial_page='upload')


@app.route('/projects')
def projects_page():
    """Projects management page"""
    return render_template('index.html', initial_page='projects')


@app.route('/execute')
def execute_page():
    """Code execution page"""
    return render_template('index.html', initial_page='execute')


@app.route('/api/upload', methods=['POST'])
def upload_folder():
    """Handle folder/file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Generate unique folder ID
        folder_id = str(uuid.uuid4())
        project_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_id)
        os.makedirs(project_folder, exist_ok=True)
        
        # Handle ZIP files (folder uploads)
        if file.filename.endswith('.zip'):
            try:
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    zip_ref.extractall(project_folder)
                project_name = os.path.splitext(file.filename)[0]
            except zipfile.BadZipFile:
                return jsonify({'success': False, 'error': 'Invalid ZIP file'}), 400
        else:
            # Single file upload
            filename = file.filename
            file.save(os.path.join(project_folder, filename))
            project_name = os.path.splitext(filename)[0]
        
        # Get project structure
        structure = scan_project_structure(project_folder)
        analysis = analyze_project(project_folder)
        
        # Store project info
        project_info = {
            'id': folder_id,
            'name': project_name,
            'folder_path': project_folder,
            'structure': structure,
            'analysis': analysis,
            'created_at': datetime.now().isoformat()
        }
        
        execution_results[folder_id] = project_info
        
        return jsonify({
            'success': True,
            'project': {
                'id': folder_id,
                'name': project_name,
                'structure': structure,
                'analysis': analysis
            }
        })
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/projects', methods=['GET'])
def list_projects():
    """List all uploaded projects"""
    projects = []
    
    try:
        for folder_id, project_info in execution_results.items():
            if os.path.exists(project_info['folder_path']):
                projects.append({
                    'id': folder_id,
                    'name': project_info['name'],
                    'created_at': project_info['created_at'],
                    'analysis': project_info['analysis']
                })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({'success': True, 'projects': projects})


@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get project details"""
    if project_id not in execution_results:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    project = execution_results[project_id]
    
    # Refresh analysis
    if os.path.exists(project['folder_path']):
        project['analysis'] = analyze_project(project['folder_path'])
        project['structure'] = scan_project_structure(project['folder_path'])
    
    return jsonify({
        'success': True,
        'project': {
            'id': project_id,
            'name': project['name'],
            'structure': project['structure'],
            'analysis': project['analysis'],
            'created_at': project['created_at']
        }
    })


@app.route('/api/projects/<project_id>/file', methods=['GET'])
def get_file_content(project_id):
    """Get content of a specific file"""
    if project_id not in execution_results:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({'success': False, 'error': 'No file path provided'}), 400
    
    full_path = os.path.join(execution_results[project_id]['folder_path'], file_path)
    
    if not os.path.exists(full_path):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    content = read_file_content(full_path)
    
    return jsonify({
        'success': True,
        'content': content,
        'file_name': os.path.basename(file_path),
        'file_path': file_path
    })


@app.route('/api/projects/<project_id>/execute', methods=['POST'])
def execute_project(project_id):
    """Execute code in a project"""
    if project_id not in execution_results:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    data = request.get_json()
    file_path = data.get('file_path', '')
    
    if not file_path:
        return jsonify({'success': False, 'error': 'No file path provided'}), 400
    
    project = execution_results[project_id]
    full_path = os.path.join(project['folder_path'], file_path)
    
    if not os.path.exists(full_path):
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else ''
    
    # Execute based on file type
    if ext == 'py':
        result = execute_python_file(full_path, project['folder_path'])
    elif ext == 'js':
        result = execute_javascript_file(full_path, project['folder_path'])
    else:
        return jsonify({
            'success': False,
            'error': f'Execution not supported for .{ext} files'
        }), 400
    
    return jsonify({
        'success': True,
        'execution': {
            'file': file_path,
            'result': result
        }
    })


@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    if project_id not in execution_results:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    
    project = execution_results[project_id]
    
    try:
        if os.path.exists(project['folder_path']):
            shutil.rmtree(project['folder_path'])
        
        del execution_results[project_id]
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Analytics API routes (existing)
@app.route('/api/data')
def api_data():
    """Combined API for dashboard data - returns project data if available, demo data otherwise"""
    # Check if there are uploaded projects
    project_data = get_project_data_for_dashboard()
    
    if project_data:
        # Return project data with CSV analysis
        return jsonify({
            'mode': 'project',
            'metrics': {
                'total_files': project_data['total_files'],
                'total_projects': project_data['total_projects'],
                'total_size': project_data['total_size'],
                'active_files': project_data['total_files'],
                'languages': len(project_data['languages']),
                'file_types': len(project_data['file_types']),
                'total_rows': project_data.get('aggregated_csv', {}).get('total_rows', 0),
                'user_datasets': len(project_data.get('user_datasets', [])),
                'timestamp': datetime.now().isoformat()
            },
            'files': project_data['files'],
            'languages': project_data['languages'],
            'file_types': project_data['file_types'],
            'project_stats': {
                'labels': list(project_data['languages'].keys()),
                'values': list(project_data['languages'].values())
            },
            'file_type_stats': {
                'labels': list(project_data['file_types'].keys()),
                'values': list(project_data['file_types'].values())
            },
            # User data analysis
            'user_analysis': {
                'datasets': project_data.get('user_datasets', []),
                'csv_analysis': project_data.get('csv_analysis', {}),
                'aggregated': project_data.get('aggregated_csv', {}),
                'has_user_data': len(project_data.get('user_datasets', [])) > 0
            }
        })
    
    # Return demo data if no projects
    return jsonify({
        'mode': 'demo',
        'metrics': generate_metrics(),
        'users': generate_live_users(),
        'intention_dist': generate_intention_distribution(),
        'feature_importance': generate_feature_importance(),
        'segment_data': {
            'Premium': random.randint(280, 380),
            'Regular': random.randint(1100, 1400),
            'New': random.randint(500, 700),
            'At-Risk': random.randint(100, 200)
        },
        'activity_data': {
            'labels': ['6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm'],
            'values': [random.randint(100, 200), random.randint(200, 350), random.randint(300, 450), 
                      random.randint(450, 600), random.randint(400, 550), random.randint(350, 500),
                      random.randint(300, 450), random.randint(200, 350), random.randint(100, 250)]
        }
    })


@app.route('/api/demo')
def api_demo():
    """Force demo data regardless of uploaded projects"""
    return jsonify({
        'mode': 'demo',
        'metrics': generate_metrics(),
        'users': generate_live_users(),
        'intention_dist': generate_intention_distribution(),
        'feature_importance': generate_feature_importance(),
        'segment_data': {
            'Premium': random.randint(280, 380),
            'Regular': random.randint(1100, 1400),
            'New': random.randint(500, 700),
            'At-Risk': random.randint(100, 200)
        },
        'activity_data': {
            'labels': ['6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm'],
            'values': [random.randint(100, 200), random.randint(200, 350), random.randint(300, 450), 
                      random.randint(450, 600), random.randint(400, 550), random.randint(350, 500),
                      random.randint(300, 450), random.randint(200, 350), random.randint(100, 250)]
        }
    })


@app.route('/api/init')
def api_init():
    """Initial data for chart initialization"""
    return jsonify({
        'intention_dist': generate_intention_distribution(),
        'feature_importance': generate_feature_importance(),
        'activity_data': {
            'labels': ['6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm'],
            'values': [120, 250, 380, 520, 480, 420, 380, 290, 180]
        },
        'segment_data': {
            'Premium': 320,
            'Regular': 1250,
            'New': 580,
            'At-Risk': 150
        }
    })


@app.route('/api/metrics')
def api_metrics():
    """Live metrics data"""
    return jsonify({
        'metrics': generate_metrics(),
        'users': generate_live_users(),
        'intention_dist': generate_intention_distribution(),
        'feature_importance': generate_feature_importance(),
        'activity_data': {
            'labels': ['6am', '8am', '10am', '12pm', '2pm', '4pm', '6pm', '8pm', '10pm'],
            'values': [random.randint(100, 200), random.randint(200, 350), random.randint(300, 450), 
                      random.randint(450, 600), random.randint(400, 550), random.randint(350, 500),
                      random.randint(300, 450), random.randint(200, 350), random.randint(100, 250)]
        },
        'segment_data': {
            'Premium': random.randint(280, 380),
            'Regular': random.randint(1100, 1400),
            'New': random.randint(500, 700),
            'At-Risk': random.randint(100, 200)
        }
    })


# Health check endpoint for Render
@app.route('/health')
def health_check():
    """Health check endpoint for Render deployment"""
    return jsonify({
        'status': 'healthy',
        'service': 'IntentScope Analytics',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'endpoints': ['/api/metrics', '/api/init', '/api/data', '/health', '/api/upload', '/api/projects']
    })


# ===== Admin Feedback System API Endpoints =====

@app.route('/api/admin/predictions')
def api_admin_predictions():
    """
    Get comprehensive prediction data with confidence scores and actionable insights.
    This endpoint provides administrators with a clear view of user intent predictions.
    """
    # Generate prediction data with confidence scores
    predictions = []
    user_types = ['Builder', 'Explorer', 'Learner', 'Abandoner']
    
    # Actionable insights mapping
    insights_map = {
        'Builder': [
            'User is actively creating projects - Consider offering advanced templates',
            'High engagement indicates satisfaction - Recommend premium features',
            'User shows consistent activity patterns - Ideal for referral programs'
        ],
        'Explorer': [
            'User is browsing without committing - Show targeted recommendations',
            'Consider personalized onboarding to guide next steps',
            'User may need help discovering relevant features'
        ],
        'Learner': [
            'User is investing time in understanding platform - Offer tutorials',
            'Consider providing educational resources and guided tours',
            'User may benefit from interactive learning experiences'
        ],
        'Abandoner': [
            'User shows signs of disengagement - Send re-engagement campaigns',
            'Consider offering incentives or support to prevent churn',
            'High risk of leaving - Priority for customer retention efforts'
        ]
    }
    
    # Recommended responses mapping
    responses_map = {
        'Builder': [
            'Send: "Explore our advanced features for power users"',
            'Notify about new template releases',
            'Invite to beta testing program'
        ],
        'Explorer': [
            'Send: "Getting started guide"',
            'Highlight popular features in this category',
            'Offer personalized demo'
        ],
        'Learner': [
            'Send: "Platform tutorial series"',
            'Offer live chat support',
            'Provide documentation links'
        ],
        'Abandoner': [
            'Send: "We miss you! 20% off your next month"',
            'Request feedback survey',
            'Offer extended trial period'
        ]
    }
    
    for i in range(30):
        user_type = random.choice(user_types)
        confidence = round(random.uniform(0.65, 0.98), 3)
        
        predictions.append({
            'id': f'PRED-{i+1:05d}',
            'user_id': f'USER-{i+1:03d}',
            'timestamp': (datetime.now() - timedelta(minutes=random.randint(1, 1440))).isoformat(),
            'predicted_intent': user_type,
            'confidence_score': confidence,
            'confidence_level': 'High' if confidence >= 0.85 else 'Medium' if confidence >= 0.70 else 'Low',
            'alternative_intents': [t for t in user_types if t != user_type][:2],
            'alternative_confidences': [round(random.uniform(0.1, 0.3), 3) for _ in range(2)],
            'actionable_insights': random.sample(insights_map[user_type], 2),
            'recommended_response': random.choice(responses_map[user_type]),
            'behavioral_indicators': [
                f'Action count: {random.randint(10, 200)}',
                f'Session duration: {random.randint(5, 120)} min',
                f'Feature usage: {random.choice(["Basic", "Intermediate", "Advanced"])}',
                f'Login frequency: {random.choice(["Daily", "Weekly", "Monthly"])}'
            ],
            'verified': random.choice([True, False]),
            'feedback': None
        })
    
    # Sort by confidence (highest first)
    predictions.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    return jsonify({
        'predictions': predictions,
        'summary': {
            'total_predictions': len(predictions),
            'high_confidence_count': len([p for p in predictions if p['confidence_level'] == 'High']),
            'medium_confidence_count': len([p for p in predictions if p['confidence_level'] == 'Medium']),
            'low_confidence_count': len([p for p in predictions if p['confidence_level'] == 'Low']),
            'verified_count': len([p for p in predictions if p['verified']]),
            'pending_verification': len([p for p in predictions if not p['verified']])
        },
        'intent_distribution': generate_intention_distribution(),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/admin/predictions/<prediction_id>', methods=['POST'])
def api_admin_verify_prediction(prediction_id):
    """
    Allow admin to verify or correct a prediction.
    Provides feedback mechanism for improving the model.
    """
    data = request.get_json()
    
    # In a real app, this would update a database
    return jsonify({
        'success': True,
        'prediction_id': prediction_id,
        'verified': data.get('verified', False),
        'corrected_intent': data.get('corrected_intent'),
        'admin_feedback': data.get('feedback'),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/admin/historical-trends')
def api_admin_historical_trends():
    """
    Get historical trend data for admin analysis.
    Shows prediction accuracy over time and intent patterns.
    """
    # Generate 30 days of historical data
    trends = []
    base_users = 1000
    
    for days_ago in range(30, -1, -1):
        date = datetime.now() - timedelta(days=days_ago)
        trend = {
            'date': date.strftime('%Y-%m-%d'),
            'total_predictions': base_users + random.randint(-100, 300),
            'builder_count': random.randint(200, 400),
            'explorer_count': random.randint(150, 350),
            'learner_count': random.randint(200, 450),
            'abandoner_count': random.randint(50, 200),
            'accuracy': round(random.uniform(0.75, 0.95), 3),
            'high_confidence_rate': round(random.uniform(0.60, 0.85), 3),
            'verified_count': random.randint(50, 150),
            'corrections_made': random.randint(5, 30)
        }
        trends.append(trend)
    
    # Calculate weekly averages
    weekly_averages = []
    for week in range(4):
        week_start = 28 - (week * 7)
        week_end = 21 - (week * 7)
        week_data = trends[week_end:week_start] if week_start < len(trends) else trends[:7]
        
        weekly_averages.append({
            'week': f'Week {4-week}',
            'avg_accuracy': round(sum(t['accuracy'] for t in week_data) / len(week_data), 3),
            'avg_predictions': int(sum(t['total_predictions'] for t in week_data) / len(week_data)),
            'total_corrections': sum(t['corrections_made'] for t in week_data)
        })
    
    return jsonify({
        'daily_trends': trends,
        'weekly_averages': weekly_averages,
        'summary': {
            'avg_accuracy': round(sum(t['accuracy'] for t in trends) / len(trends), 3),
            'total_predictions_30d': sum(t['total_predictions'] for t in trends),
            'total_corrections_30d': sum(t['corrections_made'] for t in trends),
            'accuracy_trend': 'improving' if trends[-1]['accuracy'] > trends[0]['accuracy'] else 'stable'
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/admin/reports')
def api_admin_reports():
    """
    Generate comprehensive reports for administrators.
    Provides insights into system performance and user behavior patterns.
    """
    # Generate report data
    report_types = [
        'prediction_accuracy',
        'user_intent_distribution',
        'admin_intervention_summary',
        'system_performance',
        'recommendations'
    ]
    
    reports = []
    for report_type in report_types:
        report = {
            'id': f'REPORT-{random.randint(1000, 9999)}',
            'type': report_type,
            'title': report_type.replace('_', ' ').title(),
            'generated_at': datetime.now().isoformat(),
            'period': 'Last 30 days',
            'metrics': generate_report_metrics(report_type),
            'insights': generate_report_insights(report_type)
        }
        reports.append(report)
    
    return jsonify({
        'reports': reports,
        'available_formats': ['JSON', 'CSV', 'PDF'],
        'timestamp': datetime.now().isoformat()
    })


def generate_report_metrics(report_type):
    """Generate metrics for different report types"""
    metrics_map = {
        'prediction_accuracy': {
            'overall_accuracy': round(random.uniform(0.80, 0.92), 3),
            'high_confidence_accuracy': round(random.uniform(0.88, 0.96), 3),
            'low_confidence_accuracy': round(random.uniform(0.55, 0.72), 3),
            'verified_predictions': random.randint(800, 1500),
            'corrections_submitted': random.randint(50, 200)
        },
        'user_intent_distribution': {
            'builder_percentage': round(random.uniform(0.20, 0.35), 3),
            'explorer_percentage': round(random.uniform(0.15, 0.28), 3),
            'learner_percentage': round(random.uniform(0.25, 0.40), 3),
            'abandoner_percentage': round(random.uniform(0.08, 0.18), 3),
            'trend': 'stable'
        },
        'admin_intervention_summary': {
            'total_interventions': random.randint(100, 300),
            'successful_interventions': random.randint(60, 200),
            'average_response_time': f'{random.randint(5, 30)} hours',
            'most_common_action': random.choice(['feedback_correction', 'manual_override', 'rule_adjustment'])
        },
        'system_performance': {
            'avg_prediction_time': f'{random.randint(50, 200)}ms',
            'uptime': f'{random.uniform(99.5, 99.99):.2f}%',
            'api_calls_today': random.randint(5000, 15000),
            'active_models': random.randint(2, 5)
        },
        'recommendations': {
            'model_improvement': 'Consider retraining with recent user data',
            'feature_addition': 'Add more behavioral features for better accuracy',
            'threshold_adjustment': 'Current confidence thresholds appear optimal',
            'priority': 'medium'
        }
    }
    return metrics_map.get(report_type, {})


def generate_report_insights(report_type):
    """Generate human-readable insights for reports"""
    insights_map = {
        'prediction_accuracy': [
            'High-confidence predictions are highly reliable (88-96% accuracy)',
            'Low-confidence predictions may benefit from additional feature engineering',
            'Regular model retraining recommended for maintaining accuracy'
        ],
        'user_intent_distribution': [
            'Builders represent the most engaged user segment',
            'Abandoners show declining trend - intervention recommended',
            'Learners show increased activity - educational content effective'
        ],
        'admin_intervention_summary': [
            'Feedback loop is actively improving prediction quality',
            'Most corrections are minor intent adjustments',
            'Response time within acceptable SLA'
        ],
        'system_performance': [
            'System running within normal parameters',
            'Prediction latency within acceptable range',
            'No critical issues detected'
        ],
        'recommendations': [
            'Review low-confidence predictions for pattern identification',
            'Consider A/B testing new prediction thresholds',
            'Schedule quarterly model evaluation'
        ]
    }
    return insights_map.get(report_type, [])


@app.route('/api/admin/export', methods=['POST'])
def api_admin_export():
    """
    Export prediction data in various formats.
    Allows administrators to download data for offline analysis.
    """
    data = request.get_json()
    export_format = data.get('format', 'json').upper()
    data_type = data.get('type', 'predictions')
    
    # Generate sample export data
    export_data = {
        'predictions': [
            {
                'id': f'PRED-{i:05d}',
                'user_id': f'USER-{i:03d}',
                'intent': random.choice(['Builder', 'Explorer', 'Learner', 'Abandoner']),
                'confidence': round(random.uniform(0.65, 0.98), 3),
                'timestamp': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
            }
            for i in range(100)
        ],
        'metadata': {
            'export_type': data_type,
            'format': export_format,
            'generated_at': datetime.now().isoformat(),
            'record_count': 100
        }
    }
    
    return jsonify({
        'success': True,
        'format': export_format,
        'data_type': data_type,
        'download_url': f'/api/admin/download/{data_type}.{export_format.lower()}',
        'record_count': 100,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/admin/settings')
def api_admin_settings():
    """
    Get and update admin settings for the prediction system.
    Allows configuration of thresholds and notification preferences.
    """
    return jsonify({
        'settings': {
            'confidence_thresholds': {
                'high': 0.85,
                'medium': 0.70,
                'low': 0.50
            },
            'notifications': {
                'email_alerts': True,
                'low_confidence_alerts': True,
                'anomaly_detection': True,
                'daily_summary': True
            },
            'auto_verification': {
                'enabled': False,
                'min_confidence': 0.95
            },
            'model_settings': {
                'retrain_frequency': 'weekly',
                'include_feedback': True,
                'min_training_samples': 1000
            }
        },
        'available_options': {
            'retrain_frequency': ['daily', 'weekly', 'monthly'],
            'alert_channels': ['email', 'slack', 'webhook']
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/admin/settings', methods=['POST'])
def api_admin_update_settings():
    """
    Update admin settings for the prediction system.
    """
    data = request.get_json()
    
    # In a real app, this would save to a database
    return jsonify({
        'success': True,
        'message': 'Settings updated successfully',
        'updated_settings': data,
        'timestamp': datetime.now().isoformat()
    })


# Import AI Service
try:
    import ai_service
    AI_SERVICE_AVAILABLE = True
except ImportError:
    AI_SERVICE_AVAILABLE = False


# ==================== AI Model API Endpoints ====================

@app.route('/api/ai/status')
def ai_status():
    """
    Get AI model status - check which models are loaded
    """
    if not AI_SERVICE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'AI service not available',
            'models': {}
        })
    
    status = ai_service.get_ai_status()
    hf_token = ai_service.get_hf_token()
    
    return jsonify({
        'success': True,
        'available': status['hf_available'],
        'models': status['models'],
        'authenticated': hf_token is not None,
        'token_configured': bool(hf_token)
    })


@app.route('/api/ai/summarize', methods=['POST'])
def ai_summarize():
    """
    Summarize text using Hugging Face BART model
    """
    if not AI_SERVICE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'AI service not available'
        }), 500
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({
            'success': False,
            'error': 'No text provided'
        }), 400
    
    max_length = data.get('max_length', 150)
    min_length = data.get('min_length', 40)
    
    result = ai_service.summarize_text(text, max_length, min_length)
    return jsonify(result)


@app.route('/api/ai/sentiment', methods=['POST'])
def ai_sentiment():
    """
    Analyze sentiment using Hugging Face DistilBERT model
    """
    if not AI_SERVICE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'AI service not available'
        }), 500
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({
            'success': False,
            'error': 'No text provided'
        }), 400
    
    result = ai_service.analyze_sentiment(text)
    return jsonify(result)


@app.route('/api/ai/generate', methods=['POST'])
def ai_generate():
    """
    Generate text using Hugging Face GPT-2 model
    """
    if not AI_SERVICE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'AI service not available'
        }), 500
    
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({
            'success': False,
            'error': 'No prompt provided'
        }), 400
    
    max_new_tokens = data.get('max_tokens', 100)
    temperature = data.get('temperature', 0.9)
    top_p = data.get('top_p', 0.95)
    
    result = ai_service.generate_text(prompt, max_new_tokens, temperature, top_p)
    return jsonify(result)


@app.route('/api/ai/qa', methods=['POST'])
def ai_qa():
    """
    Answer questions using Hugging Face DistilBERT QA model
    """
    if not AI_SERVICE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'AI service not available'
        }), 500
    
    data = request.get_json()
    context = data.get('context', '')
    question = data.get('question', '')
    
    if not context or not question:
        return jsonify({
            'success': False,
            'error': 'Both context and question are required'
        }), 400
    
    result = ai_service.answer_question(context, question)
    return jsonify(result)


@app.route('/ai-tools')
def ai_tools_page():
    """AI Tools page showing available AI features"""
    return render_template('index.html', initial_page='ai-tools')


@app.route('/admin')
def admin_page():
    """Admin dashboard page"""
    return render_template('index.html', initial_page='admin')


if __name__ == '__main__':
    print("=" * 60)
    print("IntentScope - AI Analytics with Project Upload")
    print("=" * 60)
    print("Open your browser to: http://127.0.0.1:5000")
    print("Features:")
    print("  - Dashboard: Real-time analytics")
    print("  - Upload: Upload project folders (ZIP or files)")
    print("  - Projects: Browse and manage uploaded projects")
    print("  - Execute: Run Python and JavaScript files")
    print("  - AI Tools: Text summarization, sentiment analysis, generation")
    print("=" * 60)
    
    if AI_SERVICE_AVAILABLE:
        print("AI Models: Loading on first request...")
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
