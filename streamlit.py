import streamlit as st

from constants import EHR
from ehr_handlers import handle_selected_ehr

st.title('Automated Benchmark Generator')

ehr_option = st.selectbox(
    'Select an EHR',
    [ ehr.value for ehr in EHR ]
)

if ehr_option:
  selected_ehr = EHR[ehr_option]
  handle_selected_ehr(selected_ehr)