import sqlite3
import os

def init_database():
    # 创建数据库连接
    db_path = os.path.join(os.getcwd(), 'led_admin.db')
    
    # 删除旧数据库
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建所有必要的表
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

    # 插入示例新闻
    sample_news = [
        ('LED显示屏技术新突破', 'LED显示屏技术在2024年取得重大突破，像素密度和亮度都有显著提升，为客户提供更优质的显示效果。', 'admin', 'published'),
        ('公司荣获行业大奖', '我公司在LED显示屏行业评选中荣获最佳创新奖，这是对我们技术实力的认可。', 'admin', 'published'),
        ('新产品发布会成功举办', '我公司新一代LED显示屏产品发布会在深圳成功举办，吸引了众多客户参与。', 'admin', 'published')
    ]

    cursor.executemany('''
        INSERT INTO news (title, content, author, status)
        VALUES (?, ?, ?, ?)
    ''', sample_news)

    conn.commit()
    conn.close()
    print('✅ 数据库重新创建完成！')
    return True

if __name__ == '__main__':
    init_database()