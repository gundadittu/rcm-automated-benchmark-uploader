from .ecw import handle_ecw
from .athena import handle_athena

from constants import EHR

def handle_selected_ehr(ehr: EHR):
  if ehr == EHR.ECW:
    handle_ecw()
  elif ehr == EHR.ATHENA:
    handle_athena()
  else:
    st.write("Selected EHR is not supported yet.")
