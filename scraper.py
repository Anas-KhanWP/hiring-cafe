# SCRAPE THE FOLLOWING:

# location (DONE!!!)
# title (DONE!!!)
# company name (DONE!!!)
# about company (DONE!!!)
# requirements (DONE!!!)
# compensation (DONE!!!)
# job type (fulltime/part time etc) (DONE!!!)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
import os
import logging
import pandas as pd

# Create a folder for logging
log_folder = 'logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Create a subfolder with the current date
current_date = datetime.datetime.now().strftime('%Y-%m-%d')
subfolder = os.path.join(log_folder, current_date)
if not os.path.exists(subfolder):
    os.makedirs(subfolder)
    
log_file = os.path.join(subfolder, 'JobData.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
logging.info(f"Script Started Running at: {current_time}")

# Initialize WebDriver
driver = webdriver.Chrome()  # Replace this with the appropriate web driver you're using (Chrome, Firefox, etc.)

# Open the URL of the webpage
url = "https://hiring.cafe/"
driver.get(url)

# Automatically scroll the page
scroll_pause_time = 2  # Pause between each scroll
screen_height = driver.execute_script("return window.screen.height;")  # Browser window height

i = 1
j = 1

# Set to keep track of already processed elements
processed_divs = set()

# List to store all the job data
job_data = []

while True:
    if j >= 2:
        break

    time.sleep(2)
    # Scroll down
    driver.execute_script(f"window.scrollTo(0, {screen_height * i});")
    i += 1
    time.sleep(scroll_pause_time)
    
    # Fetch the data using Selenium after all data is loaded
    divs = driver.find_elements(By.CSS_SELECTOR, ".my-masonry-grid_column>div")
    print(len(divs))
    
    for div in divs:
        # Check if this div has already been processed
        if div in processed_divs:
            continue  # Skip if already processed
        
        # Reset the counter
        j = 0
        processed_divs.add(div)  # Add to the set of processed elements
        
        # Initialize variables with default value "N/A"
        title, locations, jobTypes, companyName, aboutCompany, requirements, compensation, tech = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        
        try:
            # Title
            title = WebDriverWait(div, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "flex.flex-col.w-fit.mr-12"))
            ).find_element(By.CLASS_NAME, "font-bold.text-start.mt-1.line-clamp-2").text
        except:
            pass
        
        try:
            # Locations
            locations = WebDriverWait(div, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mt-1.flex.items-center.space-x-1.rounded.text-xs.px-1.font-medium.border.bg-gray-50.w-fit.text-gray-700"))
            ).find_element(By.TAG_NAME, "span").text
        except:
            pass
        
        try:
            # Job Type
            jobTypeDiv = WebDriverWait(div, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".flex.flex-wrap.gap-1\\.5"))
            ).find_elements(By.TAG_NAME, "span")
            jobTypes = ", ".join([span.text for span in jobTypeDiv if "$" not in span.text])  # Skipping Compensation
        except:
            pass
        
        try:
            # Company Name
            companyName = WebDriverWait(div, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "flex.flex-col.w-fit.mr-12"))
            ).find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "span").text
        except:
            pass
        
        try:
            # About Company
            aboutCompanySpan = WebDriverWait(div, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "line-clamp-3.font-light"))
            )
            aboutCompany = driver.execute_script("""
                let element = arguments[0];
                let childNodes = Array.from(element.childNodes);
                let directText = '';
                childNodes.forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        directText += node.textContent;
                    }
                });
                return directText.trim();
            """, aboutCompanySpan)
        except:
            pass
        
        try:
            # Requirements
            requirementsSpan = WebDriverWait(div, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "flex.flex-col.mt-4.mb-2.space-y-2.text-sm.w-full"))
            ).find_elements(By.CLASS_NAME, "flex.space-x-1.w-full")[-1].find_elements(By.TAG_NAME, "span")[1]
            requirements = driver.execute_script("""
                let element = arguments[0];
                let childNodes = Array.from(element.childNodes);
                let directText = '';
                childNodes.forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        directText += node.textContent;
                    }
                });
                return directText.trim();
            """, requirementsSpan)
        except:
            pass
        
        try:
            # Compensation
            for span in jobTypeDiv:
                if "$" in span.text:
                    compensation = span.text
                    break
        except:
            pass
        
        try:
            # Tech
            techSpan = WebDriverWait(div, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "flex.flex-col.mt-4.mb-2.space-y-2.text-sm.w-full"))
            ).find_elements(By.TAG_NAME, "div")[-1].find_elements(By.TAG_NAME, "span")[1]
            tech = driver.execute_script("""
                let element = arguments[0];
                let childNodes = Array.from(element.childNodes);
                let directText = '';
                childNodes.forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        directText += node.textContent;
                    }
                });
                return directText.trim();
            """, techSpan)
            if tech == requirements:
                tech = "N/A"
        except:
            pass
        
        # Append the data to the job_data list
        job_data.append({
            "Title": title,
            "Location": locations,
            "Job Type": jobTypes,
            "Company Name": companyName,
            "About Company": aboutCompany,
            "Requirements": requirements,
            "Compensation": compensation,
            "Tech": tech
        })
        
        print(title)
        print(locations)
        print(jobTypes)
        print(companyName)
        print(aboutCompany)
        print(requirements)
        print(compensation)
        print(tech)
        
        print("-------------------------------------")
                
    # Check if reaching the end of the page
    scroll_height = driver.execute_script("return document.body.scrollHeight;")
    if screen_height * i > scroll_height:
        # break
        j += 1
        

# Close the WebDriver session
driver.quit()

# Create a DataFrame from the job data
df = pd.DataFrame(job_data)

# Get current date and time for directory name
now = datetime.datetime.now()
directory_name = f"JobData"
file_path = os.path.join(directory_name, f"JobData_{now.strftime('%Y-%m-%d_%H-%M')}.xlsx")

# Create directory if it does not exist
os.makedirs(directory_name, exist_ok=True)

# Save the DataFrame to an Excel file
df.to_excel(file_path, index=False)

print(f"Data written to {file_path}")
logging.info(f"Data written to {file_path}")
