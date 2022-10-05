import os
import json
import boto3
import streamlit as st
import base64
from config import SAGEMAKER_ENDPOINT

SG_KEY = os.environ['aws_access_key']
SG_SECRET = os.environ['aws_secret_access_key']

st.sidebar.title('Parameters')
zoom = st.sidebar.slider(label='Zoom level', min_value=10, max_value=21, step=1, value=18)
st.title('Rootftop Detection Dashboard')

address = st.text_input(
    label='Address',
    placeholder='Insert your address here...'
)

if address != '':
    try:
        runtime = boto3.Session().client(
            'sagemaker-runtime',
            region_name="eu-west-3", 
            aws_access_key_id = SG_KEY,
            aws_secret_access_key = SG_SECRET
        )

        response = runtime.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT,
            ContentType='application/json',
            Body=b'{"address": "' + address.encode('utf-8') + b'", "zoom":' + str(zoom).encode('utf-8') + b'}'
        )['Body'].read().decode()

        formatted_response = json.loads(response)
        image_base64 = base64.b64decode(formatted_response['image_base64'])


        col1, col2 = st.columns(2)
        col1.subheader('Map of current address')
        col1.image(image_base64)

        col2.subheader('Rooftop metadata')
        col2.json({
            'surface': formatted_response['Surface'],
            'solar potential': formatted_response['solar potential'],
        })
    except Exception as e:
        st.error(f'Could not retrieve map from address. Details: {e}')
