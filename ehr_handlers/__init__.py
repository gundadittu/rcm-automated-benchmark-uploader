import streamlit as st

from .ecw import handle_ecw
from .athena import handle_athena
from .amd import handle_amd

from constants import EHR

def handle_selected_ehr(ehr: EHR):
  if ehr == EHR.ECW:
    handle_ecw()
  elif ehr == EHR.ATHENA:
    handle_athena()
  elif ehr == EHR.AMD:
    handle_amd()
  else:
    st.write("Selected EHR is not supported yet.")
