import pandas as pd
import streamlit as st
import numpy as np
import warnings
import re

def calculate_top_secondary_payers(df_secondary_matched, claim_no_col, insurance_payout_col):
    # Combine rows that have the same "Claim No"
    grouped_by_secondary_claim = df_secondary_matched.groupby([claim_no_col, 'Insurance Matched']).agg({
        insurance_payout_col: 'sum'
      }).reset_index()
    
    # Group by 'Insurance' again
    grouped_by_secondary_insurance_again = grouped_by_secondary_claim.groupby('Insurance Matched')
    
    # Calculate total payout, number of occurrences, and average payout for each insurance company
    secondary_insurance_summary_again = pd.DataFrame({
        'Insurance Payout': grouped_by_secondary_insurance_again[insurance_payout_col].sum(),
        'Occurrences': grouped_by_secondary_insurance_again.size(),
        'Average Payout': grouped_by_secondary_insurance_again[insurance_payout_col].mean()
    })
    
    # Calculate percentage of all rows
    secondary_insurance_summary_again['Percentage of Payout'] = secondary_insurance_summary_again['Insurance Payout'] / secondary_insurance_summary_again['Insurance Payout'].sum()
    
    # Sort by total payout
    secondary_insurance_summary_again = secondary_insurance_summary_again.sort_values('Percentage of Payout', ascending=False)

    st.write("Top Secondary Payers")
    st.write(secondary_insurance_summary_again)
    return secondary_insurance_summary_again


def calculate_top_primary_payers(df_primary_matched, claim_no_col, insurance_payout_col):
    # Combine rows that have the same "Claim No"
    grouped_by_primary_claim = df_primary_matched.groupby([claim_no_col, 'Insurance Matched']).agg({
      insurance_payout_col: 'sum'
    }).reset_index()
    
    # Group by 'Insurance' again
    grouped_by_primary_insurance_again = grouped_by_primary_claim.groupby('Insurance Matched')
    
    # Calculate total payout, number of occurrences, and average payout for each insurance company
    primary_insurance_summary_again = pd.DataFrame({
        'Insurance Payout': grouped_by_primary_insurance_again[insurance_payout_col].sum(),
        'Occurrences': grouped_by_primary_insurance_again.size(),
        'Average Payout': grouped_by_primary_insurance_again[insurance_payout_col].mean()
    })
    
    # Calculate percentage of all rows
    primary_insurance_summary_again['Percentage of Payout'] = primary_insurance_summary_again['Insurance Payout'] / primary_insurance_summary_again['Insurance Payout'].sum()
    
    # Sort by total payout
    primary_insurance_summary_again = primary_insurance_summary_again.sort_values('Percentage of Payout', ascending=False)

    st.write("Top Primary Payers")
    st.write(primary_insurance_summary_again)
    return primary_insurance_summary_again


def calculate_primary_cpt_payments(
  df_no_self_pay_no_patient: pd.DataFrame,
  insurance_payout_col: str,
  claim_no_col: str,
  cpt_col: str
):
    # Combine rows that have the same "Claim No"
    grouped_by_primary_claim_cpt = df_no_self_pay_no_patient[df_no_self_pay_no_patient['Primary Insurance Matched'] == df_no_self_pay_no_patient['Insurance Matched']].groupby([claim_no_col, cpt_col]).agg({
      insurance_payout_col: 'sum'
    }).reset_index()
    
    # Group by 'CPT Code' again
    grouped_by_primary_cpt_again = grouped_by_primary_claim_cpt.groupby(cpt_col)
    
    # Calculate total payout, number of occurrences, and average payout for each CPT Code
    primary_cpt_summary_again = pd.DataFrame({
        'Total Payout': grouped_by_primary_cpt_again[insurance_payout_col].sum(),
        'Occurrences': grouped_by_primary_cpt_again.size(),
        'Average Payout': grouped_by_primary_cpt_again[insurance_payout_col].mean(),
    })
    
    # Calculate percentage of all rows
    primary_cpt_summary_again['Percentage of Payout'] = primary_cpt_summary_again['Total Payout'] / primary_cpt_summary_again['Total Payout'].sum()
    
    # Sort by total payout
    primary_cpt_summary_again = primary_cpt_summary_again.sort_values('Percentage of Payout', ascending=False)
    st.write('Primary CPT Code Analysis')
    st.write(primary_cpt_summary_again)
    return primary_cpt_summary_again

def calculate_secondary_cpt_payments(
  df_no_self_pay_no_patient: pd.DataFrame,
  insurance_payout_col: str,
  claim_no_col: str,
  cpt_col: str
):
    # Combine rows that have the same "Claim No"
    grouped_by_secondary_claim_cpt = df_no_self_pay_no_patient[df_no_self_pay_no_patient['Primary Insurance Matched'] != df_no_self_pay_no_patient['Insurance Matched']].groupby([claim_no_col, cpt_col]).agg({
      insurance_payout_col: 'sum'
    }).reset_index()
    
    # Group by 'CPT Code' again
    grouped_by_secondary_cpt_again = grouped_by_secondary_claim_cpt.groupby(cpt_col)
    
    # Calculate total payout, number of occurrences, and average payout for each CPT Code
    secondary_cpt_summary_again = pd.DataFrame({
        'Total Payout': grouped_by_secondary_cpt_again[insurance_payout_col].sum(),
        'Occurrences': grouped_by_secondary_cpt_again.size(),
        'Average Payout': grouped_by_secondary_cpt_again[insurance_payout_col].mean(),
    })
    
    # Calculate percentage of all rows
    secondary_cpt_summary_again['Percentage of Payout'] = secondary_cpt_summary_again['Total Payout'] / secondary_cpt_summary_again['Total Payout'].sum()
    
    # Sort by total payout
    secondary_cpt_summary_again = secondary_cpt_summary_again.sort_values('Percentage of Payout', ascending=False)
    
    st.write('Secondary CPT Code Analysis')
    st.write(secondary_cpt_summary_again)
    return secondary_cpt_summary_again

def compute_ecw_stats(
  df: pd.DataFrame,
  insurer_col: str,
  primary_ins_col: str,
  total_payment_col: str,
  insurance_payout_col: str,
  patient_payment_col: str,
  claim_no_col: str,
  cpt_col: str
):
  with st.spinner("Generating Benchmark..."):
    st.header('Generated Benchmark Results')  

    df[insurance_payout_col] = df[insurance_payout_col].replace({'\$': '', ',': ''}, regex=True).astype(float)
    df[patient_payment_col] = df[patient_payment_col].replace({'\$': '', ',': ''}, regex=True).astype(float)
    df[total_payment_col] = df[total_payment_col].replace({'\$': '', ',': ''}, regex=True).astype(float)

    # ----- Calculate Total Payment Metrics ---
    
    # Exclude rows where Primary Insurance is "Self Pay"
    df_no_self_pay = df[df[primary_ins_col] != 'Self Pay']

    # Total Insurance Payments excluding Self Pay
    total_insurance_payments_no_self_pay = df_no_self_pay[insurance_payout_col].sum()

    # Total Patient Payment excluding Self Pay
    total_patient_payment_no_self_pay = df_no_self_pay[patient_payment_col].sum()

    # Number of unique "Claim No" excluding Self Pay
    num_unique_claims_no_self_pay = df_no_self_pay[claim_no_col].nunique()

    st.write("Total Insurance Payments " + str("${:,.2f}".format(total_insurance_payments_no_self_pay)))
    st.write("Total Patient Payments " + str("${:,.2f}".format(total_patient_payment_no_self_pay)))
    st.write("Total Encounters " + str(num_unique_claims_no_self_pay))

    # ----- Calculate Avg Payment Metrics ---

    # Ignore warnings
    warnings.filterwarnings('ignore')
    # Filter out 'Patient' from the Insurance column
    df_no_self_pay_no_patient = df_no_self_pay[df_no_self_pay[insurer_col] != 'Patient']

    # Convert strings to lowercase, remove 'zz' and spaces
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.applymap(lambda s: s.lower().replace("zz", "").replace(" ", "") if isinstance(s, str) else s)

    # Remove parentheses and their contents using regex
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.applymap(lambda x: re.sub(r'\(.*\)', '', str(x)) if isinstance(x, str) else x)

    df_no_self_pay_no_patient = df_no_self_pay_no_patient.applymap(lambda x: "unitedbehavioralhealth" if isinstance(x, str) and "ubh" in x else x)
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.applymap(lambda x: x.replace("ppo", "").replace("hmo", "") if isinstance(x, str) else x)
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.applymap(lambda x: "blueshield" if isinstance(x, str) and "blueshield" in x else x)
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.applymap(lambda x: "tricare" if isinstance(x, str) and "tricare" in x else x)
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.applymap(lambda x: "adventist" if isinstance(x, str) and "adventist" in x else x)
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.applymap(lambda x: "cigna" if isinstance(x, str) and "cigna" in x else x)
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.applymap(lambda x: "aetna" if isinstance(x, str) and "aetna" in x else x)
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.applymap(lambda x: "humana" if isinstance(x, str) and "humana" in x else x)

    df_no_self_pay_no_patient = df_no_self_pay_no_patient.replace(to_replace=r'united', value='umr', regex=True)
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.replace(to_replace=r'.*umr.*', value='umr', regex=True)
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.replace(to_replace=r'.*anthem.*', value='blue cross', regex=True)
    df_no_self_pay_no_patient = df_no_self_pay_no_patient.replace(to_replace=r'.*blue.*', value='blue cross', regex=True)

    def ngram_similarity(str1, str2, n=3):
        str1_ngrams = set([str1[i:i+n] for i in range(len(str1)-(n-1))])
        str2_ngrams = set([str2[i:i+n] for i in range(len(str2)-(n-1))])
        return len(str1_ngrams & str2_ngrams) / len(str1_ngrams | str2_ngrams)

    # Create a list of unique insurance names
    unique_insurance_names = pd.concat([df_no_self_pay_no_patient[primary_ins_col], df_no_self_pay_no_patient[insurer_col]]).unique()

    # Create a dictionary to store the matched names
    matched_names = {}

    # For each unique insurance name, find the best match in the list of unique names
    for name in unique_insurance_names:
        best_match = None
        for candidate in unique_insurance_names:
            if candidate == name:
                continue
            if ngram_similarity(name, candidate) == 0.7:
                best_match = candidate
                break

        if best_match is not None:
            matched_names[name] = best_match

    # Map the matched names back to the original data if null
    df_no_self_pay_no_patient['Primary Insurance Matched'] = df_no_self_pay_no_patient[primary_ins_col].map(matched_names).fillna(df_no_self_pay_no_patient['Primary Insurance'])
    df_no_self_pay_no_patient['Insurance Matched'] = df_no_self_pay_no_patient[insurer_col].map(matched_names).fillna(df_no_self_pay_no_patient['Insurance'])


    df_no_self_pay_no_patient = df_no_self_pay_no_patient[df_no_self_pay_no_patient['Insurance Matched'] != 'patient'];

    # Group by Claim No, calculate the sum of Insurance Payments for each group
    grouped_insurance_payments_matched = df_no_self_pay_no_patient.groupby([claim_no_col, 'Primary Insurance Matched', 'Insurance Matched'])[insurance_payout_col].sum().reset_index()

    # Create two dataframes for primary and secondary insurance payments
    df_primary_matched = grouped_insurance_payments_matched[grouped_insurance_payments_matched['Primary Insurance Matched'] == grouped_insurance_payments_matched['Insurance Matched']]
    df_secondary_matched = grouped_insurance_payments_matched[grouped_insurance_payments_matched['Primary Insurance Matched'] != grouped_insurance_payments_matched['Insurance Matched']]

    # Calculate the average primary and secondary insurance payments
    avg_primary_insurance_payment_matched = df_primary_matched[insurance_payout_col].mean()
    avg_secondary_insurance_payment_matched = df_secondary_matched[insurance_payout_col].mean()

    st.write("Average Primary " + str("${:,.2f}".format(avg_primary_insurance_payment_matched)))
    st.write("Average Secondary " + str("${:,.2f}".format(avg_secondary_insurance_payment_matched)))

    total_patient_payments = df_no_self_pay[patient_payment_col].sum()

    # Calculate number of unique claim numbers
    unique_claim_numbers = df_no_self_pay[claim_no_col].nunique()

    # Divide total patient payments by unique claim numbers
    avg_patient_payment = total_patient_payments / unique_claim_numbers
    
    st.write("Average Patient " + str("${:,.2f}".format(avg_patient_payment)))

    # ----- Calculate Top Primary Payer Metrics ---
    calculate_top_primary_payers(df_primary_matched, claim_no_col, insurance_payout_col)

    # ----- Calculate Top Secondary Payer Metrics ---
    calculate_top_secondary_payers(df_secondary_matched, claim_no_col, insurance_payout_col)

    # ----- Calculate Primary CPT Payment Metrics ---
    calculate_primary_cpt_payments(df_no_self_pay_no_patient=df_no_self_pay_no_patient, insurance_payout_col=insurance_payout_col, claim_no_col=claim_no_col, cpt_col=cpt_col)

    # ----- Calculate Secondary CPT Payment Metrics ---
    calculate_secondary_cpt_payments(df_no_self_pay_no_patient=df_no_self_pay_no_patient, insurance_payout_col=insurance_payout_col, claim_no_col=claim_no_col, cpt_col=cpt_col)

    # ----- Calculate Payment & Encounter Segments ----- 
    # Get number of encounters
    primary_num = len(df_primary_matched[insurance_payout_col])
    secondary_num = len(df_secondary_matched[insurance_payout_col])
    selfpay_num = len(df[df[primary_ins_col] == 'Self Pay'])
    df_no_self_pay_patient = df[(df[insurer_col] == 'Patient') & (df[primary_ins_col] != 'Self Pay')].groupby([claim_no_col]).agg({total_payment_col: 'sum'}).reset_index()
    patient_num_no_self_pay = df_no_self_pay_patient.groupby(claim_no_col).size().shape[0]


    # Get total $ value
    primary_sum = df_primary_matched[insurance_payout_col].sum()
    secondary_sum = df_secondary_matched[insurance_payout_col].sum()
    self_pay_payments_sum = df[df[primary_ins_col] == 'Self Pay'][total_payment_col].sum()
    patient_payment_sum = df[df[primary_ins_col] != 'Self Pay'][patient_payment_col].sum()
    
    st.write("Number of primary encounters: " + str(primary_num))
    st.write("Number of secondary encounters: " + str(secondary_num))
    st.write("Number of self-pay encounters: " + str(selfpay_num))
    st.write("Number of patient encounters: " + str(patient_num_no_self_pay))


    st.write("Total primary payments: " + str("${:,.2f}".format(primary_sum)))
    st.write("Total secondary payments: " + str("${:,.2f}".format(secondary_sum)))
    st.write("Total self-pay payments: " + str("${:,.2f}".format(self_pay_payments_sum)))
    st.write("Total patient payments: " + str("${:,.2f}".format(patient_payment_sum)))

    st.toast('Successfully generated benchmark!', icon="✅")

def handle_ecw():
  uploaded_file = st.file_uploader("Upload a 371.05 report", type='csv')
  
  if uploaded_file is not None:
      df = pd.read_csv(uploaded_file)

      st.write(df)

      primary_col = st.selectbox(
        'Which column should be used for the Primary Insurer?',
        df.columns
      )

      insurer_col = st.selectbox(
        'Which column should be used for the Insurer?',
        df.columns
      )

      insurance_payout_col = st.selectbox(
        'Which column should be used to calculate Insurance Payout?',
        df.columns
      )
      st.write('You selected:', insurance_payout_col)

      patient_payment_col = st.selectbox(
        'Which column should be used to calculate Patient Payment?',
        df.columns
      )

      total_payment_col = st.selectbox(
        'Which column should be used to calculate Total Payment?',
        df.columns
      )

      claim_no_col = st.selectbox(
        'Which column should be used to identify the claim number?',
        df.columns
      )

      cpt_col = st.selectbox(
        'Which column should be used to identify the CPT Code?',
        df.columns
      )

      if st.button('Generate Benchmark'):
        compute_ecw_stats(
          df=df,
          insurer_col=insurer_col,
          primary_ins_col=primary_col,
          total_payment_col=total_payment_col,
          insurance_payout_col=insurance_payout_col,
          patient_payment_col=patient_payment_col,
          claim_no_col=claim_no_col,
          cpt_col=cpt_col
        )