import streamlit as st
from utility_v2 import WebSearch,data_financial_preprocessing,data_org_preprocessing,create_gauge_chart,get_summary_prompt
from llm import one_limit_call
from ast import literal_eval
from streamlit_card import card
import pandas as pd
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import streamlit as st
import pandas as pd

## Streamlit Header
st.set_page_config(page_title="Lead Whisper", layout="wide")
st.markdown("""
<div style='text-align: center;'>
<h2 style='font-size: 50px;margin-top:-60px;padding-bottom:50px; font-family: Arial, sans-serif; 
                   letter-spacing: 2px; text-decoration: none;'>
<a href='https://affine.ai/' target='_blank' rel='noopener noreferrer'
               style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                      -webkit-background-clip: text;
                      -webkit-text-fill-color: transparent;
                      text-shadow: none; text-decoration: none;'>
               Lead Whisper
</a>
</span>
        <span style='font-size: 40%;'>
        <sup style='position: relative; top: 5px; background: linear-gradient(45deg, #ed4965, #c05aaf); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'></sup> 
        </span>
</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""<div style='text-align: left; margin-top:-100px;margin-left:-60px;'>
        <img src="https://affine.ai/wp-content/uploads/2024/06/logo.png" alt="logo" width="150" height="30">
        </div>""", unsafe_allow_html=True)

st.markdown("""<div style='text-align: left; margin-top:-110px;margin-left:1000px;'>
        <img src="https://cdn.cookielaw.org/logos/c605ae6f-7e1d-4c58-b524-99c2677f9cfa/4b9d194d-c494-4a03-b3f8-9087c9235c85/851e6a4f-b205-4355-bcfb-c338c27ffc5c/logo-dark@2x.png" alt="logo" width="150" height="30">
        </div>""", unsafe_allow_html=True)

## Session state
if "list_of_KPI" not in st.session_state:
    st.session_state['list_of_KPI']=None

if "Summary" not in st.session_state:
    st.session_state.Summary=None

if "Recommendation" not in st.session_state:
    st.session_state.recommendation=None

if "kpi_flag" not in st.session_state:
    st.session_state.kpi_flag=None

if "financial_data" not in st.session_state:
    st.session_state.financial_data=None

if "org_data" not in st.session_state:
    st.session_state.org_data=None

if "org_response" not in st.session_state:
    st.session_state.org_response=None

if "df" not in st.session_state:
    st.session_state.df=None

if "df_flag" not in st.session_state:
    st.session_state.df_flag=None

if "news_data" not in st.session_state:
    st.session_state.news_data=None


col_s, col_b ,col_i= st.columns([1, 2, 2],gap="large")  # Adjust the width ratio

if st.session_state.df_flag==None:
    st.session_state.df=pd.read_excel("payee_details.xlsx",sheet_name="Sheet1")
    st.session_state.df_flag=True

payee_name_list=st.session_state.df['PAYEENAME'].to_list()

selected_ticker=col_s.selectbox("Select the Payee ::",payee_name_list)
button=col_s.button("Start")

if selected_ticker=="BREVILLE CANADA, L.P.":
    col_b.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSF2AfxH1JnJZGT9rtN6nu3pg9pVoZUMwmDvg&s",width=200)
elif selected_ticker=="TRUSTLY GROUP AB":
    col_b.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQr1L1bIlcgPz2dG8dgbkwYWkk30PsJcVGejg&s",width=200)
elif selected_ticker=="MANULIFE FINANCIAL":
    col_b.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkdUgUPjXQkcvq_ZvrOgoH0G70kj64IVZyVQ&s",width=200)
elif selected_ticker=="UNIVERSITY HEALTH NETWORK":
    col_b.image("https://s3-eu-west-1.amazonaws.com/assets.in-part.com/universities/121/d7SK72jRvKuJkx50k0Tz_UHN-logo-new.png",width=200)
elif selected_ticker=="Cenovus Energy Inc.":
    col_b.image("https://cdn.cookielaw.org/logos/f9494f49-e682-408b-a250-2617c7517ebd/82a6d757-3704-4928-9049-9f920887f23c/34911ca0-0234-4f94-af80-9b3f9d921667/2021-CVE-Logo-RGB.png",width=200)
    # col_i.divider()

    # 

if button:
    if st.session_state.financial_data==None:
        st.session_state.kpi_flag=selected_ticker
        query=f"what is the revenue growth of {selected_ticker} news, reports"
        obj=WebSearch()
        text_docs_list=obj.fecth_text(query)

        st.session_state.financial_data=data_financial_preprocessing(selected_ticker,text_docs_list)

    financial_prompt_=f"""You are an expert assistant specializing in financial data analysis and lead qualification. Your primary task is to summarize and evaluate provided financial and other data from the current and past years of {selected_ticker} company to determine the qualification of potential payee customers. Use your expertise to determine whether the payee customer qualifies as a potential customer based on their financial information and stability and risk profile.

    Below is the key guidelines for defining company performance:
    1. Assess and Summarize financial data over multiple years to identify consistent stability and growth trends.
    2. Evaluate the ability to manage cash flow, risks and financial obligations effectively.   
    3. Determine the customer's financial risk profile by examining key financial indicators and metrics.
    4. Ensure that the customer meets established thresholds for financial stability and operational efficiency.
    5. Use a data-driven approach to identify customers that align with the company's long-term payment management objectives.
    6. Always perform a thorough analysis of 5-6 important metrics to maintain comprehensive evaluation standards.
    7. Highlight key strengths and weaknesses by analyzing the KPI data, focusing on growth, cash flow, profitability, and any identified risks to provide a balanced overview.
    8. Based on the analysis, determine whether the payee customer qualifies, ensuring to include considerations for monitoring critical metrics and addressing potential risks.
    9. Ensure that all analysis is relevant and accurate, strictly based on the provided context for {selected_ticker}. Do not include any incorrect details or information about any other company.

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

    ```{{"About":,'<Provide a brief overview of the company's details(company name, Domain, foundation year etc.) in 1-3 lines.>',
    "Fundamental_KPI":[{{"KPI":<kpi name>,"Score":<int>,"why":<reason of score low, Avg. or high> }}],
    "Summary":{{"Strengths":'<Analyze the provided data to highlight areas of strong performance>',
    "Weaknesses":'<Assess areas where the performance lags, focusing on inefficiencies>',
    "Risk Profile": <Evaluate the overall financial stability and risk by balancing strengths and weaknesses>}},
    "Recommendation":<Base recommendations on a comprehensive analysis of the data, emphasizing whether the payee customer qualifies based on their financial stability, growth potential, and alignment with the company's risk tolerance.>,
    "Overall Recommendation Score":'<Assign a score between 1-10 based on the payee customer's financial stability, growth potential, and alignment with the company's risk tolerance.>'
    }}```
    """+\
    f"""Here is the data of payee customers :: \n {st.session_state.financial_data}
    """
    ans,usage=one_limit_call(financial_prompt_)
    print("------------------------final Response-----------------------")
    print(ans)
    final_response=literal_eval(ans[ans.find("{"):ans.rfind("}")+1])
    st.session_state.list_of_KPI=final_response['Fundamental_KPI']
    st.session_state.About=final_response['About']
    # st.session_state.Company_Details=final_response['Company Details']
    st.session_state.Summary=final_response['Summary']
    st.session_state.Recommendation=final_response['Recommendation']
    st.session_state.Overall_Recommendation_Score=final_response['Overall Recommendation Score']

    query=f"The linkedin profile's of the ceo, cto and key decision-makers at {selected_ticker}"

    obj=WebSearch()
    text_docs_list=obj.fecth_text(query)
    st.session_state.org_data=data_org_preprocessing(selected_ticker,text_docs_list)

    org_prompt_=f"""You are an expert in corporate structures, specializing in identifying decision-making hierarchies within organizations. Your task is to extract, validate, and summarize relevant executive and company details for {selected_ticker}.  

    ## Guidelines for Data Extraction and Summarization:
    1. Collect and validate structured data from multiple web sources, including the official website, LinkedIn, Bloomberg, and other credible business directories.  
    2. Ensure extracted details are 'specific to {selected_ticker}' only—avoid incorrect or unrelated company data.  
    3. Include the company's founding year, key milestones, and executive leadership details (CEO, CFO, and key decision-makers).  
    4. Extract tenure, past experience, achievements, and LinkedIn profiles of executives.  
    5. Always return the LinkedIn url from source of document.
    6. Prioritize verified and up-to-date information. If no relevant details are found, return `"NA"`.  
    7. Ensure accuracy and consistency across different sources before structuring the final output.  

    ## Here is the data of company data :: {st.session_state.org_data}

    ## Output Format (JSON Only)
    The final response must follow the JSON structure below:  
    sample example: ```json {{
    "company_name": "<company_name>",
    "company_website": "<company_website>",
    "company_linkedin_profile": "<company_linkedin_profile>",
    "founding_year": "<founding_year>",
    "executives": [{{
        "name": "<executive_name>",
        "role": "Chief Executive Officer",
        "tenure": "<start_year> - Present",
        "linkedin_profile": "<linkedin_profile_url>",
        "contact_email": "<contact_email>"}}]}}"""

    ans,usage=one_limit_call(org_prompt_)
    st.session_state.org_response=literal_eval(ans[ans.find("{"):ans.rfind("}")+1])
    print("-------------------------org response-----------------------------------")
    print(st.session_state.org_response)

    # query=f"latest financial news, stock performance and market analysis news for {selected_ticker}"
    query=f"latest news of {selected_ticker}"
    obj=WebSearch()
    news_data=obj.fecth_text(query,top_n=7)
    # st.session_state.
    st.session_state.news_summerize_list=[]
    for i,doc in enumerate(news_data):
        try:
            if 'content' in news_data[i][0]:
                # print("-------------------summary context--------------------------")
                context=news_data[i][0]["content"]
                # print(context)
                source=news_data[i][0]["source"]
                prompt_=get_summary_prompt(selected_ticker,context)
                extracted_data,usage=one_limit_call(prompt_)
                print("----------------------Summary----------------------")
                print(extracted_data)
                if "NA" not in extracted_data:
                    st.session_state.news_summerize_list.append({"source":source,"summary":extracted_data})
            else:
                # print("-------------------summary context--------------------------")
                context=str(news_data[i][0])
                # print(context)
                source=news_data[i][0].metadata["source"]
                prompt_=get_summary_prompt(selected_ticker,context)
                extracted_data,usage=one_limit_call(prompt_)
                print("----------------------Summary----------------------")
                print(extracted_data)
                if "NA" not in extracted_data:
                    st.session_state.news_summerize_list.append({"source":source,"summary":extracted_data})
        except:
            pass
        

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


import streamlit as st

# Function to create a styled card
def profile_card(name, role, tenure, linkedin_profile, contact_email, width='400px', height='250px'):
    past_experience=[""]
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #74ebd5, #acb6e5);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            margin-right: 50px;
            width: {width};
            height: {height};">
            <h3 style="color: #333;">{name}</h3>
            <p><strong>Role:</strong> {role}</p>
            <p><strong>Tenure:</strong> {tenure}</p>
            <p><strong>LinkedIn:</strong> <a href="{linkedin_profile}" target="_blank">Profile Link</a></p>
            <p><strong>Contact:</strong> <a href="mailto:{contact_email}">{contact_email}</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )
# <p><strong>Past Experience:</strong></p>
#             <ul>
#                 {''.join(f'<li>{exp}</li>' for exp in past_experience)}
#             </ul>

Payee_transactions_data= st.session_state.df.loc[st.session_state.df['PAYEENAME']==st.session_state.kpi_flag]

if st.session_state.Summary and st.session_state.kpi_flag==selected_ticker: # 
    tab1,tab2,tab3,tab4=st.tabs(['LEAD WHISPERER​',"DECISION MAKERS","METRICS","FROM THE WEB​"])
    # avg_score=sum([dict1["Score"] for dict1 in st.session_state['list_of_KPI']])/len(st.session_state['list_of_KPI'])
    
    # col_b.markdown(f"**Lead Rating**   :: {round(avg_score,2)}")
    # overall_score=st.session_state.overall_score.replace("Overall Recommendation Score:","").replace("/10","").replace("\n","").strip()
    # print("overall_score ::",int(overall_score))
    

    with col_i:
        company_name=st.session_state.org_response['company_name'] #st.session_state.Company_Details['company_name']
        # Address=st.session_state.Company_Details['Address']
        company_linkedin_profile=st.session_state.org_response['company_linkedin_profile']
        company_url=st.session_state.org_response['company_website']
        founding_year=st.session_state.org_response['founding_year']
        executives_list=st.session_state.org_response['executives']
        st.markdown(f"### Welcome 👏 {company_name}")
        st.markdown(f"**Linkedin Profile** :: {company_linkedin_profile}")
        st.markdown(f"**Website** :: {company_url}")
        st.markdown(f"**Founding Year** :: {founding_year}")
        
        # for i in executives_list:
        #     print("------------------------------------------------")
        #     print(i)

    with tab1:
        col33,col44=st.columns([1,1],gap="large")
        with col33:
            col55,col66=st.columns([1,1])
            overall_score=st.session_state.Overall_Recommendation_Score.replace("/10","")
            gauge_chart = create_gauge_chart(int(overall_score))
            col55.plotly_chart(gauge_chart)
            if st.session_state.About:
                col66.markdown(f"### OBSERVATIONS")
                col66.markdown(st.session_state.Recommendation)
                # col66.markdown(st.session_state.About)

        if st.session_state['Summary']:
            with col33:
                # print(st.session_state.Summary)
                # st.markdown("#### Summary:")
                st.markdown("- " + st.session_state.About)
                # st.markdown("**Strengths** -"+st.session_state.Summary['Strengths'])
                # st.markdown("**Weaknesses** -"+st.session_state.Summary['Weaknesses'])
                # st.markdown("**Risk Profile** -"+st.session_state.Summary['Risk Profile'])

        # if st.session_state['Recommendation']:
        #     print(st.session_state.Recommendation)
        #     st.markdown("#### Recommendation : \n"+st.session_state.Recommendation)
        with col33:
            col33.markdown("### PREDICTIONS​")
            st.markdown("- "+st.session_state.Summary['Strengths'])
            st.markdown("- "+st.session_state.Summary['Weaknesses'])
            st.markdown("- "+st.session_state.Summary['Risk Profile'])
        with col44:
            col44.markdown("### METRIC DEEP DIVE​")
            select_company= st.session_state.df.loc[ st.session_state.df['PAYEENAME']==st.session_state.kpi_flag]
            df_melted = select_company.melt(var_name="Metric", value_name="Value")
            st.dataframe(df_melted,width=1600,hide_index=True)
            st.markdown('<a href="#" onclick="window.switch_tab()">Have they been in the news lately? And why?</a>', unsafe_allow_html=True)
            st.markdown('<a href="#" onclick="window.switch_tab()">Who are their biggest competitors and what are their differentiators?​</a>', unsafe_allow_html=True)
                
    with tab2:
        select_company= st.session_state.df.loc[ st.session_state.df['PAYEENAME']==st.session_state.kpi_flag]
        # st.markdown("**Customer Transaction History**")
        # st.dataframe(select_company,width=1600)
        # st.markdown("**Key Decision Makers**")
        cols = st.columns(3,gap="large")
        for i,data in enumerate(executives_list[:3]):
            with cols[i]:
                profile_card(**data)
        # executive_team_list=st.session_state.Company_Details['executive_team']
        # st.dataframe(executive_team_list,width=800)

    with tab3:
        # if st.session_state['list_of_KPI']:
        #     st.dataframe(st.session_state.list_of_KPI,
        #      width=1400, 
        #     column_config={
        # "KPI Name": st.column_config.TextColumn(width="200px"),
        # "Value": st.column_config.NumberColumn(width="150px"),
        # "Growth (%)": st.column_config.NumberColumn(width="1500px"),},
        #    )
        if len(st.session_state.list_of_KPI):
                for i in range(0, len(st.session_state.list_of_KPI), num_of_cols):
                    # Create a row with `num_of_cols` columns
                    cols = st.columns(num_of_cols)
                    st.markdown("<div style='margin-bottom: 20px;'>", unsafe_allow_html=True)
                    for j, kpi1 in enumerate(st.session_state.list_of_KPI[i:i + num_of_cols]):
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
    with tab4:
        for news in st.session_state.news_summerize_list:
            if "summary" in news.keys() and "source" in news.keys():
                st.markdown(f"**{news['summary'].strip()}**")
                st.markdown( news['source'])
                st.divider()


        # for news in st.session_state.news_data:
        #     if type(news)==dict:
        #         pass
        #     else:
        #         metadata=news[0].metadata
        #         # st.write(metadata)
        #         if "title" in metadata.keys() and "source" in metadata.keys():
        #             st.markdown(f"**{metadata['title'].strip()}**")
        #             if "description" in metadata.keys():
        #                 st.markdown( metadata['description'])
        #             st.markdown( metadata['source'])
        #             st.divider()

else:
    st.info("Insight for the selected customer is not available. Click the Start button to begin the analysis.")
