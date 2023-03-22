from flask import Flask, jsonify, request
import psycopg2
import yaml

app = Flask(__name__)

# Load configuration from YAML file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Connect to Localhost PostgreSQL database
try:
    conn = psycopg2.connect(**config['database'])
except psycopg2.Error as e:
    print(f"Error connecting to database: {e}")
    exit(1)

def create_tables():
    with conn, conn.cursor() as cur:
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    character_type TEXT
                )
            """)
            cur.execute("""
                ALTER TABLE IF EXISTS users
                ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY,
                ADD COLUMN IF NOT EXISTS name TEXT NOT NULL UNIQUE,
                ADD COLUMN IF NOT EXISTS character_type TEXT
            """)
        except psycopg2.Error as e:
            print(f"Error creating tables: {e}")
            conn.rollback()
        else:
            conn.commit()

create_tables()  # Call the function to create the table

# Route to retrieve a list of users
@app.route('/users', methods=['GET'])
def get_users():
    with conn, conn.cursor() as cur:
        try:
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            users = [{'user_id': row[0], 'name': row[1], 'character_type': row[2]} for row in rows]
            return jsonify({'users': users})
        except psycopg2.Error as e:
            print(f"Error getting users: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with conn, conn.cursor() as cur:
        try:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if row:
                name = row[1]
                character = row[2]
                return jsonify({"message": f"Hello {name}, congratulations for your achievement. You are strong {character} ", 'user_id': row[0]})
            else:
                return jsonify({'error': 'User not found!'}), 404
        except psycopg2.Error as e:
            print(f"Error getting user {user_id}: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500

# Route to create a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data['name']
    character_type = data['character_type']

    with conn, conn.cursor() as cur:
        try:
            # Check if the user already exists
            cur.execute("SELECT * FROM users WHERE name = %s", (name,))
            if cur.fetchone():
                return jsonify({'error': 'User with that name already exists!'})

            # Create new user
            cur.execute("INSERT INTO users (name, character_type) VALUES (%s, %s) RETURNING id", (name, character_type))
            new_user_id = cur.fetchone()[0]
            new_user = {'user_id': new_user_id, 'name': name, 'character_type': character_type}
        except psycopg2.Error as e:
            print(f"Error creating user: {e}")
            return jsonify({'error': 'Internal Server Error'}), 500
        else:
            conn.commit()
            return jsonify(new_user)

# Route to update user
def update_user(user_id):
    data = request.get_json()
    character_type = data['character_type']
    with conn, conn.cursor() as cur:
        try:
            cur.execute("UPDATE users SET character_type = %s WHERE id = %s", (character_type, user_id))
        except psycopg2.Error as e:
            print(f"Error updating user {user_id}: {e}")
            conn.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500
        else:
            conn.commit()
            return jsonify({'message': f'User {user_id} updated!', 'character_type': character_type})

# Route to delete user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    with conn, conn.cursor() as cur:
        try:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if not row:
                return jsonify({'error': 'User not found!'})

            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        except psycopg2.Error as e:
            print(f"Error deleting user {user_id}: {e}")
            conn.rollback()
            return jsonify({'error': 'Internal Server Error'}), 500
        else:
            conn.commit()
            return jsonify({'message': f'User {user_id} deleted!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)