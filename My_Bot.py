from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import undetected_chromedriver as uc
import pandas as pd
import unicodedata
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import re
import argparse
from selenium.webdriver.chrome.service import Service



# from apscheduler.schedulers.background import BackgroundScheduler

current_date = datetime.now()

# HANDLE INPUT
# The function that can return a string without diacritics


def remove_diacritics(input_str):
    # Normalize the string to decompose diacritics
    normalized_str = unicodedata.normalize('NFD', input_str)
    # Filter out combining characters (diacritics)
    without_diacritics = ''.join(char for char in normalized_str if unicodedata.category(char) != 'Mn')
    # Replace 'đ' with 'd' and 'Đ' with 'D'
    return without_diacritics.replace('đ', 'd').replace('Đ', 'D')


def the_scraped_web(city, details_of_job):
    try:
        city_list = [
            'da nang', 'dn', 'ha noi', 'hn', 'quang ngai', 'ha tinh', 
            'long xuyen', 'sam son', 'bao loc', 'lai chau', 'hai duong', 'ha tien', 'quang tri', 
            'bac kan', 'da lat', 'tuyen quang', 'ayun pa', 'tan uyen', 'ba don', 'phuc yen', 
            'nghia lo', 'cao lanh', 'vi thanh', 'go cong', 'nam dinh', 'tay ninh', 'son la', 
            'phu quoc', 'phan thiet', 'hong linh', 'mong cai', 'hong ngu', 'nghi son', 'binh long', 
            'cao bang', 'thai binh', 'dien bien phu', 'nga nam', 'hoi an', 'phan rang - thap cham', 
            'chau doc', 'tam ky', 'nha trang', 'song cau', 'lang son', 'song cong', 'vung tau', 
            'thu dau mot', 'rach gia', 'duc pho', 'bien hoa', 'phu ly', 'quy nhon', 'thuan an', 
            'vinh yen', 'dong xoai', 'bac lieu', 'yen bai', 'gia nghia', 'tu son', 'buon ma thuot', 
            'di an', 'pleiku', 'tan an', 'soc trang', 'ha giang', 'tam diep', 'bim son', 'tuy hoa', 
            'vinh chau', 'uong bi', 'phuoc long', 'thanh hoa', 'long khanh', 'kien tuong', 'can tho', 
            'ha long', 'cam ranh', 'thai hoa', 'cam pha', 'ky anh', 'dong trieu', 'viet tri', 
            'bac ninh', 'dong hoi', 'hue', 'cua lo', 'dong ha', 'pho yen', 'hoa binh', 'vinh long', 
            'sa dec', 'hoang mai', 'thai nguyen', 'ben tre', 'ca mau', 'buon ho', 'lao cai', 
            'bac giang', 'hung yen', 'chi linh', 'ninh binh', 'vinh', 'nga bay', 'duy tien', 
            'ba ria', 'tra vinh', 'cai lay', 'phu tho', 'my hao', 'my tho', 'kon tum', 'an khe'
        ]
        
        # User input
        # city = str(input('Enter the city in Viet Nam that you want to find a job: '))
        city_name0 = remove_diacritics(city).lower().strip()
        city_name = re.sub(r'[\s]+',' ',city_name0)
            
        # details_of_job = str(input('Enter job title or skill: ')).lower().strip()
        detailed_job = re.sub(r'[\s,]+|[,\s]+', ' ', details_of_job)
            
        formated_detailed_job = re.sub(r'[\s,]+|[,\s]+|[\s]+', '-', detailed_job)
        formated_city_name = re.sub(r'[\s]+', '-',city_name)
        # print(formated_city_name)
        website = 'https://itviec.com/'

        # Check the input value and create a link to load data depend on the user input
        slug_web = '?job_selected='
        if city_name == 'all cities' or city_name == '':
            if formated_detailed_job:
                scraped_web = website + 'it-jobs/' + formated_detailed_job + slug_web 
            else:
                scraped_web = website + 'it-jobs/' + slug_web 
        elif city_name == 'ho chi minh' or city_name =='hcm':
            if formated_detailed_job:
                scraped_web = website + 'it-jobs/' + formated_detailed_job + '/' + formated_city_name + '-hcm' + slug_web
            else:
                scraped_web = website + 'it-jobs/' + formated_city_name + '-hcm' + slug_web 
        elif city_name in city_list:
            if formated_detailed_job:
                scraped_web = website + 'it-jobs/' + formated_detailed_job + '/' + formated_city_name + slug_web
            else:
                scraped_web = website + 'it-jobs/' + formated_city_name + slug_web
        else:
            if formated_detailed_job:
                scraped_web = website + 'it-jobs/' + formated_detailed_job + '/' + 'others' + slug_web
            else:     
                scraped_web = website + 'it-jobs/' + 'others' + slug_web
        return (scraped_web)
        # print (scraped_web)
    except Exception as e:
        print (f'Error: {e}')


# anumber_of_pages = ''
def get_number_of_pages(scraped_web):
    # global scraped_web
    # global anumber_of_pages
    # url = web
    url = scraped_web
    # url = 'https://itviec.com/it-jobs?job_selected'

    # Navigate to the URL
    chrome_options = uc.ChromeOptions()
    chrome_options.binary_location = "/usr/bin/google-chrome"  # Path to Chrome binary
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = uc.Chrome(options=chrome_options)


    # Get the page source after the content is fully loaded
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    try:    
        paginations = soup.find('div', 'pagination-search-jobs d-flex justify-content-center ipb-16')
        # print (paginations)
        pages = paginations.find_all('a')
        number_of_pages = pages[len(pages)-2].text
        # print(len(pages))
        driver.quit()
        return (number_of_pages)
        # print (anumber_of_pages)
    except Exception:
        driver.quit()
        return 1
# print (anumber_of_pages)

# """The function is used to get all the data of all pages on the link of the website, transfer the data that I crawl 
# from the website to a tabular with pandas library, and export the table to xlsx file"""

def scraping_jobs(scraped_web, num):
    Job_Title = []
    Compay_name = []
    Job_Location = []
    Kind_of_Job = []
    Job_Descriptions = []
    Posted_Date = []
    Skills = []
    Job_Link = []
    page = 1
    
    chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    try:
        while page <= int(num):
            page_str = '&page=' + str(page)
            url = scraped_web + page_str
            print (url)

            # Navigate to the URLx
            driver = uc.Chrome(options=chrome_options)
            driver.get(url)
            
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'job-card')))


            # Get the page source after the content is fully loaded
            page_source = driver.page_source

            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            column1 = soup.find('div', 'col-md-5 card-jobs-list ips-0 ipe-0 ipe-md-6')

            jobs = column1.find_all('div', 'job-card')

            # abjob = jobs[0:2]

            for job in jobs:
                
                # Find the slug of job url
                data_search_job = job.get('data-search--job-selection-job-slug-value')
                # print(data_search_job)

                # Get a job url
                job_url = scraped_web + data_search_job + page_str
                # print (job_url)

                # Navigate to the job URL
                driver.get(job_url)
                # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'preview-job-overview')))    
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'preview-job-overview')))
                
                # Get the job page source
                job_page_source = driver.page_source
                        
                # Parse the job page source with BeautifulSoup
                soup_job = BeautifulSoup(job_page_source, 'html.parser')

                print(soup_job.contents)
                column2 = soup_job.find('div', 'col-md-7 p-0')
                # print (column2)

                try:
                    # time.sleep(5)
                    # Find job title and company name
                    data1 = column2.find('div', class_="d-flex flex-column gap-2 fw-600")
                    job_title = data1.find('h2')
                    company_name = data1.find('a')
                    Job_Title.append(job_title.text)
                    Compay_name.append(company_name.text)
                    
                    # Find job link
                    data = job.find ('h3', 'imt-3')
                    slug = data.find('a')
                    slug_job_link = slug.get('href')
                    # print (slug_job_link)
                    job_link = 'https://itviec.com' + slug_job_link
                    # print (job_link)
                    Job_Link.append(job_link)
                    
                    # Find location, kind of job, posted date 
                    data2 = column2.find('section', 'preview-job-overview')
                    preview_job = data2.find('div', class_='d-inline-block text-dark-grey')
                    location = preview_job.find('span')
                    Job_Location.append(location.text)
                    # print (location.text)
                    preview_jobs = data2.find_all('div', class_='d-inline-block text-dark-grey preview-header-item')
                    for i, element in enumerate(preview_jobs):
                        prjob = element.find('span').text
                        if i == len(preview_jobs) - 2:
                            Kind_of_Job.append(prjob)
                        elif i == len(preview_jobs) - 1:
                            if 'day' in prjob:
                                num_days = int (prjob.split()[0])
                                posted_date = current_date - timedelta(days=num_days)
                            elif 'hour' in prjob:
                                num_hours = int (prjob.split()[0])
                                posted_date = current_date - timedelta(hours=num_hours)
                            elif 'minute' in prjob:
                                num_minutes = int (prjob.split()[0])
                                posted_date = current_date - timedelta(minutes=num_minutes)
                            elif 'second' in prjob:
                                num_seconds = int (prjob.split()[0])
                                posted_date = current_date - timedelta(seconds=num_seconds)
                            Posted_Date.append(posted_date.strftime("%Y-%m-%d %H:%M:%S"))
                        # print (prjob.text)
                        
                    # Find skills requirement
                    required_skills = []
                    skills_job = data2.find('div', 'd-flex align-items-center gap-1')
                    skills = skills_job.find_all('a')
                    for skill in skills:
                        required_skills.append(skill.text.strip())
                        skills_string = ', '.join(required_skills)
                    Skills.append(skills_string)
                        
                    # Find job descriptions
                    data3 = column2.find('section', 'job-description')
                    job_description = data3.find('div', 'paragraph')
                    Job_Descriptions.append(job_description.text)
                    # key_responsibilities = job_description.find('ul')
                    # Job_Descriptions.append(key_responsibilities.text)
                    

                    # print (key_responsibilities.text)
                except:
                    pass
            # Close the browser when done
            driver.quit()
            page = page + 1

    except Exception as e:
        print (f'error: {e}')
        # print (f'Unable to find a suitable job on the website or website does not have data. Please try again.')
    
    my_dic = {'Job_Title': Job_Title,
        'Compay_name': Compay_name,
        'Job_Location': Job_Location,
        'Kind_of_Job': Kind_of_Job,
        'Job_Descriptions': Job_Descriptions,
        'Posted_Date': Posted_Date,
        'Skills': Skills,
        'Job_Link': Job_Link
    }

    # Find the maximum length of the lists
    max_length = max(len(lst) for lst in my_dic.values())

    # Pad the shorter lists with None to make them equal in length
    for key, lst in my_dic.items():
        if len(lst) < max_length:
            my_dic[key] = lst + [None] * (max_length - len(lst))

    # pd.set_option('display.max_columns', None)


    df = pd.DataFrame(my_dic)
    print (df)

    # Export the DataFrame to a excel file
    df.to_excel('jobs_data.xlsx', index=False)
    

# Send the Excel File as an Email Attachment

def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, file_path):
    if re.match(email_regex, recipient_email):
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach the body of the email
        msg.attach(MIMEText(body, 'plain'))

        # Attach the file
        attachment = open(file_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")
        msg.attach(part)

        # Set up the SMTP server
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)  # Change if using another email provider
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)  # Log in to the server

            # Send the email
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print("Email sent successfully!")

        except Exception as e:
            print(f"Failed to send email: {e}")

        finally:
            server.quit()
    else: 
        print('Sorry! Your email address is not valid. Please try again')
    

# Usage
sender_email = "pbao62904@gmail.com"
sender_password = "srad ykpc opmm apdn"
subject = "Job list"
body = "Please find the attached Excel file."
file_path = r"D:\Máy tính\Python\Project\Scraping_Web_Bot\jobs_data.xlsx"
email_regex = r'^[a-zA-Z0-9]+([\.|\_|\-]{0,1}[a-zA-Z0-9])+@([a-zA-Z0-9][\.|\-]{0,1})+\.[a-zA-Z]{2,}$'

# User_input
# recipient_email = input('Enter your email to recieve the job listing: ')
# city = str(input('Enter the city in Viet Nam that you want to find a job: '))
# details_of_job = str(input('Enter job title or skill: ')).lower().strip()

    
def run_the_script(city, details_of_job, recipient_email):
    start_time = time.time()
    
    scraped_web = the_scraped_web(city, details_of_job)
    anumber_of_page = get_number_of_pages(scraped_web)
    # print (anumber_of_page)
    
    scraping_jobs(scraped_web, anumber_of_page)
    send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, file_path)
    
    end_time = time.time()
    time_taken = round((end_time - start_time)/60, 0)
    print (f'Time to execute the script: {time_taken} minutes')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process job search parameters.')
    parser.add_argument('city', type=str, help='City in Vietnam')
    parser.add_argument('details_of_job', type=str, help='Details of the job or skill')
    parser.add_argument('recipient_email', type=str, help='Recipient email address')
    return parser.parse_args()
if __name__ == "__main__":
    args = parse_arguments()
    run_the_script(args.city, args.details_of_job, args.recipient_email)
# run_the_script(city, details_of_job, recipient_email)
    
