import sqlite3
from sqlite3 import Error


def main():

    database = "flashbackup-1905020007.pqb"

    backup = Backup(database)


    pass










class Backup():
    def __init__(self, database_path):
        self.path = database_path

        with self.create_connection(self.path) as self.conn:
            print("1. Query all cards")
            self.cards = self.get('cards')  # Key: Card ID
            self.categories = self.get('categories')  # Key: Category ID
            self.category_assigns = self.get('categoryassigns')  # Key: Card ID
            self.score_files = self.get_score_files()  # Key: Scorefile name
        

    @staticmethod
    def create_connection(db_file):
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

        return None

    def get(self, table):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pleco_flash_{}".format(table))

        column_names = [elem[0] for elem in cursor.description]
        # Takes the first column of the table as keys for a dictionary
        return dict([(row[0], Entry(dict(zip(column_names[1:], row[1:])))) for row in cursor.fetchall()])

    def get_score_files(self):
        score_file_defs = self.get('scorefiles')

        score_files = dict()

        for i_score_file, score_file_def in score_file_defs.items():
            score_file = self.get('scores_{}'.format(i_score_file))  # Key: Card ID
            score_files[score_file_def.name] = score_file

        return score_files


class Entry(dict):
    def __init__(self, *args, **kwargs):
        super(Entry, self).__init__(*args, **kwargs)
        self.__dict__ = self


if __name__ == '__main__':
    main()
