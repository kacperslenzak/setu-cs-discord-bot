from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import imgkit
import time

config = imgkit.config(wkhtmltoimage="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltoimage.exe")  # this is typically set in your computers env vars


def fetch_timetable_image(week=None):
    url = "https://studentssp.setu.ie/timetables/StudentGroupTT.aspx"

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Select dropdowns
    Select(driver.find_element("id", "cboSchool")).select_by_value("SS")
    Select(driver.find_element("id", "CboDept")).select_by_value("548715F70874B2B1561DDC98FE61E5C0")
    Select(driver.find_element("id", "CboPOS")).select_by_value("85EA4CF769354ECAD9F18363EC561526")
    Select(driver.find_element("id", "CboStudParentGrp")).select_by_value("kcmsc_b1-W_W3/W4")
    # Select(driver.find_element("id", "CboWeeks")).select_by_value("")  # setu timetable website inputs the current week itself. can be overriden

    driver.find_element("id", "BtnRetrieve").click()
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    timetable_div = soup.find("div", {"id": "divTT"})
    driver.quit()

    if not timetable_div:
        raise RuntimeError(f"No timetable found for week {week}!")

    html_template = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                background: white;
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                font-size: 12px;
            }}
            td, th {{
                border: 1px solid #000;
                padding: 4px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        {str(timetable_div)}
    </body>
    </html>
    """

    # Generate PNG as bytes buffer (no file saving)
    image_bytes = imgkit.from_string(html_template, False, config=config)

    return image_bytes  # return image as stream of bytes
