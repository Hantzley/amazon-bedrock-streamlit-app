import streamlit as st
import json
import os
import sys
import base64
import io
import time

from PIL import Image
st.set_page_config(
    page_title="Text to Image",
    layout="wide",
)

c1, c2 = st.columns([1, 8])
with c1:
    st.image("./imgs/bedrock.png", width=100)

with c2:
    st.header("Text to Image generation")
    st.caption("Using Stable Diffusion in Bedrock")

style_presets = ["3d-model", 
                 "analog-film",
                 "anime", 
                 "cinematic",
                 "comic-book",
                 "digital-art", 
                 "enhance", 
                 "fantasy-art", 
                 "isometric", 
                 "line-art", 
                 "low-poly", 
                 "modeling-compound",
                 "neon-punk", 
                 "origami", 
                 "photographic", 
                 "pixel-art", 
                 "tile-texture"]

selected_style_presets = st.sidebar.multiselect(
    "Select style presets (maximum 8):",
    style_presets,
    ["3d-model", "cinematic", "digital-art"],
    max_selections=8)

picture_width = st.sidebar.slider('Picture Width (px):', min_value=64, max_value=512, value=320, step=64)
cfg_scale = st.sidebar.slider('cfg_scale:', min_value=0, max_value=35, value=5, step=1)
steps = st.sidebar.slider('steps:', min_value=10, max_value=150, value=70, step=10)
seed = st.sidebar.number_input('seed:', min_value=0, max_value=4294967295, value=5450)



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

negative_prompts = [
    "poorly rendered",
    "poor background details",
    "poorly drawn mountains",
    "disfigured mountain features",
]

prompt = st.text_area("Prompt:", "Unicorn with beach in the background")

num_presets = len(selected_style_presets)

if st.button("Generate Image", key=prompt):

    if prompt == "" or num_presets == 0:        
        st.error("Please enter a valid prompt and select presets...")
    else:
        with st.spinner("Wait for it..."):
            
            start_time = time.time()

            tabs = st.tabs(selected_style_presets)

            x = range(num_presets)

            for n in x:

                request = json.dumps({
                    "text_prompts": (
                        [{"text": prompt, "weight": 1.0}]
                        + [{"text": negprompt, "weight": -1.0} for negprompt in negative_prompts]
                    ),
                    "cfg_scale": cfg_scale,
                    "seed": seed,
                    "steps": steps,
                    "style_preset": selected_style_presets[n],
                })
                modelId = "stability.stable-diffusion-xl-v1"

                response = boto3_bedrock.invoke_model(body=request, modelId=modelId)
                response_body = json.loads(response.get("body").read())

                print(response_body["result"])
                base_64_img_str = response_body["artifacts"][0].get("base64")
                print(f"{base_64_img_str[0:80]}...")

                image_1 = Image.open(io.BytesIO(base64.decodebytes(bytes(base_64_img_str, "utf-8"))))

                with tabs[n]:
                    st.header(selected_style_presets[n])
                    st.image(image_1, width=picture_width)

            execution_time = round(time.time() - start_time, 2)

            st.success("Done!")
            st.caption(f"Execution time: {execution_time} seconds")