import psycopg2
import settings

class DBUtil():

    @staticmethod
    def getConnection(dbconfig:str, test:bool=False):
        
        connString = DBUtil.getConnString(dbconfig)
        try:
            conn = psycopg2.connect(connString)
            print(f"Connection Successful to the database {dbconfig}!")
            if not test:
                return conn
        except ConnectionError:
            print(f"Connection Error! Please check the configuration of '{dbconfig}'")


    @staticmethod
    def getConnString(dbconfig:str) -> str:
        config = settings.DATABASES.get(dbconfig)
        if config == None:
            raise SystemError(f"Cannot find config for '{dbconfig}") 
        return f"host={config.get('host')} port={config.get('port')} dbname={config.get('db')} user={config.get('user')} password={config.get('password')}"

    @staticmethod
    def getTableList(conn):
        cur = conn.cursor()
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' order by 1 asc"
        cur.execute(sql)
        return cur.fetchall()      

    @staticmethod
    def checkTable(tableName:str, dbConfig) -> bool:
        conn = DBUtil.getConnection(dbConfig)
        cur = conn.cursor
        sql = "SELECT 1 FROM information_schema.tables WHERE table_schema='public' and table_name='%s'"
        cur.execute(sql,tableName)
        res = cur.fetchall()
        cur.close()
        conn.close()
        return len(res) > 0
    