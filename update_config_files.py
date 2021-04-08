import os

def updateCredentialsConfig(env, aws_temp_cred, credentials_config):
    if not credentials_config.has_section(env):
        credentials_config.add_section(env)

    credentials_config.set(env, 'aws_access_key_id', aws_temp_cred['AccessKeyId'])
    credentials_config.set(env, 'aws_secret_access_key', aws_temp_cred['SecretAccessKey'])
    credentials_config.set(env, 'aws_session_token', aws_temp_cred['SessionToken'])

def updateCredentialsCliFile(oktacli_config, oktacli_path, credentials_config, credentials_path):
    with open(credentials_path, 'w') as f:
        credentials_config.write(f)
    with open(oktacli_path, 'w') as f:
        oktacli_config.write(f)

def updateFiles(env, aws_temp_cred, oktacli_config, oktacli_path, credentials_config, credentials_path):
    updateCredentialsConfig(env, aws_temp_cred, credentials_config)
    updateCredentialsCliFile(oktacli_config, oktacli_path, credentials_config, credentials_path)
    if os.name == 'nt':
        print("\n Now enable the env by running command: 'set AWS_DEFAULT_PROFILE={}'\n".format(env))
    else:
        print("\n Make sure to enable this env: 'export AWS_DEFAULT_PROFILE={}'\n".format(env))