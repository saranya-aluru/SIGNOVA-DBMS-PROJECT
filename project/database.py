import os

import mysql.connector


db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "enter_your_password"),
    database=os.getenv("DB_NAME", "sign_language_db")
)

print("Database connected successfully!")

db.close()
