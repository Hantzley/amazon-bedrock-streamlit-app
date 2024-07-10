import streamlit as st
import json
import os
import sys
import base64
import io
import time

from PIL import Image
st.set_page_config(
    page_title="Image to Image",
    layout="wide",
)
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

c1, c2 = st.columns([1, 8])
with c1:
    st.image("./imgs/bedrock.png", width=100)

with c2:
    st.header("Image to Image generation")
    st.caption("Using Stable Diffusion in Bedrock")

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

def image_to_base64(img) -> str:
    """Convert a PIL Image or local image file path to a base64 string for Amazon Bedrock"""
    if isinstance(img, str):
        if os.path.isfile(img):
            print(f"Reading image from file: {img}")
            with open(img, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        else:
            raise FileNotFoundError(f"File {img} does not exist")
    elif isinstance(img, Image.Image):
        print("Converting PIL Image to base64 string")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    else:
        raise ValueError(f"Expected str (filename) or PIL Image. Got {type(img)}")

col1, col2 = st.columns(2)

with col1:
   uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    with col2:
        image_width, image_height = image.size     

        if image_width > image_height:
            crop_delta = int(round((image_width - image_height) / 2))
            box = (crop_delta,0,(image_width-crop_delta),image_height)
            new_image = image.crop(box)
            image = new_image
        elif image_height > image_width:
            crop_delta = int(round((image_height - image_width) / 2))
            box = (0,crop_delta,image_width,(image_height-crop_delta))
            new_image = image.crop(box)
            image = new_image

        #resize image to 512px x 512px
        image = image.resize((512, 512))

        st.write("Source image")
        st.image(image, width=100) # Display source image

    init_image_b64 = image_to_base64(image)
    #st.write(init_image_b64[:80] + "...")    

    prompt = st.text_area("Prompt:", "high quality, with a dynamic and engaging background")

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
                        "init_image": init_image_b64,
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