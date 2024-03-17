from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

import os
import requests
import img2pdf
import glob
from PIL import Image
from io import BytesIO
import re


if not os.path.exists('pdfs'):
    os.mkdir('pdfs')

if not os.path.exists('imgs'):
    os.mkdir('imgs')

# some images exceed pillow max size
Image.MAX_IMAGE_PIXELS = 933120000

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


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

dwn_mags = list(map(lambda s:s[s.rindex('\\')+1:s.rindex('.')],glob.glob("pdfs/*.pdf")))

not_dwn_mags = list(filter(lambda s:s[s.rindex('/')+1:] not in dwn_mags, mag_urls))

not_dwn_mags.sort(key=natural_keys)

for url in not_dwn_mags:
    issue_name = url[url.rindex('/')+1:]
    driver.get(url)
    images     = []
    element    = WebDriverWait(driver,1000).until(
        lambda driver: driver.find_element(By.CLASS_NAME,"flipbook-icon-th-large"))
    element.click()
    div_element      = driver.find_element(By.CLASS_NAME,'flipbook-thumbsScroller')
    img_elements     = div_element.find_elements(By.TAG_NAME,'img')
    img_elements     = list(map(lambda s:s.get_attribute('src'), img_elements))
    img_elements.sort(key=natural_keys)
    for pth in glob.glob("imgs/*.jpg"):
        os.remove(pth)
    for i, img in enumerate(img_elements):
        # img_src      = img.get_attribute('src')
        img_src      = img.replace("-scaled", '')
        response     = requests.get(img_src)
        image_data   = BytesIO(response.content)
        pillow_image = Image.open(image_data)
        path = "imgs/"+str(i)+".jpg"
        pillow_image.save(path)
    with open("pdfs/"+issue_name+".pdf","wb") as f:
        imgs_pth  =  glob.glob("imgs/*.jpg")
        imgs_pth.sort(key=natural_keys)
        f.write(img2pdf.convert(imgs_pth))


for pth in glob.glob("imgs/*.jpg"):
    os.remove(pth) 
if os.path.exists('imgs'):
    os.rmdir('imgs')