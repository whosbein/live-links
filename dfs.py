#!/usr/bin/env python2

import sys, os, string, sqlite3, time, re
from pprint import pprint

sites = {}

class Site(object):

    def __init__(self, id):
        self.id = id
        self.live = False

    def set_live(self, c, conn):
        self.live = True
        c.execute("update file set live = 1 where f_id = ?", [self.id])
        conn.commit()

def dfs(node, c, conn):
    global sites
    #print node.id
    node.set_live(c, conn)
    c.execute("select group_concat(t_id, ' ') from link where s_id = ?",
              [node.id])
    try:
        result = c.fetchone()[0]
        for neighbor_id in result.split():
            # is this node already in the big sites list?
            if neighbor_id not in sites:
                neighbor = Site(neighbor_id)
                sites[neighbor_id] = neighbor
            if not sites[neighbor_id].live:
                dfs(neighbor, c, conn)
    except:
        # current node has no existing links
        pass

#def create_check(node):
    #global sites
    #neighbor = 

def connect_to_database(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    return c, conn

def main(argv=None):
    global sites
    #c, conn = connect_to_database("ota.sqlite")
    c, conn = connect_to_database("new.sqlite")

    root = Site('14')
    sites['14'] = root

    #guh = '14'
    #print sites[guh].id

    dfs(root, c, conn)

    #a = Site('1')
    #a.set_live()
    #sites['1'] = a

    #b = Site('1')
    ##b.set_live()

    #if b.id in sites:
        #print 'yes'

if __name__ == "__main__":
    main()
