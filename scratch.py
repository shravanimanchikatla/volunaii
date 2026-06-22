import requests
import time

s = requests.Session()

# 1. Sign up a fake organizer
s.post("http://localhost:8080/signup", data={
    "name": "Test Organizer",
    "email": "testorg@gmail.com",
    "password": "password",
    "role": "organizer",
    "skills": ""
})

# 2. Login
s.post("http://localhost:8080/login", data={
    "email": "testorg@gmail.com",
    "password": "password"
})

# 3. Create a fake webm file
fake_audio = b"RIFFfakeaudiofilecontent"

# 4. Submit report
files = {'report_file': ('test.webm', fake_audio, 'audio/webm')}
data = {'raw_text': ''}
r = s.post("http://localhost:8080/submit_report", data=data, files=files)
r_org = s.get("http://localhost:8080/organizer")

import re
flashes = re.findall(r'class="alert.*?>(.*?)<', r_org.text, re.IGNORECASE)
print("Flashed messages:", flashes)
