# OKTA_AWS_LOGIN_SCRIPT
Python script to access AWS CLI via Okta.

```**Clone this git repo** : git clone --branch master https://github.com/IsmohiK/OKTA_AWS_LOGIN_SCRIPT.git ```  

1. Make sure You have python installed in the system. Install the necessary libraries per requirements.txt 
   (`pip install -r requirements.txt`).

2. Make sure File name : saml-providers.config has below section and content inside "/.aws" directory
   ```
  	  [devcoegiscsaml]
      apiUrl = *******************************
      SAMLurl = ******************************
   ```
   Make sure File name : config.config has below section and content inside "/.aws" directory
   ```
   [dev]
   region = us-east-1
   output = json
   ```

3. Navigate to the folder where you have cloned the repo. Example : `C:\\OKTA_AWS_LOGIN_SCRIPT` in cmd.

4. Run the script with command `python okta-aws-login-script.py <env>` (env : dev/test...)

5. It will create the necessary config files inside ```"/.aws"``` directory. Once the config files are created
   make sure you follow point 2. as it will exit the script with msg ```apiUrl for saml provider not found Hence add one```. Run the script again...

6. It will be prompted to enter the okta password. Please enter the password.
   ```
   Password is not saved in keychain or has been deleted, please enter your Okta password!!
   ```
   On pressing enter the password will be saved using keyring.
   
7. It will be then prompted to enter okta factorType i.e PUSH/TOKEN verify.
    ```
   1. OKTA-push
   2. OKTA-token:software:totp
   ```
Enter the choice 1/2...

8. It will be then prompted to enter AWS ROLE.
    ```
   1. GISC_SRE_EC2_FULL_ACCESS
   ```
Enter the choice 1/2...

9. Now enable the env by running command: 'set AWS_DEFAULT_PROFILE=<env_name>' as mentioned in the console 
   output.

10. This completes the session creation. Now check if the session is created using below command : 
    'aws --region us-east-1 ec2 describe-instances'
    Check the output and verify that the session is established with the correct account.



