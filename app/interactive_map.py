import folium
from folium.plugins import Draw
import branca.colormap as cm
from shapely.geometry import Polygon
from credentials import Mapbox_token
import warnings

warnings.simplefilter(action='ignore')


def coordinates_2_polygon(coord_list):
    # swap lat and long
    new_coord = [(t[1], t[0]) for t in coord_list]
    poly = Polygon(new_coord)
    return poly


def show_map_marker(coord, zoom):
    # df is the data that will be displayed in the map. the df need a column geomytry with the polygons of our data

    x_map = coord[0]
    y_map = coord[1]

    tileurl = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=' + str(Mapbox_token)
    mymap = folium.Map(location=[x_map, y_map], zoom_start=zoom, max_zoom=21, tiles=tileurl, attr='Mapbox',
                       name='Satellite')

    # User can add new marker
    Draw(draw_options={
        'polygon': False,
        'polyline': False,
        'rectangle': False,
        'circle': False,
        'circlemarker': False
    },
        export=True).add_to(mymap)

    icon = folium.features.CustomIcon('assets/marker.png', icon_size=(20, 20))
    # main coordinates marker
    folium.Marker(
        [x_map, y_map],
        popup="Your House",
        icon=icon
    ).add_to(mymap)

    return mymap


def show_map_roof(df, zoom):
    # df is the data that will be displayed in the map. the df need a column geomytry with the polygons of our data

    df.crs = {
        'init': 'epsg:4326'
    }
    # Center of the map
    x_map = df.centroid.x.mean()
    y_map = df.centroid.y.mean()

    # Map choropleth configuration
    colormap = cm.LinearColormap(colors=['#fecc5c', '#fd8d3c', '#f03b20']).scale(
        round(df['potential_electricity_production_in_Kwh'].min()),
        round(df['potential_electricity_production_in_Kwh'].max()))

    # Create new folium map
    mymap = folium.Map(location=[y_map, x_map], zoom_start=zoom, max_zoom=21, tiles=None, width="%100", height="%100")

    # Add Mapbox tile layer (satellite)
    tileurl = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=' + str(Mapbox_token)
    folium.TileLayer(zoom_start=zoom, max_zoom=20, tiles=tileurl, attr='Mapbox', name='Satellite', width="%100", height="%100").add_to(mymap)

    # Style configuration
    colormap.caption = "Solar Potential"
    style_function = lambda x: {"weight": 0.1,
                                'color': '#0000ff',
                                'fillColor': colormap(x['properties']['potential_electricity_production_in_Kwh']),
                                'fillOpacity': 0.7}

    # Add second layer with tooltip : allows to display a text when hovering over the object

    roof = folium.features.GeoJson(
        df,
        style_function=style_function,
        control=False,
        zoom_on_click=True,
        tooltip=folium.features.GeoJsonTooltip(fields=['ID', 'area', 'potential_electricity_production_in_Kwh'],
                                               aliases=['Roof ID', 'Area (m²)', 'Potential electricity production (Kwh)'],
                                               style=(
                                                   "background-color: white; color: #333333; font-family: arial; "
                                                   "font-size: 12px; padding: 10px;"),
                                               sticky=True
                                               )
    )
    # Add Light Map tile layer
    folium.TileLayer(tiles='CartoDB positron', name="Light Map", zoom_start=zoom, max_zoom=20, width="%100", height="%100").add_to(mymap)

    colormap.add_to(mymap)
    mymap.add_child(roof)
    mymap.keep_in_front(roof)
    folium.LayerControl().add_to(mymap)

    return mymap
