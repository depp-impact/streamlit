#import login
#import tcdfView
import streamlit as st
import tcdfViewAws
import dbUtil as SQLUtil
import traceback

mysql_db = SQLUtil.mysql_db()
host=st.secrets["mysql"]["host"]
schema=st.secrets["mysql"]["database"]
userid=st.secrets["mysql"]["user"]
passwd=st.secrets["mysql"]["password"]
mydb = mysql_db.connect(host, userid, passwd, schema)


def get_table_column():
    sql = f"select COLUMN_NAME, COLUMN_COMMENT from INFORMATION_SCHEMA.COLUMNS where TABLE_SCHEMA = 'tcfd' and TABLE_NAME = 'property_information'"
    #st.text(sql)
    try:
        recs = mysql_db.fetch(mydb, sql)
        property_columns = {}

        for rec in recs:
            comment = rec[1]
            if('\n' in rec[1]):
                comment = rec[1].split('\n')[0]
            if('(' in rec[1]):
                comment = rec[1].split('(')[0]
            property_columns.update({rec[0]:comment.replace('\u3000',' ')})

        output_columns = {}
        sql = f"select COLUMN_NAME, COLUMN_COMMENT from INFORMATION_SCHEMA.COLUMNS where TABLE_SCHEMA = 'tcfd' and TABLE_NAME = 'output_information'"
        
        #st.text(sql)
        recs = mysql_db.fetch(mydb, sql)
        for rec in recs:
            comment = rec[1]
            if('\n' in rec[1]):
                comment = rec[1].split('\n')[0]
            if('(' in rec[1]):
                comment = rec[1].split('(')[0]
            output_columns.update({rec[0]:comment.replace('\u3000',' ')})
        return property_columns, output_columns
    except:
        st.text(traceback.format_exc)

st.set_page_config(
    page_title="milize tcfd viewer",
    layout="wide",
    initial_sidebar_state="expanded", 
)
if(mydb is None):
    st.text('mydb is None')
else:
    property_columns, output_columns = get_table_column()
    tcdfViewAws.view(st, mydb, property_columns, output_columns, 'milize', 'milize')
