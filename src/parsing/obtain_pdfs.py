import re
import os
import urllib.request
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

# method that will get the pdfs from the url
def get_pdf_links(driver, wd, linking_urls):

    # list that will hold all the pdfs
    pdf_list = []

    # get xpath for pdf link
    xpath = r'/html/body/div/div/div/div[2]/div/div/div/p/a'

    # iterate over each url and begin parsing
    for url in linking_urls:

        # scrape the current url
        driver.get(url)

        # throw try-catch just in case element is stale
        try:
            # fetch the pdf
            pdf_link = wd.until(EC.element_to_be_clickable((By.XPATH, xpath))).get_attribute('href')

            # append the pdf link
            pdf_list.append(pdf_link)
            print(url)

        # exception
        except:
            pass

    # stop the driver
    driver.quit()

    # return list
    return pdf_list


# scrape the pages with selenium
def find_pdfs(driver, wd, beginning_url):

    # list that will store links to pdf links
    pdf_link_list = []

    # get urls of all pages that contains company data
    urls, n_comp_per_page = get_pages(driver, wd, beginning_url)

    # iterate over all urls
    for i,url in enumerate(urls):

        # scrape the page
        driver.get(url)

        # iterate over all number of pages
        for j in range(n_comp_per_page):

            # get the xpath corresponding to the ith company on the given page
            xpath = f'/html/body/div[3]/div[3]/div[5]/div[1]/div[3]/div[2]/div[2]/div[2]/ul[2]/div[{j+1}]/li/p[1]/a'

            # throw try-catch block just in case element no longer can be accessed
            try:
                # get the link that maps to the pdf link
                link_to_pdf_link = wd.until(EC.element_to_be_clickable((By.XPATH, xpath))).get_attribute('href')

                # append the link to the list of links to pdf links
                pdf_link_list.append(link_to_pdf_link)

            # exception
            except:
                pass

    # get list of pdfs
    pdf_list = get_pdf_links(driver, wd, pdf_link_list)

    # return all links to pdf links
    return pdf_list


# method that gets urls of all pages to be scrapped
def get_pages(driver, wd, beginning_url):

    # list that represents all pages to be scrapped
    page_urls = []

    # scrape the current url
    driver.get(beginning_url)

    # get the xpath of the results number
    rnum_xpath = r'/html/body/div[3]/div[3]/div[5]/div[1]/div[3]/div[2]/div[1]/p'

    # get results number element
    results_ele = wd.until(EC.element_to_be_clickable((By.XPATH, rnum_xpath)))

    # remove comma for splitting purposes
    results_number = results_ele.text.replace(',', '')

    # extract all numbers
    nums = re.findall(r'\d+', results_number)

    # convert numbers to list
    _, n_companies_per_page, n_companies = [int(num) for num in nums]

    # find number of pages
    n_pages = round(n_companies / n_companies_per_page)

    # find xpath of next button
    next_path = r'//*[@id="yui-pg0-0-next-link"]'

    # iterate over number of pages
    for i in range(n_pages):

        # add the url to list of page urls
        page_urls.append(driver.current_url)

        # find the "next" button
        wd.until(EC.element_to_be_clickable((By.XPATH, next_path))).click()

    # return the pages to be scrapped
    return page_urls, n_companies_per_page

# method to save pdfs
def save_pdfs(pdf_dir, pdf_links):

    # iterate over all pdf links
    for link in pdf_links:

        # convert link (of type string) to pdf (of type bytes)
        pdf = urllib.request.urlopen(link)

        # fname
        fname = link.split('SWOTPDF/')[-1]

        # create an absolute path
        abs_path = os.path.join(pdf_dir, fname) + '.pdf'

        # open file
        with open(abs_path, 'wb') as fp:

            # write the pdf out
            fp.write(pdf.read())


# runner
if __name__ == "__main__":

    # scrape the SWOT website
    starting_url = 'https://bi-gale-com.ezproxy.lib.vt.edu/global/search?u=viva_vpi#displayGroup=swot&sort=articleTitle&log=false'

    # get driver path
    path = r'C:\Users\Haji\Projects\personal\SWOT-Analysis\geckodriver.exe'\

    # get path to save all pdfs
    pdf_dir = r'C:\Users\Haji\Projects\personal\SWOT-Analysis\data\pdfs'

    # create driver
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(executable_path=path, options=options)

    # get exceptions to ignore
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)

    # create WebDriverWait object
    wd = WebDriverWait(driver, 12, ignored_exceptions=ignored_exceptions)

    # scrape
    pdfs = find_pdfs(driver=driver, wd=wd, beginning_url=starting_url)

    # save the pdfs
    save_pdfs(pdfs, pdf_dir)