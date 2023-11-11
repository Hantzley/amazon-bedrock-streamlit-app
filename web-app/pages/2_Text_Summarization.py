import streamlit as st
import json
import os
import sys
import time

st.set_page_config(
    page_title="Text Summarization",
    layout="wide",
)
c1, c2 = st.columns([1, 8])
with c1:
    st.image("./imgs/bedrock.png", width=100)

with c2:
    st.header("Text summarization")
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

sample_text_1 = """AWS took all of that feedback from customers, and today we are excited to announce Amazon Bedrock, \
a new service that makes FMs from AI21 Labs, Anthropic, Stability AI, and Amazon accessible via an API. \
Bedrock is the easiest way for customers to build and scale generative AI-based applications using FMs, \
democratizing access for all builders. Bedrock will offer the ability to access a range of powerful FMs \
for text and images—including Amazons Titan FMs, which consist of two new LLMs we’re also announcing \
today—through a scalable, reliable, and secure AWS managed service. With Bedrock’s serverless experience, \
customers can easily find the right model for what they’re trying to get done, get started quickly, privately \
customize FMs with their own data, and easily integrate and deploy them into their applications using the AWS \
tools and capabilities they are familiar with, without having to manage any infrastructure (including integrations \
with Amazon SageMaker ML features like Experiments to test different models and Pipelines to manage their FMs at scale)."""

sample_text_2 = """Customer: Hi there, I'm having a problem with my iPhone.
Agent: Hi! I'm sorry to hear that. What's happening?
Customer: The phone is not charging properly, and the battery seems to be draining very quickly. I've tried different charging cables and power adapters, but the issue persists.
Agent: Hmm, that's not good. Let's try some troubleshooting steps. Can you go to Settings, then Battery, and see if there are any apps that are using up a lot of battery life?
Customer: Yes, there are some apps that are using up a lot of battery.
Agent: Okay, try force quitting those apps by swiping up from the bottom of the screen and then swiping up on the app to close it.
Customer: I did that, but the issue is still there.
Agent: Alright, let's try resetting your iPhone's settings to their default values. This won't delete any of your data. Go to Settings, then General, then Reset, and then choose Reset All Settings.
Customer: Okay, I did that. What's next?
Agent: Now, let's try restarting your iPhone. Press and hold the power button until you see the "slide to power off" option. Slide to power off, wait a few seconds, and then turn your iPhone back on.
Customer: Alright, I restarted it, but it's still not charging properly.
Agent: I see. It looks like we need to run a diagnostic test on your iPhone. Please visit the nearest Apple Store or authorized service provider to get your iPhone checked out.
Customer: Do I need to make an appointment?
Agent: Yes, it's always best to make an appointment beforehand so you don't have to wait in line. You can make an appointment online or by calling the Apple Store or authorized service provider.
Customer: Okay, will I have to pay for the repairs?
Agent: That depends on whether your iPhone is covered under warranty or not. If it is, you won't have to pay anything. However, if it's not covered under warranty, you will have to pay for the repairs.
Customer: How long will it take to get my iPhone back?
Agent: It depends on the severity of the issue, but it usually takes 1-2 business days.
Customer: Can I track the repair status online?
Agent: Yes, you can track the repair status online or by calling the Apple Store or authorized service provider.
Customer: Alright, thanks for your help.
Agent: No problem, happy to help. Is there anything else I can assist you with?
Customer: No, that's all for now.
Agent: Alright, have a great day and good luck with your iPhone!"""

instruction = st.text_area("Instruction:", "Please provide a summary of the following text.")

st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
sample_text = st.sidebar.radio(
    "Select sample text or type your own:",
    ["Sample 1", "Sample 2"],
    horizontal=True
    )

max_tokens_to_sample = st.sidebar.slider("max_tokens_to_sample:", min_value=500, max_value=4096, value=4096)
temperature = st.sidebar.slider("temperature:", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
top_k = st.sidebar.slider('top_k:', min_value=10, max_value=500, value=250, step=10)
top_p = st.sidebar.slider('top_p:', min_value=0.0, max_value=1.0, value=0.5, step=0.1)

if sample_text == "Sample 1":
    text = st.text_area("Input Text:", sample_text_1, height=300)
elif sample_text == "Sample 2":
    text = st.text_area("Input Text:", sample_text_2, height=300)

if st.button("Generate Response", key=instruction):
    if text == "" or instruction == "":        
        st.error("Please enter a valid instruction and text...")
    else:
        with st.spinner("Wait for it..."):    
            
            start_time = time.time()
            prompt = f"""Human: {instruction}
            <text>
            {text}
            </text>

            Assistant:"""

            body = json.dumps({"prompt": prompt,
                "max_tokens_to_sample":4096,
                "temperature": temperature,
                "top_k": top_k,
                "top_p":top_p,
                "stop_sequences":[]
                }) 

            response = boto3_bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
            response_body = json.loads(response.get('body').read())

            st.write(response_body.get('completion'))

            execution_time = round(time.time() - start_time, 2)

            st.success("Done!")
            st.caption(f"Execution time: {execution_time} seconds")