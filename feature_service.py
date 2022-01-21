# Import modules
import arcpy
import sys
import time

# Set variables and environment
arcpy.env.workspace = r"Z:\ArcPro\gis_data\feature_service.gdb"
input_layer = r"C:\Users\AppData\ESRI\Desktop10.6\ArcCatalog\Connection to Database.sde\raw_data"
output_layer = r"Z:\ArcPro\gis_data\feature_service.gdb\Bridges"

# Copy features to file geodatabase
arcpy.CopyFeatures_management(input_layer, output_layer)

# Set variables for altering field names
fc = "Bridges"
field_names = [f.name for f in arcpy.ListFields(fc)] 
start = time.time()

# Alter field names
if "BRDGID" in field_names:
    arcpy.AlterField_management(fc, 'BRDGID', 'BRDG_ID', 'Bridge ID')
if "ITEM_2" in field_names:
    arcpy.AlterField_management(fc, 'ITEM_2', 'DISTRICT', 'District')
if "ITEM_3" in field_names:
    arcpy.AlterField_management(fc, 'ITEM_3', 'COUNTY', 'County')
if "ITEM_4" in field_names:
    arcpy.AlterField_management(fc, 'ITEM_4', 'CITY_CD', 'City Code')
if "ITEM_7" in field_names:
    arcpy.AlterField_management(fc, 'ITEM_7', 'FACLTY_CARRD', 'Facility Carried')
if "ITEM_6_1" in field_names:
    arcpy.AlterField_management(fc, 'ITEM_6_1', 'FEAT_INTSECT', 'Feature Intersected')
if "ITEM_9" in field_names:
    arcpy.AlterField_management(fc, 'ITEM_9', 'LOCN', 'Location')
if "ITEM_41" in field_names:
    arcpy.AlterField_management(fc, 'ITEM_41', 'OPRTL_STAT_CD', 'Operational Status Code')
if "ITEM_16" in field_names:
    arcpy.AlterField_management(fc, 'ITEM_16', 'LAT', 'Latitude')
if "ITEM_17" in field_names:
    arcpy.AlterField_management(fc, 'ITEM_17', 'LONG', 'Longitude')
    
end = time.time()
print('Time elapsed = ' + str(end - start))



# Set variables for creating new data field
in_table = "Bridges"
field_name = "OPRTL_STAT"
field_name_cd = "OPRTL_STAT_CD"
field_type = "TEXT"
field_length = "40"
field_alias = "Operational Status"

# Variables for field calculation
expression = "getClass(!OPRTL_STAT_CD!)"
codeblock = """def getClass(OPRTL_STAT_CD):
    if OPRTL_STAT_CD is 'A':
        return "Open"
    if OPRTL_STAT_CD is 'B':
        return "Open - Closing/Posting Recommended"
    if OPRTL_STAT_CD is 'D':
        return "Open"
    if OPRTL_STAT_CD is 'E':
        return "Open"
    if OPRTL_STAT_CD is 'G':
        return "Closed"
    if OPRTL_STAT_CD is 'K':
        return "Closed"
    if OPRTL_STAT_CD is 'P':
        return "Posted"
    if OPRTL_STAT_CD is 'R':
        return "Posted"
    if OPRTL_STAT_CD is 'U':
        return "Under Construction" """
    
try:
    
    # Create new field
    arcpy.AddField_management(in_table, field_name, field_type, "", "", field_length, field_alias)
    
    # Populate field with values from Item 41
    arcpy.CalculateField_management(in_table, field_name, expression, "PYTHON3", codeblock)
    
except:
    print(arcpy.GetMessages())
    
print('Complete')



# Set variables for symbolizing new layer
aprx = r"Z:\ArcPro\gis_data\feature_service.aprx"
template = r"ArcPro\gis_data\feature\service.gdb\Bridges.lyrx"
symbology_field = ["VALUE_FIELD", "Operational Status", "Operation Status"]

try:
    # Apply symbology
    arcpy.ApplySymbologyFromLayer_management(in_table, template, symbology_field)
    
except:
    print(arcpy.GetMessages())
    
    

# Overwrite feature service on ArcGIS Online
from arcgis.gis import GIS
import os

# Set variables and set the path to the project
prjPath = r"Z:\ArcPro\gis_data\feature_service.aprx"
arcpy.env.workspace = r"Z:\ArcPro\gis_data\feature_service.gdb"
portal = "http://www.arcgis.com" # Can also reference a local portal
user = "username"
password = "password"
fcList = sorted(arcpy.ListFeatureClasses())
sd_fs_name = "Feature Service Name"

# Set sharing options
shrOrg = True
shrEveryone = True

# Local paths to create temporary content
relPath = sys.path[0]
sddraft = os.path.join(relPath, "WebUpdate.sddraft")
sd = os.path.join(relPath, "WebUpdate.sd")

# Create a new SDDraft and stage to SD
print("Creating SD file")
arcpy.env.overwriteOutput = True
prj = arcpy.mp.ArcGISProject(prjPath)
mp = prj.listMaps()[0]

arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, "MY_HOSTED_SERVICES", "FEATURE_ACCESS", "", True, True)
arcpy.StageService_server(sddraft, sd)

print("Connection to {}".format(portal))
gis = GIS(portal, user, password)

# Find the SD, update it, publish with overwrite and set sharing and metadata
print("Search for original SD on portal...")
sdItem = gis.content.search("{} AND owner:{}".format(sd_fs_name, user), item_type = "Service Definition")[0]
print("Found SD: {}, ID: {} n Uploading and overwriting...".format(sdItem.title, sdItem.id))
sdItem.update(data=sd)
print("Overwriting existing feature service...")
fs = sdItem.publish(overwrite=True)

# Sharing options
print("Setting sharing options...")
fs.share(org=shrOrg, everyone=shrEveryone)

print("Finished updating: {} - ID: {}".format(fs.title, fs.id))