# Skylark Drones — Business Intelligence Agent

A conversational business intelligence agent that connects to live Monday.com boards containing Deals and Work Orders data, cleans messy operational data, and answers founder-level business questions with actionable insights.

## 1. Overview

The application is designed around a common business intelligence workflow:

**Founder question → Query interpretation → Monday.com data → Data cleaning → Business intelligence → Cross-board analysis → Business answer**

The agent currently works with two Monday.com boards:

- **Deals** — sales pipeline and deal information
- **Work Orders** — project execution and financial information

The application reads data dynamically from Monday.com rather than hardcoding the provided CSV data.

---

## 2. Key Capabilities

### Sales & Pipeline

The agent can answer questions about:

- Current sales pipeline
- Open, won, and dead deals
- Pipeline value
- Won deal value
- Largest open deals
- Pipeline distribution by sector

### Work Order Execution

The agent can answer questions about:

- Total work orders
- Completed work orders
- Ongoing work
- Not-started work
- Work orders by sector
- Execution/completion performance

### Financial Intelligence

The agent can provide:

- Total work order value
- Billed amount
- Collected amount
- Receivables
- Amount still to be billed

### Cross-Board Business Intelligence

The application combines information from the Deals and Work Orders boards to provide sector-level business context.

For example:

> "How is Mining doing?"

can combine:

- Open pipeline
- Number of open deals
- Work-order volume
- Completed work orders
- Completion rate
- A leadership-oriented takeaway

The agent can also identify sectors where meaningful pipeline exists alongside relatively weak execution.

### Data Quality

The application explicitly surfaces data-quality limitations rather than silently treating missing values as valid business information.

Examples include:

- Missing closure probabilities
- Missing deal values
- Missing receivables
- Blank or inconsistent categorical values

---

## 3. Architecture

```text
                         ┌─────────────────────┐
                         │    User Question    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Conversational    │
                         │    Agent Layer      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │      Monday.com API          │
                    │                              │
                    │   ┌────────┐   ┌──────────┐ │
                    │   │ Deals  │   │Work      │ │
                    │   │ Board  │   │Orders    │ │
                    │   └────────┘   └──────────┘ │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │   Data Cleaning &   │
                         │    Normalization    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Business Intelligence│
                         │      Functions       │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
             Pipeline Analysis              Work Order Analysis
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │   Cross-Board      │
                         │      Analysis       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Founder-Level       │
                         │ Business Response   │
                         └─────────────────────┘


---
## 4. Technology Stack
-Python
-Pandas — data processing and analysis
-Requests — Monday.com GraphQL API communication
-Streamlit — conversational web interface
-python-dotenv — local environment configuration
-Monday.com GraphQL API — live business data source

5. Project Structure
Skylark_Drones_Assignment/
│
├── agent.py
├── app.py
├── business_intelligence.py
├── data_cleaner.py
├── monday_client.py
├── inspect_data.py
├── check_financials.py
├── test_agent.py
├── test_bi.py
├── requirements.txt
├── README.md
├── DECISION_LOG.md
└── .gitignore

Main modules

monday_client.py

Handles communication with Monday.com and retrieves board data dynamically through the GraphQL API.

data_cleaner.py

Cleans and normalizes retrieved business data, including dates, numeric values, missing values, and categorical fields.

business_intelligence.py

Contains the business analysis functions for pipeline, work orders, financials, data quality, and cross-board sector analysis.

agent.py

Interprets user questions and routes them to the appropriate business intelligence functionality.

app.py

Provides the Streamlit conversational interface.

6. Monday.com Configuration

The application expects two Monday.com boards.

Deals Board

Contains sales pipeline information such as:

Deal status
Deal stage
Deal value
Sector/service
Product
Closure information
Client information
Work Orders Board

Contains execution and financial information such as:

Execution status
Sector
Type of work
Work order value
Billing information
Collection information
Receivables
Work order status

The application does not hardcode the CSV data. It retrieves the current board contents dynamically from Monday.com.

The Monday.com integration is read-only.

7. Environment Variables

For local development, create a .env file in the project root:

MONDAY_API_TOKEN=your_monday_api_token
DEALS_BOARD_ID=your_deals_board_id
WORK_ORDERS_BOARD_ID=your_work_orders_board_id

Do not commit .env to GitHub.

For the hosted Streamlit application, the same values are configured through Streamlit Secrets.

8. Local Setup

Clone the repository and enter the project directory:

git clone https://github.com/Poojithmanepalli/Skylark_Drones_Assignment.git
cd Skylark_Drones_Assignment

Create a virtual environment:

python -m venv venv

Activate it on Windows PowerShell:

.\venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Configure the .env file with the Monday.com credentials.

Run the application:

streamlit run app.py

The application will open in the browser.

9. Example Questions

The agent supports questions such as:

What is our current pipeline?
What are our top deals?
How are our work orders doing?
Which sectors have the most work orders?
How much is receivable?
What data quality issues do we have?
How is Mining doing?
How is Renewables performing?
Give me an overview of Railways.
Which sectors have strong pipeline but execution risk?

The agent is designed to answer these questions using live Monday.com data rather than a static copy of the supplied CSV data.

10. Data Resilience

Real-world business data frequently contains missing or inconsistent values.

The application therefore:

Handles missing values gracefully
Converts numeric business fields into usable numeric representations
Normalizes date fields
Preserves missing information instead of inventing values
Handles blank categorical fields
Reports important data-quality limitations
Avoids probability-weighted pipeline calculations when closure probabilities are unavailable

For example, if closure probability is missing for all deals, the application explicitly reports that a probability-weighted pipeline cannot currently be calculated.

The application also retains data-quality caveats alongside business results so that incomplete source data does not silently become misleading information.

11. Leadership Updates

The optional leadership-update requirement is interpreted as providing concise business context in addition to raw metrics.

The application follows a simple pattern:

Metric → Context → Potential implication → Area requiring attention

For example, sector analysis can compare sales pipeline with operational execution to highlight areas where leadership may need to investigate further.

Leadership-oriented analysis is intended to help quickly understand:

Where pipeline is concentrated
Where operational workload is concentrated
Which sectors are executing well
Where potential execution risks exist
What data-quality limitations may affect decisions

12. Hosted Prototype

The application is deployed using Streamlit Community Cloud.

Live Application

https://skylarkdronesassignment-c8jvekwjyflpffslmeanqj.streamlit.app/

The hosted application can be tested without local setup and connects to the configured Monday.com boards dynamically.

13. Security

Credentials are not stored in the source code.

Local credentials are provided through .env, while the hosted application uses Streamlit Secrets.

The following files and directories are excluded from version control:

.env
venv/
__pycache__/
*.pyc
.streamlit/secrets.toml

The Monday.com integration is read-only.

API credentials should never be committed to the repository or included in the source-code ZIP.

14. Future Improvements

With additional development time, the agent could be extended with:

More flexible natural-language intent recognition
LLM-assisted query interpretation
More advanced relational queries across boards
Time-period analysis such as monthly and quarterly trends
Additional leadership dashboards
Automated leadership-report generation
More sophisticated anomaly and risk detection
Expanded automated test coverage

The current implementation prioritizes reliable access to live Monday.com data, transparent business calculations, cross-board analysis, data resilience, and explainable results.

