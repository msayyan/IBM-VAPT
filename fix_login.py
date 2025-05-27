#!/usr/bin/env python3
"""
Login Fix Script
Updates existing user passwords to use pbkdf2 hashes
"""

import sqlite3
from werkzeug.security import generate_password_hash

def fix_passwords():
    print("🔧 FIXING PASSWORD HASHES IN EXISTING DATABASE")
    print("=" * 60)
    
    try:
        # Connect to the database
        conn = sqlite3.connect('instance/forum.db')
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute('SELECT id, username FROM user')
        users = cursor.fetchall()
        
        print(f"Found {len(users)} users to update")
        
        # Default passwords for existing users
        default_passwords = {
            'admin': 'adminpass',
            'tech_enthusiast': 'techpass', 
            'movie_buff': 'moviepass',
            'bookworm': 'bookpass',
            'gamer_pro': 'gamerpass',
            'travel_lover': 'travelpass',
            'foodie_fan': 'foodiepass'
        }
        
        # Update each user's password
        for user_id, username in users:
            if username in default_passwords:
                new_password = default_passwords[username]
                hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
                
                cursor.execute(
                    'UPDATE user SET password = ? WHERE id = ?',
                    (hashed_password, user_id)
                )
                print(f"✅ Updated password for {username}")
            else:
                # For unknown users, set a default password
                hashed_password = generate_password_hash('password123', method='pbkdf2:sha256')
                cursor.execute(
                    'UPDATE user SET password = ? WHERE id = ?',
                    (hashed_password, user_id)
                )
                print(f"✅ Set default password for {username}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 PASSWORD HASHES FIXED!")
        print("=" * 60)
        print("✅ All users now use pbkdf2:sha256 hashes")
        print("✅ Login should work now")
        print("\n📋 Test Accounts:")
        print("   admin / adminpass")
        print("   tech_enthusiast / techpass")
        print("   movie_buff / moviepass")
        print("   bookworm / bookpass")
        print("   gamer_pro / gamerpass")
        print("   travel_lover / travelpass")
        print("   foodie_fan / foodiepass")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing passwords: {e}")
        return False

if __name__ == "__main__":
    fix_passwords() 