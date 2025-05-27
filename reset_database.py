#!/usr/bin/env python3
"""
Database Reset Script
Recreates the database with pbkdf2 password hashes
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash

def reset_database():
    print("🔄 RESETTING DATABASE WITH CORRECT PASSWORD HASHES")
    print("=" * 60)
    
    # Database path
    db_path = 'instance/forum.db'
    
    # Check if database exists
    if os.path.exists(db_path):
        try:
            # Try to delete the database
            os.remove(db_path)
            print("✅ Old database deleted")
        except PermissionError:
            print("❌ Cannot delete database - Flask app may be running")
            print("Please stop the Flask app first (Ctrl+C in the terminal running app.py)")
            return False
    
    # Create instance directory if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')
        print("✅ Created instance directory")
    
    # Create new database with correct schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE user (
            id INTEGER PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password VARCHAR(128) NOT NULL,
            role VARCHAR(20) DEFAULT 'user'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE post (
            id INTEGER PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE reply (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user (id),
            FOREIGN KEY (post_id) REFERENCES post (id)
        )
    ''')
    
    print("✅ Database tables created")
    
    # Insert users with pbkdf2 hashes
    users = [
        ('admin', 'adminpass', 'admin'),
        ('tech_enthusiast', 'techpass', 'user'),
        ('movie_buff', 'moviepass', 'user'),
        ('bookworm', 'bookpass', 'user'),
        ('gamer_pro', 'gamerpass', 'user'),
        ('travel_lover', 'travelpass', 'user'),
        ('foodie_fan', 'foodiepass', 'user')
    ]
    
    for username, password, role in users:
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        cursor.execute(
            'INSERT INTO user (username, password, role) VALUES (?, ?, ?)',
            (username, hashed_password, role)
        )
    
    print("✅ Users created with pbkdf2 password hashes")
    
    # Insert sample posts
    posts = [
        ('Welcome to the Tech Forum!', 'Discuss the latest tech trends here.', 1),
        ('Best Programming Languages?', 'What are your favorite programming languages and why?', 2),
        ('Upcoming Movie Releases', 'Excited for any upcoming movies? Let\'s discuss!', 3),
        ('Book Recommendations for Sci-Fi Fans', 'Looking for good sci-fi books to read.', 4),
        ('Gaming News and Reviews', 'Share your thoughts on the latest video games.', 5),
        ('Travel Destinations for 2024', 'Planning any trips for next year? Share your ideas!', 6),
        ('Delicious Food Recipes', 'Post your favorite recipes here.', 1),
        ('DIY Home Improvement Tips', 'Share your DIY projects and tips.', 2),
        ('Art and Creative Projects', 'Showcase your artistic creations.', 3),
        ('Science and Technology Updates', 'Discuss recent scientific discoveries.', 4),
        ('History and Historical Events', 'Let\'s talk about historical events and figures.', 5),
        ('XSS Test', '<script>alert("XSS");</script>', 6),
        ('SQL Test', '\' or 1=1; --', 1),
        ('Favorite tech gadgets', 'What are your favorite tech gadgets?', 2),
        ('Best gaming console', 'Which is the best gaming console?', 3)
    ]
    
    for title, content, user_id in posts:
        cursor.execute(
            'INSERT INTO post (title, content, user_id) VALUES (?, ?, ?)',
            (title, content, user_id)
        )
    
    print("✅ Sample posts created")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("🎉 DATABASE RESET COMPLETED!")
    print("=" * 60)
    print("✅ New database created with pbkdf2 password hashes")
    print("✅ All users and posts recreated")
    print("\n📋 Test Accounts:")
    print("   admin / adminpass (admin role)")
    print("   tech_enthusiast / techpass")
    print("   movie_buff / moviepass")
    print("   bookworm / bookpass")
    print("   gamer_pro / gamerpass")
    print("   travel_lover / travelpass")
    print("   foodie_fan / foodiepass")
    print("\n🚀 You can now restart the Flask app!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        reset_database()
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        print("Make sure Flask app is stopped and try again.") 