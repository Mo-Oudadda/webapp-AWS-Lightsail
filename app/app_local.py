import requests
import json
import boto3
import streamlit as st
import base64
from PIL import Image
from config import SAGEMAKER_ENDPOINT

st.sidebar.title('Parameters')
zoom = st.sidebar.slider(label='Zoom level', min_value=10, max_value=21, step=1, value=18)
st.title('Rootftop Detection Dashboard')

address = st.text_input(
    label='Address',
    placeholder='Insert your address here...'
)

if address != '':
    # Local
    try:
        url = "http://localhost:8080/invocations"
        params = b'{"address": "' + address.encode('utf-8') + b'", "zoom":' + str(zoom).encode('utf-8') + b'}'
        params = params.decode()
        response = requests.post(url, data=params)
        data = response.json()
        image_base64 = base64.b64decode(data['image_base64'])

        col1, col2 = st.columns(2)
        col1.subheader('Map of current address')
        col1.image(image_base64)

        col2.subheader('Rooftop metadata')
        col2.json({
            'surface': data['Surface'],
            'solar potential': data['solar potential'],
        })
    except Exception as e:
        st.error(f'Could not retrieve map from address. Details: {e}')