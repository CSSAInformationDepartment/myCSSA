import settings
import psycopg2
import os
from core import DBUtil
from adapter import DBCopier


def main():
    print('CSSA DEV Database Migration Tool')

    ## Check database connection:
    if settings.DATABASES.get('source') == None or settings.DATABASES.get('destination') == None:
        raise SyntaxError('Database Configuration is not complete')
    else:
        DBUtil.getConnection('source', test=True)
        DBUtil.getConnection('destination', test=True)
        copier = DBCopier()



if __name__ == '__main__':
    main()
