import psycopg2
import configparser


def make_base(cur):
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name_u VARCHAR(50),
        surname_u VARCHAR(50),
        email VARCHAR(100)
    );
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS phones (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        u_phone BIGINT
    );
    ''')
    print("Tables created successfully")


def add_user(cur, name, surname, email, phones=None):
    cur.execute('''
    INSERT INTO users (name_u, surname_u, email)
    VALUES (%s, %s, %s)
    RETURNING id;
    '''
                , (name, surname, email))
    user_id = cur.fetchone()[0]
    if phones:
        for phone in phones:
            cur.execute('''
            INSERT INTO phones (user_id, u_phone)
            VALUES (%s, %s);
            '''
                        , (user_id, phone))
    print("User added successfully")


def alt_user(cur, user_id, name_u=None, surname_u=None, email=None):
    if name_u:
        cur.execute('''
        UPDATE users SET name_u = %s WHERE id = %s;
        '''
                    , (name_u, user_id))
    if surname_u:
        cur.execute('''
        UPDATE users SET surname_u = %s WHERE id = %s;
        '''
                    , (surname_u, user_id))
    if email:
        cur.execute('''
        UPDATE users SET email = %s WHERE id = %s;
        '''
                    , (email, user_id))
    print("User updated successfully")


def delete_user(cur, user_id):
    cur.execute('''
    DELETE FROM phones WHERE user_id = %s;
    '''
                , (user_id,))
    cur.execute('''
    DELETE FROM users WHERE id = %s;
    '''
                , (user_id,))
    print("User deleted successfully")


def delete_phone(cur, phone_id):
    cur.execute('''
    DELETE FROM phones WHERE id = %s;
    '''
                , (phone_id,))
    print("Phone deleted successfully")


def find_out(cur, type, data):
    def print_bd(data):
        if data:
            for row in data:
                print("Name:", row[0])
                print("Surname:", row[1])
                print("Email:", row[2])
                print("Phone:", row[3])
                print()
        else:
            print("No matching records found")

    if type == 'name':
        cur.execute('''
        SELECT name_u, surname_u, email, u_phone FROM users AS u
        LEFT JOIN phones AS p ON u.id = p.user_id
        WHERE name_u = %s;
        '''
                    , (data,))
        print_bd(cur.fetchall())
    elif type == 'surname':
        cur.execute('''
        SELECT name_u, surname_u, email, u_phone FROM users AS u
        LEFT JOIN phones AS p ON u.id = p.user_id
        WHERE surname_u = %s;
        '''
                    , (data,))
        print_bd(cur.fetchall())
    elif type == 'email':
        cur.execute('''
        SELECT name_u, surname_u, email, u_phone FROM users AS u
        LEFT JOIN phones AS p ON u.id = p.user_id
        WHERE email = %s;
        '''
                    , (data,))
        print_bd(cur.fetchall())
    elif type == 'phone':
        cur.execute('''
        SELECT name_u, surname_u, email, u_phone FROM users AS u
        LEFT JOIN phones AS p ON u.id = p.user_id
        WHERE u_phone = %s;
        '''
                    , (data,))
        print_bd(cur.fetchall())


config = configparser.ConfigParser()
config.read('config.ini')
conn = psycopg2.connect(database=config['DEFAULT']['DATABASE'],
                        user=config['DEFAULT']['USER'],
                        password=config['DEFAULT']['PASSWORD'],
                        host=config['DEFAULT']['HOST'],
                        port=config['DEFAULT']['PORT'])
cur = conn.cursor()
make_base(cur)
add_user(cur, 'Ivan', 'Ivanov', 'ivanov@mail.ru', [1234567890, 9876543210])
add_user(cur, 'Petr', 'Petrov', 'petrov@mail.ru', [3456789012])
add_user(cur, 'Sergey', 'Sergeev', 'sergeev@mail.ru', [5678901234, 4321098765])
add_user(cur, 'Ivan', 'Sidorov', 'sidorov@mail.ru', [])
find_out(cur, 'name', 'Ivan')
find_out(cur, 'surname', 'Ivanov')
find_out(cur, 'email', 'petrov@mail.ru')
find_out(cur, 'phone', 1234567890)
alt_user(cur, 1, name_u='Alex')
delete_user(cur, 1)
find_out(cur, 'name', 'Ivan')
conn.close()
