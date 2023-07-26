import pandas as pd
import streamlit as st
import re
from PIL import Image

def compute_amd_stats(
  data: pd.DataFrame,
  insurance_payment_col: str,
  patient_payment_col: str,
  cpt_code_col: str,
  primary_ins_col: str,
  secondary_ins_col: str,
  ins_col: str,
  claim_id_col: str
):
  with st.spinner('Generating Benchmark...'):
    st.header('Generated Benchmark Results')
    
    # Remove dollar signs, commas, and parentheses
    data[insurance_payment_col] = data[insurance_payment_col].replace({'\$': '', ',': '', '\(': '-', '\)': ''}, regex=True).astype(float)
    data[patient_payment_col] = data[patient_payment_col].replace({'\$': '', ',': '', '\(': '-', '\)': ''}, regex=True).astype(float)

    # Remove self-pay
    data_filtered = data[data[primary_ins_col].apply(lambda x: 'self' not in str(x).lower())]
    # data_filtered = data[data[primary_ins_col] != 'SELF PAY']
  
    # ---- Calculate Total Payment Metrics ----
    total_insurance_payments_filtered = data_filtered[insurance_payment_col].sum()
    total_patient_payments_filtered = data_filtered[patient_payment_col].sum()
    total_unique_visits_filtered = data_filtered[claim_id_col].nunique()
    st.write("Total Insurance Payments " + str("${:,.2f}".format(total_insurance_payments_filtered)))
    st.write("Total Patient Payments " + str("${:,.2f}".format(total_patient_payments_filtered)))
    st.write("Total Encounters " + str(total_unique_visits_filtered))

    # ---- Calculate Avg Payment Metrics ----
    filtered_df_primary = data_filtered[data_filtered[primary_ins_col] == data_filtered[ins_col]]
    sum_insurance_payments = filtered_df_primary.groupby([claim_id_col]).agg({insurance_payment_col: 'sum'}).reset_index()
    mean_insurance_payments = sum_insurance_payments[insurance_payment_col].mean()
    st.write("Average Primary Payments " + str("${:,.2f}".format(mean_insurance_payments)))

    filtered_df_secondary = data_filtered[data_filtered[secondary_ins_col] == data_filtered[ins_col]]
    sum_insurance_payments_secondary  = filtered_df_secondary.groupby([claim_id_col]).agg({insurance_payment_col: 'sum'}).reset_index()
    mean_insurance_payments_secondary  = sum_insurance_payments_secondary [insurance_payment_col].mean()
    st.write("Average Secondary Payments " + str("${:,.2f}".format(mean_insurance_payments_secondary)))

    total_patient_payments_filtered = data_filtered[patient_payment_col].sum()
    total_unique_visits_filtered = data_filtered[claim_id_col].nunique()
    st.write("Average Patients Payments " + str("${:,.2f}".format(total_patient_payments_filtered/total_unique_visits_filtered)))

    # ---- Calculate Top Primary Payer Metrics ----
    grouped_by_claim_payer = filtered_df_primary.groupby([claim_id_col, ins_col]).agg({insurance_payment_col: 'sum'}).reset_index()

    grouped_by_payer_again = grouped_by_claim_payer.groupby(ins_col)

    payer_summary_again = pd.DataFrame({
        'Total Payout': grouped_by_payer_again[insurance_payment_col].sum(),
        'Occurrences': grouped_by_payer_again.size(),
        'Average Payout': grouped_by_payer_again[insurance_payment_col].mean(),
    })

    total_rows_payer_again = grouped_by_claim_payer.shape[0]
    payer_summary_again['Percentage of All Rows'] = payer_summary_again['Occurrences'] / total_rows_payer_again * 100

    # Sort by total payout
    payer_summary_again = payer_summary_again.sort_values('Occurrences', ascending=False)

    st.write("Top Primary Payer Metrics")
    st.write(payer_summary_again)

    # ---- Calculate Top Secondary Payer Metrics ----
    grouped_by_claim_payer = filtered_df_secondary.groupby([claim_id_col, ins_col]).agg({insurance_payment_col: 'sum'}).reset_index()

    grouped_by_payer_again = grouped_by_claim_payer.groupby(ins_col)

    payer_summary_again = pd.DataFrame({
        'Total Payout': grouped_by_payer_again[insurance_payment_col].sum(),
        'Occurrences': grouped_by_payer_again.size(),
        'Average Payout': grouped_by_payer_again[insurance_payment_col].mean(),
    })

    total_rows_payer_again = grouped_by_claim_payer.shape[0]
    payer_summary_again['Percentage of All Rows'] = (payer_summary_again['Occurrences'] / total_rows_payer_again) * 100

    # Sort by total payout
    payer_summary_again = payer_summary_again.sort_values('Occurrences', ascending=False)

    st.write("Top Secondary Payer Metrics")
    st.write(payer_summary_again)

    # ---- Calculate Primary CPT Metrics ----
    grouped_by_claim_cpt = filtered_df_primary.groupby([claim_id_col, cpt_code_col]).agg({insurance_payment_col: 'sum'}).reset_index()

    grouped_by_cpt_again = grouped_by_claim_cpt.groupby(cpt_code_col)

    cpt_summary_again = pd.DataFrame({
        'Total Payout': grouped_by_cpt_again[insurance_payment_col].sum(),
        'Occurrences': grouped_by_cpt_again.size(),
        'Average Payout': grouped_by_cpt_again[insurance_payment_col].mean(),
    })

    total_rows_cpt_again = grouped_by_claim_cpt.shape[0]
    cpt_summary_again['Percentage of All Rows'] = cpt_summary_again['Occurrences'] / total_rows_cpt_again * 100

    # Sort by total payout
    cpt_summary_again = cpt_summary_again.sort_values('Occurrences', ascending=False)

    st.write("Primary CPT Analysis")
    st.write(cpt_summary_again)

    # ---- Calculate Secondary CPT Metrics ----
    grouped_by_claim_cpt = filtered_df_secondary.groupby([claim_id_col, cpt_code_col]).agg({insurance_payment_col: 'sum'}).reset_index()

    grouped_by_cpt_again = grouped_by_claim_cpt.groupby(cpt_code_col)

    cpt_summary_again = pd.DataFrame({
        'Total Payout': grouped_by_cpt_again[insurance_payment_col].sum(),
        'Occurrences': grouped_by_cpt_again.size(),
        'Average Payout': grouped_by_cpt_again[insurance_payment_col].mean(),
    })

    total_rows_cpt_again = grouped_by_claim_cpt.shape[0]
    cpt_summary_again['Percentage of All Rows'] = cpt_summary_again['Occurrences'] / total_rows_cpt_again * 100

    # Sort by total payout
    cpt_summary_again = cpt_summary_again.sort_values('Occurrences', ascending=False)

    st.write("Secondary CPT Analysis")
    st.write(cpt_summary_again)

    # ---- Calculate Payment & Encounter Segment Metrics ----
    insurance_primary = filtered_df_primary.groupby([claim_id_col]).agg({insurance_payment_col: 'sum'}).reset_index()
    insurance_secondary = filtered_df_secondary.groupby([claim_id_col]).agg({insurance_payment_col: 'sum'}).reset_index()
    patient_pay = data_filtered[data_filtered[patient_payment_col] > 0].groupby([claim_id_col]).agg({patient_payment_col: 'sum'}).reset_index()
    self_pay = data[data[primary_ins_col].apply(lambda x: 'self' in str(x).lower())]

    primary_num = len(insurance_primary)
    secondary_num = len(insurance_secondary)
    selfpay_num = len(self_pay)
    patient_num_no_self_pay = len(patient_pay)

    # Get total $ value
    primary_sum = insurance_primary[insurance_payment_col].sum()
    secondary_sum = insurance_secondary[insurance_payment_col].sum()
    self_pay_payments_sum = self_pay[patient_payment_col].sum()
    patient_payment_sum = patient_pay[patient_payment_col].sum()

    st.write("Number of primary encounters: " + str(primary_num))
    st.write("Number of secondary encounters: " + str(secondary_num))
    st.write("Number of self-pay encounters: " + str(selfpay_num))
    st.write("Number of patient encounters: " + str(patient_num_no_self_pay))

    st.write("Total primary payments: " + str(primary_sum))
    st.write("Total secondary payments: " + str(secondary_sum))
    st.write("Total self-pay payments: " + str(self_pay_payments_sum))
    st.write("Total patient payments: " + str(patient_payment_sum))

def handle_amd():
  uploaded_file = st.file_uploader("Upload Transaction Details", type='csv')

  with st.expander("How to download the Transaction Details report"):
    st.write("Log into to the AMD PM (NOT EHR) -> Reports -> Financial Totals -> Transaction Details")
    image1 = Image.open('imgs/amd-1.png')
    st.image(image1)
    
    st.write("Set your required \"Low Date\" and \"High Date\"")

    st.write("Select \"Include Charges\" and \"Include Payments\"")

    st.write("Select \"Export on Run\" and set it to \"CSV\"")
  
  if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    
    # Remove first two rows and update the columns
    data = data.iloc[2:]
    data.columns = data.iloc[0]
    data = data.iloc[1:]

    st.write(data)

    primary_col = st.selectbox(
      'Which column should be used for the Primary Insurer?',
      data.columns
    )

    secondary_col = st.selectbox(
      'Which column should be used for the Secondary Insurer?',
      data.columns
    )

    insurer_col = st.selectbox(
      'Which column should be used for the Insurer?',
      data.columns
    )

    insurance_payout_col = st.selectbox(
      'Which column should be used to calculate Insurance Payment?',
      data.columns
    )

    patient_payment_col = st.selectbox(
      'Which column should be used to calculate Patient Payment?',
      data.columns
    )

    claim_no_col = st.selectbox(
      'Which column should be used to identify the claim number?',
      data.columns
    )

    cpt_col = st.selectbox(
      'Which column should be used to identify the CPT Code?',
      data.columns
    )

    if st.button('Generate Benchmark'):
      compute_amd_stats(
        data=data,
        insurance_payment_col=insurance_payout_col,
        patient_payment_col=patient_payment_col,
        cpt_code_col=cpt_col,
        primary_ins_col=primary_col,
        secondary_ins_col=secondary_col,
        ins_col=insurer_col,
        claim_id_col=claim_no_col
      )