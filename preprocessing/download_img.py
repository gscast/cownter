import leafmap.foliumap as lf
import folium

# Set your coordinates (latitude and longitude)
latitude = 37.7749
longitude = -122.4194

# Set the zoom level (adjust as needed)
zoom_level = 14

# Create a folium map centered on the specified coordinates
m = folium.Map(location=[latitude, longitude], zoom_start=zoom_level)

# Add OpenStreetMap TIF layer
osm_layer = lf.osm_gdf_from_point((latitude, longitude))
m.add_child(osm_layer)

# Create a TIF URL
tif_url = lf.get_osm_xyz_url(latitude, longitude, zoom_level)

# Download the TIF file
output_directory = "path/to/your/output/directory"
lf.download_tif(tif_url, output_directory)

# Display the map
m.save("osm_map.html")
