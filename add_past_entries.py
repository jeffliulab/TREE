import sqlite3
from datetime import datetime
from encrypt import encrypt_text
import getpass

"""
注意：由于并不推荐以导入的方式增加日记
这样会丢失日记的即时性和公正性
所以历史日记方式用这个脚本手动添加
并且每次修改或者添加前都需要重新执行一次本文件
否则会导致重复添加
"""

# --- ▼▼▼ 脚本现在操作新的历史数据库文件 ▼▼▼ ---
HISTORICAL_DB_PATH = 'historical_diary.db'

# --- ▼▼▼ 在这里尽情填写您想添加的所有历史日记 ▼▼▼ ---
# 这是一个列表，您可以添加任意多个日记字典
# 每个字典代表一篇日记，包含 'date', 'title', 和 'content'
PAST_ENTRIES = [
    {
        # 日期格式必须是 '年-月-日 时:分:秒'
        "date": "2023-08-15 10:30:00",
        "title": "初抵大学城X",
        "content": """
今天是我来到这座城市的第一天，空气中充满了未知与期待。
宿舍楼下的那棵老槐树，见证了无数人的来来往往。
我在这里放下行李，也放下了过去，准备开始一段崭新的人生旅程。
希望一切顺利。
"""
    },
    {
        "date": "2023-12-24 21:00:00",
        "title": "平安夜的图书馆",
        "content": """
窗外是节日的喧嚣，图书馆里却异常安静。
为了期末考试，我和几个新认识的朋友在这里并肩作战。
虽然没有派对和礼物，但这种为了共同目标而奋斗的感觉，或许是这个年纪最好的礼物。
我们互相交换了苹果，寓意平平安安。
"""
    },
    {
        "date": "2024-05-20 18:00:00",
        "title": "第一次项目答辩",
        "content": """
紧张又兴奋的一天。我们小组的项目得到了教授的认可。
从最初的构想到最终的实现，每一步都充满了挑战。
当看到最终成果时，所有的辛苦都烟消云散。
这让我明白了团队合作的力量。
"""
    },
    # --- 您可以在这里继续添加更多日记 ---
    # {
    #     "date": "YYYY-MM-DD HH:MM:SS",
    #     "title": "您的日记标题",
    #     "content": "您的日记内容"
    # },
]
# --- ▲▲▲ 历史日记填写结束 ▲▲▲ ---


def init_historical_db():
    """如果历史数据库不存在，则创建它和其中的 diary 表"""
    conn = sqlite3.connect(HISTORICAL_DB_PATH)
    c = conn.cursor()
    # 表结构必须和主数据库的 diary 表完全一致
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
    print(f"已确保 '{HISTORICAL_DB_PATH}' 数据库和表结构存在。")

def add_entries_to_db():
    """将 PAST_ENTRIES 列表中的所有日记加密并插入历史数据库。"""
    print("--- 开始向历史数据库添加日记 ---")
    
    password = getpass.getpass("请输入您的日记登录密码 (用于加密): ")
    if not password:
        print("错误：密码不能为空。")
        return

    conn = sqlite3.connect(HISTORICAL_DB_PATH)
    c = conn.cursor()

    added_count = 0
    for entry in PAST_ENTRIES:
        try:
            title = entry["title"]
            content_plain = entry["content"].strip()
            content_encrypted = encrypt_text(content_plain, password)
            created_at = entry["date"]

            # 将加密后的数据插入历史数据库
            c.execute(
                'INSERT INTO diary (title, content, created_at) VALUES (?, ?, ?)',
                (title, content_encrypted, created_at)
            )
            print(f"  成功添加日记: '{title}' ({created_at})")
            added_count += 1
        except Exception as e:
            print(f"  添加日记 '{title}' 时发生错误: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n--- 操作完成 ---")
    print(f"总共成功添加了 {added_count} 篇历史日记到 '{HISTORICAL_DB_PATH}'。")

if __name__ == '__main__':
    print(f"本脚本将创建或向 '{HISTORICAL_DB_PATH}' 文件中添加数据。")
    print("它不会修改您现有的 'diary.db' 文件。")
    answer = input("您是否希望继续？(yes/no): ")
    if answer.lower() == 'yes':
        # 1. 先确保数据库和表存在
        init_historical_db()
        # 2. 再添加数据
        add_entries_to_db()
    else:
        print("操作已取消。")
