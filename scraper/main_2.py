
def main():
    with sync_playwright() as playwright, playwright.chromium.launch_persistent_context( 
        user_data_dir,
        headless=False,
        args=[
            f"--disable-extensions-except={path_to_extension}",
            f"--load-extension={path_to_extension}",
        ],) as browser:

        
        if not os.path.exists('login_state.json'):
            logger.info("No login state found")
            login(browser)
            logger.info("Login completed")

        start_time = time.time()
        processed_companies = 0
        total_companies_all_pages = 0

        context = browser.new_page()
        page = agentql.wrap(context)
        stealth_sync(page)

        if os.path.exists('login_state.json'):
            with open('login_state.json', 'r') as f:
                storage = json.load(f)
                if 'cookies' in storage:
                    browser.add_cookies(storage['cookies'])

        page.goto(URL)
        response = page.query_elements(DISPLAY_BTN)
        
        random_click(page, response.display_button)
        
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(4000)

        
        current_url = page.url
        if "p1.htm" in current_url:
            new_url = current_url.replace("p1.htm", "p26.htm")
            logger.info(f"Navigating directly to page 26: {new_url}")
            page.goto(new_url)
            page.wait_for_load_state("networkidle")
            current_page = 26
        else:
            logger.warning(f"Unexpected URL format: {current_url}")
            return
        
        
        #response = page.query_elements(PAGINATION)
        #random_click(page, response.pagination.p13_page_link) # response.pagination.p13_page_link.click()
        #page.wait_for_load_state("networkidle")

        # Wait for page to load completely

        has_next_page = True


        while has_next_page:
            logger.info(f"\nProcessing page {current_page}")

            # Get company links with retry mechanism
            links_response = get_company_links_with_retry(page)
            
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
                    
                    if info_data and 'company_info' in info_data:
                        company_data = info_data['company_info']
                        logger.info("Company Information:")
                        logger.info(f"Name: {company_data['company_name']}")
                        logger.info(f"Status: {company_data['status']}")
                        logger.info(f"Phone: {company_data['phone_1'] if company_data['phone_1'] else 'N/A'}")
                        logger.info(f"Mobile: {company_data['mobile_1'] if company_data['mobile_1'] else 'N/A'}")
                        logger.info(f"Email: {company_data['email_1'] if company_data['email_1'] else 'N/A'}")
                        logger.info("-------------------")
                        processed_companies += 1
                    
                    # Close the company page if it exists
                    if company_page:
                        try:
                            company_page.close()
                        except:
                            pass
                    
                    # Calculate and display timing for this company
                    company_time = time.time() - company_start_time
                    logger.info(f"Company processed in: {company_time:.2f} seconds")
                    
                    # Add longer wait between companies
                    wait_time = random.uniform(2, 4)
                    logger.info(f"Waiting {wait_time:.1f} seconds before next company...")
                    page.wait_for_timeout(int(wait_time * 1000))
                    
                    # Calculate and show progress
                    elapsed_time = time.time() - start_time
                    avg_time_per_company = elapsed_time / (i + 1)
                    remaining_companies = total_companies - (i + 1)
                    estimated_remaining_time = remaining_companies * avg_time_per_company
                    
                    logger.info(f"Progress: {i+1}/{total_companies} ({((i+1)/total_companies*100):.1f}%)")
                    logger.info(f"Estimated time remaining: {estimated_remaining_time/60:.1f} minutes")
                    logger.info("-------------------")
                    
                except Exception as e:
                    logger.error(f"Error processing company {i+1} on page {current_page}: {str(e)}")
                    # Clean up any hanging pages
                    for p in context.pages[1:]:
                        try:
                            p.close()
                        except:
                            pass
                    continue

            try:
                pagination = page.query_elements(PAGINATION)
                if pagination and pagination.pagination.next_page_link:
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