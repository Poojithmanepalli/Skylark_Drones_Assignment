# Skylark Drones — Decision Log

## 1. Problem Interpretation

The objective was interpreted as building a conversational business intelligence agent that can answer founder-level questions using live data from two Monday.com boards: Deals and Work Orders.

The agent therefore focuses on three layers:

1. Retrieve current data dynamically from Monday.com.
2. Clean and normalize messy business data.
3. Transform the cleaned data into business-level metrics and insights.

The supplied CSV data was treated as source data to be imported into Monday.com rather than as a static dataset to be embedded or hardcoded into the application.

---

## 2. Key Assumptions

### Monday.com as the Source of Truth

Monday.com is treated as the current source of business data. The application queries the Deals and Work Orders boards dynamically through the Monday.com GraphQL API.

### Read-Only Integration

The integration is intentionally read-only because the assignment requires the agent to consume business information rather than modify operational records.

### Missing Data

Missing values are treated as unavailable information rather than being replaced with assumptions that could create misleading business conclusions.

For example, closure probability is missing for the available Deals data. Therefore, a probability-weighted pipeline is not presented.

### Sector Matching

Sector names are used as a common business dimension across the Deals and Work Orders boards. This allows the agent to perform cross-board sector analysis.

---

## 3. Data Resilience Decisions

The provided data contains real-world inconsistencies such as:

- Missing values
- Blank categorical fields
- Inconsistent date representations
- Missing deal values
- Missing financial values
- Incomplete operational information

A dedicated cleaning layer was therefore implemented rather than performing analysis directly on raw API responses.

The cleaning process converts dates and numeric fields into usable representations, handles missing values, and preserves important data-quality limitations.

The agent also communicates data-quality caveats alongside business results.

This approach prioritizes trustworthy results over artificially complete-looking data.

---

## 4. Monday.com Integration Choice

The Monday.com GraphQL API was selected instead of hardcoding the CSV contents.

This provides several advantages:

- Data is retrieved dynamically.
- Changes in Monday.com can be reflected in the application.
- The implementation satisfies the read-only integration requirement.
- The same business logic can operate on the current contents of the boards.

API credentials are stored outside the source code using environment variables locally and Streamlit Secrets for the hosted application.

---

## 5. Technology Choices

### Python

Python was selected because it provides a strong ecosystem for data processing, API integration, and business analytics.

### Pandas

Pandas was used for cleaning, transformation, aggregation, and analysis of the Deals and Work Orders data.

### Streamlit

Streamlit was selected for the hosted conversational interface because it allows the business intelligence functionality to be exposed through a simple web application without requiring users to install the project locally.

### Rule-Based Query Routing

The initial query-understanding layer uses transparent intent and keyword matching.

This was chosen because the core business calculations should remain deterministic and explainable. A query is mapped to existing BI functions rather than allowing a language model to independently calculate business metrics.

---

## 6. Cross-Board Analysis

A key design decision was to support questions that require information from both boards.

For example, a question such as:

> "How is Mining doing?"

is interpreted as a request for a broader business overview rather than only a single metric.

The application combines:

- Open deals
- Open pipeline
- Work-order volume
- Completed work orders
- Completion rate

This allows the response to provide business context instead of returning isolated numbers.

The same principle is used for identifying potential execution-risk sectors by comparing pipeline activity with work-order completion.

---

## 7. Interpretation of "Leadership Updates"

The optional leadership-update requirement was interpreted as providing concise decision-support context rather than generating a long report.

The intended pattern is:

**Metric → Context → Potential implication → Area requiring attention**

For example, a sector with substantial open pipeline but relatively weak work-order completion can be highlighted as an area that may require leadership attention.

The goal is to help a founder or leadership team quickly understand:

- Where pipeline is concentrated
- Where operational workload is concentrated
- Which sectors are executing well
- Where potential execution risks exist
- Which data-quality limitations could affect decisions

---

## 8. Trade-Offs

### Deterministic Logic vs. LLM-Based Interpretation

The current implementation prioritizes deterministic and explainable business logic.

This means the agent does not yet understand every possible natural-language formulation. However, the trade-off is greater transparency: business metrics are calculated directly from the retrieved data rather than generated by an LLM.

With more time, an LLM could be added as a semantic interpretation layer while keeping the underlying calculations deterministic.

### Breadth vs. Reliability

The implementation focuses on a smaller set of meaningful founder-level business questions rather than attempting to support arbitrary questions with unreliable calculations.

Cross-board sector analysis was added because it provides significant business value while remaining explainable.

### Data Completeness vs. Data Integrity

Missing values are not automatically fabricated or inferred. This may result in some metrics being unavailable, but it reduces the risk of presenting incorrect information as fact.

---

## 9. Error and Data Quality Handling

The application reports data-quality limitations when they materially affect analysis.

Examples observed in the source data include:

- Closure Probability missing across Deals
- Deal value missing for a subset of Deals
- Amount receivable missing for some Work Orders
- Blank sector or status values

The system therefore distinguishes between:

- A genuine zero
- A missing value
- A value that cannot be calculated because source data is incomplete

This distinction is important for business reporting.

---

## 10. What I Would Do Differently With More Time

The next improvements would focus on expanding the agent from rule-based intent routing into a more flexible semantic business intelligence system.

Potential improvements include:

### LLM-Assisted Query Interpretation

An LLM could classify a founder's question into structured components such as:

- Business entity
- Sector
- Time period
- Metric
- Comparison
- Desired level of detail

The LLM would interpret the question, while Python would continue to perform the actual calculations.

### More Flexible Relational Queries

The system could support more complex questions involving relationships between Deals and Work Orders, such as:

- Pipeline versus execution performance
- Sector trends over time
- Deal-to-work-order conversion
- Client-level relationships
- Billing and collection performance by sector
- Operational backlog

### Time-Based Analysis

The current implementation could be extended to support:

- Monthly trends
- Quarterly trends
- Year-over-year comparisons
- Expected versus actual billing
- Pipeline movement over time

### Leadership Reporting

A dedicated leadership-summary mode could generate a compact executive update containing:

- Key metrics
- Positive developments
- Risks
- Data-quality caveats
- Recommended areas for investigation

---

## 11. Final Design Principle

The central design principle of the implementation is:

**Use live business data, make calculations transparent, surface data limitations, and provide context rather than only returning raw numbers.**

The system is intentionally structured so that additional query-understanding capabilities can be added later without replacing the underlying data retrieval, cleaning, and business intelligence layers.