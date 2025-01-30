from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=st.secrets.azure.base_url or os.getenv('base_url'),
    api_version=st.secrets.azure.api_version or os.getenv('api_version'),
    api_key=st.secrets.azure.api_key or os.getenv('api_key'))


def one_limit_call(prompt_):
    try:
        # Create completion request
        completion = client.chat.completions.create(
            model=st.secrets.azure.model or os.getenv('model'),
            temperature=0,
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant expert in finding and analyzing the company financial data.'},
                {"role": "user", "content": prompt_}
            ],
        )
        usage = {
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens
            }
        
        return completion.choices[0].message.content, usage

    except Exception as e:
        print("Exception in one_limit_call Azure Call:", e)