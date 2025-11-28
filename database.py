import sqlite3
import json
from datetime import datetime

class UserDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('user_data.db')
        self.create_table()
    
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                messages INTEGER DEFAULT 0,
                reputation INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                joined_date TEXT,
                banner TEXT DEFAULT 'default'
            )
        ''')
        self.conn.commit()
    
    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (str(user_id),))
        result = cursor.fetchone()
        
        if result:
            return {
                'user_id': result[0],
                'username': result[1],
                'messages': result[2],
                'reputation': result[3],
                'xp': result[4],
                'level': result[5],
                'joined_date': result[6],
                'banner': result[7]
            }
        return None
    
    def create_user(self, user_id, username, joined_date):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO users (user_id, username, messages, reputation, xp, level, joined_date, banner)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (str(user_id), username, 0, 0, 0, 0, joined_date, 'default'))
        self.conn.commit()
    
    def update_user(self, user_id, **kwargs):
        cursor = self.conn.cursor()
        
        valid_columns = ['messages', 'reputation', 'xp', 'level', 'username', 'banner']
        for key, value in kwargs.items():
            if key in valid_columns:
                cursor.execute(f'UPDATE users SET {key} = ? WHERE user_id = ?', (value, str(user_id)))
        
        self.conn.commit()
    
    def increment_messages(self, user_id):
        user = self.get_user(user_id)
        if user:
            new_count = user['messages'] + 1
            self.update_user(user_id, messages=new_count)
            
            # Add XP for message
            new_xp = user['xp'] + 1
            self.update_user(user_id, xp=new_xp)
            
            # Check level up
            new_level = self.calculate_level(new_xp)
            if new_level > user['level']:
                self.update_user(user_id, level=new_level)
            
            return new_count
        return 0
    
    def calculate_level(self, xp):
        return int((xp / 100) ** 0.5)
    
    def get_progress(self, xp, level):
        current_level_xp = (level ** 2) * 100
        next_level_xp = ((level + 1) ** 2) * 100
        xp_in_level = xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        return (xp_in_level / xp_needed) * 100 if xp_needed > 0 else 0

# Initialize database
db = UserDatabase()
