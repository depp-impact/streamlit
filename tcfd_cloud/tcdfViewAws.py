import traceback
#from turtle import onclick
from streamlit_folium import st_folium      # streamlitでfoliumを使う
import folium
import json

import dbUtil as SQLUtil
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import pandas as pd
import requests

#st.text(host)
#st.text(userid)
#st.text(passwd)
#st.text(schema)
#st.text(f"user={userid},password={passwd},host={host}, database={schema}")

def show_map_data(inputdata):
    lat = inputdata[0]['緯度']
    lon = inputdata[0]['経度']
    copyright_osm = '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    map = folium.Map(location=[lat, lon], zoom_start=15,attr=copyright_osm)

    #pop=f"{row['都道府県名']}({row['都道府県庁所在地']})<br>　人口…{row['人口']:,}人<br>　面積…{row['面積']:,}km2"
    folium.Marker(
        # 緯度と経度を指定
        location=[lat, lon],
        # ツールチップの指定(都道府県名)
        #tooltip=row['都道府県名'],
        # ポップアップの指定
        #popup = folium.Popup(pop, max_width=300),
        # アイコンの指定(アイコン、色)
        icon = folium.Icon(icon="home",icon_color="white", color="red")
    ).add_to(map)

# 表示するデータを読み込み
# df = pd.read_csv('pref.csv')
# 読み込んだデータ(緯度・経度、ポップアップ用文字、アイコンを表示)
# for i, row in df.iterrows():
    # ポップアップの作成(都道府県名＋都道府県庁所在地＋人口＋面積)
#     pop=f"{row['都道府県名']}({row['都道府県庁所在地']})<br>　人口…{row['人口']:,}人<br>　面積…{row['面積']:,}km2"
#     folium.Marker(
        # 緯度と経度を指定
#         location=[row['緯度'], row['経度']],
#         # ツールチップの指定(都道府県名)
#         tooltip=row['都道府県名'],
#         # ポップアップの指定
#         popup=folium.Popup(pop, max_width=300),
        # アイコンの指定(アイコン、色)
#         icon=folium.Icon(icon="home",icon_color="white", color="red")
#     ).add_to(m)
    st_data = st_folium(map, width=1200, height=800)
    #st.components.v1.html(folium.Figure().add_child(map_).render(), height=500)

def get_calculate_result(mydb, pid, outColumns):
    sql = f"select water_depth {outColumns['water_depth']}, river_name {outColumns['river_name']},"\
                f"damage_rate {outColumns['damage_rate']}, damage_amount {outColumns['damage_amount']} "\
                f"from tcfd.output_information where property_id = '{pid}';"
    #print(sql)
    df = pd.read_sql(sql, mydb, coerce_float=True)
    gb = GridOptionsBuilder.from_dataframe(df)
    #gb.configure_selection(use_checkbox=True)
    gridOptions = gb.build()
    
    #物件データの表示
    data = AgGrid(df, fit_columns_on_grid_load=True,
                gridOptions=gridOptions, height=85)

#def get_property(pref, property_columns, output_columns):
def get_property(st, mydb, inColumns, outColumns, pref):
    #property_type = 1:マンション 2:アパート 3:戸建て 4:企業 5:農地等
    sql = f"select property_id {inColumns['property_id']}, contract_number {inColumns['contract_number']},"\
                f"property_type {inColumns['property_type']}, loan_amount {inColumns['loan_amount']},"\
                f"loan_balance {inColumns['loan_balance']}, DATE_FORMAT(loan_end_date,'%Y/%m/%d') {inColumns['loan_end_date']},"\
                f"address {inColumns['address']}, latitude {inColumns['latitude']}, longitude {inColumns['longitude']},"\
                f"assessed_land_amount {inColumns['assessed_land_amount']}, assessed_building_amount {inColumns['assessed_building_amount']},"\
                f"assessed_apartment_amount {inColumns['assessed_apartment_amount']} "\
            f"from tcfd.property_information where address like '{pref}%' and (latitude is not null and longitude is not null);"
    df = pd.read_sql(sql, mydb, coerce_float=True)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(use_checkbox=True)
    gridOptions = gb.build()
    
    #物件データの表示
    data = AgGrid(df, fit_columns_on_grid_load=True,
                gridOptions=gridOptions, height=400)
              #enable_enterprise_modules=True, 
              #allow_unsafe_jscode=True, 
              #update_mode=GridUpdateMode.SELECTION_CHANGED)
    
    #col1, col2 = st.columns(2)
    if(data["selected_rows"] != []):
        st.text('深水深・被害額 計算結果')
        #inLabel1, inLabel2, inLabel3, inLabel4 = st.columns(4)
        #st.text()
        #st.write(data["selected_rows"])
        calc = get_calculate_result(mydb, data["selected_rows"][0]['物件ID'], outColumns)
        lat = data["selected_rows"][0]['緯度']
        lon = data["selected_rows"][0]['経度']

        #水防Mapから詳細な深水深をAPIで取得
        #print(lat, lon)
        apiurl = f'https://suiboumap.gsi.go.jp/shinsuimap/Api/Public/GetMaxDepth?lon={lon}&lat={lat}'
        sinsui_depth = requests.get(apiurl)
        sinsui_depth = sinsui_depth.json()

        if(sinsui_depth is None):
            st.text('水防マップ深水深：該当無し')
        else:
            #sinsui_depth = sinsui_depth.json()
            #print(sinsui_depth)
            #print(sinsui_depth['Depth'])
            st.text('(参考) 水防マップAPIで参照した深水深の値：'+str(sinsui_depth['Depth'])+'m')
        show_map_data(data["selected_rows"])
    #st.dataframe(df, height=800, width=2000)
    #AgGrid(df, fit_columns_on_grid_load=True,width=1500, height=800)
    #st.table(df,height=800)


def view(st, mydb, inColumns, outColumns, userid, passwd):
    pref={ '01':'北海道','02':'青森県','03':'岩手県','04':'宮城県','05':'秋田県','06':'山形県','07':'福島県',
        '08':'茨城県','09':'栃木県','10':'群馬県','11':'埼玉県','12':'千葉県','13':'東京都','14':'神奈川県',
        '15':'新潟県','16':'富山県','17':'石川県','18':'福井県','19':'山梨県','20':'長野県','21':'岐阜県',
        '22':'静岡県','23':'愛知県','24':'三重県','25':'滋賀県','26':'京都府','27':'大阪府','28':'兵庫県',
        '29':'奈良県','30':'和歌山県','31':'鳥取県','32':'島根県','33':'岡山県','34':'広島県','35':'山口県',
        '36':'徳島県','37':'香川県','38':'愛媛県','39':'高知県','40':'福岡県','41':'佐賀県','42':'長崎県',
        '43':'熊本県','44':'大分県','45':'宮崎県','46':'鹿児島県','47':'沖縄県',
        '81':'北海道開発局','82':'東北地方整備局','83':'関東地方整備局','84':'北陸地方整備局','85':'中部地方整備局',
        '86':'近畿地方整備局','87':'中国地方整備局','88':'四国地方整備局','88':'九州地方整備局','89':'沖縄総合事務局',
        }
    optpref = st.sidebar.selectbox('県名', pref.values())
    get_property(st, mydb, inColumns, outColumns, optpref)


