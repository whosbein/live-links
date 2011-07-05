#!/usr/bin/env python
"""
Methods to create and fill the database containing information about the files.
"""

import sys, os, string, sqlite3
from argparse import ArgumentParser

def gen_files_table(db_name, local_path, c, conn):
    """
    Generates the information for the database.
    """

    file_types = set() # set of encountered file types
    urls = set(['.php', '.htm', '.html'])

    for root, dirs, files in os.walk(local_path):
        for name in files:
            # name is individual file name
            filename = os.path.join(root, name) # full filename
            ext = os.path.splitext(filename)[1]
            file_types.add(ext)
            path = string.replace(root, local_path, '')
            depth = 0
            if path != '':
                depth = path.count('/') + 1
            size = os.path.getsize(filename)
            if ext in urls:
                file_type = 'url'
            else:
                file_type = 'file'

            sql = 'insert into file ' \
                  '(name, depth, path, size, type, ext) ' \
                  'values (\'%s\', %i, \'%s\', %i, \'%s\', \'%s\');' \
                  % (name, depth, path, size, file_type, ext)
            c.execute(sql)
            item_id = c.lastrowid

    conn.commit()

def check_for_database(db_name):
    """
    Checks for the database and its required tables and creates them if they
    don't exist.

    Assumes the database is called [db_name].sqlite
    """

    db_name = db_name + '.sqlite'

    if not os.path.exists(db_name):
        print "Creating database %s" % db_name
        file = open(db_name, 'w')
        file.close()

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    sql = 'create table if not exists file (f_id INTEGER PRIMARY KEY, \
          name TEXT, depth INT, path TEXT, live BOOLEAN DEFAULT 0, size INT, \
          type TEXT, ext TEXT)'
    c.execute(sql)
    conn.commit()

    return c, conn

def main(argv=None):
    parser = ArgumentParser(description='Database creator')

    parser.add_argument('-n', '--name', action='store', dest='name',
                        required=True,
                        help='The name of the database')
    parser.add_argument('-p', '--path', action='store', dest='path',
                        required=True,
                        help='The path to the local files')
    args = parser.parse_args()

    c, conn = check_for_database(args.name)

    gen_files_table(args.name, args.path, c, conn)

if __name__ == "__main__":
    main()
