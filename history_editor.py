import os
import sqlite3
from flask import (
    Blueprint, render_template, request, jsonify, redirect, url_for, session
)
from encrypt import encrypt_text, decrypt_text

# --- 1. 创建一个蓝图对象 ---
# 'history_editor' 是蓝图的名字，后面会用到。
# __name__ 是必需的参数。
# template_folder='templates' 告诉蓝图模板文件在哪里。
history_bp = Blueprint(
    'history_editor', 
    __name__, 
    template_folder='templates'
)

# --- 数据库路径和初始化函数 (现在属于这个蓝图了) ---
HISTORICAL_DB_PATH = 'historical_diary.db'

def init_historical_db_once():
    """如果历史数据库不存在，则创建它和其中的 diary 表"""
    if not os.path.exists(HISTORICAL_DB_PATH):
        conn = sqlite3.connect(HISTORICAL_DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS diary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print(f"已成功创建并初始化 '{HISTORICAL_DB_PATH}'")


# --- 2. 将所有路由的装饰器从 @app.route 改为 @history_bp.route ---

# [视图路由] - 显示历史日记的编辑器页面
@history_bp.route('/editor') # 注意：这里的路径是相对于蓝图的
def editor_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # 模板名不变，蓝图知道去 'templates' 文件夹里找
    return render_template('history_editor.html')

# --- API 端点 (CRUD for historical_diary.db) ---

# [API - READ] 获取所有历史日记列表
@history_bp.route('/api/entries', methods=['GET'])
def get_historical_entries():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    
    init_historical_db_once()
    try:
        conn = sqlite3.connect(HISTORICAL_DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT id, title, content, created_at FROM diary ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        
        password = session.get('key')
        entries = [
            {
                "id": row['id'], 
                "title": row['title'], 
                "content": decrypt_text(row['content'], password), 
                "created_at": row['created_at']
            } for row in rows
        ]
        return jsonify(entries)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# [API - CREATE] 添加一篇新的历史日记
@history_bp.route('/api/entries', methods=['POST'])
def add_historical_entry():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    password = session.get('key')
    try:
        init_historical_db_once()
        content_encrypted = encrypt_text(data['content'], password)
        with sqlite3.connect(HISTORICAL_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO diary (title, content, created_at) VALUES (?, ?, ?)',
                (data['title'], content_encrypted, data['date'])
            )
            new_id = cursor.lastrowid
        return jsonify({"success": True, "id": new_id, "title": data['title']}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# [API - UPDATE] 更新一篇指定的历史日记
@history_bp.route('/api/entries/<int:entry_id>', methods=['PUT'])
def update_historical_entry(entry_id):
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json()
    password = session.get('key')
    try:
        content_encrypted = encrypt_text(data['content'], password)
        with sqlite3.connect(HISTORICAL_DB_PATH) as conn:
            conn.execute(
                'UPDATE diary SET title = ?, content = ?, created_at = ? WHERE id = ?',
                (data['title'], content_encrypted, data['date'], entry_id)
            )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# [API - DELETE] 删除一篇指定的历史日记
@history_bp.route('/api/entries/<int:entry_id>', methods=['DELETE'])
def delete_historical_entry(entry_id):
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        with sqlite3.connect(HISTORICAL_DB_PATH) as conn:
            conn.execute('DELETE FROM diary WHERE id = ?', (entry_id,))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500