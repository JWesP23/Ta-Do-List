import psycopg2
from psycopg2.errors import UniqueViolation

#creates connection object
#TODO put password in an env file or otherwise store as env var
conn = psycopg2.connect(
    dbname="to_do_db",
    user="postgres",
    password="JackFrost5!",
    host="localhost"
)

#Open a cursor to perform database operations
cur = conn.cursor()

#create users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255),
    password_hash TEXT NOT NULL
);
""")

#create tasks table
cur.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    parent_task_id INT REFERENCES tasks(id) ON DELETE CASCADE
);
""")

#cur.execute("""INSERT INTO tasks (user_id, title, description, completed)
#VALUES (1, 'Finish project', 'Complete the to-do list website', FALSE);""")
#cur.execute('''DELETE FROM tasks
#               WHERE id = 3;''')

#######Example how to fetch from DB########
'''cur.execute("SELECT * FROM tasks")
#fetch and print results returned from SQL statement
print(cur.fetchall())'''

cur.execute("INSERT INTO users (username, email, password_hash) VALUES ('alice', 'alice@example.com', 'hashedpassword');")
print(cur.fetchall())

########## DB Access Functions ##########

#Adds a new user to the database
#Takes username, password, and email as params
#Returns True if user is successfully added, otherwise returns false
def add_user(username : str, email : str, password_hash) -> bool:

    try:
        cur.execute(f"""
                        INSERT INTO users (username, email, password_hash)
                        VALUES ({username}, {email}, {password_hash});
            """)

    except UniqueViolation:
        return False

    return True


#Adds a new task to the database
#Takes title, completed, description, and is_subtask as params
#Returns True if task is successfully added, otherwise returns false
def add_task(title : str, completed : bool, description : str = "None", is_subtask : bool = False) -> bool:

    #TODO get user_id from current user
    user_id = "1"

    if is_subtask:
        #TODO get parent_task_id from parent task
        parent_task_id = "1"

        try:
            cur.execute(f"""
                            INSERT INTO tasks (user_id, title, description, completed, parent_task_id)
                            VALUES ({user_id}, {title}, {description}, {completed}, {parent_task_id});
                """)

        except UniqueViolation:
            return False

    else:
        try:
            cur.execute(f"""
                            INSERT INTO tasks (user_id, title, description, completed)
                            VALUES ({user_id}, {title}, {description}, {completed});
                """)

        except UniqueViolation:
            return False

    return True







#close cursor and connection objects
cur.close()
conn.close()