from .ecw import handle_ecw
from constants import EHR

def handle_selected_ehr(ehr: EHR):
  if ehr == EHR.ECW:
    handle_ecw()
  else:
    st.write("Selected EHR is not supported yet.")
