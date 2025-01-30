import streamlit as st
from utility_v2 import WebSearch,data_preprocessing,get_prompt,create_gauge_chart
from llm import one_limit_call
from ast import literal_eval
from streamlit_card import card
import pandas as pd
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import streamlit as st

st.set_page_config(page_title="Lead Qualification Engine", layout="wide")

st.markdown("""
<div style='text-align: center;'>
<h2 style='font-size: 70px;margin-top:-60px;padding-bottom:50px; font-family: Arial, sans-serif; 
                   letter-spacing: 2px; text-decoration: none;'>
<a href='https://affine.ai/' target='_blank' rel='noopener noreferrer'
               style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                      -webkit-background-clip: text;
                      -webkit-text-fill-color: transparent;
                      text-shadow: none; text-decoration: none;'>
               Lead Qualification Engine
</a>
</h2>
</div>
""", unsafe_allow_html=True)

## Session state
if "list_of_KPI" not in st.session_state:
    st.session_state['list_of_KPI']=None

if "Summary" not in st.session_state:
    st.session_state.Summary=None

if "Recommendation" not in st.session_state:
    st.session_state.recommendation=None

if "kpi_flag" not in st.session_state:
    st.session_state.kpi_flag=None

if "final_data" not in st.session_state:
    st.session_state.final_data=None


col_s, col_b ,col_i= st.columns([2, 3, 1],gap="medium")  # Adjust the width ratio



selected_ticker=col_s.selectbox("Select the Payee ::", ['BREVILLE CANADA, L.P.', 'TRUSTLY GROUP AB','MANULIFE FINANCIAL',"UNIVERSITY HEALTH NETWORK","Cenovus Energy Inc."])
button=col_s.button("Start")

# if selected_ticker=="NVDA":
#     col_i.image("data:image/png;base64,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")
# else:
#     col_i.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQUpFnBUSXL5obSOxgPEquMFg1a4PrU-aF0xg&s")

if button:
    if st.session_state.final_data==None:
        st.session_state.kpi_flag=selected_ticker
        query=f"what is the revenue growth of {selected_ticker} news, reports"
        obj=WebSearch()
        text_docs_list=obj.fecth_text(query)

        final_data=data_preprocessing(text_docs_list)
        st.session_state.final_data=final_data

    prompt_="""You are an expert assistant specializing in financial data analysis and lead qualification. Your primary task is to evaluate provided financial and other data from the current and past years to determine the qualification of potential payee customers. You are working for global leader to managing payments, cash flow, and risk.
Use your expertise to determine whether the payee customer qualifies as a potential customer based on their financial information and stability and risk profile.


Below is the key guidelines for defining company performance:
1. Assess financial data over multiple years to identify consistent stability and growth trends.
2. Evaluate the ability to manage cash flow, risks and financial obligations effectively.
3. Determine the customer's financial risk profile by examining key financial indicators and metrics.
4. Ensure that the customer meets established thresholds for financial stability and operational efficiency.
5. Use a data-driven approach to identify customers that align with the company's long-term payment management objectives.
6. Always perform a thorough analysis of 5-6 important metrics to maintain comprehensive evaluation standards.
7. Highlight key strengths and weaknesses by analyzing the KPI data, focusing on growth, cash flow, profitability, and any identified risks to provide a balanced overview.
8. Based on the analysis, determine whether the payee customer qualifies, ensuring to include considerations for monitoring critical metrics and addressing potential risks.

Scoring Guidelines
To assign a score between 1-5 based on performance, you can use the following steps:
1. Define Performance Ranges:
    1. (Poor): Below industry average, significant issues.
    2. (Below Average): Slightly below industry average, some issues.
    3. (Average): Meets industry average, stable performance.
    4. (Above Average): Above industry average, strong performance.
    5. (Excellent): Significantly above industry average, outstanding performance.
2. Assign Scores to Each KPI:
    1. Compare each KPI to industry benchmarks or historical performance.
    2. Assign a score based on where the KPI falls within the defined ranges.

Consider the following key point to structure the output and The output should be in following format:
Extract the following information in below list if available otherwise "N/A"

```{{"About":,'<Provide a brief overview of the company's details(Domain, foundation year etc.) in 1-3 lines.>',
"Fundamental_KPI":[{"KPI":<kpi name>,"Score":<int>,"why":<reason of score low, Avg. or high> }]}},
"Company Details":{"company_name":<name of company>,"Address":<address of company>,"company url":<company website url>,"executive_team":[{"name":<name>,"email":<email>,"position":<position>}]},
"Summary":{"Strengths":'<Analyze the provided data to highlight areas of strong performance>',
"Weaknesses":'<Assess areas where the performance lags, focusing on inefficiencies>',
"Risk Profile": <Evaluate the overall financial stability and risk by balancing strengths and weaknesses>},
"Recommendation":<Base recommendations on a comprehensive analysis of the data, emphasizing whether the payee customer qualifies based on their financial stability, growth potential, and alignment with the company's risk tolerance.>,
"Overall Recommendation Score":'<Assign a score between 1-10 based on the payee customer's financial stability, growth potential, and alignment with the company's risk tolerance.>'
}}```
"""+\
f"""Here is the data of payee customers :: \n {st.session_state.final_data}
"""
    ans,usage=one_limit_call(prompt_)
    print("------------------------final Response-----------------------")
    print(ans)
    final_response=literal_eval(ans[ans.find("{"):ans.rfind("}")+1])
    st.session_state.list_of_KPI=final_response['Fundamental_KPI']
    st.session_state.About=final_response['About']
    st.session_state.Company_Details=final_response['Company Details']
    st.session_state.Summary=final_response['Summary']
    st.session_state.Recommendation=final_response['Recommendation']
    st.session_state.Overall_Recommendation_Score=final_response['Overall Recommendation Score']

# Define the number of columns
num_of_cols = 6

# Function to determine color based on score
def get_score_color(score):
    if score >= 4:
        return 'green'
    elif score >= 2:
        return 'Orange'
    else:
        return 'red'

# Function to determine background color based on score
def get_card_background_color(score):
    if score >= 4:
        return '#e0f7e0'  # Light green
    elif score >= 2:
        return '#fff9c4'  # Light yellow
    else:
        return '#ffcccb'  # Light red

Payee_transactions_data={
  "BREVILLE CANADA, L.P.": {
    "# Customers Transacting to":[ 2],
    "# Transactions": [5],
    "# Currencies Transacted": [1],
    "Fee Amount":[ 20],
    "Payment Amount":[ 3052105]
  },
  "TRUSTLY GROUP AB": {
    "# Customers Transacting to": [1],
    "# Transactions": [1],
    "# Currencies Transacted": [1],
    "Fee Amount": [2],
    "Payment Amount": [1035186]
  },
  "MANULIFE FINANCIAL": {
    "# Customers Transacting to": [3],
    "# Transactions":[ 4],
    "# Currencies Transacted": [1],
    "Fee Amount": [6],
    "Payment Amount": [307355]
  },
  "UNIVERSITY HEALTH NETWORK": {
    "# Customers Transacting to":[ 3],
    "# Transactions": [8],
    "# Currencies Transacted": [1],
    "Fee Amount": [30.75],
    "Payment Amount": [126401]
  },
  "Cenovus Energy Inc.": {
    "# Customers Transacting to":[ 1],
    "# Transactions": [1],
    "# Currencies Transacted": [1],
    "Fee Amount": [15],
    "Payment Amount": [1340342]
  }
}


if st.session_state.Summary and st.session_state.kpi_flag==selected_ticker: # 
    tab1,tab2,tab3=st.tabs(['Textual Summary',"Data","KPI Level"])
    # avg_score=sum([dict1["Score"] for dict1 in st.session_state['list_of_KPI']])/len(st.session_state['list_of_KPI'])
    
    # col_b.markdown(f"**Lead Rating**   :: {round(avg_score,2)}")
    # overall_score=st.session_state.overall_score.replace("Overall Recommendation Score:","").replace("/10","").replace("\n","").strip()
    # print("overall_score ::",int(overall_score))
    overall_score=st.session_state.Overall_Recommendation_Score.replace("/10","")
    gauge_chart = create_gauge_chart(int(overall_score))
    col_b.plotly_chart(gauge_chart)

    with tab1:
        if st.session_state.About:
            st.markdown(st.session_state.About)

        if st.session_state['Summary']:
            print(st.session_state.Summary)
            st.markdown("#### Summary:")
            st.markdown("**Strengths** -"+st.session_state.Summary['Strengths'])
            st.markdown("**Weaknesses** -"+st.session_state.Summary['Weaknesses'])
            st.markdown("**Risk Profile** -"+st.session_state.Summary['Risk Profile'])

        if st.session_state['Recommendation']:
            print(st.session_state.Recommendation)
            st.markdown("#### Recommendation : \n"+st.session_state.Recommendation)
    
    with tab2:
        select_company=Payee_transactions_data[st.session_state.kpi_flag]
        st.markdown("**Customer Transaction History**")
        st.dataframe(select_company,width=800)

    with tab3:
        if st.session_state['list_of_KPI']:
            st.dataframe(st.session_state.list_of_KPI,
             width=1400, 
            column_config={
        "KPI Name": st.column_config.TextColumn(width="200px"),
        "Value": st.column_config.NumberColumn(width="150px"),
        "Growth (%)": st.column_config.NumberColumn(width="1500px"),},
           )

else:
    st.info("Insight for the selected customer is not available. Click the Start button to begin the analysis.")
