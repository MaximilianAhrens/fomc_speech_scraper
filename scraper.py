# -*- coding: utf-8 -*-
# by Maximilian Ahrens | Oxford 2021

import os, glob, sys
import pandas as pd
import numpy as np
import random

# for email crash alert
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# for security
#import keyring

#=================================
# Email notifications
#=================================
def send_email_alert(email_message):
    email = 'create new email for this'
    send_to_email = 'maximilian.ahrens@outlook.com'
    subject = 'MALEX code | cluster {} | NEW LOCATION'.format(args.cluster)
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = send_to_email
    msg['Subject'] = subject
    message = email_message
    msg.attach(MIMEText(message, 'plain'))
    # Send the message via SMTP server.
    server = smtplib.SMTP_SSL('smtp.gmail.com')
    #server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    #server.starttls()
    server.login(email, keyring.get_password("email_alert", email))
    text = msg.as_string()
    server.sendmail(email, send_to_email, text)
    server.quit()
    print('email sent to ' + str(send_to_email))
    return


#=================================
# selenium-chrome
#=================================
def get_user_agent(): # occasionally check for updates on user-agent
    if sys.platform == "darwin":
         #return '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36' 
        return f'--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{random.randint(5,15)}_{random.randint(1,10)}) AppleWebKit/537.{random.randint(10,50)} (KHTML, like Gecko) Chrome/{random.randint(89,96)}.0.4389.{random.randint(10,200)} Safari/537.36'
    elif sys.platform == "linux":
        return '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'

    
def start_selenium_browser(headless = True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.set_capability('unhandledPromptBehavior', 'accept')
    chrome_options.set_capability("UNEXPECTED_ALERT_BEHAVIOUR", "ACCEPT")
    chrome_options.set_capability("unexpectedAlertBehaviour", "accept")
    chrome_options.set_capability("CapabilityType.UNEXPECTED_ALERT_BEHAVIOUR", "ACCEPT")
    chrome_options.set_capability("UnexpectedAlertBehaviour", "ACCEPT")
    # to cloak identity
    chrome_options.add_argument("window-size=1920,1080")

    #chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # add user agent
    chrome_options.add_argument(get_user_agent())

    # changed to $cdc_asdjflasutopfhvcZLmcfl_ to $abc_bteoxlasutojuvcZLgarch_ in chromedriver file
    # they need to be same length

    # use proxy IP
    #option.add_argument('proxy-server=106.122.8.51:3128')

    # to save resources
    prefs = {"profile.managed_default_content_settings.images":2,
             "profile.default_content_setting_values.notifications":2,
             "profile.managed_default_content_settings.stylesheets":2,
             "profile.managed_default_content_settings.cookies":2,
             "profile.managed_default_content_settings.javascript":1,
             "profile.managed_default_content_settings.plugins":1,
             "profile.managed_default_content_settings.popups":2,
             "profile.managed_default_content_settings.geolocation":2,
             "profile.managed_default_content_settings.media_stream":2,
    }
    #chrome_options.add_experimental_option("prefs",prefs)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # define driver
    if sys.platform == "darwin":
        driver = webdriver.Chrome("/Users/maximilianahrens/OneDrive - Nexus365/01_papers/2021 Central Bank speeches and risk signals/code/chromedriver/chromedriver_mac_96",
                                  options = chrome_options)
    elif sys.platform == "linux":
        #driver = webdriver.Chrome('/usr/bin/chromedriver_linux',options=chrome_options)
        driver = webdriver.Chrome('/RAPID',
                                  options=chrome_options)
    return driver




