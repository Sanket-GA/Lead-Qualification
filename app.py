import streamlit as st
from utility import FinancialKPIs,data_preprocessing,kpi_dictionary
from llm import one_limit_call
from ast import literal_eval
from streamlit_card import card
import pandas as pd


st.set_page_config(page_title="Lead 360", layout="wide")

st.markdown("""
<div style='text-align: center;'>
<h2 style='font-size: 70px;margin-top:-60px;padding-bottom:50px; font-family: Arial, sans-serif; 
                   letter-spacing: 2px; text-decoration: none;'>
<a href='https://affine.ai/' target='_blank' rel='noopener noreferrer'
               style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                      -webkit-background-clip: text;
                      -webkit-text-fill-color: transparent;
                      text-shadow: none; text-decoration: none;'>
                Lead 360
</a>
</h2>
</div>
""", unsafe_allow_html=True)

## Session state
if "list_of_KPI" not in st.session_state:
    st.session_state['list_of_KPI']=None

if "summary" not in st.session_state:
    st.session_state.summary=None

if "recommendation" not in st.session_state:
    st.session_state.recommendation=None

if "kpi_flag" not in st.session_state:
    st.session_state.kpi_flag=None


col_s, col_b ,col_i= st.columns([1, 3, 1],gap="large")  # Adjust the width ratio


# col_s.markdown(
#     """
#     <style>
#     div[data-testid="stSelectbox"] {
#         width: 300px !important;  /* Adjust width */
#         height: 30px !important;  /* Adjust height */
#     }
#     div[data-testid="stButton"] button {
#         width: 100px !important; /* Adjust button width */
#         height: 35px !important; /* Adjust button height */
#         margin: 50px 2px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

selected_ticker=col_s.selectbox("Select the Payee ::", ['SMAR', 'NVDA'])
button=col_s.button("Start")

if selected_ticker=="NVDA":
    col_i.image("data:image/png;base64,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")
else:
    col_i.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQUpFnBUSXL5obSOxgPEquMFg1a4PrU-aF0xg&s")

if button:
    st.session_state.kpi_flag=selected_ticker
    kpi_tracker = FinancialKPIs(selected_ticker)
    financial_details=kpi_tracker.get_all()
    financial_details2=data_preprocessing(financial_details)
    prompt_=f"""You are an expert assistant specializing in financial data analysis and lead qualification. Your primary task is to evaluate financial data from the past three years to determine the qualification of potential payee customers. The client is a global leader in managing payments, cash flow, and risk.
Use your expertise to determine whether the payee customer qualifies as a potential customer based on their financial stability and risk profile.

kpi_dictionary:
{kpi_dictionary}

Below is the key guidelines for defining company performance:
1. Assess financial data over multiple years to identify consistent stability and growth trends.
2. Evaluate the ability to manage cash flow, risks, and financial obligations effectively.
3. Determine the customer's financial risk profile by examining key financial indicators and metrics.
4. Ensure that the customer meets established thresholds for financial stability and operational efficiency.
5. Use a data-driven approach to identify customers that align with the company's long-term payment management objectives.
6. Similarly, refer to the KPI dictionary to ensure a consistent and accurate analysis of all metric-level data.
7. Always perform a thorough analysis of all metrics provided in the KPI dictionary to maintain comprehensive evaluation standards.
8. Highlight key strengths and weaknesses by analyzing the KPI data, focusing on growth, cash flow, profitability, and any identified risks to provide a balanced overview.
9. Based on the analysis, determine whether the payee customer qualifies, ensuring to include considerations for monitoring critical metrics and addressing potential risks.

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
    

Output JSON should consist of the following format::\n
Example:
json matrix: ```[{{"KPI":<kpi name>,"Score":<int>,"why":<reason of score low, Avg. or high> }}]```

## Summary
- Strengths: <Analyze the provided KPI data to highlight areas of strong performance>
- Weaknesses: <Assess areas where the performance lags, focusing on inefficiencies>
- Risk Profile: <Evaluate the overall financial stability and risk by balancing strengths and weaknesses>

## Recommendation:
Base recommendations on a comprehensive analysis of the KPI data, emphasizing whether the payee customer qualifies based on their financial stability, growth potential, and alignment with the company's risk tolerance.

"""+\
f"""Here is the financial data of payee customers :: \n {financial_details2}
"""
    ans,usage=one_limit_call(prompt_)
    list_of_KPI=literal_eval(ans[ans.find("["):ans.find("]")+1])
    print("Num of KPI ::",len(list_of_KPI))
    st.session_state['list_of_KPI']=list_of_KPI
    st.session_state.summary="### "+ ans[ans.find("Summary"):ans.find("Recommendation")].replace("#","")
    st.session_state.recommendation="### "+ ans[ans.find("Recommendation"):].replace("#","")
    print("st.session_state.summary ::",st.session_state.summary)
    print("st.session_state.summary ::",st.session_state.recommendation)

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



if st.session_state['summary'] and st.session_state.kpi_flag==selected_ticker:
    tab1,tab2,tab3=st.tabs(['Textual Summary',"Data","KPI Level"])

    # Section 1: Summarized Insights
    if selected_ticker == 'SMAR' :
        with tab1:
            st.markdown(f"##### About the {selected_ticker}")
            st.write(
                f"{selected_ticker} (NASDAQ: Smartsheet Inc.) is a service provider with annual revenue of approximately $800 million and a global presence. "
                "They have been receiving money from Convera. Based on the prediction and CLTV, they are in the must-reach-out segment, and we expect significant business benefits by converting them."
            )
        with tab2:
            col10, col11 = st.columns(2)
            col10.write(f"**Fundamental of {selected_ticker}:**")
            with col10:
                by_the_numbers_data = pd.DataFrame({
                    "#Payments": [12],
                    "Payment USD": ["$75,000"],
                    "#Beneficiaries": [8],
                    "Time since last payment": ["45 days"],
                    "Fee USD": ["$1,500"]
                })
                st.dataframe(by_the_numbers_data, hide_index=True)

            # Section 3: Machine Learning Predictions
            col11.write(f"**Fundamental of {selected_ticker}:**")
            with col11:
                ml_predictions_data = pd.DataFrame({
                    "Lead Conversion Score": [90],
                    "Expected CLTV": ["$250,000"],
                    "Recommended Product": ["Enterprise Service Plan"]
                })
                st.dataframe(ml_predictions_data, hide_index=True)

            # Section 4: Secondary Research
            col21, col22 = st.columns(2)
            col21.write("**Secondary Research:**")
            secondary_research_data = pd.DataFrame({
                "Annual Sales/Revenue": ["$800 Million"],
                "Global Employee Count": ["3,000"],
                "Global Employee Footprint": ["80 Countries"],
                "Share of Voice": ["20%"],
                "Brand Sentiment": ["Positive"]
            })
            col21.dataframe(secondary_research_data, hide_index=True)


            # Section 5: Targeting Info
            # Placeholder data for targeting info
            col22.write("**Key Decision Makers:**")
            targeting_info_data = pd.DataFrame({
                "Name": ["John Doe", "Jane Smith"],
                "Designation": ["CFO", "Head of Operations"],
                "Location": ["New York, USA", "London, UK"],
                "Contact": ["johndoe@smartsheet.com", "janesmith@smartsheet.com"]
            })
            col22.dataframe(targeting_info_data,hide_index=True)
        col_b.write("**Headquarter:** Bellevue, Washington, USA")
        col_b.write("**Vendor Spend:** $3 Million")


    if selected_ticker == "NVDA":
        with tab1:
            # Section 1: Summarized Insights
            st.markdown(f"##### About the {selected_ticker}")
            st.write(
                "NVIDIA (NASDAQ: NVDA) is a global leader in AI computing and GPU manufacturing, with annual revenue of approximately $27 billion. "
                "They have been receiving money from Convera. Based on the prediction and CLTV, they are in the must-reach-out segment, and we expect significant business benefits by converting them."
            )

        # Section 2: By the Numbers
        with tab2:
            st.subheader("By the Numbers")
            col1, col2 = st.columns(2)
            with col1:
                by_the_numbers_data = pd.DataFrame({
                    "#Payments": [25],
                    "Payment USD": ["$200,000"],
                    "#Beneficiaries": [15],
                    "Time since last payment": ["30 days"],
                    "Fee USD": ["$5,000"]
                })
                st.dataframe(by_the_numbers_data, hide_index=True)

            # Section 3: Machine Learning Predictions
            with col2:
                ml_predictions_data = pd.DataFrame({
                    "Lead Conversion Score": [95],
                    "Expected CLTV": ["$1,000,000"],
                    "Recommended Product": ["AI Computing Solutions"]
                })
                st.dataframe(ml_predictions_data, hide_index=True)

            # Section 4: Secondary Research
            col21, col22 = st.columns(2)
            col21.subheader("Secondary Research")
            secondary_research_data = pd.DataFrame({
                "Annual Sales/Revenue": ["$27 Billion"],
                "Global Employee Count": ["22,000"],
                "Global Employee Footprint": ["50 Countries"],
                "Share of Voice": ["35%"],
                "Brand Sentiment": ["Very Positive"]
            })
            col21.dataframe(secondary_research_data, hide_index=True)

            # Section 5: Targeting Info

            col22.write("**Key Decision Makers:**")
            targeting_info_data = pd.DataFrame({
                "Name": ["Jensen Huang", "Jane Smith"],
                "Designation": ["CEO", "Head of AI Operations"],
                "Location": ["Santa Clara, USA", "London, UK"],
                "Contact": ["jhuang@nvidia.com", "janesmith@nvidia.com"]
            })
            col22.dataframe(targeting_info_data, hide_index=True)
        col_b.write()
        col_b.write()
        col_b.write()
        col_b.write()
        col_b.write()
        col_b.write()
        col_b.write()
        col_b.write()
        col_b.write("**Headquarter:** Santa Clara, California, USA")
        col_b.write("**Vendor Spend:** $5 Million")

    with tab1:
        if st.session_state['summary']:
            st.markdown("##"+st.session_state.summary)

        if st.session_state['recommendation']:
            st.markdown("##"+st.session_state.recommendation)

    with tab3:
        if st.session_state['list_of_KPI']:
            tabs = st.radio( "Filters :: ",["High Scores", "Medium Scores", "Low Scores"],horizontal=True)
            # Filter KPIs based on selected tab
            if tabs == "High Scores":
                filtered_KPI = [kpi for kpi in st.session_state['list_of_KPI'] if kpi['Score'] >= 4]
            elif tabs == "Medium Scores":
                filtered_KPI = [kpi for kpi in st.session_state['list_of_KPI'] if 2 <= kpi['Score'] < 4]
            else:
                filtered_KPI = [kpi for kpi in st.session_state['list_of_KPI'] if kpi['Score'] == 1]

            if len(filtered_KPI):
                for i in range(0, len(filtered_KPI), num_of_cols):
                    # Create a row with `num_of_cols` columns
                    cols = st.columns(num_of_cols)
                    st.markdown("<div style='margin-bottom: 20px;'>", unsafe_allow_html=True)
                    for j, kpi1 in enumerate(filtered_KPI[i:i + num_of_cols]):
                        score_color = get_score_color(kpi1['Score'])
                        card_bg_color = get_card_background_color(kpi1['Score'])
                        with cols[j]:
                            st.write(
                                f"""<div style='padding: 10px; border: 1px solid #ddd; border-radius: 8px; 
                                    height: 220px; overflow-y: auto; background-color: {card_bg_color};'>
                                    <p style="font-size: 18px; font-weight: bold; margin: 0; color: {score_color};">
                                        {kpi1['Score']}
                                    </p>
                                    <p style="font-size: 14px; font-weight: bold; margin: 5px 0; color: {score_color};">
                                        {kpi1['KPI']}
                                    </p>
                                    <p style="margin: 5px 0; font-size: 14px; color: #666;">
                                        {kpi1['why']}
                                    </p>
                                </div>""",
                                unsafe_allow_html=True,
                            )
                        st.markdown("</div>", unsafe_allow_html=True)  # Close the margin wrapper
            else:
                st.info("No KPIs belong to this category.")  

else:
    st.info("Insight for the selected customer is not available. Click the Start button to begin the analysis.")
