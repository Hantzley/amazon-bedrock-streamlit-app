#!/usr/bin/env python3
import aws_cdk as cdk
import boto3

from aws_cdk import Aspects
from cdk_nag import AwsSolutionsChecks
from stack.vpc_stack import VpcStack
from stack.web_stack import WebStack

region_name = boto3.Session().region_name
account_id = boto3.client('sts').get_caller_identity().get('Account')
env=cdk.Environment(account=account_id, region=region_name)

app = cdk.App()

vpc_stack = VpcStack(app, "GenAiBedrockVpcStack", env=env)
WebStack(app, "GenAiBedrockWebStack", vpc=vpc_stack.vpc, env=env)

app.synth()

Aspects.of(app).add(AwsSolutionsChecks())