from tkinter import *
import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import date
from tkinter import messagebox
import pyautogui
import datetime


def scraper():
    time.sleep(5)
    ab = 1
    while True:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            ch = driver.find_element_by_xpath('//*[@id="colMain_contentMain"]/div/ul/li[{}]/a'.format(ab)).text
            chh = driver.find_element_by_xpath('//*[@id="colMain_contentMain"]/div/ul/li[{}]/a'.format(ab))
            if "results" in ch:
                if ".zip" in ch:
                    print("Founded!! Downloading  {}".format(ch) )
                    chh.click()

            elif "Results" in ch:
                if ".zip" in ch:
                    print("Founded!! Downloading  {}".format(ch))
                    chh.click()
            elif "RESULTS" in ch:
                if ".zip" in ch:
                    print("Founded!! Downloading  {}".format(ch))
                    chh.click()

            ab += 1
        except:
            break


def link_open():
    global i
    for i in url_map:
        driver.get(i)
        time.sleep(5)
        scraper()


f = open("link.txt", "w")

driver = webdriver.Chrome()
driver.get('https://www.teamunify.com/team/szfllsc/page/legacy?url=%2FEventsPast.jsp%3Fteam%3Dszfllsc')

event = driver.find_element_by_xpath('//*[@id="event_cat"]').click()
time.sleep(5)
event_select = driver.find_element_by_xpath('//*[@id="event_cat"]/option[9]').click()
time.sleep(3)
event = driver.find_element_by_xpath('//*[@id="event_cat"]').click()
time.sleep(2)
datestart = driver.find_element_by_name('date_start').send_keys('01/01/2010')
dateend = driver.find_element_by_name('date_end').send_keys('01/10/2020')
time.sleep(2)
submitclk =driver.find_element_by_class_name('button').click()
time.sleep(2)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
elems = driver.find_elements_by_xpath("//a[@href]")

url_map = []
for elem in elems:
    if elem.get_attribute("href").split("team/szfllsc/page/legacy?url=%2FEventShow")[0] == "https://www.teamunify.com/" and elem.get_attribute(
            "href") != "https://www.teamunify.com/":
        if elem.get_attribute("href") not in url_map:
            check= elem.find_element_by_class_name("event-title-link").text
            if "RESULTS" in check:
                url_map.append(elem.get_attribute("href"))
                f.write(elem.get_attribute("href"))
                f.write("\n")
                continue
            elif "results" in check:
                url_map.append(elem.get_attribute("href"))
                f.write(elem.get_attribute("href"))
                f.write("\n")
                continue

            elif  "Results" in check:
                url_map.append(elem.get_attribute("href"))
                f.write(elem.get_attribute("href"))
                f.write("\n")
                continue

link_open()
