from bs4 import BeautifulSoup
from datetime import date
import os
import pandas as pd
import requests
import re
import time
import traceback
    
# Returns a dataframe with urls for any odd lot forms filed for the given CIK_num
def get_odd_lot_form_url(CIK_num):
    try:
        # Search for the company with CIK number CIK_num
        search_results_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + \
            CIK_num + "&type=SC+TO-I&dateb=&owner=exclude&count=100"
        result_site = requests.get(search_results_url)
        data = result_site.text
        EDGAR_results_page = BeautifulSoup(data, 'html.parser')

        # Get list of tags with the string \"SC TO-I\", this signals a tender offer document.\n",
        sc_to_i_tag_list = EDGAR_results_page.find_all("td", string="SC TO-I")
        # If no tender offer tags found, quit now
        if len(sc_to_i_tag_list) < 1:
            return None

        final_dates = []
        final_urls = []
        for tag in sc_to_i_tag_list:
            # Get the url to the details page
            filing_details_url = tag.find_next("a")['href']  # extension for the document
            detail_url = "https://www.sec.gov/" + filing_details_url
            print(detail_url)

            # Get the html of the details page
            details_site = requests.get(detail_url)
            details_site_data = details_site.text
            FILING_detail_page = BeautifulSoup(details_site_data, 'html.parser')

            # Get the tender offer/tender ammendment 
            tender_document_tag = FILING_detail_page.find('td', string="Complete submission text file")
            tender_document_url = "https://www.sec.gov/" + tender_document_tag.find_next("a")['href']
            form = requests.get(tender_document_url)

            # If this tender offer has no odd lot provision, then skip this iteration and do
            # not add it
            if re.search(r'(odd lot)', form.text, re.IGNORECASE) is None:
                continue

            # Get date of tender offer
            row_cells = tag.find_next_siblings("td")
            date = pd.to_datetime(row_cells[2].get_text(), format='%Y-%m-%d', errors='ignore').date()

            # Add the information
            final_dates.append(date)
            final_urls.append(detail_url)
            
        if len(final_urls) < 1:
            return None
        # Return the information as a dataframe
        return pd.DataFrame({'cik': '"' + str(CIK_num) + '"', 'date': final_dates, 'url': final_urls})
    except:
        print("Exception occured while attempting to produce submission text file, returning None")
        traceback.print_exc()
        return None

# Returns a dataframe with general information about tender offers
def get_tender_offer_data(CIK_nums):
    ciks = []
    dates = []
    urls = []
    for CIK_num in CIK_nums:
        try:
            # Search for the company with CIK number CIK_num
            search_results_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + \
                CIK_num + "&type=SC+TO-I&dateb=&owner=exclude&count=100"
            result_site = requests.get(search_results_url)
            data = result_site.text
            EDGAR_results_page = BeautifulSoup(data, 'html.parser')

            # Get list of tags with the string \"SC TO-I\", this signals a tender offer document.\n",
            sc_to_i_tag_list = EDGAR_results_page.find_all("td", string="SC TO-I")
            # If no tender offer tags found, quit now
            if len(sc_to_i_tag_list) < 1:
                continue

            for tag in sc_to_i_tag_list:
                # Get the url to the details page
                filing_details_url = tag.find_next("a")['href']  # extension for the document
                detail_url = "https://www.sec.gov/" + filing_details_url
                print(detail_url)

#                 # Get the html of the details page
#                 details_site = requests.get(detail_url)
#                 details_site_data = details_site.text
#                 FILING_detail_page = BeautifulSoup(details_site_data, 'html.parser')
# 
#                 # Get the tender offer/tender ammendment 
#                 tender_document_tag = FILING_detail_page.find('td', string="Complete submission text file")
#                 tender_document_url = "https://www.sec.gov/" + tender_document_tag.find_next("a")['href']
#                 form = requests.get(tender_document_url)
# 
#                 # If this tender offer has no odd lot provision, then skip this iteration and do
#                 # not add it
#                 if re.search(r'(odd lot)', form.text, re.IGNORECASE) is None:
#                     continue

                # Get date of tender offer
                row_cells = tag.find_next_siblings("td")
                date = pd.to_datetime(row_cells[2].get_text(), format='%Y-%m-%d', errors='ignore').date()

                # Add the information
                ciks.append('"' + str(CIK_num) + '""')
                dates.append(date)
                urls.append(detail_url)

        except:
            print("Exception occured while attempting to produce submission text file, returning None")
            traceback.print_exc()
    
    return pd.DataFrame({'cik': ciks, 'date': dates, 'url': urls})

    
def main():
    print("Beginning running")
    with open("CIK_Numbers.txt", "r") as cik_numbers_file: 
        cik_numbers = cik_numbers_file.readlines()
        print(len(cik_numbers))
        # Get only the first 5000
        cik_numbers = cik_numbers[:5000]
        try:
            tender_offer_data = get_tender_offer_data(cik_numbers)
            tender_offer_data.to_csv("tender_offer_data_1.csv", index=False)
            """ 
            ### Get urls for odd lot forms
            url_data = pd.DataFrame(columns={'cik': [], 'date': [], 'url': []})
            try:
                for cik_number in cik_numbers:
                    df = get_odd_lot_form_urls(cik_number.rstrip())
                    if df is not None and not df.empty:
                        url_data = url_data.append(df, ignore_index=True)
                print(url_data)
                url_data.to_csv("url_data_7.csv", index=False)
            except:
                # If there is an exception, save what we have
                print("Exception occured. Writing now to not lose data")
                url_data.to_csv("url_data_7.csv", index=False)
                traceback.print_exc()
            """
        except:
            print("get_tender_offer_data failed")
            traceback.print_exc()

            
if __name__ == "__main__": 
    main()