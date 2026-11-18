import capsolver
import os
import requests
import time
from dotenv import load_dotenv
from playwright.sync_api import StorageState, sync_playwright , Playwright
from dotenv import load_dotenv
load_dotenv()

CAPSOLVER_API_KEY = os.getenv("CAPSOLVER_API_KEY")
capsolver.api_key = CAPSOLVER_API_KEY

site_key = "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"  # site key of your target site
site_url = "https://www.google.com/recaptcha/api2/demo"  # page url of your target site
api_key = capsolver.api_key 

path_to_extension = "./cap-solver"
user_data_dir = "/tmp/test-user-data-dir"

def run(playwright: Playwright):
    context = playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        args=[
            f"--disable-extensions-except={path_to_extension}",
            f"--load-extension={path_to_extension}",
        ],
    )

    page = context.new_page()
    page.goto("https://www.google.com/recaptcha/api2/demo")
    page.wait_for_timeout(999999)

    if len(context.background_pages) == 0:
        background_page = context.wait_for_event('backgroundpage')
    else:
        background_page = context.background_pages[0]

    # Test the background page as you would any other page.
    page = context.new_page(StorageState="login_state.json")
    page.goto("https://www.google.com/recaptcha/api2/demo")
    page.wait_for_selector("text=I'm not a robot")
    page.wait_for_timeout(999999)
    context.close()












def test_airtable_connection():
    logger.info("\nTesting Airtable Connection...")
    logger.info(f"API Key (first 10 chars): {AIRTABLE_API_KEY[:10]}...")
    logger.info(f"Base ID: {AIRTABLE_BASE_ID}")
    logger.info(f"Table Name: {AIRTABLE_TABLE_NAME}")
    
    test_record = {
        "Company Name": "Test Company",
        "Status": "Test Status",
        "Cifra Afaceri": "123456",
        "Phone 1": "123-456-7890",
        "Email 1": "test@test.com"
    }
    
    try:
        logger.info("\nInitializing Airtable API...")
        airtable = Api(AIRTABLE_API_KEY)
        logger.info("API initialized successfully")
        
        logger.info("\nConnecting to table...")
        table = airtable.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        logger.info("Table connection successful")
        
        logger.info("\nAttempting to create test record...")
        response = table.create(test_record)
        logger.info("Test record created successfully!")
        logger.info(f"Record ID: {response.get('id', 'No ID returned')}")
        return True
        
    except Exception as e:
        logger.error(f"\nError during test: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response headers: {e.response.headers}")
            logger.error(f"Response body: {e.response.text}")
        return False


def solve_captcha(page):
    """Solve CAPTCHA using capsolver"""
    try:
        # Check for reCAPTCHA
        captcha_frame = page.get_by_prompt("the reCAPTCHA iframe")
        if captcha_frame:
            logger.info("Detected reCAPTCHA, attempting to solve...")
            
            # Get the site key
            site_key = "6LeWHRsUAAAAAAfnolncWBMlfLgGUsxQitRPu5YR"
            
            if site_key:
                logger.info(f"Found reCAPTCHA site key: {site_key}")
                solution = capsolver.solve({
                    "type": "ReCaptchaV2TaskProxyLess",
                    "websiteURL": "https://membri.listafirme.ro",
                    "websiteKey": site_key,
                })
                
                if solution.get('gRecaptchaResponse'):
                    logger.info("Got reCAPTCHA solution, applying...")
                    # Apply the solution
                    page.evaluate("""
                        function(token) {
                            if (typeof grecaptcha !== 'undefined' && grecaptcha.enterprise) {
                                grecaptcha.enterprise.callback(token);
                            } else if (typeof grecaptcha !== 'undefined') {
                                grecaptcha.callback(token);
                            }
                            return true;
                        }
                    """, solution['gRecaptchaResponse'])
                    return True
                
        # Check for image CAPTCHA
        image_captcha = page.get_by_prompt("the image verification challenge")
        if image_captcha:
            logger.info("Detected image CAPTCHA, attempting to solve...")
            
            # Get the image data and question type
            image_data = page.evaluate("""
                () => {
                    const img = document.querySelector('img[class*="captcha"]');
                    return img ? img.src : null;
                }
            """)
            
            question_type = page.evaluate("""
                () => {
                    const text = document.querySelector('.rc-imageselect-desc-no-canonical');
                    return text ? text.innerText : '';
                }
            """)
            
            if image_data and image_data.startswith('data:image/'):
                # Extract base64 data
                base64_data = image_data.split(',')[1]
                
                # Map question type to capsolver question format
                question_map = {
                    "taxis": "/m/0pg52",
                    "bus": "/m/01bjv",
                    "school bus": "/m/02yvhj",
                    "motorcycles": "/m/04_sv",
                    "tractors": "/m/013xlm",
                    "chimneys": "/m/01jk_4",
                    "crosswalks": "/m/014xcs",
                    "traffic lights": "/m/015qff",
                    "bicycles": "/m/0199g",
                    "parking meters": "/m/015qbp",
                    "cars": "/m/0k4j",
                    "bridges": "/m/015kr",
                    "boats": "/m/019jd",
                    "palm trees": "/m/0cdl1",
                    "mountains or hills": "/m/09d_r",
                    "fire hydrant": "/m/01pns0",
                    "stairs": "/m/01lynh"
                }
                
                # Extract the object type from the question
                for key, value in question_map.items():
                    if key.lower() in question_type.lower():
                        question = value
                        break
                else:
                    question = "/m/0k4j"  # Default to cars if no match found
                
                solution = capsolver.solve({
                    "type": "ReCaptchaV2Classification",
                    "websiteURL": page.url,
                    "image": base64_data,
                    "question": question
                })
                
                if solution.get('answer'):
                    logger.info("Got image CAPTCHA solution, applying...")
                    # Click the cells according to the solution
                    cells = solution['answer']
                    for cell_index in cells:
                        # Convert 0-based index to row and column
                        row = cell_index // 3
                        col = cell_index % 3
                        page.click(f'.rc-imageselect-tile:nth-child({row * 3 + col + 1})')
                        time.sleep(random.uniform(0.3, 0.7))
                    
                    # Click verify button
                    verify_button = page.get_by_prompt("the verify button")
                    if verify_button:
                        verify_button.click()
                        page.wait_for_load_state("networkidle")
                        return True
        
        return False
    except Exception as e:
        logger.error(f"Error solving CAPTCHA: {str(e)}")
        return False


with sync_playwright() as playwright:
    run(playwright)





"""solution = capsolver.solve({
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": "https://www.google.com/recaptcha/api2/demo",
            "websiteKey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
          })


def capsolver():
    payload = {
        "clientKey": api_key,
        "task": {
            "type": 'ReCaptchaV2TaskProxyLess',
            "websiteKey": site_key,
            "websiteURL": site_url
        }
    }
    res = requests.post("https://api.capsolver.com/createTask", json=payload)
    resp = res.json()
    task_id = resp.get("taskId")
    if not task_id:
        print("Failed to create task:", res.text)
        return
    print(f"Got taskId: {task_id} / Getting result...")
 
    while True:
        time.sleep(3)  # delay
        payload = {"clientKey": api_key, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
        resp = res.json()
        status = resp.get("status")
        if status == "ready":
            return resp.get("solution", {}).get('gRecaptchaResponse')
        if status == "failed" or resp.get("errorId"):
            print("Solve failed! response:", res.text)
            return
 
 
token = capsolver()
print(token)"""

#if __name__ == "__main__":
    