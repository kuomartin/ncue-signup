import ddddocr
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from concurrent.futures.thread import ThreadPoolExecutor
import asyncio
import sys
import os
import yaml

with open('profile.yml','r') as stream:
    profile=yaml.safe_load(stream)


login_url = profile['login_url']
even_id = profile['even_id']
name = profile['user']['name']
passwd = profile['user']['password']
headless=profile['headless']
sys.stdout = sys.stderr = open(os.devnull, "a", encoding='UTF-8')
ocr = ddddocr.DdddOcr()

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
if headless:options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')


driver = webdriver.Chrome('chromedriver', options=options)

driver.quit()


def main(url):
    driver = webdriver.Chrome('chromedriver', chrome_options=options)
    driver.get(login_url)
    time.sleep(1)
    user_id = driver.find_element(By.ID, "Ecom_User_ID")
    user_id.click()
    user_id.send_keys(name)

    user_passwd = driver.find_element(By.NAME, "Ecom_Password")
    user_passwd.click()
    user_passwd.send_keys(passwd)
    login = driver.find_element(By.NAME, "LoginButton")
    login.click()
    driver.get(url)
    try:
        while True:
            driver.switch_to.alert.accept()
    except BaseException:
        pass
    png = driver.find_element(By.ID, "imgcode").screenshot_as_png
    res = ocr.classification(png)
    print("res:", res)
    check = driver.find_element(By.NAME, "checkword")
    check.click()
    check.send_keys(res)
    meals = driver.find_elements(By.NAME, "meal")
    for meal in meals:
        meal.click()
        if meal.get_attribute("value") == '2':
            break
    send = driver.find_element(By.NAME, "B1")
    send.click()
    driver.quit()


executor = ThreadPoolExecutor(20)


def scrape(url, *, loop):
    loop.run_in_executor(executor, main, url)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    for url in [
            f"https://apss.ncue.edu.tw/sign_up/sign_app.php?crs_seq={i}" for i in even_id] * 20:
        scrape(url, loop=loop)

    loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop)))
