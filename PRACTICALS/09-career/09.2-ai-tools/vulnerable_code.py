import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # SAFE: Use '?' as a placeholder. 
    # The driver handles escaping the input safely.
    query = "SELECT * FROM users WHERE id = ?"
    
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result
