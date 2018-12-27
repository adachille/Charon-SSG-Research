from bs4 import BeautifulSoup
import requests


def produce_submission_text_file(CIK_num):
    search_results_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + \
                 CIK_num + "&type=SC+TO-I&dateb=&owner=exclude&count=100"
    result_site = requests.get(search_results_url)
    data = result_site.text
    EDGAR_results_page = BeautifulSoup(data, 'html.parser')

    sc_to_i_list = EDGAR_results_page.find_all("td", string="SC TO-I")
    for form_td_tag in sc_to_i_list:
        filing_details_url = form_td_tag.find_next("a")['href']  # extension for the document

        detail_url = "https://www.sec.gov/" + filing_details_url
        details_site = requests.get(detail_url)
        details_site_data = details_site.text
        FILING_detail_page = BeautifulSoup(details_site_data, 'html.parser')

        submission_text_file = FILING_detail_page.find('td', string="Complete submission text file")
        final_file_url = submission_text_file.find_next("a")['href']
        final_url = "https://www.sec.gov/" + final_file_url

        form_sc_to_i = requests.get(final_url)
        new_form = open("SC-I Forms/" + CIK_num + ".txt", "w")
        new_form.write(form_sc_to_i.text)

def main():
    cik_numbers_file = open("CIK_Numbers.txt", "r")
    cik_numbers = cik_numbers_file.readlines()
    cik_numbers = cik_numbers[1000:10000]
    # i = 0
    for cik_number in cik_numbers:
        produce_submission_text_file(cik_number.rstrip())
        # print(str(i) + ": " + cik_number)
        # i += 1

if __name__ == "__main__": main()