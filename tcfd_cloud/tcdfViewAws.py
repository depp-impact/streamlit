#from tkinter.messagebox import RETRY
#from tkinter.tix import AUTO
import traceback
#from turtle import width
#from turtle import onclick
import streamlit as st
from streamlit_folium import st_folium      # streamlitでfoliumを使う
import folium
import json

import dbUtil as SQLUtil
import tcfdGeoJson

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import pandas as pd
import requests
property_id = ''

mysql_db = SQLUtil.mysql_db()

def show_map_data(mydb, inputdata, schema, outColumns):
    lat = inputdata[0]['緯度']
    lon = inputdata[0]['経度']
    #copyright_osm = '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    #map = folium.Map(location=[lat, lon], zoom_start=15,attr=copyright_osm)
    map = folium.Map(location=[lat, lon],
                     tiles='https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png',
                     attr='国土地理院',
                     zoom_start=13,
                     zoom_control=False,scrollWheelZoom=False,dragging=False)

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

    #if(riverName != ''):
    pol = tcfdGeoJson.searchSQL(mydb, lat, lon, schema)
    if(pol is None):
        return 
    #for json in outfiles:
    folium.GeoJson(pol, name='浸水域', 
        style_function=lambda feature: {
        "fill_color": "1111cc",
        "line_color": "1111cc",
        "fill_opacity":"0.7",
        "fill":"True",
        #"weight": 10 / (feature["id"] + 1),
        #"fillOpacity": feature["id"] * 0.2
        }
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

    #st_data = st_folium(map, width=800, height=400)
    col1, col2 = st.columns(2)
    with col1:
        st.components.v1.html(folium.Figure().add_child(map).render(), height=500,width=700)
    with col2:
        calc_df = get_calculate_result(mydb, inputdata[0]['物件ID'], outColumns)
        #水防Mapから詳細な深水深をAPIで取得
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
    
    return calc_df

def get_calculate_result(mydb, pid, output_columns):
    try:
        sql = f"select water_depth {output_columns['water_depth']}, river_name {output_columns['river_name']},"\
                    f"damage_rate {output_columns['damage_rate']}, damage_amount {output_columns['damage_amount']} "\
                f"from tcfd.output_information where property_id = '{pid}';"
        st.text('深水深・被害額 計算結果')
        #print(sql)
        df = pd.read_sql(sql, mydb, coerce_float=True)
        #print(df)
        if(len(df) == 0):
            st.text('計算結果が見つかりませんでした。')
            return ''
        gb = GridOptionsBuilder.from_dataframe(df)
        #gb.configure_selection(use_checkbox=True)
        gridOptions = gb.build()
        
        #結果データの表示
        data = AgGrid(df, fit_columns_on_grid_load=True,
                        gridOptions=gridOptions, height=60)
        #print(df.columns)

        #print(df)
        #print(df['河川名'][0])
        return df
    except:
        print(traceback.format_exc())
        return ''

def get_property(st, mydb, inColumns, outColumns, optpref, schema):
    try:
        #property_type = 1:マンション 2:アパート 3:戸建て 4:企業 5:農地等
        sql = f"select i.property_id {inColumns['property_id']}, i.contract_number {inColumns['contract_number']},"\
                    f"i.property_type {inColumns['property_type']}, i.loan_amount {inColumns['loan_amount']},"\
                    f"i.loan_balance {inColumns['loan_balance']}, DATE_FORMAT(i.loan_end_date,'%Y/%m/%d') {inColumns['loan_end_date']},"\
                    f"i.address {inColumns['address']}, i.latitude {inColumns['latitude']}, i.longitude {inColumns['longitude']},"\
                    f"i.assessed_land_amount {inColumns['assessed_land_amount']}, i.assessed_building_amount {inColumns['assessed_building_amount']},"\
                    f"i.assessed_apartment_amount {inColumns['assessed_apartment_amount']} "\
                "from tcfd.property_information i "\
                f" left join tcfd.output_information o on o.property_id = i.property_id "\
                f"where i.address like '{optpref}%' and (i.latitude is not null and i.longitude is not null) and "\
                f"o.damage_rate <> 0"
        #f"water_depth {outColumns['water_depth']}, river_name {outColumns['river_name']},"\
        #f"damage_rate {outColumns['damage_rate']}, damage_amount {outColumns['damage_amount']} "\
        #print(sql)
        df = pd.read_sql(sql, mydb, coerce_float=True)
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection(use_checkbox=True)
        #gb.configure_auto_height(True)
        #gb.configure_grid_options()
        gridOptions = gb.build()

        if(len(df) == 0):
            st.text('物件データが見つかりませんでした。')
            return
        
        st.text('計算物件一覧')

        hi = len(df)*50
        if(hi >= 350):
            hi=350

        #物件データの表示
        #data = AgGrid(df, fit_columns_on_grid_load=True,
        #            gridOptions=gridOptions,height=hi,columns_auto_size_mode=AUTOS)
        data = AgGrid(df, fit_columns_on_grid_load=True,gridOptions=gridOptions,height=hi)
                #enable_enterprise_modules=True, 
                #allow_unsafe_jscode=True, 
                #update_mode=GridUpdateMode.SELECTION_CHANGED)
        
        #col1, col2 = st.columns(2)
        if(data["selected_rows"] != []):
            #property_id = data["selected_rows"][0]['物件ID']
            #st.text(f'property_id:{property_id}')
            #st.text(f'物件ID:{data["selected_rows"][0]["物件ID"]}')

            #if(property_id == data["selected_rows"][0]['物件ID']):
            #    print('property_id == ',data["selected_rows"][0]['物件ID'])
            #    return
            property_id = data["selected_rows"][0]['物件ID']
            #inLabel1, inLabel2, inLabel3, inLabel4 = st.columns(4)
            #st.text()
            #st.write(data["selected_rows"])
            lat = data["selected_rows"][0]['緯度']
            lon = data["selected_rows"][0]['経度']

            show_map_data(mydb, data["selected_rows"], schema, outColumns)
        #st.dataframe(df, height=800, width=2000)
        #AgGrid(df, fit_columns_on_grid_load=True,width=1500, height=800)
        #st.table(df,height=800)
    except:
        print(traceback.format_exc())

def view(st, mydb, inColumns, outColumns, userid, passwd, schema,optpref):
    get_property(st, mydb, inColumns, outColumns, optpref, schema)
