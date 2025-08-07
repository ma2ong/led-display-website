import os
import sqlite3

def get_database_path():
    """获取数据库路径，兼容Windows和Linux系统"""
    if os.name == 'nt':  # Windows系统
        return os.path.join(os.getcwd(), 'led_admin.db')
    else:  # Linux/Unix系统 (Vercel)
        return '/tmp/database.db'

def get_database_connection():
    """获取数据库连接"""
    db_path = get_database_path()
    return sqlite3.connect(db_path)

def init_database():
    """初始化数据库"""
    db_path = get_database_path()
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
    
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建产品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                price REAL,
                image_url TEXT,
                specifications TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建询盘表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                company TEXT,
                message TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建新闻表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                author TEXT,
                status TEXT DEFAULT 'published',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入示例数据
        sample_products = [
            ('室内LED显示屏P2.5', 'indoor', '高清室内LED显示屏，适用于会议室、展厅等场所', 8500.00, '/assets/products/indoor-p2.5.jpg', '像素间距：2.5mm\n亮度：800cd/㎡\n刷新率：3840Hz'),
            ('户外LED显示屏P10', 'outdoor', '高亮度户外LED显示屏，防水防尘，适用于户外广告', 12000.00, '/assets/products/outdoor-p10.jpg', '像素间距：10mm\n亮度：6500cd/㎡\n防护等级：IP65'),
            ('租赁LED显示屏P3.91', 'rental', '轻便租赁LED显示屏，快速安装，适用于舞台演出', 9800.00, '/assets/products/rental-p3.91.jpg', '像素间距：3.91mm\n重量：6.5kg/㎡\n安装：快锁设计'),
            ('创意LED显示屏', 'creative', '异形创意LED显示屏，可定制各种造型', 15000.00, '/assets/products/creative-led.jpg', '可定制形状\n高刷新率\n无缝拼接')
        ]
        
        cursor.executemany('''
            INSERT INTO products (name, category, description, price, image_url, specifications)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_products)
        
        # 插入管理员用户
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', ('admin', 'admin123', 'admin'))
        
        conn.commit()
        conn.close()
        print(f"数据库初始化完成: {db_path}")
    else:
        print(f"数据库已存在: {db_path}")