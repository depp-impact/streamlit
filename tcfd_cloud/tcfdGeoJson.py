from shapely.geometry import Point, Polygon
import geopandas as gpd

def expotGeoJSON(gems):
    outfiles = []
    fileindex = 1
    for gem in gems:
        poly = str(gem.replace('MULTIPOLYGON(((','').replace(')))',''))
        poly = poly.split(',')
        coordinates = []
        for xy in poly:
            xy = [float(xy.split(' ')[1]),float(xy.split(' ')[0])]
            coordinates.append(tuple(xy))

        newdata = gpd.GeoDataFrame()
        poly = Polygon(coordinates)
        newdata.loc[0, 'geometry'] = poly
        #newdata.crs = from_epsg(6668)
        outfp = f"gem_{fileindex}"
        poly_json = newdata.to_json()
        return poly_json
        #newdata.to_file(filename=outfp+'.json', driver='GeoJSON')
        #newdata.to_file(filename=outfp+'.shp', driver="ESRI Shapefile")

        #newdata.to_file(outfp)
        #outfiles.append(outfp+'.json')
        #tt = gpd.read_file(outfp)
    return None

def searchSQL(mydb, lat, lon, riverName, schema):
    cur = mydb.cursor(dictionary=True)
    sql = f"SELECT river_name,ST_AsText(geom) as gem FROM {schema}.mlit_river_inundation_area"\
            + f" WHERE river_name = '{riverName}' and ST_Intersects(geom, ST_GeomFromText('POINT({lat} {lon})', 0));"
    print(sql)
    result = []
    cur.execute(sql)
    data = cur.fetchall()

    if(data is None or len(data)==0):
        return None
    else:
        gem = []
        for n, rec in enumerate(data):
            result.append(rec['river_name'])
            gem.append(rec['gem'])
    cur.close()
    selectPoly = expotGeoJSON(gem)
    return selectPoly


