from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

import os
import requests
# from fpdf import FPDF
import img2pdf
import glob
from PIL import Image
from io import BytesIO


if not os.path.exists('pdfs'):
    os.mkdir('pdfs')

if not os.path.exists('imgs'):
    os.mkdir('imgs')

# driver_path = r"chromedriver.exe"
options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)


driver.get("https://www.dbazi.com/magazine-archives")

mag_urls = []

while True:
    buttons = driver.find_elements(By.CLASS_NAME, "read-magz")
    for b in buttons:
        mag_urls.append(b.get_attribute('href'))
    
    if not driver.find_elements(By.CLASS_NAME,"next"):
        break

    next_page = driver.find_elements(By.CLASS_NAME,"next")[0]
    href_next_page = next_page.get_attribute('href')
    driver.get(href_next_page)

# there are always two href from a url
mag_urls = list(set(mag_urls))
mag_urls = sorted(mag_urls)



for url in mag_urls:
    issue_name = url[url.rindex('/')+1:]
    driver.get(url)
    images     = []
    element    = WebDriverWait(driver,60).until(
        lambda driver: driver.find_element(By.CLASS_NAME,"flipbook-icon-th-large"))
    element.click()
    div_element      = driver.find_element(By.CLASS_NAME,'flipbook-thumbsScroller')
    img_elements     = div_element.find_elements(By.TAG_NAME,'img')

    for i, img in enumerate(img_elements):
        img_src      = img.get_attribute('src')
        img_src      = img_src.replace("-scaled", '')
        response     = requests.get(img_src)
        image_data   = BytesIO(response.content)
        pillow_image = Image.open(image_data)
        path = "imgs/"+str(i)+".jpg"
        pillow_image.save(path)
        # print(glob.glob("imgs/*.jpg"))
    with open("pdfs/"+issue_name+".pdf","wb") as f:
        f.write(img2pdf.convert(glob.glob("imgs/*.jpg")))


    
if os.path.exists('imgs'):
    os.rmdir('imgs')