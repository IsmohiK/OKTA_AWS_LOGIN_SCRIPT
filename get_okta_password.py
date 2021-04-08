import keyring
import getpass

def get_okta_password(username, saml_provider):
    """Handles getting the user password from keychain/keystorage/credvault"""

    service = "okta-aws-cli-{}".format(saml_provider)
    try:
        password = keyring.get_password(service, username)
        if password is None:
            print("Password is not saved in keychain or has been deleted, please enter your Okta password!!")
            password = getpass.getpass()
            keyring.set_password(service, username, password)
            return password
        else:
            return password
    except Exception as e:
        print(e)