import streamlit as st
import json
import os
import sys
import time
from langchain.llms.bedrock import Bedrock


st.set_page_config(
    page_title="Text Summarization",
    layout="wide",
)
c1, c2 = st.columns([1, 8])
with c1:
    st.image("./imgs/bedrock.png", width=100)

with c2:
    st.header("Text generation")
    st.caption("Using Claude in Bedrock")

module_path = ".."
sys.path.append(os.path.abspath(module_path))
from utils import bedrock, print_ww

# ---- ⚠️ Un-comment and edit the below lines as needed for your AWS setup ⚠️ ----
# os.environ["AWS_DEFAULT_REGION"] = "<REGION_NAME>"  # E.g. "us-east-1"
# os.environ["AWS_PROFILE"] = "<YOUR_PROFILE>"
# os.environ["BEDROCK_ASSUME_ROLE"] = "<YOUR_ROLE_ARN>"  # E.g. "arn:aws:..."

boto3_bedrock = bedrock.get_bedrock_client(
    assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
    region=os.environ.get("AWS_DEFAULT_REGION", None)
)

modelId = 'anthropic.claude-v2' # change this to use a different version from the model provider
accept = 'application/json'
contentType = 'application/json'

sample_instruction = """Write an email from Bob, Customer Service Manager, to the customer "John Doe" that provided negative feedback on the service provided by our customer support engineer."""


instruction = st.text_area("Prompt:", sample_instruction, height=100)


max_tokens_to_sample = st.sidebar.slider("max_tokens_to_sample:", min_value=500, max_value=4096, value=4096)
temperature = st.sidebar.slider("temperature:", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
top_k = st.sidebar.slider('top_k:', min_value=10, max_value=500, value=250, step=10)
top_p = st.sidebar.slider('top_p:', min_value=0.0, max_value=1.0, value=0.5, step=0.1)


if st.button("Generate Response", key=instruction):
    if instruction == "":        
        st.error("Please enter a prompt...")
    else:
        with st.spinner("Wait for it..."):    
            
            start_time = time.time()
            prompt = f"""Human: {instruction}

            Assistant:"""

            inference_modifier = {
                "max_tokens_to_sample": max_tokens_to_sample,
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p,
                "stop_sequences": ["\n\nHuman"],
            }
            
            textgen_llm = Bedrock(
                model_id="anthropic.claude-v2",
                client=boto3_bedrock,
                model_kwargs=inference_modifier,
            )
            
            response = textgen_llm(prompt)

            st.write(response)

            execution_time = round(time.time() - start_time, 2)

            st.success("Done!")
            st.caption(f"Execution time: {execution_time} seconds")