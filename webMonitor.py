# Importing libraries
import time
import sys
import hashlib
import configparser
from urllib.request import urlopen, Request
import webbrowser
from datetime import datetime

# Setup email for sending notification
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# configure configparser and loading variables from config.ini file
config = configparser.ConfigParser()
config.read('./config.ini')
config.sections()

# get variables from config.ini file
webSite = config.get('Conditions', 'webSite')
frequency = int(config.get('Conditions', 'frequency'))
sendingEmail = config.get('Conditions', 'sendingEmail')
accountPSWD = config.get('Conditions', 'accountPSWD')
recipientList = [config.get('Conditions', 'recipient1'), config.get('Conditions', 'recipient2')]
mailSubject = config.get('Conditions', 'mailSubject')
maxEmails = int(config.get('Conditions', 'maxEmails'))

#Set up users for email
gmail_user = sendingEmail
gmail_pwd = accountPSWD
recipients = recipientList

#Create Module
def mail(to, subject, text):
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()



# setting the URL you want to monitor

url = Request(webSite, headers={'User-Agent': 'Mozilla/5.0'})


# to perform a GET request and load the
# content of the website and store it in a var
response = urlopen(url).read()


# to create the initial hash
currentHash = hashlib.sha224(response).hexdigest()
print("running")
time.sleep(frequency)
counter = 0
while counter < maxEmails:
    try:
        now = datetime.now()
        print("checking for changes @", now)
        # perform the get request and store it in a var
        response = urlopen(url).read()

        # create a hash
        currentHash = hashlib.sha224(response).hexdigest()

        # wait for 30 seconds
        time.sleep(frequency)

        # perform the get request
        response = urlopen(url).read()

        # create a new hash
        newHash = hashlib.sha224(response).hexdigest()

        # check if new hash is same as the previous hash
        if newHash == currentHash:
            continue

        # if something changed in the hashes
        else:
            counter += 1
            # notify
            now = datetime.now()
            print("something changed @", now)

            #send it
            mail(recipients, webSite,"Site content changed @ {}".format(now))
            webbrowser.open_new(webSite)
            # again read the website
            response = urlopen(url).read()

            # create a hash
            currentHash = hashlib.sha224(response).hexdigest()

            # wait for 30 seconds
            time.sleep(frequency)
            continue

    # To handle exceptions
    except Exception as e:
        now = datetime.now()
        print("error @ ", now)
