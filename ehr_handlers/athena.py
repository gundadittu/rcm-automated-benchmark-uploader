import pandas as pd
import streamlit as st
import re

def compute_athena_stats(
  data: pd.DataFrame,
  insurance_payment_col: str,
  cpt_code_col: str,
  primary_ins_col: str,
  secondary_ins_col: str,
  ins_col: str,
  claim_id_col: str
):
  with st.spinner('Generating Benchmark...'):
    st.header('Generated Benchmark Results')

    data[insurance_payment_col] = data[insurance_payment_col].abs()
    data[cpt_code_col] = data[cpt_code_col].str.split(',').str[0]

    data_filtered = data[data[primary_ins_col] != '*SELF PAY*']

    # ------ Calculate Total Payer Payments ------
    total_insurance_payments_filtered = data[(data[ins_col] != '*SELF PAY*')]
    total_insurance_payments_filtered_sum = total_insurance_payments_filtered[insurance_payment_col].sum()

    total_patient_payments_filtered = data_filtered[data_filtered[ins_col] == '*SELF PAY*'][insurance_payment_col].sum()
    total_unique_visits_filtered = data_filtered[claim_id_col].nunique()

    st.write("Total Insurance Payments " + str("${:,.2f}".format(total_insurance_payments_filtered_sum)))
    st.write("Total Patient Payments " + str("${:,.2f}".format(total_patient_payments_filtered)))
    st.write("Total Encounters " + str(total_unique_visits_filtered))

    # ------ Calculate Average Payer Payments ------
    filtered_df_primary = data_filtered[data_filtered[ins_col] == data_filtered[primary_ins_col]]
    sum_insurance_payments = filtered_df_primary.groupby([claim_id_col]).agg({ insurance_payment_col : 'sum'}).reset_index()
    mean_insurance_payments = sum_insurance_payments[insurance_payment_col].mean()
    mean_insurance_payments
    st.write("Average Primary Payments " + str("${:,.2f}".format(mean_insurance_payments)))

    filtered_df_secondary = data_filtered[data_filtered[ins_col] != data_filtered[primary_ins_col]]
    filtered_df_secondary = filtered_df_secondary[data[secondary_ins_col] != '*SELF PAY*']

    sum_insurance_payments_secondary  = filtered_df_secondary.groupby([claim_id_col]).agg({ insurance_payment_col : 'sum'}).reset_index()
    mean_insurance_payments_secondary  = sum_insurance_payments_secondary [insurance_payment_col].mean()
    mean_insurance_payments_secondary
    st.write("Average Secondary Payments " + str("${:,.2f}".format(mean_insurance_payments_secondary)))

    total_patient_payments_filtered = total_patient_payments_filtered
    total_unique_visits_filtered = data_filtered[claim_id_col].nunique()
    st.write("Average Patients Payments " + str("${:,.2f}".format(total_patient_payments_filtered/total_unique_visits_filtered)))

    # ----- Calculate Primary Insurance Metrics ----
    # Function to remove text within parentheses
    def remove_parentheses_text(s):
        return re.sub(r'\(.*\)', '', s).strip()

    grouped_by_claim_cpt = filtered_df_primary.groupby([claim_id_col, ins_col]).agg({insurance_payment_col: 'sum'}).reset_index()
    grouped_by_claim_cpt[ins_col] = grouped_by_claim_cpt[ins_col].apply(remove_parentheses_text)
    grouped_by_cpt_again = grouped_by_claim_cpt.groupby(ins_col)

    cpt_summary_again = pd.DataFrame({
        'Total Payout': grouped_by_cpt_again[insurance_payment_col].sum(),
        'Occurrences': grouped_by_cpt_again.size(),
        'Average Payout': grouped_by_cpt_again[insurance_payment_col].mean(),
    })

    total_rows_cpt_again = grouped_by_claim_cpt.shape[0]
    cpt_summary_again['Percentage of Payout'] = cpt_summary_again['Total Payout'] / cpt_summary_again['Total Payout'].sum()

    # Sort by total payout
    cpt_summary_again = cpt_summary_again.sort_values('Occurrences', ascending=False)

    st.write('Top Primary Payers')
    st.write(cpt_summary_again)

    # ----- Calculate Secondary Insurance Metrics ----
    # Take out selfpay in secondary
    grouped_by_claim_cpt = grouped_by_claim_cpt[grouped_by_claim_cpt[ins_col] != '*SELF PAY*']

    # Function to remove text within parentheses
    def remove_parentheses_text(s):
        return re.sub(r'\(.*\)', '', s).strip()

    grouped_by_claim_cpt = filtered_df_secondary.groupby([claim_id_col, ins_col]).agg({ insurance_payment_col : 'sum'}).reset_index()
    grouped_by_claim_cpt[ins_col] = grouped_by_claim_cpt[ins_col].apply(remove_parentheses_text)


    grouped_by_cpt_again = grouped_by_claim_cpt.groupby(ins_col)

    cpt_summary_again = pd.DataFrame({
        'Total Payout': grouped_by_cpt_again[insurance_payment_col].sum(),
        'Occurrences': grouped_by_cpt_again.size(),
        'Average Payout': grouped_by_cpt_again[insurance_payment_col].mean(),
    })

    total_rows_cpt_again = grouped_by_claim_cpt.shape[0]
    cpt_summary_again['Percentage of Payout'] = cpt_summary_again['Total Payout'] / cpt_summary_again['Total Payout'].sum()
    # Sort by total payout
    cpt_summary_again = cpt_summary_again.sort_values('Occurrences', ascending=False)

    st.write('Top Secondary Payers')
    st.write(cpt_summary_again)

    # ------ Primary Payer CPT Analysis -------
    grouped_by_claim_cpt = filtered_df_primary.groupby([claim_id_col, cpt_code_col]).agg({ insurance_payment_col : 'sum'}).reset_index()

    grouped_by_cpt_again = grouped_by_claim_cpt.groupby(cpt_code_col)

    cpt_summary_again = pd.DataFrame({
        'Total Payout': grouped_by_cpt_again[insurance_payment_col].sum(),
        'Occurrences': grouped_by_cpt_again.size(),
        'Average Payout': grouped_by_cpt_again[insurance_payment_col].mean(),
    })

    total_rows_cpt_again = grouped_by_claim_cpt.shape[0]
    cpt_summary_again['Percentage of Payout'] = cpt_summary_again['Total Payout'] / cpt_summary_again['Total Payout'].sum()

    # Sort by total payout
    cpt_summary_again = cpt_summary_again.sort_values('Occurrences', ascending=False)

    st.write('Primary Insurance CPT Analysis')
    st.write(cpt_summary_again)

    # ----- Secondary Payer CPT Analysis ----- 
    # Take out selfpay in secondary
    filtered_df_secondary = filtered_df_secondary[filtered_df_secondary[ins_col] != '*SELF PAY*']

    grouped_by_claim_cpt = filtered_df_secondary.groupby([claim_id_col, cpt_code_col]).agg({ insurance_payment_col : 'sum'}).reset_index()
    
    grouped_by_cpt_again = grouped_by_claim_cpt.groupby(cpt_code_col)

    cpt_summary_again = pd.DataFrame({
        'Total Payout': grouped_by_cpt_again[insurance_payment_col].sum(),
        'Occurrences': grouped_by_cpt_again.size(),
        'Average Payout': grouped_by_cpt_again[insurance_payment_col].mean(),
    })

    total_rows_cpt_again = grouped_by_claim_cpt.shape[0]
    cpt_summary_again['Percentage of Payout'] = cpt_summary_again['Total Payout'] / cpt_summary_again['Total Payout'].sum()

    # Sort by total payout
    cpt_summary_again = cpt_summary_again.sort_values('Occurrences', ascending=False)

    st.write('Secondary Insurance CPT Analysis')
    st.write(cpt_summary_again)

    # ------ Payment & Encounter Segments ------
    # Get number of encounters
    insurance_primary = filtered_df_primary.groupby([claim_id_col]).agg({insurance_payment_col: 'sum'}).reset_index()
    insurance_secondary = filtered_df_secondary.groupby([claim_id_col]).agg({insurance_payment_col: 'sum'}).reset_index()
    patient_pay = data_filtered[data_filtered[ins_col] == '*SELF PAY*']
    self_pay = data[data[primary_ins_col] == '*SELF PAY*'].groupby([claim_id_col]).agg({insurance_payment_col: 'sum'}).reset_index()

    primary_num = len(insurance_primary)
    secondary_num = len(insurance_secondary)
    selfpay_num = len(self_pay)
    patient_num_no_self_pay = len(patient_pay)

    # Get total $ value
    primary_sum = insurance_primary[insurance_payment_col].sum()
    secondary_sum = insurance_secondary[insurance_payment_col].sum()
    self_pay_payments_sum = self_pay[insurance_payment_col].sum()
    patient_payment_sum = patient_pay[insurance_payment_col].sum()

    st.write("Number of primary encounters: " + str(primary_num))
    st.write("Number of secondary encounters: " + str(secondary_num))
    st.write("Number of self-pay encounters: " + str(selfpay_num))
    st.write("Number of patient encounters: " + str(patient_num_no_self_pay))

    st.write("Total primary payments: " + str("${:,.2f}".format(primary_sum)))
    st.write("Total secondary payments: " + str("${:,.2f}".format(secondary_sum)))
    st.write("Total self-pay payments: " + str("${:,.2f}".format(self_pay_payments_sum)))
    st.write("Total patient payments: " + str("${:,.2f}".format(patient_payment_sum)))

    st.balloons()

def handle_athena():
  uploaded_file = st.file_uploader("Upload Transaction Activity", type='csv')
  
  if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
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
      'Which column should be used to calculate Payment?',
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
      compute_athena_stats(
        data=data,
        insurance_payment_col=insurance_payout_col,
        cpt_code_col=cpt_col,
        primary_ins_col=primary_col,
        secondary_ins_col=secondary_col,
        ins_col=insurer_col,
        claim_id_col=claim_no_col
      )