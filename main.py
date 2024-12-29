import pprint
import time

from numpy.f2py.auxfuncs import throw_error
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.webdriver import WebDriver
import pandas as pd

# variables
# ==============
# path to driver file
driver_path = "D:\\projects\\lib\\edgedriver_win64\\msedgedriver.exe"
# browser - edge, chrome, firefox - make sure to get the driver for corresponding browser
browser_type = "edge"
# first page link
page_link = "https://www.amazon.in/Toys-Games-Skillmatics/s?rh=n%3A1350380031%2Cp_89%3ASkillmatics"
# total number of pages to fetch the data from
max_pages_to_check = 1
# ==============


driver: WebDriver | None = None


def open_page():
    global driver
    driver.get(page_link)

def get_product_title(ele):
    try:
        title = ele.find_element(By.TAG_NAME, "h2").find_element(By.TAG_NAME, "span").text
        return title
    except Exception as e:
        print(e)

def get_product_link(ele):
    try:
        link = ele.find_element(By.TAG_NAME, "a").get_attribute("href")
        return link
    except Exception as e:
        print(e)

def get_product_price(ele):
    try:
        price = ele.find_element(By.CLASS_NAME, "a-price-whole").text
        return price
    except Exception as e:
        print(e)

def get_original_price(ele):
    try:
        original_price = ele.find_elements(By.CLASS_NAME, "a-price")[1].text
        original_price = original_price.replace("₹", "")
        return original_price
    except Exception as e:
        print(e)

def get_discount(ele, product):
    try:
        original_price = float(product.get("original_price").replace(",", ""))
        price = float(product.get("price").replace(",", ""))
        discount = round(((original_price - price) / original_price) * 100, 2)
        return discount
    except Exception as e:
        print(e)

def get_purchase_count(ele):
    try:
        purchase_count = ele.find_element(By.XPATH, '*//*[@data-cy="reviews-block"]/div[2]/span').text.split(" ")[0]
        return purchase_count
    except Exception as e:
        print(e)

def get_ratings(ele):
    try:
        ratings = ele.find_element(By.XPATH, '*//*[@data-cy="reviews-block"]/div[1]').find_elements(By.TAG_NAME, "span")[0].get_attribute("innerText").split(" ")[0]
        return ratings
    except Exception as e:
        print(e)

def get_rating_count(ele):
    try:
        ratings_count = ele.find_element(By.XPATH, '*//*[@data-cy="reviews-block"]/div[1]/a/span').text
        return ratings_count
    except Exception as e:
        print(e)

def get_image(ele):
    try:
        image = ele.find_element(By.TAG_NAME, "img")
        image_link = image.get_attribute("src")
        return image_link
    except Exception as e:
        print(e)

def get_age_group(ele):
    try:
        age_group = ele.find_element(By.XPATH, '*//*[@data-cy="product-details-recipe"]/div[1]/span').text
        return age_group
    except Exception as e:
        print(e)

def get_product_info():
    global driver
    products = []
    product_ele = driver.find_element(By.XPATH, "//*[@id=\"search\"]/div[1]/div[1]/div/span[1]/div[1]")
    product_list_ele = product_ele.find_elements(By.XPATH, '//*[@data-component-type="s-search-result"]')
    print(f"Found {len(product_list_ele)} products...")
    for ele in product_list_ele:
        driver.implicitly_wait(0)
        product = {
            "title": get_product_title(ele),
            "link": get_product_link(ele),
            "price": get_product_price(ele),
            "original_price": get_original_price(ele),
            "purchase_count": get_purchase_count(ele),
            "ratings": get_ratings(ele),
            "ratings_count": get_rating_count(ele),
            "image": get_image(ele),
            "age_group": get_age_group(ele),
        }
        product["discount"] = get_discount(ele, product)
        driver.implicitly_wait(5)
        products.append(product)
        pprint.pprint(product, indent=4)
        print("\n=======================================\n")

    return products


def get_next_page():
    global driver
    try:
        spans = driver.find_element(By.CLASS_NAME, "s-pagination-strip").find_elements(By.TAG_NAME, "span")
        last_span = spans[len(spans) - 1]
        if last_span.get_attribute("disabled") == "true":
            return False
        last_span.click()
        return True
    except Exception as e:
        print(e)
        return False


def write_to_file(products):
    print("Writing to file...")
    df = pd.DataFrame(products)
    df.to_csv("output.csv", index=False)
    print("Done!")


def load_webdriver():
    global driver
    service = Service(driver_path)
    if browser_type == "edge":
        driver = webdriver.Edge(service=service)
    elif browser_type == "chrome":
        driver = webdriver.Chrome(service=service)
    elif browser_type == "firefox":
        driver = webdriver.Firefox(service=service)
    else:
        throw_error("Invalid browser type")

def main():
    global driver

    final_products = []
    page_count = 0

    load_webdriver()
    open_page()

    while page_count < max_pages_to_check:
        print("Loading page number: " + str(page_count + 1))
        while driver.execute_script("return document.readyState") != "complete":
            print("waiting for page to load...")
            time.sleep(1)
        # wait 5 second explictly due to js loading the items
        print("waiting for 5 seconds...")
        time.sleep(5)
        products = get_product_info()
        final_products += products
        page_count += 1
        if not get_next_page():
            break

    write_to_file(final_products)

    input("Press Enter to close the browser...")
    driver.quit()


if __name__ == "__main__":
    main()
