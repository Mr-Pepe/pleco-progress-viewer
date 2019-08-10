import os
from plecoviewer.utils import Backup


def main():

    database_dir = "../backups"

    backups = []
    for root, _, fnames in os.walk(os.path.join(database_dir)):
        valid_fnames = [fname for fname in fnames if fname.split('.')[-1] == 'pqb']

        for i_fname, fname in enumerate(valid_fnames):
            print('Loading Backup {}/{}'.format(i_fname + 1, len(valid_fnames)))
            backups.append(Backup(os.path.join(root, fname)))


if __name__ == '__main__':
    main()
