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


col_s, col_b = st.columns([1, 3])  # Adjust the width ratio


col_s.markdown(
    """
    <style>
    div[data-testid="stSelectbox"] {
        width: 300px !important;  /* Adjust width */
        height: 30px !important;  /* Adjust height */
    }
    div[data-testid="stButton"] button {
        width: 100px !important; /* Adjust button width */
        height: 35px !important; /* Adjust button height */
        margin: 50px 2px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

selected_ticker=col_s.selectbox("Select the Payee ::", ['SMAR', 'NVDA'])
button=col_s.button("Start")



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
    st.info("Insight for the selected customer is not available. Click the Start button to begin the analysis.")
