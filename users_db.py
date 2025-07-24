import mysql.connector

def init_user_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Add password if set
        database="users_db"
    )
    cursor = db.cursor()

    # ✅ Use IF NOT EXISTS to avoid duplicate table error
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100),
            email VARCHAR(100),
            password VARCHAR(100)
        )
    """)

    db.commit()
    cursor.close()
    db.close()
