
# Streamlit demo application for Amazon Bedrock

This project offers a somple front-end application built with Streamlit to showcase Amazon Bedrock. 
You can deploy this CDK project in your AWS account. Alternatively, you can run the Streamlit application on your local machine. 
See sections below for instructions.


## Architecture
![Architecture](./images/architecture.png)


## Prequisites

Make sure you have access to the Bedrock models before using this application. You can request access to the Bedrock models through the console:

![Model Access](./images/model-access.png)


### Enable AWS IAM permissions for Bedrock
The AWS identity you assume from your notebook environment (which is the Studio/notebook Execution Role from SageMaker, or could be a role or IAM User for self-managed notebooks), must have sufficient AWS IAM permissions to call the Amazon Bedrock service.

To grant Bedrock access to your identity, you can:

Open the AWS IAM Console
Find your Role (if using SageMaker or otherwise assuming an IAM Role), or else User
Select Add Permissions > Create Inline Policy to attach new inline permissions, open the JSON editor and paste in the below example policy:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockFullAccess",
            "Effect": "Allow",
            "Action": ["bedrock:*"],
            "Resource": "*"
        }
    ]
}
```

If you are running the application from your local machine, make sure you have the following tools installed:
* AWS CLI
* Node.js
* IDE for your programming language
* AWS CDK Toolkit (v2.0 or later)
* Git, JQ, etc
* Docker


## Deploy application in your AWS account

We recommend you use an AWS Cloud9 development enviroment for this project. See this [Cloud9 setup guide](./cloud9.md).

Clone the repository and enter the project directory:

```
git clone https://github.com/Hantzley/amazon-bedrock-streamlit-app.git
cd amazon-bedrock-streamlit-app

```

Create a virtualenv on MacOS or Linux:

```
python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
source .venv/bin/activate
```


Once the virtualenv is activated, you can install the required dependencies.

```
pip install -r requirements.txt
```

If your account is not yet boostrapped for CDK, execute the following command:

```
cdk bootstrap
```

At this point you can now list the stacks in the project.

```
cdk ls
```
You should see the following output:

```
GenAiBedrockVpcStack
GenAiBedrockWebStack
```

Deploy the application as a container on Elastic Container Services in our AWS account:

```
cdk deploy GenAiBedrockWebStack
```
The `GenAiBedrockWebStack` depends on `GenAiBedrockVpcStack`. CDK will resolve that dependency and automatically deploy `GenAiBedrockVpcStack` first.

Copy the `WebApplicationServiceURL` from the output and paste it on your browser.


## Run application on your local machine

Alternatively, you can execute the Streamlit application on your local machine:

```
cd web-app
streamlit run Home.py 
```

The application should open in your browser.


Enjoy!


## Screenshots

### Text generation

![Text generation](./images/01-text-generation.png)

### Text summarization

![Text summarization](./images/02-text-summarization.png)

### Text to image

![Text to image](./images/03-text-to-image.png)

## Image to image

![Image to image](./images/04-image-to-image.png)