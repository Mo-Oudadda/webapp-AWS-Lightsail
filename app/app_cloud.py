import math
import os
import boto3
import numpy as np
import streamlit as st
from streamlit_folium import folium_static, st_folium
from interactive_map import *
from style import card
import base64
from config import SAGEMAKER_ENDPOINT
from random import gauss

SG_KEY = os.environ['aws_access_key']
SG_SECRET = os.environ['aws_secret_access_key']


def generate_points(center_x, center_y, mean_radius=0.00007, sigma_radius=0.0004, num_points=6):
    points = []
    for theta in np.linspace(0, 2 * math.pi - (2 * math.pi / num_points), num_points):
        radius = gauss(mean_radius, sigma_radius)
        x = center_x + radius * math.cos(theta)
        y = center_y + radius * math.sin(theta)
        points.append([x, y])
    return points


def get_json_api(address, zoom, lat=0, lng=0):
    runtime = boto3.Session().client(
        'sagemaker-runtime',
        region_name="eu-west-3",
        aws_access_key_id=SG_KEY,
        aws_secret_access_key=SG_SECRET
    )
    params = b'{"address": "' + address.encode('utf-8') + b'", "zoom": ' + str(zoom).encode(
        'utf-8') + b', "lat": ' + str(
        lat).encode('utf-8') + b', "lng": ' + str(lng).encode('utf-8') + b'}'

    response = runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType='application/json',
        Body=params
    )['Body'].read().decode()

    formatted_response = json.loads(response)

    return formatted_response


st.set_page_config(
    page_title="Rootftop Detection Dashboard",
    page_icon="🔆",
    layout="wide",
)

st.write(
    "<style>.main * div.row-widget.stRadio > div{flex-direction:row;}</style>",
    unsafe_allow_html=True,
)
st.title('🔆 Rootftop Detection')
st.sidebar.title('Parameters')
zoom = st.sidebar.slider(label='Zoom level', min_value=15, max_value=21, step=1, value=19)

st.sidebar.title('Personalize your solar analysis')

electric_bill = st.sidebar.text_input(label='Your Average Monthly Electric Bill In Є', value=90)

address = st.text_input(label='Search for your home. Discover your solar savings potential.',
                        placeholder='Insert your address here...')

if address != '':
    ## Searsh Page
    lat, lng = (0, 0)
    try:
        data_marker = get_json_api(address, zoom, lat, lng)
        address_coord = data_marker['address coordinates']
        lat, lng = (float(address_coord[0]), float(address_coord[1]))
    except Exception as e:
        st.error(f'Could not retrieve map from address. Details: {e}')
    # To refresh the page after clicking in predict
    placeholder = st.empty()
    with placeholder:
        col_instruction, col_predict, space2 = st.columns([6, 2, 2], gap="medium")
        with col_instruction:
            st.info('If the red dot not centered in your building, Drag a marker from the map tool bar and '
                    'drop it in the centre of your building.')
            m_marker = show_map_marker([lat, lng], zoom)
            # Geoson with the new marker coordinates and zoom
            st_data = st_folium(m_marker, height=500, width=700)

        with col_predict:
            bu = st.markdown("""
            <style>
            div.stButton > button:first-child { 
            background-color:#44c767;
            border-radius:28px;
            border:1px solid #18ab29;
            display:inline-block;
            cursor:pointer;
            color:#ffffff;
            font-family:Arial;
            font-size:18px;
            padding:16px 31px;
            text-decoration:none;

            }
            </style>""", unsafe_allow_html=True)
            predict = st.button('Predict')

    ## Prediction Page
    if predict:
        try:
            new_coord = st_data['last_active_drawing']['geometry']['coordinates']
            new_coord[0], new_coord[1] = new_coord[1], new_coord[0]
            new_zoom = st_data['zoom']
        except:
            new_coord = [lat, lng]
            new_zoom = zoom

        placeholder.empty()
        # new session of streamlit
        import streamlit as st

        data = get_json_api(address, new_zoom, new_coord[0], new_coord[1])
        image_base64 = base64.b64decode(data['image_base64'])

        # roof = data['coordinates']
        address_coord = data['address coordinates']
        roof = generate_points(address_coord[0], address_coord[1])
        roof2 = generate_points(address_coord[0] + 0.0002, address_coord[1] + 0.0002)
        building1 = coordinates_2_polygon(roof)
        building2 = coordinates_2_polygon(roof2)
        data_building = [[1, building1, data['surface'], data['solar potential']],
                         [2, building2, data['surface'] + 10, data['solar potential'] + 100]]

        df = gpd.GeoDataFrame(data_building,
                              columns=['ID', 'geometry', 'Area', 'Solar Power Potential'])

        df.crs = {'init': 'epsg:4326'}

        col_map, space1, col_data, space2 = st.columns([4, 0.5, 2, 0.5])

        with col_map:
            m = show_map_roof(df, 18)
            folium_static(m)
        # summary cards
        with col_data:
            st.success('Analysis complete. Your roof has: : ')
            st.markdown('Roof Type : ' + 'Flat')
            card(text='Area', value=data['surface'], symbol='m² available for solar panels',
                 icon="fas fa-chart-area")
            card(text='Solar Power', value=data['solar potential'], symbol='Kw', icon="fas fa-sun")
            card(text='Solar installation', value=data['solar installation'], symbol='panel of 250W',
                 icon="fas fa-solar-panel")
            card(text='Savings', value=(int(electric_bill) - 10) * 12 * 24,
                 symbol='Є estimated net savings over 20 years',
                 icon="fas fa-piggy-bank")

st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
with st.expander('About'):
    st.header('How Project Rooftop Works')
    st.subheader('1  Search for your Home')
    st.info('We use Google Earth imagery to detect and classify your rooftop via a machine learning model.'
            'Then we analyze your roof shape and local weather patterns to create a personalized solar plan.')

    st.subheader('2  Personalize your solar analysis')
    st.info(
        'Adjust your electric bill to fine-tune your savings estimate and the recommended number of solar panels '
        'for your home.')

    st.subheader('3 Solar saving')
    st.info('Solar savings are calculated using roof size and shape, shaded roof areas, local weather, '
            'local electricity prices, solar costs, and estimated incentives over time.')
