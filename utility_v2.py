from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.document_loaders import AsyncChromiumLoader
# from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_community.document_loaders import AsyncHtmlLoader
from googlesearch import search  
import io
import requests
from PyPDF2 import PdfReader
from llm import one_limit_call

class WebSearch():
    def __init__(self):
        pass
    
    def do_search(self,query,top_n=5):
        search_url_obj=search(query, tld = "co.in", num = top_n , stop = 5, pause = 2)
#         search_urls=[link for link in search_url_obj]
        search_urls=[link for link in search_url_obj if "ambitionbox" not in link]
        print("search_urls ::",search_urls)
        return search_urls
    
    def fecth_text(self,query):
        search_urls=self.do_search(query,top_n=5)
        text_docs=[]
        for url in search_urls:
            print(url)
            if url.endswith(".pdf"):
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}
                    # Fetch the PDF and load it into memory
                    response = requests.get(url=url, headers=headers, timeout=30)
                    # Load the PDF into a BytesIO object
                    on_fly_mem_obj = io.BytesIO(response.content)
                    pdf_reader = PdfReader(on_fly_mem_obj)
                    # Extract text from each page
                    pdf_text = ""
                    for page in pdf_reader.pages:
                        pdf_text += page.extract_text() + "\n"
                    # Store the extracted text
                    text_docs.append([{"file_name": url, "content": pdf_text}])
                except:
                    print("Url Not process ::",url)
            else:
                try:
                    loader = AsyncHtmlLoader([url])
                    docs = loader.load()
                    html2text = Html2TextTransformer()
                    docs_transformed = html2text.transform_documents(docs)
                    print(docs_transformed)
                    text_docs.append(docs_transformed)
                except:
                    print("Url Not process ::",url)
        return text_docs


def data_preprocessing(text_docs_list):
    final_summerize_response=[]
    for i,doc in enumerate(text_docs_list):
        print("-------------------------------------------------------------------------")
        if 'content' in text_docs_list[i][0]:
            context=text_docs_list[i][0]['content']
            prompt_=get_prompt(context)
            extracted_data,usage=one_limit_call(prompt_)
            print(extracted_data)
            final_summerize_response.append(extracted_data)
        else:
            context=text_docs_list[i][0].page_content
            prompt_=get_prompt(context)
            extracted_data,usage=one_limit_call(prompt_)
            print(extracted_data)
            final_summerize_response.append(extracted_data)
    final_data='\n\n'.join(final_summerize_response)
    return final_data


def get_prompt(context):
    prompt_=f"""You are a structured data extraction specialist trained to extract financial and lead qualification data for sales and investment analysis. Your goal is to analyze web search results, extract the most relevant details and present them in a structured JSON format.

    Below is the key guidelines for extracting the data:
    1. Extract structured information from web search results related to Company Name. Identify key financial, operational and reputational details.
    2. Extract yearly revenue, profit, and funding details from the provided context.
    3. Always extract all the details yearly. If multiple financial reports exist, use the latest available data.
    4. Look for founding year, milestones, and expansion history.
    5. Extract from the official website, LinkedIn, or government business directories.
    6. Use LinkedIn, Bloomberg, and official websites to verify CEO, CFO, and executive team details.
    7. Include tenure, past experience, and notable achievements of leaders.
    8. Identify positive and negative mentions from news articles, press releases and financial data.
    9. Extract market trends, competition and growth prospects.
    10. No any relevant information found return 'No Relevant information found'.
    11. Do not forgot to extract important information and Do not return the incorrect information or any other information.

    company_context:{context}
    response: """
    return prompt_

import plotly.graph_objects as go

def create_gauge_chart(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Customer Lead Potential", 'font': {'size': 14}},
        gauge={'axis': {'range': [0, 10]},
               'bar': {'color': "blue"},
               'steps': [
                   {'range': [0, 4], 'color': "red"},
                   {'range': [4, 7], 'color': "yellow"},
                   {'range': [7, 10], 'color': "green"}
               ]
              }
    ))

    fig.update_layout(
        margin={'t': 40, 'b': 10, 'l': 0, 'r': 0},
        height=150 ,
        width=300
    )
    
    return fig