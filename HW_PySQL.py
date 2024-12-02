import psycopg2
import os.path
from dotenv import load_dotenv

def get_config(path=str):
    dotenv_path = path
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    database = os.getenv('database_name')
    user = os.getenv('user')
    password = os.getenv('password')
    return  database, user, password

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS client(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(20) NOT NULL,
            last_name VARCHAR(30) NOT NULL,
            email VARCHAR (50) NOT NULL
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone(
            id SERIAL PRIMARY KEY,
            number VARCHAR (20) NOT NULL,
            client_id INTEGER REFERENCES client(id)        
        );
        """)
    conn.commit()

def add_client(conn, first_name, last_name, email, phone=None):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO client(first_name, last_name, email) 
            VALUES(%s, %s, %s) RETURNING id;
        """, (first_name, last_name, email))
        client_id = cur.fetchone()
        if phone != None:
            add_phone(conn, client_id, phone)
        
def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO phone(number, client_id) 
                VALUES(%s, %s);
            """, (phone, client_id))
        conn.commit()
  
def change_client(conn, client_id, first_name=None, last_name=None, email=None, phone=None, phone_id=None):
    with conn.cursor() as cur:
        if first_name != None:
            cur.execute("""
            UPDATE client SET first_name=%s WHERE id=%s;
            """, (first_name, client_id))
        if last_name != None:
            cur.execute("""
            UPDATE client SET last_name=%s WHERE id=%s;
            """, (last_name, client_id))
        if email != None:
            cur.execute("""
            UPDATE client SET email=%s WHERE id=%s;
            """, (email, client_id))
        if phone != None and phone_id !=None:
            cur.execute("""
            UPDATE phone SET number=%s WHERE client_id=%s AND id=%s;
            """, (phone, client_id, phone_id))
        conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phone WHERE client_id=%s AND number=%s;
        """, (client_id, phone))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phone WHERE client_id=%s;
        """, (client_id,))
        cur.execute("""
        DELETE FROM client WHERE id=%s;
        """, (client_id,))
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        if first_name != None:
            cur.execute("""
                SELECT id FROM client WHERE first_name=%s;
                """, (first_name,))
        if last_name != None:
            cur.execute("""
                SELECT id FROM client WHERE last_name=%s;
                """, (last_name,))
        if email != None:
            cur.execute("""
                SELECT id FROM client WHERE email=%s;
                """, (email,))
        if phone != None:
            cur.execute("""
                SELECT client_id FROM phone WHERE number=%s;
                """, (phone,))
        result = cur.fetchone()
        return 'Ничего не найдено' if result is None else result[0]


with psycopg2.connect(database=(get_config('config.env')[0]), 
                      user=(get_config('config.env')[1]), 
                      password=(get_config('config.env')[2])) as conn:
    
    create_db(conn)
    add_client(conn, 'Егом', 'Павлов', 'eg_pavlov@mail.ru')
    add_client(conn, 'Саша', 'Кротов', 'alex59@gmail.com', '8-123-456-78-87')
    add_client(conn, 'Елена', 'Романова', 'ElenaRo95@mail.ru', '+7-321-654-12-34')
    add_phone(conn, 2, '8-800-555-35-35')
    change_client(conn, 2, 'Александр', None, 'A_Krotov@mail.ru', '8-963-555-18-17', 2)
    change_client(conn, 1, 'Егор')
    delete_phone(conn, 2, '8-963-555-18-17')
    delete_client(conn, 3)
    print(find_client(conn, 'Александр'))
    print(find_client(conn, phone='8-123-456-78-87'))
    
conn.close()

