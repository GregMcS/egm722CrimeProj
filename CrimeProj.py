import geopandas as gpd #gpd for creating geodatabases, tables with geometry data
import matplotlib.pyplot as plt 
import pandas as pd
import cartopy.crs as ccrs

crime = gpd.read_file('crimeDataEdit3.csv') #load point data csv
crime.crs = 'epsg:27700' #set point crs
crime.head #display head of point gdf

parishes = gpd.read_file('parishBound.csv') #load polygon data csv
parishes.crs = 'epsg:27700' #set polygon crs
parishes.head #display head of polygon gdf

print(crime.crs == parishes.crs) #confirm both gdf set to same crs

f, ax = plt.subplots(1, figsize=(12, 12))
ax = parishes.plot(ax=ax, alpha=0.8) #adjust alpha value to change colour intensity
#ax.set_axis_off()  #uncomment this line to remove national grid numbers
f.suptitle('Suffolk Parishes') #set plot title
plt.show() 

parishes.loc[6, 'geometry'] #adjust number to select parish

crime.plot(figsize=(12,10)) #display point data with nat grid to check AOI

clipped = [] #create an empty list 
for parish in parishes['Parish'].unique(): #iterate over polygon table for unique instances of a value ['Parish']
    tmp_clip = gpd.clip(crime, parishes[parishes['Parish'] == parish]) #clip point data to those which have a matching 'Parish'
    clipped.append(tmp_clip) #populate clipped list with points clipped to polygons

clipped_gdf = gpd.GeoDataFrame(pd.concat(clipped)) 
clip_total = clipped_gdf.count()

clip_total

crimes = clipped_gdf #rename clipped gdf 
crimes.crs = 'epsg:27700' #set new points gdf crs
crimes.plot(figsize=(12,10)); #display new point plot to confirm contained to AOI

base = parishes.plot(figsize = (20,18), color='white', edgecolor='black') #use polygon layer as a base

crimes.plot(ax=base, marker='d', color='blue', markersize=5) #display point layer on top of base

join = gpd.sjoin(parishes, crimes, how='inner', lsuffix='left', rsuffix='right') #perform the spatial join
join # show the joined table

crime_stats = join.groupby(['Parish', 'Crime_type']).count()
print(crime_stats.loc['Sproughton CP']) #Edit to select parish of interest

print(join.groupby(['Parish'])['Crime_type'].count()) #count number of crimes per parish

#adapted from https://geographicdata.science/book/notebooks/08_point_pattern_analysis.html

f, ax = plt.subplots(1, figsize=(12, 10))

hb = ax.hexbin(
    crimes['X'], 
    crimes['Y'],
    gridsize=50, # Generate and add hexbin with 50 hexagons in each
    linewidths=0,
    alpha=1, #edit value from 0 - 1 to increase intensity
    cmap='Reds' #Colour ramp to use 
)

# Add colorbar
plt.colorbar(hb)
# Remove axes
ax.set_axis_off()

# adapted from https://gis.stackexchange.com/questions/397876/how-can-i-create-a-choropleth-by-combining-a-polygon-geopanda-with-a-point-geopa

polygons = parishes
polygon_id_field = 'OBJECTID'
#points = crimes #
#points.crs = 'epsg:27700'

join = gpd.sjoin(parishes, crimes, how='left', predicate='contains')
count = join.groupby(polygon_id_field)[polygon_id_field].count()
count.name='pointcount'
polygons = pd.merge(left=polygons, right=count, left_on=polygon_id_field, right_index=True)

fig, ax = plt.subplots(figsize = (20,18))
polygons.plot(column = 'pointcount', cmap = 'Spectral_r', ax=ax, legend=True, #for different colour palettes edit cmap value
              legend_kwds={'label':'Number of crimes reported'})
polygons.geometry.boundary.plot(color=None, edgecolor='k',linewidth = 0, ax=ax)

fig = plt.figure(figsize=(20, 20))
ax1 = plt.subplot(2, 2, 1, projection=ccrs.Mercator()) # upper left
ax2 = plt.subplot(2, 2, 2, projection=ccrs.Mercator()) # upper right
ax3 = plt.subplot(2, 2, 3, projection=ccrs.Mercator()) # lower left
ax4 = plt.subplot(2, 2, 4, projection=ccrs.Mercator()) # lower right

crimes.plot(ax=ax1);

parishes.plot(ax=ax2, color='white', edgecolor='black') #use polygon layer as a base
crimes.plot(ax=ax2, marker='d', color='blue', markersize=5) #display point layer on top of base

hb = ax3.hexbin(crimes['X'], crimes['Y'], gridsize=50, linewidths=0, alpha=1, cmap='Reds')

polygons.plot(column = 'pointcount', cmap = 'Spectral_r', ax=ax4, legend=True, legend_kwds={'label':'Number of crimes reported'})
polygons.geometry.boundary.plot(color=None, edgecolor='k', linewidth = 0, ax=ax4)

#for further interaction in maps see https://towardsdatascience.com/interactive-geographical-maps-with-geopandas-4586a9d7cc10 

crime_count = join.groupby(['Ward'])['Crime_type'].count()

ward_count = parishes.set_index('Ward').join(crime_count.rename('Crime Count'))
ward_count.explore(column='Crime Count', tooltip=['Ward', 'Crime Count'], cmap = 'Spectral_r')
 
#set column to name of column to be used in legend
#add or remove column names from tooltip to change what is displayed on hover