import os
import agentql
from playwright.sync_api import Page, ElementHandle, sync_playwright
from playwright_stealth import stealth_sync
from pyairtable import Api 
from dotenv import load_dotenv
from login_json import login
import random
import time
import logging
import capsolver
import base64
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

class PageLocators:
    """Encapsulation of all locators for better maintainability."""
    AFISEAZA_BUTTON = 'button[title="Afișează firmele din selecția curentă"]'
    NR_COMPANII = "a[data-original-title='Firme pe pagină']"
    INPUT_NR_COMPANII = "div.popover-content input[name='ps']"
    OK_NUMAR_COMPANII = "div.popover-content button.btn.btn-primary[type='submit']" 


class TestPage:
    """Encapsulation of page actions for better test organization."""
    def __init__(self, page):
        self.page = page

    def click_afiseaza_button(self):
        """Clicks the 'Afișează' button."""
        self.page.locator(PageLocators.AFISEAZA_BUTTON).click()
    
    def get_afiseaza_button(self) -> ElementHandle:
        """Returns the locator for the 'Afișează' button."""
        return self.page.locator('button[title="Afișează firmele din selecția curentă"]')

class FirmePePaginaHandler:
    """Handles the Firme pe pagină interaction."""
    
    def __init__(self, page: Page):
        self.page = page

    def open_firme_pe_pagina(self):
        """Clicks the 'Firme pe pagină' button."""
        self.page.locator(PageLocators.NR_COMPANII).click()
        self.page.wait_for_selector(PageLocators.INPUT_NR_COMPANII, state="visible")

    def set_firme_count(self, count: int):
        """Fills the input field with the desired count and clicks OK."""
        # Fill the input field
        self.page.locator(PageLocators.INPUT_NR_COMPANII).press_sequentially(str(count))
        # Click the OK button
        self.page.locator(PageLocators.OK_NUMAR_COMPANII).click()

    def update_firme_pe_pagina(self, count: int = 100):
        """
        Orchestrates the entire process:
        1. Opens the 'Firme pe pagină' dropdown.
        2. Sets the count to the specified value (default: 100).
        """
        self.open_firme_pe_pagina()
        self.set_firme_count(count)


# Setup logging
log_filename = f'logs/scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

EMAIL= os.getenv("EMAIL")
PASSWORD= os.getenv("PASSWORD")
os.environ["AGENTQL_API_KEY"]=os.getenv("AGENTQL_API_KEY")
URL = "https://membri.listafirme.ro/"
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
CAPSOLVER_API_KEY = os.getenv("CAPSOLVER_API_KEY")
capsolver.api_key = CAPSOLVER_API_KEY
path_to_extension = "./cap-solver"
user_data_dir = "/tmp/user-data-dir"

COMPANY_LINKS = """
        {table
            {
                company_name_link(located in the second column of the table)[]
            }  
        }
            """

PAGINATION = """
        {
            pagination(pagination class)
            {
                p7_page_link
                p13_page_link
                p8_page_link
                next_page_link
            }
        }
    
    """

COMPANY_INFO = """
        {
            company_info
            {
                table_date(id="date-de-identificare")
                {
                    company_name(nume firma)
                    status(stare)
                }
                table_bilant(id="bilant")
                    {turnover(cifra afaceri 2023 interger)}
                table_contact (id="contact")
                    {
                    phone_1(first phone number only numbers)
                    phone_2(second phone number only numbers)
                    phone_3(third phone number only numbers)
                    mobile_1(first mobile number only numbers)
                    mobile_2(second mobile number only numbers)
                    mobile_3(third mobile number only numbers)
                    mobile_4(forth mobile number only numbers)
                    email_1(first email adress)
                    email_2(second email adress)
                    email_3(third email adress)
                        
                    }
                

            }
        }
        """

DISPLAY_BTN = """
        {
            display_button(afiseaza)
        }
        """
OK_BUTTON = """
        {
            ok_button
        }
        """


def random_mouse_movement(page: Page):
    for _ in range(10):
        page.mouse.move(random.randint(0, 1000), random.randint(0, 1000))
        time.sleep(random.uniform(0.1, 0.5))


def random_click(page: Page, element: ElementHandle):
    # Get element's bounding box
    box = element.bounding_box()
    if not box:
        return False
    
    # Calculate center point
    center_x = box["x"] + box["width"] / 2
    center_y = box["y"] + box["height"] / 2
    
    # Add random offset (-3 to +3 pixels)
    offset_x = random.uniform(-3, 3)
    offset_y = random.uniform(-3, 3)
    
    # Move to element with random approach
    page.mouse.move(center_x + offset_x, center_y + offset_y, 
                   steps=random.randint(5, 10))
    
    # Random delay before click
    time.sleep(random.uniform(0.1, 0.3))
    
    # Click with random duration
    page.mouse.click(center_x + offset_x, center_y + offset_y,
                    delay=random.randint(50, 150))
    
    return True


def random_scroll(page: Page):
    # Get page height
    page_height = page.evaluate('() => document.documentElement.scrollHeight')
    
    # Random number of scroll actions (2-4)
    num_scrolls = random.randint(2, 4)
    
    for _ in range(num_scrolls):
        # Random scroll distance (100-300 pixels)
        scroll_amount = random.randint(100, 300)
        
        # Smooth scroll with random duration
        page.mouse.wheel(0, scroll_amount)
        time.sleep(random.uniform(0.5, 1.5))
        
        # Sometimes pause between scrolls
        if random.random() < 0.3:  # 30% chance
            time.sleep(random.uniform(0.5, 1.0))
    
    # Sometimes scroll back up a bit
    if random.random() < 0.5:  # 50% chance
        page.mouse.wheel(0, -random.randint(50, 150))
        time.sleep(random.uniform(0.3, 0.7))


def smooth_scroll_to_element(page: Page, element: ElementHandle):
    # Get element position
    box = element.bounding_box()
    if not box:
        return False
    
    # Get current scroll position
    current_scroll = page.evaluate('() => window.pageYOffset')
    
    # Calculate target scroll position (slightly above element)
    target_scroll = box['y'] - 150  # 150px above element
    
    # Calculate distance to scroll
    distance = target_scroll - current_scroll
    
    # Perform smooth scroll in steps
    steps = 5
    for i in range(steps + 1):
        # Calculate intermediate scroll position
        progress = i / steps  # 0 to 1
        current = current_scroll + (distance * progress)
        
        # Scroll to position
        page.evaluate(f'window.scrollTo(0, {current})')
        
        # Random delay between steps
        time.sleep(random.uniform(0.05, 0.15))
    
    # Small random adjustment at the end
    final_offset = random.randint(-50, 50)
    page.evaluate(f'window.scrollTo(0, {target_scroll + final_offset})')
    return True


def sanitize_data(data):
    # Ensure turnover is a plain numeric value
    if "turnover" in data and isinstance(data["turnover"], (int, float)):
        # Airtable expects numeric values in plain format (no separators)
        data["turnover"] = float(data["turnover"])
    return data

def push_to_airtable(info_data):
    if not info_data or 'company_info' not in info_data:
        logger.error("Missing company_info in data")
        return
    
    company_data = info_data['company_info']
    #info_data = sanitize_data(company_data)
    
    # Debug log the received data
    logger.info(f"Received company data: {company_data}")
    
    logger.info("\nAirtable Configuration:")
    logger.info(f"Base ID: {AIRTABLE_BASE_ID}")
    logger.info(f"Table Name: {AIRTABLE_TABLE_NAME}")
    logger.info(f"API Key length: {len(AIRTABLE_API_KEY)} characters")

    # Safely get nested data with validation
    try:
        # Format data for Airtable
        airtable_record = {
            "Company Name": company_data.get('company_name', 'N/A'),
            "Status": company_data.get('status', 'N/A'),
            "Cifra Afaceri": company_data.get('turnover', 'N/A'),
            "Phone 1": company_data.get('phone_1', 'N/A'),
            "Phone 2": company_data.get('phone_2', 'N/A'),
            "Phone 3": company_data.get('phone_3', 'N/A'),
            "Phone 4": company_data.get('phone_4', 'N/A'),
            "Mobile 1": company_data.get('mobile_1', 'N/A'),
            "Mobile 2": company_data.get('mobile_2', 'N/A'),
            "Mobile 3": company_data.get('mobile_3', 'N/A'),
            "Mobile 4": company_data.get('mobile_4', 'N/A'),
            "Email 1": company_data.get('email_1', 'N/A'),
            "Email 2": company_data.get('email_2', 'N/A'),
            "Email 3": company_data.get('email_3', 'N/A'),
            "Email 4": company_data.get('email_4', 'N/A')
            
        }
        
        logger.info("\nAttempting to connect to Airtable...")
        airtable = Api(AIRTABLE_API_KEY)
        table = airtable.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        logger.info("Creating record...")
        response = table.create(airtable_record)
        logger.info("Successfully pushed to Airtable")
        logger.info(f"Created record ID: {response.get('id', 'No ID returned')}")
        
    except Exception as e:
        logger.error(f"\nError pushing to Airtable: {str(e)}")
        logger.error(f"Raw company data: {company_data}")
        logger.error("Data attempted to push:", airtable_record)


def get_company_links_with_retry(page, max_retries=1):
    max_links = 0
    final_response = None
    
    for attempt in range(max_retries):
        # Scroll to bottom to ensure all elements are loaded
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        links_response = page.query_elements(COMPANY_LINKS)
        num_links = len(links_response.table.company_name_link) if links_response else 0
        
        # Keep track of the maximum number of links we've seen
        if num_links > max_links:
            max_links = num_links
            final_response = links_response
            # If we found more links, give it one more try
            continue
            
        # If we didn't find more links than before, we're probably done
        if num_links == max_links:
            logger.info(f"Found {max_links} links on the page")
            return final_response
            
        logger.info(f"Found {num_links} links on attempt {attempt + 1}, retrying...")
    
    logger.info(f"Found {max_links} companies on this page")
    return final_response



def check_for_captcha(page):
    """Check if CAPTCHA is present on the page"""
    try:
        
         # Check for image CAPTCHA
        image_captcha = page.get_by_prompt("the image verification challenge")
        if image_captcha:
            logger.warning("Image CAPTCHA detected!")
            return True
        
        # Check for common CAPTCHA identifiers
        captcha_frame = page.get_by_prompt("the reCAPTCHA iframe")
        if captcha_frame:
            logger.warning("CAPTCHA detected!")
            return True
            
        return False
    except Exception as e:
        logger.error(f"Error checking for CAPTCHA: {str(e)}")
        return False

def wait_for_url_change(page, max_wait=120):
    
    try:
        logger.info("Waiting for verification page to change...")
        
        # Wait for the URL to change from the specific pattern
        page.wait_for_url(
            lambda url: "trafic-neuzual.asp?url=" not in url,
            timeout=max_wait * 1000  # Convert seconds to milliseconds
        )
        
        current_url = page.url
        logger.info(f"Verification page changed successfully. Current URL: {current_url}")
        return True

    except TimeoutError:
        logger.error(f"Timeout after {max_wait} seconds waiting for verification page to change")
        return False


def handle_verification_page(page):
    """Handle the unusual traffic verification page"""
    try:
        # Check if we're on the verification page
        if "trafic-neuzual.asp?url=" in page.url:
            logger.info("Detected unusual traffic verification page")
            
            # Wait for page to load completely
            #ok_button = page.
            
            # Wait for button to be enabled
            button_locator = "#btnSubmit"
        
        # Wait for the button to be visible and click it
            button_element = page.locator(button_locator)


            max_wait = 30  # Maximum seconds to wait
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                if button_element:
                    # Check if button is enabled
                    if button_element.is_enabled():
                        logger.info("OK button is now enabled")
                        
                        # Get button position
                        box = button_element.bounding_box()
                        if box:
                            # Start from a random position on screen
                            viewport = page.viewport_size
                            start_x = random.randint(0, viewport["width"])
                            start_y = random.randint(0, viewport["height"])
                            
                            # Move mouse from random start to button
                            page.mouse.move(start_x, start_y)
                            time.sleep(random.uniform(0.1, 0.2))
                            
                            # Calculate target position (center of button)
                            target_x = box["x"] + box["width"]/2
                            target_y = box["y"] + box["height"]/2
                            
                            # Move to button with natural movement
                            steps = 10
                            for i in range(steps):
                                x = start_x + (target_x - start_x) * (i + 1) / steps
                                y = start_y + (target_y - start_y) * (i + 1) / steps
                                # Add small random deviation
                                x += random.uniform(-5, 5)
                                y += random.uniform(-5, 5)
                                page.mouse.move(x, y)
                                time.sleep(random.uniform(0.02, 0.05))
                            
                            
                            # Click with natural delay
                            page.mouse.move(target_x, target_y)
                            page.mouse.click(target_x, target_y,)

                            max_wait = 120
                            start_time = time.time()
                            
                            wait_for_url_change(page,max_wait)
                            #while True:
                                #current_url = page.url
                                #logger.info(f"Current URL: {current_url}")
                                
                                #if "trafic-neuzual.asp?url=" not in current_url:
                                    #logger.info("Verification page changed, continuing...")
                                   # break
                                    
                                #if time.time() - start_time > max_wait:
                                    #logger.error("Timeout waiting for verification page to change")
                                    #return False
                                
                                #logger.info("Waiting for verification page to change...")
                                #time.sleep(5)  # Wait 5 seconds between checks
                                
                            logger.info("Successfully clicked OK button")
                            return True
                    else:
                        elapsed = time.time() - start_time
                        logger.info(f"Button found but not enabled yet. Waiting... ({elapsed:.1f}s elapsed)")
                        time.sleep(1)
                        continue
                
                elapsed = time.time() - start_time
                logger.info(f"Waiting for OK button... ({elapsed:.1f}s elapsed)")
                time.sleep(1)
            
            logger.error(f"Button not enabled after {max_wait} seconds")
                
    except Exception as e:
        logger.error(f"Error handling verification page: {str(e)}")
    return False




def extract_data(page):
    """Extracts company details, contact information, and financial data."""
    # Initialize data structure
    company_data = {}

    # Extract company name
    company_name = page.locator('table#date-de-identificare th span[itemprop="legalName"]').text_content().strip()
    company_data["company_name"] = company_name
    status = page.locator('table#date-de-identificare td:has-text("Stare") + td').text_content().strip()
    company_data["status"] = status

    # Extract phone and mobile numbers
    phone_rows = page.locator('table#contact td a.clicktocall[href^="tel:"]')
    phone_index = 1
    mobile_index = 1

    for i in range(phone_rows.count()):
        phone_href = phone_rows.nth(i).get_attribute("href")
        phone_number = phone_href.replace("tel:", "") if phone_href else None
        if phone_number:
            if "07" in phone_number:  # Mobile numbers
                company_data[f"mobile_{mobile_index}"] = phone_number
                mobile_index += 1
            else:  # Landline numbers
                company_data[f"phone_{phone_index}"] = phone_number
                phone_index += 1

    # Extract email addresses
    email_rows = page.locator('table#contact td a[href^="mailto:"]')
    email_index = 1

    for i in range(email_rows.count()):
        email_href = email_rows.nth(i).get_attribute("href")
        email_address = email_href.replace("mailto:", "") if email_href else None
        if email_address:
            company_data[f"email_{email_index}"] = email_address
            email_index += 1

    # Extract turnover for 2023
    
    turnover_locator = "//table[contains(@class, 'table-bilant')]//tr[2]/td[2]"
    turnover_element = page.locator(turnover_locator)
    turnover_text = turnover_element.inner_text().strip()
    
    turnover_cleaned = turnover_text.replace('\u00a0', '').replace(' ', '')
    
    company_data["turnover"] = int(turnover_cleaned)
   
    company_data = {"company_info": company_data}

    logger.info("Extracted company data:")
    logger.info(company_data)

    return company_data



def process_company_page(context, page, company_link, retry_count=0):
    """Process a single company page"""
    try:
        logger.info("Opening company page...")
        if page.is_closed():
            logger.error("Main page is closed")
            return None, None
        
        # Add random mouse movements before clicking
        random_mouse_movement(page)
        
        # Smooth scroll to company link
        smooth_scroll_to_element(page, company_link)
        time.sleep(random.uniform(0.3, 0.5))
        
        """# Sometimes add small random scroll adjustments
        if random.random() < 0.4:  # 40% chance
            page.mouse.wheel(0, random.randint(-50, 50))
            time.sleep(random.uniform(0.2, 0.5))"""
        
        # Move to element area with some randomness
        box = company_link.bounding_box()
        if box:
            # Scroll directly to element
            page.evaluate(f"window.scrollTo(0, {max(0, box['y'] - 100)})")
            time.sleep(0.2)
            
            # Direct mouse movement to link
            page.mouse.move(
                box["x"] + box["width"]/2,
                box["y"] + box["height"]/2
            )
        
        # Fast click with minimal timeout
        with page.expect_popup(timeout=30000) as new_page_info:  # Increased timeout to 30 seconds
                try:
                    # Move mouse to element first
                    company_link.hover()
                    page.wait_for_timeout(100)  # Small delay after hover
                    company_link.click(delay=random.randint(50, 150))
                except Exception as e:
                    logger.error(f"Click error on attempt {retry_count + 1}: {str(e)}")
                    # Fallback to JavaScript click
                    page.evaluate("(element) => element.click()", company_link)

        try:
            company_page = new_page_info.value
            if not company_page:
                raise Exception("No popup page received")
                #company_page.reload(timeout=30000)
        except Exception as e:
            logger.error(f"Popup error: {str(e)}")
            return None, None
        
        company_page.wait_for_load_state("networkidle")
        logger.info("Company page loaded")
        
        #company_page = agentql.wrap(company_page)
        #company_page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Check for verification page and handle it
        if handle_verification_page(company_page):
            logger.info("Successfully handled verification page")

        company_page.wait_for_load_state("networkidle")
        logger.info("Company page loaded")
        
        # Get company info immediately
        #company_info = company_page.query_data(COMPANY_INFO)

        company_info = extract_data(company_page)
        logger.info("Extracted company data:")
        logger.info(company_info)

         # More natural scrolling behavior
        scroll_count = random.randint(1, 2)
        for _ in range(scroll_count):
            random_scroll(company_page)
            time.sleep(random.uniform(0.2, 0.4))
            
            # Sometimes move mouse while scrolling
            if random.random() < 0.4:  # 40% chance
                random_mouse_movement(company_page)

        
        if company_info:
                push_to_airtable(company_info)
                return company_info, company_page
            
        return None, company_page
        
    except Exception as e:
        if retry_count < 2:
            logger.error(f"Error on attempt {retry_count + 1}: {str(e)}")
            if company_page and not company_page.is_closed():
                try:
                    company_page.close()
                except:
                    pass
            wait_time = 2 * (retry_count + 1)
            logger.info(f"Retrying in {wait_time}s...")
            time.sleep(wait_time)
            return process_company_page(context, page, company_link, retry_count + 1)
        else:
            logger.warning("Max retries reached, skipping")
            if company_page and not company_page.is_closed():
                try:
                    company_page.close()
                except:
                    pass
            return None, None




def main():
    with sync_playwright() as playwright, playwright.chromium.launch_persistent_context( 
        user_data_dir,
        headless=False,
        args=[
            f"--disable-extensions-except={path_to_extension}",
            f"--load-extension={path_to_extension}",
            f"--disable-blink-features=AutomationControlled",
            f"--viewport=1920,1080",
        ],) as context:  # Rename browser to context since it's actually a BrowserContext
        
        if not os.path.exists('login_state.json'):
            logger.info("No login state found")
            login(context)
            return
        
        start_time = time.time()
        processed_companies = 0
        total_companies_all_pages = 0

        page = agentql.wrap(context.new_page())
        stealth_sync(page)

        #page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Load cookies from login state
        if os.path.exists('login_state.json'):
            with open('login_state.json', 'r') as f:
                storage = json.load(f)
                if 'cookies' in storage:
                    context.add_cookies(storage['cookies'])

        page.goto(URL)

        page.wait_for_load_state("networkidle")
        main_page=TestPage(page)
        afiseaza_button = main_page.get_afiseaza_button()

        page.wait_for_load_state("networkidle")

        
        if not afiseaza_button:
            logger.error("Failed to find display button")
            return
        else:
            random_click(page, afiseaza_button)
        
        
        

        """nr_companii = FirmePePaginaHandler(page)
        nr_companii.update_firme_pe_pagina(100)"""

        page.wait_for_timeout(2000)

        current_url = page.url
        if "p1.htm" in current_url:
            new_url = current_url.replace("p1.htm", "p43.htm")
            logger.info(f"Navigating directly to page 43: {new_url}")
            page.goto(new_url)
            page.wait_for_load_state("networkidle")
            current_page = 43
        else:
            logger.warning(f"Unexpected URL format: {current_url}")
            return
        
        
        #response = page.query_elements(PAGINATION)sß
        #random_click(page, response.pagination.p13_page_link) # response.pagination.p13_page_link.click()
        #page.wait_for_load_state("networkidle")

        # Wait for page to load completely

        has_next_page = True


        while has_next_page:
            logger.info(f"\nProcessing page {current_page}")

            # Get company links with retry mechanism
            links_response = get_company_links_with_retry(page)
            logger.info(links_response)
            
            if not links_response or not links_response.table.company_name_link:
                logger.warning("No company links found")
                break

            total_companies = len(links_response.table.company_name_link)
            total_companies_all_pages += total_companies
            logger.info(f"\nStarting to process {total_companies} companies on page {current_page}")

            # Process each company
            for i, company_link in enumerate(links_response.table.company_name_link):
                company_start_time = time.time()  # Start timing for this company
                try:
                    logger.info(f"\nProcessing company {i+1}/{total_companies} on page {current_page}")
                    
                    # Process company with retry logic
                    info_data, company_page = process_company_page(context, page, company_link)
                    
                    if company_page and not company_page.is_closed():
                        try:
                            company_page.close()
                        except Exception as e:
                            logger.error(f"Error closing company page: {str(e)}")
                    
                    # Calculate and display timing for this company
                    company_time = time.time() - company_start_time
                    logger.info(f"Company processed in: {company_time:.2f} seconds")
                    
                    # Add longer wait between companies
                    if i < len(links_response.table.company_name_link):
                        wait_time = random.uniform(2, 4)
                        logger.info(f"Waiting {wait_time:.1f} seconds before next company...")
                        time.sleep(wait_time)

                    processed_companies += 1
                    
                    # Calculate and show progress
                    elapsed_time = time.time() - start_time
                    avg_time_per_company = elapsed_time / (i + 1)
                    remaining_companies = total_companies - (i + 1)
                    estimated_remaining_time = remaining_companies * avg_time_per_company
                    
                    logger.info(f"Progress: {i+1}/{total_companies} ({((i+1)/total_companies*100):.1f}%)")
                    logger.info(f"Estimated time remaining: {estimated_remaining_time/60:.1f} minutes")
                    logger.info("-------------------")
                    
                except Exception as e:
                    logger.error(f"Error processing company {i} on page {current_page}: {str(e)}")
                    continue

            try:
                arrow_locator = "ul.pagination a:has(i.fa.fa-arrow-right)"
                pagination = page.locator(arrow_locator)

                if pagination:
                    logger.info(f"\nMoving to page {current_page + 1}")
                    
                    # Get current URL and modify for next page
                    current_url = page.url
                    next_page = current_page + 1
                    current_page_str = f"p{current_page}.htm"
                    next_page_str = f"p{next_page}.htm"

                    if current_page_str in current_url:
                        new_url = current_url.replace(current_page_str, next_page_str)
                        logger.info(f"Navigating to next page: {new_url}")
                        page.goto(new_url)
                        page.wait_for_load_state("networkidle")
                        page.wait_for_timeout(random.uniform(2000, 3000))
                        current_page += 1
                    else:
                        logger.warning(f"Could not find expected page pattern in URL: {current_url}")
                        has_next_page = False
                        
                else:
                    logger.info("No next page found")
                    has_next_page = False
                    
                
            except Exception as e:
                logger.error(f"Error during pagination: {str(e)}")
                has_next_page = False
        
            
            # Calculate and display final statistics

        # Final statistics
        total_time = time.time() - start_time
        logger.info("\nFinal Statistics:")
        logger.info(f"Total pages processed: {current_page}")
        logger.info(f"Total companies found: {total_companies_all_pages}")
        logger.info(f"Successfully processed companies: {processed_companies}/{total_companies_all_pages}")
        logger.info(f"Total execution time: {total_time/60:.2f} minutes")
        if processed_companies > 0:
            logger.info(f"Average time per company: {total_time/processed_companies:.2f} seconds")
            logger.info(f"Success rate: {(processed_companies/total_companies_all_pages*100):.1f}%")


    
        


if __name__ == "__main__":
    main()