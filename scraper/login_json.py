import os
import agentql
import random
import time
from playwright.sync_api import Page,ElementHandle,sync_playwright
from playwright_stealth import stealth_sync
from dotenv import load_dotenv
load_dotenv()
EMAIL= os.getenv("EMAIL")
PASSWORD= os.getenv("PASSWORD")
os.environ["AGENTQL_API_KEY"]=os.getenv("AGENTQL_API_KEY")


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.dropdown = self.page.get_by_role("link", name="Intră în cont")
        self.dropdown_menu = self.page.locator("li").filter(has_text="Intră în cont Sign in with Google Ține-mă minte Intră în cont Creează cont").locator("div").first  # Scoped locator
        self.name_input = self.page.get_by_role("textbox", name="email sau mobil")  # Scoped to login form
        self.password_input = self.page.get_by_role("textbox", name="parola")  # Scoped to login form
        self.remember_me_checkbox = self.page.get_by_role("checkbox", name="Ține-mă minte")  # Scoped to login form
        self.login_button = self.page.get_by_role("button", name="Intră în cont")  # Scoped to login form
        

    def open_dropdown(self):
        """Opens the login dropdown menu."""
        self.dropdown.click()
        self.dropdown_menu.wait_for(state="visible")

    def fill_login_form(self, username: str, password: str, remember_me: bool = False):
        """Fills in the login form with the provided details."""
        self.name_input.press_sequentially(username)
        self.password_input.press_sequentially(password)
        if remember_me:
            self.remember_me_checkbox.check()
        else:
            self.remember_me_checkbox.uncheck()

    def submit_login(self):
        """Clicks the login button to submit the form."""
        self.login_button.click()

    def login(self, username: str, password: str, remember_me: bool = False):
        """Performs the full login sequence."""
        self.open_dropdown()
        self.fill_login_form(username, password, remember_me)
        self.submit_login()




INITIAL_URL = 'https://listafirme.ro'

EMAIL_INPUT_QUERY = """
    {
        access_account_button(intra in cont)
        {
            email_username_field
            password_field
            remember_me_checkbox
            login_account_button
        }
    }
        """

ACCES_QUERY = """
        {
            access_account_button(intra in cont)
        
        }
            """

AFISEAZA_CRITERII = """
        {
            selections_link(Afișează selecțiile salvate)
            dropdown_toggle(afiseaza)
        }
            """

AFISEAZA_LINK = """
        {
            link(aplica setul de criterii)
        }
            """


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



def login(browser=None):

    if browser is None:
        with sync_playwright() as playwright, playwright.chromium.launch(headless=False) as browser:
            _do_login(browser)
    else:
        _do_login(browser)
            
def _do_login(browser):           
            
            
    page=agentql.wrap(browser.new_page())
    stealth_sync(page)
    page.goto(INITIAL_URL)
    page.wait_for_load_state('networkidle')

            #use query_elements() to locate "Log In" button on the page
    """response = page.query_elements(ACCES_QUERY)
    '''response.access_account_button.click()'''
    random_click(page,response.access_account_button)
        # Wait for navigation and form to be visible
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(10000)  # Wait a bit longer to ensure form is loaded
    
         # Query for form elements after they're loaded
    form_response = page.query_elements(EMAIL_INPUT_QUERY)
    
        # Fill in the form
    form_response.access_account_button.email_username_field.press_sequentially(EMAIL)
    form_response.access_account_button.password_field.press_sequentially(PASSWORD)
    '''form_response.access_account_button.remember_me_checkbox.click()'''
    random_click(page, form_response.access_account_button.remember_me_checkbox)
    '''form_response.access_account_button.login_account_button.click()'''
    random_click(page, form_response.access_account_button.login_account_button)"""
    
    login_page = LoginPage(page)

        # Perform login
    login_page.login(username=EMAIL, password=PASSWORD, remember_me=True)
    
    page.wait_for_load_state('networkidle')
        

    browser.contexts[0].storage_state(path="login_state.json")

    """response = page.query_elements(AFISEAZA_CRITERII)

    page.wait_for_load_state('networkidle')

        # Get the button's bounding box
    button = response.dropdown_toggle
    bbox = button.bounding_box()

        # Move mouse to center of button
    page.mouse.move(bbox['x'] + bbox['width']/2, bbox['y'] + bbox['height']/2)
    page.wait_for_timeout(1000)

        # Click the button to show dropdown
    button.click()
    page.wait_for_timeout(2000)

         # Try to click the link with force
    selections = response.selections_link
    bbox = selections.bounding_box()

    if bbox:
            # Move mouse directly to the link
        page.mouse.move(bbox['x'] + bbox['width']/2, bbox['y'] + bbox['height']/2)
        page.wait_for_timeout(1000)
            # Force click the link
        selections.click(force=True)

    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(20000)

    new_response = page.query_elements(AFISEAZA_LINK)
    '''new_response.link.click()'''
    random_click(page, new_response.link)"""
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(7000)
    

if __name__ == "__main__":
    login()
      

