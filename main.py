import sqlite3
from sqlite3 import Error


def main():

    database = "flashbackup-1905020007.pqb"

    with create_connection(database) as conn:
        print("1. Query all cards")
        cards = get(conn, 'cards')                      # Key: Card ID
        categories = get(conn, 'categories')            # Key: Category ID
        category_assigns = get(conn, 'categoryassigns') # Key: Card ID
        score_files = get_score_files(conn)             # Key: Scorefile name


        pass


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def get(conn, table):
    cur = conn.cursor()
    cur.execute("SELECT * FROM pleco_flash_{}".format(table))

    # Takes the first column of the table as keys for a dictionary
    return dict([(row[0], row[1:]) for row in cur.fetchall()])


def get_score_files(conn):
    score_file_defs = get(conn, 'scorefiles')

    score_files = dict()

    for i_score_file, score_file_def in score_file_defs.items():
        score_file = get(conn, 'scores_{}'.format(i_score_file))  # Key: Card ID
        score_files[score_file_def[0]] = score_file

    return score_files




if __name__ == '__main__':
    main()
