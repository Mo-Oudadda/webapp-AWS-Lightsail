import os
import boto3
import streamlit as st
from streamlit_folium import folium_static, st_folium
from interactive_map import *
from style import card
import base64
from config import SAGEMAKER_ENDPOINT


SG_KEY = os.environ['aws_access_key']
SG_SECRET = os.environ['aws_secret_access_key']


@st.experimental_singleton
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
    page_title="SmartRoof Dashboard",
    page_icon="🔆",
    layout="centered",
)

st.write(
    "<style>.main * div.row-widget.stRadio > div{flex-direction:row;}</style>",
    unsafe_allow_html=True,
)
st.title('🔆 SmartRoof')

zoom = 20

address = st.text_input(label='Search for your home. Discover your solar savings potential.',
                        placeholder='Insert your address here...')
st.sidebar.title('Instructions')
st.sidebar.header('1. Search for your home')

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
        st.sidebar.warning('If the red dot not centered in your building, drag a marker from the map tool bar and '
                           'drop it in the centre of your building.')
        col_marker, col_predict = st.columns([6, 1], gap="medium")
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

        with col_marker:
            m_marker = show_map_marker([lat, lng], zoom)
            # Geoson with the new marker coordinates and zoom
            st_data = st_folium(m_marker, height=500, width=700)

    if "load_state" not in st.session_state:
        st.session_state.load_state = False
    ## Prediction Page
    if predict or st.session_state.load_state:
        st.session_state.load_state = True
        try:
            new_coord = st_data['last_active_drawing']['geometry']['coordinates']
            new_coord[0], new_coord[1] = new_coord[1], new_coord[0]
            new_zoom = st_data['zoom']
        except:
            new_coord = [lat, lng]
            new_zoom = zoom

        placeholder.empty()
        # new session of streamlit
        already_detected = False
        import streamlit as st

        # space1, col_map, space2 = st.columns([0.5, 2, 0.5])
        if not already_detected:
            data = get_json_api(address, new_zoom, new_coord[0], new_coord[1])
            image_base64 = base64.b64decode(data['image_base64'])

            # roof = data['coordinates']
            address_coord = data['address coordinates']
            data_building = []
            for roof in data['roofs']:
                roof_geocoord = roof['coordinates']
                building = coordinates_2_polygon(roof_geocoord)
                data_building.append(
                    [
                        roof['Building_ID'], building, roof['area'],
                        roof['potential_electricity_production_in_Kwh'], roof['number_of_panels'],
                        roof['total_investment_in_€TTC'], roof['return_on_investment_in_years'],
                        roof['roof_type']
                    ]
                )

            df = gpd.GeoDataFrame(data_building,
                                  columns=['ID', 'geometry', 'area', 'potential_electricity_production_in_Kwh',
                                           'number_of_panels', 'total_investment_in_€TTC', 'return_on_investment',
                                           'roof_type'])

            df.crs = {'init': 'epsg:4326'}

            # with col_map:

            st.markdown('Map of roof(s) detected')
            m = show_map_roof(df, new_zoom)
            folium_static(m)

            already_detected = True

        # summary cards
        st.sidebar.markdown('Wrong building ? Select another roof to view details.')
        roofID = st.sidebar.selectbox(
            'Select your roof ID ',
            df['ID'].values.tolist(),
            key='my_checkbox'
        )
        st.sidebar.header('2. Personalize your solar analysis')
        st.sidebar.markdown(
            'We use your bill to estimate how much electricity you use based on typical utility rates in your area. ')
        electric_bill = st.sidebar.text_input(label='Your Average Monthly Electric Bill In Є', value=90, )
        st.markdown(
            "<h4 style='text-align: center;'>Fine-tune your information to find out how much you could save.</h1>",
            unsafe_allow_html=True)

        if roofID:
            type_col, area_col = st.columns([5, 5], gap="medium")
            with type_col:
                card(text='Roof type',
                     value=df.iloc[roofID - 1]['roof_type'],
                     symbol='roof',
                     icon="fas fa-home")
            with area_col:
                card(text='Area',
                     value=df.iloc[roofID - 1]['area'],
                     symbol='m² available for solar panels',
                     icon="fas fa-chart-area")
            power_col, panel_col = st.columns([5, 5], gap="medium")
            with power_col:
                card(text='Potential electricity production',
                     value=int(df.iloc[roofID - 1]['potential_electricity_production_in_Kwh']),
                     symbol='Kw',
                     icon="fas fa-sun")
            with panel_col:
                card(text='Number of panels',
                     value=int(df.iloc[roofID - 1]['number_of_panels']),
                     symbol='panel of 2 m²',
                     icon="fas fa-solar-panel")
            invest_col, return_col = st.columns([5, 5], gap="medium")
            with invest_col:
                card(text='Total investment',
                     value=int(df.iloc[roofID - 1]['total_investment_in_€TTC']),
                     symbol='€ TTC',
                     icon="fas fa-piggy-bank")
            with return_col:
                card(text='Return on investment',
                     value=int(df.iloc[roofID - 1]['return_on_investment']),
                     symbol='years',
                     icon="fas fa-hand-holding-usd")

st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
with st.expander('About'):
    st.header('How Project Rooftop Works')
    st.subheader('1  Search for your Home')
    st.info('We use Google Earth imagery to detect and classify your rooftop via a machine learning model. '
            'Then we analyze your roof shape and local weather patterns to create a personalized solar plan.')

    st.subheader('2  Personalize your solar analysis')
    st.info(
        'Adjust your electric bill to fine-tune your savings estimate and the recommended number of solar panels '
        'for your home.')

    st.subheader('3 Solar saving')
    st.info('Solar savings are calculated using roof size and shape, shaded roof areas, local weather, '
            'local electricity prices, solar costs, and estimated incentives over time.')