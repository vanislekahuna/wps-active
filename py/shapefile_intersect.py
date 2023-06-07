'''20230604 CWFIS version. Use to intersect shapefile of point locations, with tile-index file produced by 

20230530 intersect one shapefile with another. NB probably need to adjust which field is reported on.

adapted from:  bcws_select_tiles
20230520 project fire locations onto Sentinel-2 tiles
Use this to update :
.tiles_select used by safe_unzip_select.py
'''
from misc import run, err, args, exists, sep
from osgeo import ogr
import sys
import os

rd = 'reproject'
if not exists(rd):
    os.mkdir(rd)

# shapefile_reproject.py [input shapefile] [shapefile or raster to get CRS from] [output shapefile]

def print_feature(feature):
    num_fields = feature.GetFieldCount()
    
    # Loop through all attribute fields
    for i in range(num_fields):
        field_name = feature.GetFieldDefnRef(i).GetName()
        field_value = feature.GetField(i)
        print(f"{field_name}: {field_value}")

# intersect one shapefile with another
my_tiles = {}
def shapefile_intersect(s1_path, s2_path):
    # Open the first shapefile
    print('r', s1_path)
    s1_driver = ogr.GetDriverByName('ESRI Shapefile')
    s1_dataSource = s1_driver.Open(s1_path, 0)
    if s1_dataSource is None:
        err('opening:' + s1_path)

    s1_layer = s1_dataSource.GetLayer()
    s1_crs = s1_layer.GetSpatialRef()   
    
    # Open the second shapefile
    print('r', s2_path)
    s2_driver = ogr.GetDriverByName('ESRI Shapefile')
    s2_dataSource = s2_driver.Open(s2_path, 0)
    if s2_dataSource is None:
        err('opening:' + s2_path)
    
    s2_layer = s2_dataSource.GetLayer()
    s2_crs = s2_layer.GetSpatialRef()

    if s1_crs.ExportToWkt() == s2_crs.ExportToWkt():
        print("The CRS of the two shapefiles is the same.")
    else:
        print("The CRS of the two shapefiles is different.")
        print(s1_path, s1_crs.ExportToWkt())
        print(s2_path, s2_crs.ExportToWkt())
        sys.exit(1)

    # Loop through features in the first shapefile
    for feature1 in s1_layer:
        # print_feature(feature1) # print(feature1)
        geometry1 = feature1.GetGeometryRef()
        # Loop through features in the second shapefile 
        for feature2 in s2_layer:
            geometry2 = feature2.GetGeometryRef()
            # Check if the two geometries intersect
            # print_feature(feature2)
            if geometry1.Intersects(geometry2):
                print("Features intersect!")
                #print_feature(feature1)
                my_fire = feature1.GetField("FIRE_NUM")
                my_tile = feature2.GetField("Name")
                if my_fire not in my_tiles:
                    my_tiles[my_fire] = set()
                my_tiles[my_fire].add(my_tile)
                print("-------------------")
                #print_feature(feature2)
                #print(geometry1)
                #print(geometry2)
    # Clean up and close the shapefile data sources
    s1_dataSource = None
    s2_dataSource = None

shapefile_intersect('CWFIS.shp',
                    's2_gid/s2_gid.shp')

'''

s1 = 'prot_current_fire_points.shp'
shapefile_intersect(s1, s2)


if not exists('.select'):
    os.mkdir('.select')

tiles_select = set()
for fire in my_tiles:
    this_fire = []

    print(fire, my_tiles[fire])
    for tile in my_tiles[fire]:
        tiles_select.add(tile)
        this_fire += [tile]
    
    open('.select/' + fire, 'wb').write((' '.join(this_fire)).encode())
    bs = '/media/' + os.popen('whoami').read().strip() + '/disk4/active/'
    if os.path.exists(bs):
        tf = bs + fire
        if not os.path.exists(tf):
            try:
                os.mkdir(tf)
            except:
                print("Warning: mkdir failed:", tf) 
        tf +=  '/.tiles'
        print('+w', tf)
        open(bs + fire + '/.tiles', 'wb').write((' '.join(this_fire)).encode())

tiles_select = list(tiles_select)
print(tiles_select)

open('.tiles_select', 'wb').write((' '.join(['T' + t for t in tiles_select])).encode())
'''
