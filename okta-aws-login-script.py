import os
import sys
import configparser
import requests
import json
import re
import base64
import keyring
import boto3
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from mfa import verifymfa
from get_okta_password import get_okta_password
from update_config_files import updateFiles

#### Get the username from Environment varibale ####
username = os.environ['USERNAME']
basepath = os.environ['USERPROFILE']
print("username : ",username)
print("basepath : ",basepath)

##### Takes the environment as input #####

if not len(sys.argv) > 1:
    print("Error!! Specify the environment Also. Thanks!!")
    sys.exit(1)
else:
	print("Environment : ", sys.argv[1])



#### Getting file path for aws config ####
aws_dir = basepath + "/.aws"
config_path = basepath + "/.aws/config"
oktacli_path = basepath + "/.aws/oktacli"
credentials_path = basepath + "/.aws/credentials"
saml_providers_path = basepath + "/.aws/saml-providers"
env = sys.argv[1]

#### Creating .aws directory if not present ####
if not os.path.exists(aws_dir):
    print(".aws directory not present. hence creating one")
    os.makedirs(aws_dir)
    print(aws_dir, "created")
else:
    print(aws_dir, "found")

######################################################################################################
#### Reading the config file nad creating one if we are not getting ####
config_configuration = configparser.ConfigParser()
if os.path.isfile(config_path):
    config_configuration.read(config_path)
    print(config_path + " found")
else:
    print("AWS config file not found Hence creating one")
    create_file = open(config_path, "w")
    config_configuration.add_section("Profile "+env)
    print(config_path + " created")
    config_configuration.write(create_file)
    create_file.close()

oktacli_config = configparser.ConfigParser()
if os.path.isfile(oktacli_path):
    oktacli_config.read(oktacli_path)
    print(oktacli_path + " found")
else:
    print("AWS okta cli config file not found Hence creating one")
    print("AWS config file not found Hence creating one")
    create_file = open(oktacli_path, "w")
    oktacli_config.add_section(env)
    print(oktacli_path + " created")
    oktacli_config.write(create_file)
    create_file.close()
    oktacli_config.read(oktacli_path)

credentials_config = configparser.ConfigParser()
if os.path.isfile(credentials_path):
    credentials_config.read(credentials_path)
    print(credentials_path + " found")
else:
    print("AWS credentials config file not found Hence creating one")
    create_file = open(credentials_path, "w")
    credentials_config.add_section(env)
    print(credentials_path + " created")
    credentials_config.write(create_file)
    create_file.close()
    credentials_config.read(credentials_path)

saml_providers_config = configparser.ConfigParser()
saml_provider = env + "coegiscsaml"
if os.path.isfile(saml_providers_path):
    saml_providers_config.read(saml_providers_path)
    print(saml_providers_path + " found")
else:
    print("AWS saml_providers config file not found Hence creating one")
    create_file = open(saml_providers_path, "w")
    saml_providers_config.add_section(saml_provider)
    print(saml_providers_path + " created")
    saml_providers_config.write(create_file)
    create_file.close()
    saml_providers_config.read(credentials_path)



#####################################################################################################

if saml_providers_config.has_section(saml_provider):
    apiUrl = saml_providers_config.get(saml_provider, "apiUrl")
    print("apiUrl found")
else:
    print("apiUrl for saml provider not found Hence add one")
    sys.exit(1)

if saml_providers_config.has_section(saml_provider):
    SAMLurl = saml_providers_config.get(saml_provider, "SAMLurl")
    print("SAMLurl found")
else:
    print("SAMLurl for saml provider not found Hence add one")
    sys.exit(1)

headers = {}
payload = {}
conf_dict = {}

#### Getting password from user ####
password = get_okta_password(username, saml_provider)

#### Creating header ####
headers['Accept'] = 'application/json'
headers['Content-Type'] = 'application/json'

#### creating okta session ####
oktasession = requests.Session()

url = "{}/authn".format(apiUrl)
payload['username'] = username
payload['password'] = password

login = oktasession.post(url, headers=headers, data=json.dumps(payload))
if login.status_code == 401:
    login_response = json.loads(login.text)
    print(login_response)
    keyring.delete_password(keyring_service(saml_provider), username)
    sys.exit(1)

try:
    status = json.loads(login.text)['status']
except Exception as e:
    print(e)
    keyring.delete_password(keyring_service(saml_provider), username)
    sys.exit(1)

if status == "SUCCESS":
    sessionToken = json.loads(login.text)['sessionToken']

elif status == "MFA_REQUIRED":
    stateToken = json.loads(login.content)['stateToken']
    oktacli_config.read(oktacli_path)
    status, sessionToken = verifymfa(json.loads(login.text), payload, oktacli_config,oktasession,headers, stateToken)
    print("The status of sessionToken creation for MFA : ", status)

elif status != 'SUCCESS':
    print("Something went wrong. Please try again!!")
    sys.exit(1)


redirect_url = "https://sonytech.okta.com/login/sessionCookieRedirect?checkAccountSetupComplete=true&token=" + sessionToken + "&redirectUrl=" + SAMLurl
testurl = oktasession.get(redirect_url)

'''
 Obtain the SSO AppLink URL from for the AWS chicklet
'''
sso_appLink = oktasession.get(SAMLurl, headers=headers)
SAMLResponseHtmlParser = BeautifulSoup(sso_appLink.text, "html.parser")
for inputTag in SAMLResponseHtmlParser.find_all('input'):
    if inputTag.get('name') == 'SAMLResponse':
        SAMLResponse = inputTag.get('value')

#### Get the Role List ####
base = ET.fromstring(base64.b64decode(SAMLResponse))
saml_xmlns = "{urn:oasis:names:tc:SAML:2.0:assertion}"
saml_attribute = saml_xmlns + "Attribute"
saml_attributevalue = saml_xmlns + "AttributeValue"
saml_role_url = "https://aws.amazon.com/SAML/Attributes/Role"
role_list = []
for saml_attribute in base.iter(saml_attribute):
    if saml_attribute.get('Name') == saml_role_url:
        for attributevalue in saml_attribute.iter(saml_attributevalue):
            role_list.append(attributevalue.text)
count = 1
for role in role_list:
    print(str(count) + ". " + role.split("role/")[1])
    count = count + 1
choice = input("Enter the choice 1/2/3... ")
arns = role_list[int(choice)-1].split(',')
arn_dict = {}
for arn in arns:
    if ":role/" in arn:
        arn_dict['RoleArn'] = arn
    elif ":saml-provider/":
        arn_dict['PrincipalArn'] = arn
arn_dict['SAMLResponse'] = SAMLResponse

'''
Returns a set of temporary security credentials for users who have been authenticated
via a SAML authentication response.
'''
sts_client = boto3.client('sts')
response = sts_client.assume_role_with_saml(RoleArn=arn_dict['RoleArn'],
                                            PrincipalArn=arn_dict['PrincipalArn'],
                                            SAMLAssertion=arn_dict['SAMLResponse'])

aws_temp_cred = response['Credentials']

'''
Creates a session. A session stores configuration state.
'''

role_session = boto3.session.Session(
    aws_access_key_id=aws_temp_cred['AccessKeyId'],
    aws_secret_access_key=aws_temp_cred['SecretAccessKey'],
    aws_session_token=aws_temp_cred['SessionToken'])

updateFiles(env, aws_temp_cred, oktacli_config, oktacli_path, credentials_config, credentials_path)

