import settings
import psycopg2, psycopg2.extras
from core import DBUtil

class SQLDataTable():
    columns = []
    rows = []

    def __init__(self):
        self.columns = []
        self.rows = []

    def getColString(self):
        return ','.join(self.columns)

    def getValueString(self, rowIdx, anonymous=False):
        pass


class SQLTableAdapter():
    conn:object = None
    table:SQLDataTable = SQLDataTable() 

    def __init__(self, dbConfig:str):
        self.conn = DBUtil.getConnection(dbConfig)
        self.table

    def __getColumns(self, tableName:str):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = "SELECT column_name FROM information_schema.columns WHERE table_schema='public' and table_name = '%s'"
        cur.execute(sql,tableName)
        self.table.columns = cur.fetchall()
        cur.close()

    def __getRows(self, tableName:str):
        cur = self.conn.cursor()
        sql = "SELECT * FROM %s"
        cur.execute(sql,tableName)
        self.table.rows = cur.fetchall()
        cur.close()

    def getDataTable(self, tableName:str):
        self.table = SQLDataTable()
        self.__getColumns(tableName)
        self.__getRows(tableName)

    def changeConnection(self, dbConfig):
        if self.conn:
            self.conn.close()
        self.conn = DBUtil.getConnection(dbConfig)

    def clean(self):
        if self.conn:
            self.conn.close()
        self.table = None



class DBCopier():
    SOURCE = 'source'
    DESTINATION = 'destination'
    table_list = []

    def __init__(self):
        self.table_list = DBUtil.getTableList(DBUtil.getConnection(self.SOURCE))
        print(len(self.table_list))

    def copyToDestination(self):
        for table in self.table_list:
            pass