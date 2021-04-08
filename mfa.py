import json
import time

def verifymfa(response, payload, oktacli_config, oktasession, headers, stateToken=None):
    """Handle MFA for user"""
    mfa_list = []
    for factor in response['_embedded']['factors']:
        mfa_list.append(factor['provider'] + '-' + factor['factorType'])
    try:
        mfa = oktacli_config.get("default", "mfa_factor")
    except:
        count = 1
        for m in mfa_list:
            print(str(count) + ". " + m)
            count = count + 1
        mfa = input("Enter the choice")
        mfa = mfa_list[int(mfa)-1]
        if oktacli_config.has_section("default"):
            pass
        else:
            oktacli_config.add_section("default")
        oktacli_config.set('default', 'mfa_factor', mfa)

    mfa = mfa.split("-")
    factors = response['_embedded']['factors']
    ##print(factors)    
    for i in range(0,len(factors)):
        if (factors[i]['provider'] == mfa[0] and factors[i]['factorType'] == mfa[1]) :
            index = i
            break
    factorType = response['_embedded']['factors'][index]['factorType']
    factorId = response['_embedded']['factors'][index]['id']
    verifyUrl = response['_embedded']['factors'][index]['_links']['verify']['href']

    if factorType == "token:software:totp":
        tokenCode = input("OKTA MFA Code : ")
        payload = {'stateToken': stateToken, 'passCode': tokenCode}
        mfaverify = oktasession.post(verifyUrl, data=json.dumps(payload), headers=headers)
        sessionToken = json.loads(mfaverify.text)['sessionToken']
        status = json.loads(mfaverify.text)['status']
    elif factorType == "push":
        print("Check OktaVerify app to verify the push request sent!!")
        payload = {'stateToken': stateToken}
        sessionToken = None
        while sessionToken is None:
            temp = oktasession.post(verifyUrl, data=json.dumps(payload), headers=headers)
            status = json.loads(temp.text)['status']
            if status == 'SUCCESS':
                sessionToken = json.loads(temp.text)['sessionToken']
            elif status == 'TIMEOUT':
                print("Push Request timed out. Try again.")
                sys.exit(1)
            else:
                time.sleep(4)

    return status, sessionToken
