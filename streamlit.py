import streamlit as st

from constants import EHR
from ehr_handlers.ecw import handle_ecw

st.title('Automated Benchmark Generator')

option = st.selectbox(
    'Select an EHR',
    [ ehr.value for ehr in EHR ]
)

selected_ehr = EHR[option]
st.write('You selected:', selected_ehr.value)

benchmark_container = st.container()

with benchmark_container:
  def handle_selected_ehr(ehr: EHR):
    if ehr == EHR.ECW:
      handle_ecw()
    else:
      st.write("Selected EHR is not supported yet.")
  
  handle_selected_ehr(selected_ehr)