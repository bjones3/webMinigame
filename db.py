import urlparse
import os
import psycopg2
import json

conn = None


def get_conn():
    global conn
    if conn is None:
        urlparse.uses_netloc.append('postgres')
        db_url = os.environ['DATABASE_URL']
        url = urlparse.urlparse(db_url)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    return conn


def load(slug):
    my_conn = get_conn()
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute('SELECT game_state FROM game_states WHERE slug = %s;', [slug])
            row = cursor.fetchone()
            if not row:
                return None
            return row[0]


def save(slug, data):
    my_conn = get_conn()
    json_game_state = json.dumps(data, indent=4)
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute('INSERT INTO game_states (slug, game_state) VALUES (%s, %s) '
                           'ON CONFLICT (slug) DO UPDATE SET game_state=%s;',
                           [slug, json_game_state, json_game_state])


def get_leaderboard_data():
    my_conn = get_conn()
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute("SELECT slug, game_state->'resources'->'cash' AS cash, "
                           "game_state->'seedCounts'->'m' AS m FROM game_states "
                           "WHERE game_state->'resources'->'cash' IS NOT NULL "
                           "ORDER BY 2 DESC LIMIT 10;")
            result = cursor.fetchall()
            return result


def get_admin_data():
    data = {}
    my_conn = get_conn()
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM game_states;')
            result = cursor.fetchone()
            data['game_count'] = result[0]

            cursor.execute('SELECT password FROM admin;')
            result = cursor.fetchone()
            data['password'] = result[0]
        return data
