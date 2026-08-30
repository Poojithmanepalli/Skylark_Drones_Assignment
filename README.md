# Skylark Drones — Business Intelligence Agent

A conversational business intelligence agent that connects to live Monday.com boards containing Deals and Work Orders data, cleans messy operational data, and answers founder-level business questions with actionable insights.

---

## 1. Overview

The application is designed around a business intelligence workflow:

**Founder Question → Query Understanding → Monday.com Data → Data Cleaning → Business Intelligence → Cross-Board Analysis → Business Answer**

The agent works with two Monday.com boards:

- **Deals** — sales pipeline and deal information
- **Work Orders** — project execution and financial information

The application reads data dynamically from Monday.com rather than relying on hardcoded CSV data.

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
- Execution and completion performance

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
- Leadership-oriented observations

The agent can also identify sectors where meaningful pipeline exists alongside relatively weak execution.

### Conversational Query Understanding

The application supports natural-language variations of business questions.

For example, users do not need to use the exact wording of predefined questions. Questions such as:

- "How is Mining doing?"
- "Give me an overview of Mining."
- "Which sector executes best?"
- "Where are we strongest operationally?"
- "Which part of the business needs attention?"

can be interpreted and mapped to the relevant business intelligence analysis.

### Data Quality Handling

The application explicitly surfaces data-quality limitations rather than silently treating missing values as valid business information.

Examples include:

- Missing closure probabilities
- Missing deal values
- Missing receivables
- Blank or inconsistent categorical values

---

## 3. Architecture

The application follows a modular architecture:

```text
                         ┌─────────────────────┐
                         │    User Question    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Query Understanding │
                         │  & Agent Layer      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │       Monday.com API         │
                    │                              │
                    │   ┌────────┐   ┌──────────┐ │
                    │   │ Deals  │   │   Work   │ │
                    │   │ Board  │   │  Orders  │ │
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
                                    │
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
```

### Main Components

| Component | Responsibility |
|---|---|
| `app.py` | Streamlit user interface and conversation history |
| `agent.py` | Query understanding, routing, and response generation |
| `monday_client.py` | Monday.com GraphQL API communication |
| `data_cleaner.py` | Cleaning and normalization of board data |
| `business_intelligence.py` | Core business intelligence calculations |
| `check_financials.py` | Financial and receivables analysis |
| `inspect_data.py` | Data inspection and debugging utilities |
| `test_agent.py` | Agent-level tests |
| `test_bi.py` | Business intelligence tests |

---

## 4. Technology Stack

- **Python** — core application and business logic
- **Pandas** — data processing, cleaning, and analysis
- **Requests** — Monday.com GraphQL API communication
- **Streamlit** — conversational web interface
- **python-dotenv** — local environment configuration
- **Monday.com GraphQL API** — live business data source
- **OpenAI API** — semantic understanding of natural-language business questions

The implementation intentionally uses a lightweight Python-based stack so that the application remains easy to understand, deploy, and maintain.

---

## 5. Monday.com Integration

The application retrieves live data from Monday.com using its GraphQL API.

Two boards are used:

### Deals Board

Contains sales pipeline information such as:

- Deal name
- Sector
- Deal value
- Deal status
- Closure probability
- Other relevant deal attributes

### Work Orders Board

Contains execution and financial information such as:

- Work order
- Sector
- Status
- Work order value
- Billing information
- Collection information
- Receivables

The application dynamically retrieves board data at runtime.

No business results are hardcoded into the application.

---

## 6. Data Cleaning & Normalization

Real-world operational data may contain missing, inconsistent, or differently formatted values.

The application therefore performs data cleaning before business analysis.

Typical transformations include:

- Normalizing column names
- Handling missing values
- Converting numeric fields safely
- Normalizing categorical values
- Handling blank sectors
- Converting financial fields into usable numeric values
- Preventing malformed records from breaking the analysis

This allows the business intelligence layer to operate on a consistent representation of the underlying Monday.com data.

---

## 7. Business Intelligence Layer

The business intelligence layer contains reusable functions for answering common business questions.

### Pipeline Analysis

Examples:

- Total pipeline
- Open pipeline
- Won pipeline
- Dead/lost deals
- Largest open deals
- Pipeline by sector

### Work Order Analysis

Examples:

- Total work orders
- Completed work orders
- Ongoing work
- Not-started work
- Work orders by sector
- Completion rates

### Financial Analysis

Examples:

- Total work order value
- Billed amount
- Collected amount
- Receivables
- Unbilled amount

### Cross-Board Analysis

The application can combine Deals and Work Orders data using common business dimensions such as sector.

This enables questions such as:

- Which sectors have strong pipeline but weak execution?
- How is a particular sector performing?
- Which sectors have significant business activity?
- Where should leadership pay attention?

---

## 8. Conversational Query Handling

The agent accepts natural-language questions rather than requiring users to select a predefined report.

The query handling process is:

```text
User Question
      ↓
Understand Intent
      ↓
Identify Business Area
      ↓
Select Relevant Analysis
      ↓
Retrieve Live Monday.com Data
      ↓
Perform Calculation
      ↓
Generate Business-Oriented Response
```

The application also supports semantic variations of business questions.

For example, questions about operational strength may be mapped to work-order execution analysis even when the user does not use the exact phrase "work-order execution."

---

## 9. Leadership-Oriented Insights

The goal is not only to return raw numbers but also to provide information that is useful for decision-making.

For example, instead of only returning:

> Mining has 100 work orders.

the agent can combine relevant operational and pipeline information to provide context about:

- Business activity
- Pipeline strength
- Execution performance
- Completion rate
- Potential execution risks

This supports a founder-level view of the business rather than simply presenting database records.

---

## 10. Error Handling

The application includes handling for common data and API issues.

### API Failures

If Monday.com cannot be reached or an API request fails, the application catches the exception and returns a user-facing error rather than crashing silently.

### Data Quality Issues

Missing or malformed values are handled during data cleaning.

The application avoids presenting unavailable information as if it were valid.

### Query Handling

If a question cannot be confidently mapped to the supported business analyses, the agent communicates the supported areas instead of inventing a result.

---

## 11. Project Structure

```text
Skylark_Drones_Assignment/
│
├── agent.py
├── app.py
├── business_intelligence.py
├── check_financials.py
├── data_cleaner.py
├── inspect_data.py
├── monday_client.py
│
├── test_agent.py
├── test_bi.py
│
├── requirements.txt
├── README.md
├── DECISION_LOG.md
└── .gitignore
```

---

## 12. Local Setup

### 12.1 Clone the Repository

```bash
git clone https://github.com/Poojithmanepalli/Skylark_Drones_Assignment.git
cd Skylark_Drones_Assignment
```

### 12.2 Create a Virtual Environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 12.3 Install Dependencies

```powershell
pip install -r requirements.txt
```

### 12.4 Configure Environment Variables

Create a `.env` file in the project root.

Example:

```text
MONDAY_API_TOKEN=your_monday_api_token
DEALS_BOARD_ID=your_deals_board_id
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
OPENAI_API_KEY=your_openai_api_key
```

Do not commit `.env` to GitHub.

The repository's `.gitignore` excludes environment secrets.

### 12.5 Run the Application

```powershell
streamlit run app.py
```

The application will be available locally through the Streamlit URL shown in the terminal.

---

## 13. Streamlit Deployment

The application is deployed using Streamlit Community Cloud.

Deployment steps:

1. Push the project to a public GitHub repository.
2. Connect the GitHub repository to Streamlit.
3. Select the `main` branch.
4. Select `app.py` as the main file.
5. Select a compatible Python version.
6. Add required secrets through Streamlit's Secrets configuration.
7. Deploy the application.

The deployed application reads credentials from Streamlit Secrets rather than storing them in the repository.

### Required Streamlit Secrets

```toml
MONDAY_API_TOKEN = "your_monday_api_token"
DEALS_BOARD_ID = "your_deals_board_id"
WORK_ORDERS_BOARD_ID = "your_work_orders_board_id"
OPENAI_API_KEY = "your_openai_api_key"
```

---

## 14. Testing

The project includes tests for the agent and business intelligence components.

Run:

```powershell
python test_agent.py
```

and:

```powershell
python test_bi.py
```

The application was also manually tested using both predefined example questions and natural-language variations.

Examples include:

```text
What is our current pipeline?
```

```text
What are our top deals?
```

```text
How are our work orders doing?
```

```text
How is Mining doing?
```

```text
Where are we strongest operationally?
```

```text
Which sector has the highest revenue?
```

---

## Hosted Application

The working hosted prototype is available at:

https://skylarkdronesassignment-c8jvekwjyflpffslmeanqj.streamlit.app/

## Source Repository

The complete source code and documentation are available at:

https://github.com/Poojithmanepalli/Skylark_Drones_Assignment

---

## Documentation

Additional design decisions and implementation trade-offs are documented in:

**`DECISION_LOG.md`**

The Decision Log covers:

- Key assumptions
- Technical trade-offs
- Technology choices
- Interpretation of leadership updates
- What could be improved with additional development time

---

## Security

Sensitive credentials are intentionally excluded from the repository.

The following are not committed:

```text
.env
venv/
__pycache__/
.streamlit/secrets.toml
```

API credentials should be supplied through local environment variables or Streamlit Secrets.

---

## Future Improvements

With additional development time, the application could be extended with:

- More advanced natural-language query planning
- Additional cross-board metrics
- More granular financial analysis
- Interactive visual dashboards
- More comprehensive automated testing
- Additional business KPIs
- Improved conversational context across multiple follow-up questions
- More advanced anomaly and risk detection

---

## Conclusion

The Skylark Drones Business Intelligence Agent provides a lightweight conversational interface over live Monday.com business data.

It combines:

**Live Data + Data Cleaning + Business Intelligence + Cross-Board Analysis + Natural-Language Query Understanding**

to turn operational data into founder-level business insights.