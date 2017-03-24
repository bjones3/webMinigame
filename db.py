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


def get_leaderboard_data(game_config):
    my_conn = get_conn()
    with my_conn:
        with my_conn.cursor() as cursor:
            cursor.execute("SELECT slug, "
                           "COUNT(DISTINCT plots) AS plot_count, "
                           "COUNT(DISTINCT seeds) AS seed_types, "
                           "MAX(cash) AS CASH "
                           "FROM (SELECT slug, "
                           "    jsonb_object_keys(game_state->'plots') AS plots, "
                           "    jsonb_object_keys(game_state->'seedCounts') AS seeds, "
                           "    (game_state->'resources'->>'%s')::int AS cash "
                           "    FROM game_states) AS subquery "
                           "GROUP BY slug ORDER BY plot_count DESC, seed_types DESC, cash DESC "
                           "LIMIT 20;" % game_config.CASH_RESOURCE)
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
