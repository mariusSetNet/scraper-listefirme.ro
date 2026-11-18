# Listafirme Scraper LLM

A professional web scraping tool designed to extract company data from `listafirme.ro` and automatically synchronize it with an Airtable database. This project leverages **AgentQL** for intelligent element location, **Playwright** for browser automation, and **CapSolver** for handling CAPTCHA challenges.

## 🚀 Features

- **Intelligent Scraping**: Uses AgentQL to locate elements semantically, making the scraper more resilient to UI changes.
- **Session Management**: Implements a login state mechanism to avoid repeated authentications.
- **CAPTCHA Solving**: Integrated with CapSolver to bypass reCAPTCHA and image-based challenges.
- **Airtable Integration**: Automatically pushes extracted company information (Name, Status, Phone, Email) to a specified Airtable base.
- **Robust Pagination**: Handles multi-page navigation to ensure comprehensive data extraction.
- **Stealth Mode**: Utilizes `playwright-stealth` to minimize detection by anti-bot systems.

## 🛠️ Prerequisites

- **Python 3.11+**
- **Airtable Account** (API Key, Base ID, and Table Name)
- **AgentQL API Key**
- **CapSolver API Key**

## 📦 Installation

Follow these steps to set up the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/scraper-llm.git
cd scraper-llm
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.

**Windows:**
```bash
python -m venv env
.\env\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r scraper/requirements.txt
```

### 4. Install Playwright Browsers
```bash
playwright install chromium
```

## ⚙️ Configuration

The project uses a `.env` file to manage sensitive credentials. 

1. Copy the example environment file:
   ```bash
   cp scraper/.env.example scraper/.env
   ```
2. Open `scraper/.env` and fill in your details:
   ```env
   EMAIL=your_email@example.com
   PASSWORD=your_password
   AGENTQL_API_KEY=your_agentql_key
   CAPSOLVER_API_KEY=your_capsolver_key
   AIRTABLE_API_KEY=your_airtable_key
   AIRTABLE_BASE_ID=your_base_id
   AIRTABLE_TABLE_NAME=your_table_name
   ```

## 🚀 Usage

To start scraping, follow this specific sequence:

### Step 1: Generate Login State
Before running the main scraper, you must generate a session state file (`login_state.json`). This allows the scraper to remain authenticated.

```bash
python scraper/login_json.py
```
*This will open a browser, perform the login, and save the cookies/storage state to `scraper/login_state.json`.*

### Step 2: Run the Scraper
Once the login state is generated, execute the main scraping script:

```bash
python scraper/main.py
```
*The scraper will navigate through the company listings, extract data, and push it to your Airtable base.*

## 📁 Project Structure

```text
scraper-llm/
├── env/                    # Python virtual environment
├── scraper/
│   ├── cap-solver/         # CAPTCHA solver browser extension
│   ├── instructions/       # Project documentation and guidelines
│   ├── logs/               # Execution logs
│   ├── .env                # Environment variables (Private)
│   ├── .env.example        # Environment template
│   ├── login_json.py       # Script to generate session state
│   ├── login_state.json    # Saved authentication state
│   ├── main.py             # Main scraping logic and Airtable integration
│   ├── requirements.txt    # Project dependencies
│   └── cap_test.py         # CAPTCHA solving test utility
└── README.md               # Project documentation
```

## 📝 License
This project is for educational/internal use. Please ensure you comply with the target website's Terms of Service.
