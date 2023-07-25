import streamlit as st

from constants import EHR
from ehr_handlers import handle_selected_ehr

st.title('Automated Revenue Benchmark Generator')
st.write('This tool only helps generate a benchmark. It does NOT upload your benchmark for you.')
st.write('Please upload your benchmark here afterwards: https://athelas.retool.com/apps/784f8256-1898-11ee-8939-2f7149adaf6a/Revenue%20Ops%20Benchmark%20Uploader')

ehr_option = st.selectbox(
    'Select an EHR',
    [ ehr.value for ehr in EHR ]
)

if ehr_option:
  selected_ehr = EHR[ehr_option]
  handle_selected_ehr(selected_ehr)