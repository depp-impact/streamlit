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
    initial_sidebar_state="expanded"
)

pref={ '01':'北海道','02':'青森県','03':'岩手県','04':'宮城県','05':'秋田県','06':'山形県','07':'福島県',
    '08':'茨城県','09':'栃木県','10':'群馬県','11':'埼玉県','12':'千葉県','13':'東京都','14':'神奈川県',
    '15':'新潟県','16':'富山県','17':'石川県','18':'福井県','19':'山梨県','20':'長野県','21':'岐阜県',
    '22':'静岡県','23':'愛知県','24':'三重県','25':'滋賀県','26':'京都府','27':'大阪府','28':'兵庫県',
    '29':'奈良県','30':'和歌山県','31':'鳥取県','32':'島根県','33':'岡山県','34':'広島県','35':'山口県',
    '36':'徳島県','37':'香川県','38':'愛媛県','39':'高知県','40':'福岡県','41':'佐賀県','42':'長崎県',
    '43':'熊本県','44':'大分県','45':'宮崎県','46':'鹿児島県','47':'沖縄県',
    #'81':'北海道開発局','82':'東北地方整備局','83':'関東地方整備局','84':'北陸地方整備局','85':'中部地方整備局',
    #'86':'近畿地方整備局','87':'中国地方整備局','88':'四国地方整備局','88':'九州地方整備局','89':'沖縄総合事務局',
    }
optpref = st.sidebar.selectbox('県名', pref.values())

if(mydb is None):
    st.text('mydb is None')
else:
    property_columns, output_columns = get_table_column()
    tcdfViewAws.view(st, mydb, property_columns, output_columns, 'milize', 'milize', schema,optpref)
