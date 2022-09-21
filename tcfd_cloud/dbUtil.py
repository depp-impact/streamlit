# coding: utf-8
import os,sys, traceback
import mysql.connector

#sys.path.append('./config')
#import configfile

class mysql_db():
    def __init__(self):
        pass
    #接続
    def connect(self, host, userid, passwd, schema):
        try:
            mydb = mysql.connector.connect(user=userid, password=passwd, 
                                            host=host, database=schema )
            return mydb
        except:
            print(traceback.format_exc())
            return  None

    #データ取得
    def fetch(self, mydb, sql):
        try:
            cur = mydb.cursor()
            cur.execute(sql)
            return cur.fetchall()
        except:
            return None
        finally:
            cur.close()
    
    #コマンドSQL実行
    def execute(self, mydb, sql):
        try:
            cur = mydb.cursor()
            cur.execute(sql)
        except:
            return None
        finally:
            cur.close()

    def close(self, mydb):
        if( mydb is None ):
            return 
        mydb.close()
    
    def userinfo(self, mydb, userid, passwd):
        try:
            sql = f"select * from gis.user_information where user_id='{userid}' and pass_word='{passwd}';"
            print(sql)
            rec = self.fetch(mydb, sql)
            if(rec is None):
                return False
            else:
                if(len(rec) == 0):
                    return False
                return True
        except:
            print(traceback.format_exc())
            return False