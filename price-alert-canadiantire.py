from configparser import ConfigParser
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

config = ConfigParser()
config.read("creds")
email_user = config.get('email', 'user')
email_pass = config.get('email', 'pass')
config.read("items")
items_monitored = config.get('items', 'monitored')
ITEMS = []
filtersToCheck = items_monitored.split(', ')
for item in filtersToCheck:
    print("Adding item {} for monitoring".format(item))
    ITEMS.append(['{}.html'.format(item), 0])
# checking item status every 60 seconds
SLEEP_INTERVAL = 60
SMTP_URL = "smtp.gmail.com:587"
BASE_URL = "http://www.canadiantire.ca/en/pdp/"
XPATH_REGULAR_PRICE = '//span[@class="price__reg-value"]'
XPATH_SALE_PRICE = '//span[@class="price__total-value"]'
driver = webdriver.Chrome()


def send_email(element, price, discount):
    global BASE_URL
    try:
        s = smtplib.SMTP(SMTP_URL)
        s.starttls()
        s.login(email_user, email_pass)
    except smtplib.SMTPAuthenticationError:
        print("Failed to login")
    else:
        print("Logged in! Composing message..")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Item Alert {}%".format(discount)
        msg["From"] = email_user
        msg["To"] = email_user
        text = "Discount {0}% on Canadiantire! New price: {1} for product {2}".format(discount, price, BASE_URL+element)
        part = MIMEText(text, "plain")
        msg.attach(part)
        s.sendmail(email_user, email_user, msg.as_string())
        print("Message has been sent.")

while True:
    for item in ITEMS:
        #TODO if the comment is needed
        print("Checking item {}".format(item))
        driver.get(BASE_URL+item[0])
        try:
            salePriceElem = driver.find_element_by_xpath(XPATH_SALE_PRICE)
            regularPrice = float(driver.find_element_by_xpath(XPATH_REGULAR_PRICE).text[1:])
            salePrice = float(salePriceElem.text[1:])
            discountPercentage = round((salePrice - regularPrice) / regularPrice * 100, 2)
            if discountPercentage != item[1]:
                item[1] = discountPercentage
                print(discountPercentage)
                send_email(item[0], salePrice, discountPercentage)
        except NoSuchElementException:
            continue
    print("Sleeping for {} seconds".format(SLEEP_INTERVAL))
    time.sleep(SLEEP_INTERVAL)

driver.close()
