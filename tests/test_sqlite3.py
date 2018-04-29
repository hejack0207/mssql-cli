# coding=utf-8
from __future__ import unicode_literals
import os
import unittest
import tempfile

class TestSqlite3(unittest.TestCase):

    def test_sqlite3(self):
        import sqlite3
        conn = sqlite3.connect('/tmp/database')

        curs = conn.cursor()
        tblcmd = 'create table people (name char(30),job char(10),pay int(4))'
        curs.execute(tblcmd)
        curs.execute('insert into people values(?,?,?)',('Bob','dev',5000))
        conn.commit()

        curs.execute('select * from people')
        for row in curs.fetchall():
            print(row)

