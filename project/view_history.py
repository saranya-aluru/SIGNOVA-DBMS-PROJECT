import os

import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "enter_your_password"),
        database=os.getenv("DB_NAME", "sign_language_db")
    )


def get_signs():
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            sign_id,
            sign_name,
            display_word,
            description,
            sign_type,
            image_url,
            video_url
        FROM signs
        ORDER BY sign_id
    """)

    signs = cursor.fetchall()

    cursor.close()
    db.close()

    return signs


def get_sign(sign_name):
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            sign_id,
            sign_name,
            display_word,
            description,
            sign_type,
            image_url,
            video_url
        FROM signs
        WHERE sign_name = %s
    """, (sign_name,))

    sign = cursor.fetchone()

    cursor.close()
    db.close()

    return sign


def save_recognition(sign_name):
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT sign_id
        FROM signs
        WHERE sign_name = %s
    """, (sign_name,))

    result = cursor.fetchone()

    if result:
        sign_id = result[0]

        cursor.execute("""
            INSERT INTO recognition_history (sign_id)
            VALUES (%s)
        """, (sign_id,))

        db.commit()

    cursor.close()
    db.close()
