# app.py
# 后端逻辑
import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_bcrypt import Bcrypt
import sqlite3
from datetime import datetime
from config import SECRET_KEY, USERNAME, PASSWORD_HASH
from encrypt import encrypt_text, decrypt_text
# 新增的日记中主题功能
from zoneinfo import ZoneInfo
# 新增的历史日记功能
from history_editor import history_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY
bcrypt = Bcrypt(app)

# 我们为这个蓝图的所有路由都加上了 /history 的前缀, 这样更清晰地将功能分区
app.register_blueprint(history_bp, url_prefix='/history')

# --- ▼▼▼ 主题和时区配置 ▼▼▼ ---
THEMES = [
    # 示例：未来可以添加其他主题
    # {
    #     "title": "波士顿日记-6月",
    #     "start": datetime(2025, 6, 1, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
    #     "end": None,
    #     "timezone": ZoneInfo("America/New_York")
    # },
    #====================================================================
    #==============================  日记  ==============================
    #====================================================================
    {
        "title": "2025年夏：蛇形物语（前篇）",
        "start": datetime(2025, 5, 25, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
        "end": datetime(2025, 8, 24, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
        "timezone": ZoneInfo("America/New_York") 
    },
    {
        "title": "2025年秋：蛇形物语（后篇）",
        "start": datetime(2025, 8, 24, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
        "end": datetime(2025, 12, 5, 19, 40, 0, tzinfo=ZoneInfo("UTC")),
        "timezone": ZoneInfo("America/New_York") 
    },
    {
        "title": "2025年冬：狭间的宴会",
        "start": datetime(2025, 12, 5, 19, 40, 1, tzinfo=ZoneInfo("UTC")),
        "end": datetime(2026, 3, 15, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
        "timezone": ZoneInfo("America/New_York") 
    },
    # {
    #     "title": "2026年春：主题待定中",
    #     "start": datetime(2026, 3, 15, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
    #     "end": datetime(2026, 6, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
    #     "timezone": ZoneInfo("America/New_York") 
    # },
    # {
    #     "title": "2026年夏：主题待定中",
    #     "start": datetime(YYYY, MM, DD, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
    #     "end": datetime(YYYY, MM, DD, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
    #     "timezone": ZoneInfo("America/New_York") 
    # },
    #====================================================================
    #=========================== 人界书  =============================
    #====================================================================
    # {
    #     "title": "古典时代",
    #     "start": datetime(2200, 1, 1, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
    #     "end": datetime(2299, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
    #     "timezone": ZoneInfo("America/New_York") 
    # },
    # {
    #     "title": "西北往事",
    #     "start": datetime(YYYY, MM, DD, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
    #     "end": datetime(YYYY, MM, DD, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
    #     "timezone": ZoneInfo("America/New_York") 
    # },
    # {
    #     "title": "东北往事",
    #     "start": datetime(YYYY, MM, DD, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
    #     "end": datetime(YYYY, MM, DD, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
    #     "timezone": ZoneInfo("America/New_York") 
    # },
    # {
    #     "title": "塔纳波契亚",
    #     "start": datetime(YYYY, MM, DD, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
    #     "end": datetime(YYYY, MM, DD, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
    #     "timezone": ZoneInfo("America/New_York") 
    # },
    # {
    #     "title": "",
    #     "start": datetime(YYYY, MM, DD, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
    #     "end": datetime(YYYY, MM, DD, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
    #     "timezone": ZoneInfo("America/New_York") 
    # },






    #====================================================================
    #============================ 黄金律法  ==============================
    #====================================================================
    # {
    #     "title": "我的童年",
    #     "start": datetime(YYYY, MM, DD, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
    #     "end": datetime(YYYY, MM, DD, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
    #     "timezone": ZoneInfo("America/New_York") 
    # },
    # {
    #     "title": "TITLE",
    #     "start": datetime(YYYY, MM, DD, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
    #     "end": datetime(YYYY, MM, DD, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
    #     "timezone": ZoneInfo("America/New_York") 
    # },
    # {
    #     "title": "TITLE",
    #     "start": datetime(YYYY, MM, DD, 0, 0, 1, tzinfo=ZoneInfo("UTC")),
    #     "end": datetime(YYYY, MM, DD, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
    #     "timezone": ZoneInfo("America/New_York") 
    # },
]
# 为不属于任何特殊主题的日记设置一个默认显示时区
DEFAULT_TIMEZONE = ZoneInfo("UTC")
# 常用时区：
# Asia/Shanghai
# Asia/Tokyo
# America/Los_Angeles
# Pacific/Honolulu
# Europe/London
# Europe/Paris
# Australia/Sydney
# Pacific/Auckland
# --- ▲▲▲ 配置结束 ▲▲▲ ---

DB_PATH = 'diary.db'
PROJECT_DB = 'project.db'
HISTORICAL_DB_PATH = 'historical_diary.db' # 新增的历史日记数据库路径


def init_db():
    conn = sqlite3.connect(DB_PATH)
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




def init_project_db():
    conn = sqlite3.connect(PROJECT_DB)
    c = conn.cursor()
    # projects 表
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            created_at TEXT
        )
    ''')
    # 动态加 archived 列
    c.execute("PRAGMA table_info(projects)")
    cols = [r[1] for r in c.fetchall()]
    if 'archived' not in cols:
        c.execute("ALTER TABLE projects ADD COLUMN archived INTEGER DEFAULT 0")

    # 2025/7/1更新：增加了优先级设置，S > A > B > C > Z，默认Z
    if 'priority' not in cols:
        c.execute("ALTER TABLE projects ADD COLUMN priority TEXT DEFAULT 'Z'")

    # tasks 表
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            task TEXT,
            done INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()


# 2025/7/1增加的两个init内容，防止更新数据库内容后缺少字段
init_db()
init_project_db()

def count_tasks(project_id, done=None):
    """返回某项目的子任务数量；done=None 返回总数，done=0/1 返回对应状态数"""
    conn = sqlite3.connect(PROJECT_DB)
    c = conn.cursor()
    if done is None:
        c.execute('SELECT COUNT(*) FROM tasks WHERE project_id=?', (project_id,))
    else:
        c.execute('SELECT COUNT(*) FROM tasks WHERE project_id=? AND done=?', (project_id, done))
    result = c.fetchone()[0]
    conn.close()
    return result


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u == USERNAME and bcrypt.check_password_hash(PASSWORD_HASH, p):
            session['logged_in'] = True
            session['key'] = p
            return redirect(url_for('home'))
        return render_template('login.html', error='登录失败，请检查用户名或密码')
    return render_template('login.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # — 写日记提交 —
    if request.method == 'POST':
        title = request.form['title'].strip() or datetime.now().strftime('%Y-%m-%d 日记')
        content = request.form['content'].strip()
        enc = encrypt_text(content, session['key'])
        with sqlite3.connect(DB_PATH) as conn:
            # 2025-7-2增加了下面这一行
            utc_now = datetime.now(ZoneInfo("UTC")).strftime('%Y-%m-%d %H:%M:%S')
            conn.execute(
                'INSERT INTO diary (title, content, created_at) VALUES (?, ?, ?)',
                (title, enc, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
        return redirect(url_for('home'))

    # 2025/7/1更新
    conn = sqlite3.connect(PROJECT_DB)
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()

    c.execute('''
        SELECT
            p.id, p.title, p.priority,
            COUNT(t.id) AS total,
            SUM(t.done) AS done
        FROM projects p
        LEFT JOIN tasks t ON p.id = t.project_id
        WHERE p.archived = 0
        GROUP BY p.id
        ORDER BY
            CASE p.priority
                WHEN 'S' THEN 1
                WHEN 'A' THEN 2
                WHEN 'B' THEN 3
                WHEN 'C' THEN 4
                WHEN 'Z' THEN 5
                ELSE 6
            END,
            p.created_at DESC
    ''')
    all_projects = c.fetchall()

    # 按优先级对项目进行分组
    PRIORITY_ORDER = ['S', 'A', 'B', 'C', 'Z']
    projects_by_priority = {priority: [] for priority in PRIORITY_ORDER}
    for project in all_projects:
        p_key = project['priority']
        if p_key in projects_by_priority:
            projects_by_priority[p_key].append(project)

    # — 为每个项目取最早的三个【未完成】子任务 —
    tasks_map = {}
    for project in all_projects:
        pid = project['id']
        # 这里 c 还是上面打开的 cursor，不需要重复连接
        c.execute('''
            SELECT task FROM tasks
            WHERE project_id = ? AND done = 0
            ORDER BY datetime(created_at) ASC
            LIMIT 3
        ''', (pid,))
        tasks_map[pid] = [row[0] for row in c.fetchall()]

    conn.close()

    return render_template(
        'home.html',
        # 传递分组后的字典和优先级顺序
        projects_by_priority=projects_by_priority,
        priority_order=PRIORITY_ORDER,
        tasks_map=tasks_map
    )


@app.route('/diary')
def diary_list():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    all_rows = []

    # 1. 读取主数据库
    conn_main = sqlite3.connect(DB_PATH)
    c_main = conn_main.cursor()
    c_main.execute('SELECT title, content, created_at FROM diary')
    all_rows.extend(c_main.fetchall())
    conn_main.close()

    # 2. 读取历史数据库
    if os.path.exists(HISTORICAL_DB_PATH):
        conn_hist = sqlite3.connect(HISTORICAL_DB_PATH)
        c_hist = conn_hist.cursor()
        c_hist.execute('SELECT title, content, created_at FROM diary')
        all_rows.extend(c_hist.fetchall())
        conn_hist.close()

    # 3. 预处理
    processed_entries = []
    now_utc = datetime.now(ZoneInfo("UTC"))
    
    for title, enc_content, created_at_str in all_rows:
        try:
            created_at_utc = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=ZoneInfo("UTC"))
        except ValueError:
            continue

        entry_theme = None
        for theme in THEMES:
            theme_end = theme.get("end") or now_utc
            if theme["start"] <= created_at_utc <= theme_end:
                entry_theme = theme
                break
        
        processed_entries.append({
            "title": title,
            "content": decrypt_text(enc_content, session['key']),
            "created_at_utc": created_at_utc,
            "theme": entry_theme
        })

    # 4. 按时间正序排序 (旧 -> 新)
    processed_entries.sort(key=lambda x: x['created_at_utc'])

    # 5. 构建正序时间轴
    timeline_items = []
    
    for i, current_entry in enumerate(processed_entries):
        current_theme = current_entry["theme"]
        
        prev_theme = processed_entries[i - 1]["theme"] if i > 0 else None
        next_theme = processed_entries[i + 1]["theme"] if (i + 1) < len(processed_entries) else None

        # --- A. 顶部盖子 (Header) ---
        # 逻辑：如果当前有主题，且上一个条目主题不同。
        # 说明这是该主题的第一篇（最旧的一篇），也就是主题的【开始】。
        # 正序显示时，我们需要在这里打开 div。
        if current_theme and current_theme != prev_theme:
            timeline_items.append({
                "type": "theme_header",
                "title": current_theme["title"]
            })

        # --- B. 添加日记本体 ---
        display_timezone = current_theme["timezone"] if current_theme else DEFAULT_TIMEZONE
        local_time = current_entry["created_at_utc"].astimezone(display_timezone)
        formatted_time = local_time.strftime('%Y-%m-%d %H:%M:%S %Z')
        
        timeline_items.append({
            "type": "diary_entry",
            "title": current_entry["title"],
            "content": current_entry["content"],
            "created_at": formatted_time
        })

        # --- C. 底部盖子 (Terminator) ---
        # 逻辑：如果当前有主题，且下一个条目主题不同。
        # 说明这是该主题的最后一篇（最新的一篇），也就是主题的【结束】。
        # 正序显示时，我们需要在这里关闭 div。
        if current_theme and current_theme != next_theme:
            timeline_items.append({
                "type": "theme_terminator"
            })

    # 6. 直接发送列表，不需要前端 reverse
    return render_template('diary_list.html',
                           timeline_items=timeline_items,
                           entry_count=len(processed_entries))



@app.route('/backup')
def backup():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return send_file(DB_PATH,
                     as_attachment=True,
                     download_name='diary_backup.db')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/project')
def project_home():
    # 兼容旧链接，直接到仪表盘
    return redirect(url_for('home'))


@app.route('/project/create', methods=['GET', 'POST'])
def project_create():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # 2025/7/1修改
    # if request.method == 'POST':
    #     title = request.form['title'].strip()
    #     desc = request.form['description'].strip()
    #     with sqlite3.connect(PROJECT_DB) as conn:
    #         conn.execute(
    #             'INSERT INTO projects (title, description, created_at) VALUES (?, ?, ?)',
    #             (title, desc, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #         )
    #     return redirect(url_for('home'))
    # 在 project_create() 函数内部，替换 if request.method == 'POST' 分支

    # 2025/7/1修改
    if request.method == 'POST':
        title = request.form['title'].strip()
        desc = request.form['description'].strip()
        # --- ▼▼▼ 新增代码 ▼▼▼ ---
        priority = request.form.get('priority', 'Z')
        # --- ▲▲▲ 新增代码 ▲▲▲ ---
        
        with sqlite3.connect(PROJECT_DB) as conn:
            conn.execute(
                # --- ▼▼▼ 修改 SQL 语句和参数 ▼▼▼ ---
                'INSERT INTO projects (title, description, created_at, priority) VALUES (?, ?, ?, ?)',
                (title, desc, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), priority)
            )
        return redirect(url_for('home'))
    return render_template('project_create.html')




# app.py 中的 project_detail 路由，替换原来的同名函数：

@app.route('/project/<int:project_id>', methods=['GET', 'POST'])
def project_detail(project_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(PROJECT_DB)
    c = conn.cursor()

    if request.method == 'POST':
        # 1) 新增子任务
        if 'new_task' in request.form:
            task = request.form['new_task'].strip()
            if task:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                c.execute(
                    'INSERT INTO tasks (project_id, task, created_at) VALUES (?, ?, ?)',
                    (project_id, task, now)
                )

        # 2) 切换完成状态
        elif 'toggle' in request.form:
            tid = int(request.form['toggle'])
            c.execute('UPDATE tasks SET done = 1 - done WHERE id = ?', (tid,))

        # 3) 编辑子任务文本（新加分支）
        elif 'edit_task_id' in request.form:
            tid      = int(request.form['edit_task_id'])
            new_text = request.form.get('edit_task_text', '').strip()
            if new_text:
                c.execute('UPDATE tasks SET task = ? WHERE id = ?', (new_text, tid))

        # 2025/7/1修改
        # 4) 更新项目标题 / 简介
        # elif 'update_title' in request.form or 'update_description' in request.form:
        #     new_title = request.form.get('update_title', '').strip()
        #     new_desc  = request.form.get('update_description', '').strip()
        #     if new_title:
        #         c.execute('UPDATE projects SET title = ? WHERE id = ?', (new_title, project_id))
        #     # 简介允许清空
        #     c.execute('UPDATE projects SET description = ? WHERE id = ?', (new_desc, project_id))
        
        # 2025/7/1修改
        # --- ▼▼▼ 替换原来的 "更新项目标题 / 简介" 分支 ▼▼▼ ---
        elif 'update_title' in request.form:
            new_title = request.form.get('update_title', '').strip()
            new_desc  = request.form.get('update_description', '').strip()
            # --- ▼▼▼ 新增代码 ▼▼▼ ---
            new_priority = request.form.get('update_priority', 'Z')
            
            if new_title:
                c.execute('UPDATE projects SET title = ? WHERE id = ?', (new_title, project_id))
            c.execute('UPDATE projects SET description = ? WHERE id = ?', (new_desc, project_id))
            # --- ▼▼▼ 新增代码 ▼▼▼ ---
            c.execute('UPDATE projects SET priority = ? WHERE id = ?', (new_priority, project_id))
        # --- ▲▲▲ 替换结束 ▲▲▲ ---

        # 5) 归档（MISSION COMPLETE），并跳转到已完成页面
        elif 'complete' in request.form:
            c.execute('UPDATE projects SET archived = 1 WHERE id = ?', (project_id,))
            conn.commit()
            conn.close()
            return redirect(url_for('project_archive'))

        conn.commit()

    # 2025/7/1修改，execute拉取中增加了priority字段
    # GET 拉取最新数据（包含 archived 字段）
    c.execute(
      'SELECT title, description, created_at, archived, priority '
      'FROM projects WHERE id = ?',
      (project_id,)
    )
    project = c.fetchone()

    c.execute(
      'SELECT id, task, done, created_at '
      'FROM tasks WHERE project_id = ? ORDER BY created_at',
      (project_id,)
    )
    tasks = c.fetchall()

    conn.close()
    return render_template(
      'project_detail.html',
      project_id=project_id,
      project=project,
      tasks=tasks
    )


@app.route('/project/archive')
def project_archive():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect(PROJECT_DB)
    c = conn.cursor()
    c.execute('''
        SELECT p.id, p.title, p.description, p.created_at,
               COUNT(t.id) AS total,
               SUM(t.done) AS done
        FROM projects p
        LEFT JOIN tasks t ON p.id = t.project_id
        WHERE p.archived = 1
        GROUP BY p.id
        ORDER BY p.created_at DESC
    ''')
    projects = c.fetchall()
    tasks_map = {}
    for pid, *_ in projects:
        c.execute('SELECT task, done FROM tasks WHERE project_id = ? ORDER BY datetime(created_at) ASC', (pid,))
        tasks_map[pid] = c.fetchall()
    conn.close()
    return render_template('project_archive.html', projects=projects, tasks_map=tasks_map)


if __name__ == '__main__':
    # 2025/7/1更新：将两个init移动到了开头，防止更新数据库字段后发生不匹配的问题
    # init_db()
    # init_project_db()
    # 保留了最后的debug，用于本地开发测试
    app.run(debug=True)
