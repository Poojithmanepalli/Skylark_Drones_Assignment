import os
import json

from dotenv import load_dotenv

load_dotenv()

from monday_client import get_deals, get_work_orders

from data_cleaner import (
    clean_deals,
    clean_work_orders
)

from business_intelligence import (
    pipeline_summary,
    pipeline_by_sector,
    top_deals,
    work_order_summary,
    work_orders_by_sector,
    financial_summary,
    data_quality_summary,
    cross_board_sector_analysis
)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# ============================================================
# OPENAI CONFIGURATION
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = None

if OpenAI is not None and OPENAI_API_KEY:
    try:
        openai_client = OpenAI(
            api_key=OPENAI_API_KEY
        )
    except Exception:
        openai_client = None


# ============================================================
# FORMATTING
# ============================================================

def format_rupees(value):

    if value is None:
        return "₹0"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "₹0"

    crore = value / 10_000_000

    if crore >= 1:
        return f"₹{crore:.2f} crore"

    lakh = value / 100_000

    return f"₹{lakh:.2f} lakh"


# ============================================================
# DATA LOADING
# ============================================================

def load_data():

    deals = clean_deals(
        get_deals()
    )

    work_orders = clean_work_orders(
        get_work_orders()
    )

    return deals, work_orders


# ============================================================
# SECTOR DETECTION
# ============================================================

def find_sector(question):

    sector_names = {
        "mining": "Mining",
        "renewables": "Renewables",
        "railways": "Railways",
        "powerline": "Powerline",
        "construction": "Construction",
        "others": "Others",
        "dsp": "DSP",
        "tender": "Tender",
        "security and surveillance": "Security and Surveillance",
        "manufacturing": "Manufacturing",
        "aviation": "Aviation"
    }

    question = question.lower()

    for name, display_name in sector_names.items():

        if name in question:
            return display_name

    return None


# ============================================================
# OPENAI SEMANTIC UNDERSTANDING
# ============================================================

def understand_question(question):

    """
    Use OpenAI only to understand the user's intent.

    OpenAI does NOT calculate business metrics.
    Python/Pandas remains responsible for calculations.
    """

    if openai_client is None:
        return None

    system_prompt = """
You are the intent-understanding layer of a business intelligence application.

The application has two data sources:

1. Deals
   - sales pipeline
   - deal stages
   - deal values
   - sectors

2. Work Orders
   - operational execution
   - work order counts
   - completion
   - billing
   - collections
   - receivables
   - sectors

Your job is ONLY to understand the user's business question.

Do NOT calculate numbers.
Do NOT invent data.
Do NOT answer the question.

Return ONLY valid JSON.

Allowed intents:

pipeline
top_deals
pipeline_by_sector
work_orders
work_orders_by_sector
financials
data_quality
cross_board_analysis
sector_overview
operational_performance
unsupported

Definitions:

pipeline:
Questions about overall sales pipeline, open deals, won deals, dead deals, pipeline value.

top_deals:
Questions asking for biggest, largest, or top deals.

pipeline_by_sector:
Questions asking about sales pipeline/deal opportunities by sector.

work_orders:
Questions about overall work-order execution, completed work orders, ongoing work, not-started work.

work_orders_by_sector:
Questions asking which sectors have the most work orders or operational workload by sector.

financials:
Questions about billing, collections, receivables, collected money, billed money, or amount to be billed.

data_quality:
Questions about missing data, data quality, incomplete records, or data issues.

cross_board_analysis:
Questions requiring comparison or relationship between sales pipeline and operational work orders across sectors.

sector_overview:
Questions such as:
- How is Mining doing?
- How is Renewables performing?
- Give me an overview of Railways.
- Tell me about Mining.
These should combine Deals and Work Orders.

operational_performance:
Questions such as:
- Where are we strongest operationally?
- Which sector executes best?
- Which sector has the best completion rate?
- Which sector is performing best operationally?

unsupported:
Questions asking for metrics that are not currently represented by the application's available BI functions, or questions that cannot reasonably be answered from Deals and Work Orders.

Important:
"Revenue" is NOT automatically the same as work-order count.
If a user asks "Which sector has the highest revenue?", classify it as:
- financials if it is a general financial question
- pipeline_by_sector if they explicitly mean sales/deal revenue
- unsupported if they specifically require a sector-level revenue metric that the available functions do not provide.

Return this exact structure:

{
  "intent": "...",
  "sector": "Mining or Renewables or Railways or ... or null",
  "comparison": true or false,
  "time_period": "description or null"
}
"""

    try:

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            response_format={
                "type": "json_object"
            },
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        content = response.choices[0].message.content

        result = json.loads(content)

        return result

    except Exception:

        return None


# ============================================================
# OPERATIONAL PERFORMANCE
# ============================================================

def answer_operational_performance(work_orders):

    result = work_orders.copy()

    if result.empty:
        return (
            "### Operational Performance\n\n"
            "No work-order data is currently available."
        )

    sector_counts = work_orders_by_sector(
        work_orders
    )

    cross_data = cross_board_sector_analysis(
        result.assign(
            **{}
        ) if False else load_data()[0],
        work_orders
    )

    valid = cross_data[
        cross_data["total_work_orders"] > 0
    ].copy()

    if valid.empty:

        return (
            "### Operational Performance\n\n"
            "There are currently no sectors with recorded "
            "work orders, so operational performance cannot "
            "be compared."
        )

    valid = valid.sort_values(
        "completion_rate",
        ascending=False
    )

    best = valid.iloc[0]

    best_sector = best["Sector/service"]

    if not best_sector:
        best_sector = "Unknown"

    best_rate = float(
        best["completion_rate"]
    )

    best_count = int(
        best["total_work_orders"]
    )

    response = (
        "### Strongest Operational Performance\n\n"
        f"**{best_sector}** currently has the highest "
        f"recorded work-order completion rate at "
        f"**{best_rate:.1f}%** across "
        f"**{best_count} work orders**.\n\n"
    )

    response += "### Sector Performance\n\n"

    for _, row in valid.head(5).iterrows():

        sector_name = row["Sector/service"]

        if not sector_name:
            sector_name = "Unknown"

        response += (
            f"- **{sector_name}:** "
            f"{row['completion_rate']:.1f}% completion "
            f"({int(row['total_work_orders'])} work orders)\n"
        )

    if best_count <= 2:

        response += (
            "\n**Leadership context:** "
            "The highest completion rate is based on a "
            "small number of work orders, so it should be "
            "interpreted cautiously. High-volume sectors "
            "provide a stronger operational signal."
        )

    return response


# ============================================================
# SECTOR BUSINESS OVERVIEW
# ============================================================

def answer_sector_overview(
    sector,
    deals,
    work_orders
):

    cross_data = cross_board_sector_analysis(
        deals,
        work_orders
    )

    sector_data = cross_data[
        cross_data["Sector/service"].astype(str).str.lower()
        == sector.lower()
    ]

    response = (
        f"### {sector} — Business Overview\n\n"
    )

    if sector_data.empty:

        response += (
            f"No matching data was found for **{sector}** "
            "across the Deals and Work Orders boards."
        )

        return response

    row = sector_data.iloc[0]

    pipeline = row["pipeline_value"]

    open_deals = int(
        row["open_deals"]
    )

    total_work_orders = int(
        row["total_work_orders"]
    )

    completed_work_orders = int(
        row["completed_work_orders"]
    )

    completion_rate = row[
        "completion_rate"
    ]

    response += "**Sales Pipeline**\n\n"

    response += (
        f"- **Open deals:** {open_deals}\n"
        f"- **Open pipeline:** "
        f"**{format_rupees(pipeline)}**\n\n"
    )

    response += "**Work Order Execution**\n\n"

    response += (
        f"- **Total work orders:** "
        f"{total_work_orders}\n"
        f"- **Completed:** "
        f"{completed_work_orders}\n"
    )

    if total_work_orders > 0:

        response += (
            f"- **Completion rate:** "
            f"**{completion_rate:.1f}%**\n\n"
        )

    else:

        response += (
            "- **Completion rate:** "
            "Not available because no work orders "
            "are currently recorded.\n\n"
        )

    response += "**Leadership Takeaway**\n\n"

    if total_work_orders == 0:

        response += (
            f"{sector} has {format_rupees(pipeline)} "
            f"in open pipeline across {open_deals} deals, "
            "but there are currently no recorded work "
            "orders in the Work Orders board. "
            "This makes operational execution difficult "
            "to assess from the available data."
        )

    elif completion_rate < 40:

        response += (
            f"{sector} deserves attention because it has "
            f"{format_rupees(pipeline)} in open pipeline "
            f"while only {completion_rate:.1f}% of its "
            "recorded work orders are completed. "
            "This suggests a potential execution risk."
        )

    elif completion_rate < 70:

        response += (
            f"{sector} has {format_rupees(pipeline)} in "
            f"open pipeline and a {completion_rate:.1f}% "
            "work-order completion rate. "
            "Execution is progressing, but there is "
            "still meaningful operational backlog to monitor."
        )

    else:

        response += (
            f"{sector} has {format_rupees(pipeline)} in "
            f"open pipeline and a relatively strong "
            f"{completion_rate:.1f}% completion rate "
            "across its recorded work orders."
        )

    return response


# ============================================================
# CROSS-BOARD ANALYSIS
# ============================================================

def answer_cross_board(
    deals,
    work_orders
):

    result = cross_board_sector_analysis(
        deals,
        work_orders
    )

    response = (
        "### Cross-Board Sector Analysis\n\n"
    )

    for _, row in result.iterrows():

        sector_name = row["Sector/service"]

        if not sector_name:
            sector_name = "Unknown"

        pipeline = row["pipeline_value"]

        work_order_count = int(
            row["total_work_orders"]
        )

        completion_rate = row[
            "completion_rate"
        ]

        response += (
            f"**{sector_name}** — "
            f"open pipeline: "
            f"{format_rupees(pipeline)}, "
            f"work orders: "
            f"{work_order_count}"
        )

        if work_order_count > 0:

            response += (
                f", completion: "
                f"{completion_rate:.1f}%"
            )

        else:

            response += (
                ", no work orders currently recorded"
            )

        response += "\n\n"

    risk_data = result[
        (result["total_work_orders"] > 0)
        & (result["pipeline_value"] > 0)
        & (result["completion_rate"] < 50)
    ]

    response += "### Business Takeaway\n\n"

    if not risk_data.empty:

        risk_sectors = []

        for _, row in risk_data.iterrows():

            sector_name = row["Sector/service"]

            if not sector_name:
                sector_name = "Unknown"

            risk_sectors.append(
                f"**{sector_name}** "
                f"({format_rupees(row['pipeline_value'])} "
                f"pipeline, "
                f"{row['completion_rate']:.1f}% completion)"
            )

        response += (
            "Potential execution-risk sectors are: "
            + ", ".join(risk_sectors)
            + ". These areas combine open pipeline "
            "with relatively low work-order completion "
            "and may deserve leadership attention."
        )

    else:

        response += (
            "No sector currently meets the defined "
            "high-pipeline / low-execution risk criteria."
        )

    response += (
        "\n\n**Data caveat:** A 0% completion rate "
        "for sectors with no work orders does not "
        "indicate poor execution; there is no "
        "operational denominator for those sectors."
    )

    return response


# ============================================================
# PIPELINE
# ============================================================

def answer_pipeline(deals):

    summary = pipeline_summary(
        deals
    )

    sector_data = pipeline_by_sector(
        deals
    )

    response = (
        f"### Current Pipeline\n\n"
        f"- **Open deals:** {summary['open_deals']}\n"
        f"- **Open pipeline:** "
        f"**{format_rupees(summary['open_pipeline'])}**\n"
        f"- **Won deals:** {summary['won_deals']}\n"
        f"- **Won value:** "
        f"**{format_rupees(summary['won_value'])}**\n"
        f"- **Dead deals:** {summary['dead_deals']}\n\n"
    )

    response += "**Top open-pipeline sectors:**\n\n"

    for sector_name, row in sector_data.head(5).iterrows():

        display_sector = (
            sector_name
            if sector_name
            else "Unknown"
        )

        response += (
            f"- **{display_sector}:** "
            f"{format_rupees(row['pipeline_value'])} "
            f"({int(row['deal_count'])} deals)\n"
        )

    response += (
        "\n**Data caveat:** Closure Probability is "
        "missing for all deals, so a probability-weighted "
        "pipeline cannot currently be calculated."
    )

    return response


# ============================================================
# TOP DEALS
# ============================================================

def answer_top_deals(deals):

    result = top_deals(
        deals,
        5
    )

    response = "### Top Open Deals\n\n"

    for _, row in result.iterrows():

        response += (
            f"- **{row['item_name']}** — "
            f"{format_rupees(row['Masked Deal value'])} — "
            f"{row['Sector/service']} — "
            f"{row['Deal Stage']}\n"
        )

    return response


# ============================================================
# WORK ORDERS
# ============================================================

def answer_work_orders(work_orders):

    summary = work_order_summary(
        work_orders
    )

    response = (
        f"### Work Order Overview\n\n"
        f"- **Total:** "
        f"{summary['total_work_orders']}\n"
        f"- **Completed:** "
        f"{summary['completed']}\n"
        f"- **Ongoing:** "
        f"{summary['ongoing']}\n"
        f"- **Not started:** "
        f"{summary['not_started']}\n\n"
        f"Other execution statuses are also present, "
        f"including 'Executed until current month', "
        f"'Pause / struck', and 'Partial Completed'."
    )

    return response


# ============================================================
# WORK ORDERS BY SECTOR
# ============================================================

def answer_work_orders_by_sector(work_orders):

    result = work_orders_by_sector(
        work_orders
    )

    response = (
        "### Work Orders by Sector\n\n"
    )

    for sector_name, count in result.head(10).items():

        display_sector = (
            sector_name
            if sector_name
            else "Unknown"
        )

        response += (
            f"- **{display_sector}:** "
            f"{int(count)} work orders\n"
        )

    return response


# ============================================================
# PIPELINE BY SECTOR
# ============================================================

def answer_pipeline_by_sector(deals):

    result = pipeline_by_sector(
        deals
    )

    response = (
        "### Deal Pipeline by Sector\n\n"
    )

    for sector_name, row in result.head(10).iterrows():

        display_sector = (
            sector_name
            if sector_name
            else "Unknown"
        )

        response += (
            f"- **{display_sector}:** "
            f"{format_rupees(row['pipeline_value'])} "
            f"({int(row['deal_count'])} open deals)\n"
        )

    return response


# ============================================================
# FINANCIALS
# ============================================================

def answer_financials(work_orders):

    financials = financial_summary(
        work_orders
    )

    response = (
        "### Work Order Financials\n\n"
        f"- **Total order value:** "
        f"{format_rupees(financials['total_amount'])}\n"
        f"- **Billed:** "
        f"{format_rupees(financials['billed_amount'])}\n"
        f"- **Collected:** "
        f"{format_rupees(financials['collected_amount'])}\n"
        f"- **Receivable:** "
        f"{format_rupees(financials['receivable'])}\n"
        f"- **To be billed:** "
        f"{format_rupees(financials['to_be_billed'])}\n"
    )

    return response


# ============================================================
# DATA QUALITY
# ============================================================

def answer_data_quality(
    deals,
    work_orders
):

    issues = data_quality_summary(
        deals,
        work_orders
    )

    response = "### Data Quality\n\n"

    for issue in issues:

        response += f"- {issue}\n"

    return response


# ============================================================
# SEMANTIC INTENT ROUTER
# ============================================================

def answer_from_intent(
    intent_data,
    question,
    deals,
    work_orders
):

    if not intent_data:
        return None

    intent = intent_data.get(
        "intent"
    )

    sector = intent_data.get(
        "sector"
    )

    if sector:
        known_sector = find_sector(
            sector
        )

        if known_sector:
            sector = known_sector

    # --------------------------------------------------------
    # SECTOR OVERVIEW
    # --------------------------------------------------------

    if intent == "sector_overview":

        if not sector:
            sector = find_sector(
                question
            )

        if sector:
            return answer_sector_overview(
                sector,
                deals,
                work_orders
            )

        return None

    # --------------------------------------------------------
    # OPERATIONAL PERFORMANCE
    # --------------------------------------------------------

    if intent == "operational_performance":

        return answer_operational_performance(
            work_orders
        )

    # --------------------------------------------------------
    # CROSS BOARD
    # --------------------------------------------------------

    if intent == "cross_board_analysis":

        return answer_cross_board(
            deals,
            work_orders
        )

    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    if intent == "pipeline":

        return answer_pipeline(
            deals
        )

    # --------------------------------------------------------
    # TOP DEALS
    # --------------------------------------------------------

    if intent == "top_deals":

        return answer_top_deals(
            deals
        )

    # --------------------------------------------------------
    # PIPELINE BY SECTOR
    # --------------------------------------------------------

    if intent == "pipeline_by_sector":

        return answer_pipeline_by_sector(
            deals
        )

    # --------------------------------------------------------
    # WORK ORDERS
    # --------------------------------------------------------

    if intent == "work_orders":

        return answer_work_orders(
            work_orders
        )

    # --------------------------------------------------------
    # WORK ORDERS BY SECTOR
    # --------------------------------------------------------

    if intent == "work_orders_by_sector":

        return answer_work_orders_by_sector(
            work_orders
        )

    # --------------------------------------------------------
    # FINANCIALS
    # --------------------------------------------------------

    if intent == "financials":

        return answer_financials(
            work_orders
        )

    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    if intent == "data_quality":

        return answer_data_quality(
            deals,
            work_orders
        )

    # --------------------------------------------------------
    # UNSUPPORTED
    # --------------------------------------------------------

    if intent == "unsupported":

        return (
            "### Unable to answer that precisely\n\n"
            "I can analyze the Deals and Work Orders "
            "data, but the requested metric is not "
            "currently available in the implemented "
            "business intelligence layer.\n\n"
            "I don't want to infer or invent a number "
            "that is not supported by the available data."
        )

    return None


# ============================================================
# EXISTING KEYWORD FALLBACK
# ============================================================

def keyword_answer_question(question):

    """
    Original deterministic routing logic.

    This is intentionally kept as a fallback so the
    application continues working if OpenAI is unavailable.
    """

    question = question.lower().strip()

    deals, work_orders = load_data()

    sector = find_sector(
        question
    )

    # --------------------------------------------------------
    # SECTOR BUSINESS OVERVIEW
    # --------------------------------------------------------

    if (
        sector
        and (
            "how is" in question
            or "how are" in question
            or "how's" in question
            or "performance" in question
            or "performing" in question
            or "doing" in question
            or "overview" in question
            or "situation" in question
            or "tell me about" in question
            or "what's happening" in question
            or "what is happening" in question
        )
        and not any(word in question for word in [
            "top deal",
            "largest deal",
            "biggest deal",
            "data quality"
        ])
    ):

        return answer_sector_overview(
            sector,
            deals,
            work_orders
        )

    # --------------------------------------------------------
    # OPERATIONAL PERFORMANCE
    # --------------------------------------------------------

    if any(word in question for word in [
        "strongest operationally",
        "strongest operational",
        "best operationally",
        "best operational",
        "best completion rate",
        "highest completion rate",
        "which sector executes best",
        "which sector executes the best"
    ]):

        return answer_operational_performance(
            work_orders
        )

    # --------------------------------------------------------
    # CROSS BOARD
    # --------------------------------------------------------

    if (
        (
            "sector" in question
            or "sectors" in question
        )
        and (
            "pipeline" in question
            or "execution" in question
            or "work order" in question
        )
        and (
            "compare" in question
            or "strong" in question
            or "risk" in question
            or "performance" in question
            or "doing" in question
            or "focus" in question
            or "attention" in question
        )
    ):

        return answer_cross_board(
            deals,
            work_orders
        )

    # --------------------------------------------------------
    # PIPELINE
    # --------------------------------------------------------

    if any(word in question for word in [
        "pipeline",
        "deal pipeline",
        "sales pipeline"
    ]):

        return answer_pipeline(
            deals
        )

    # --------------------------------------------------------
    # TOP DEALS
    # --------------------------------------------------------

    if any(word in question for word in [
        "top deals",
        "largest deals",
        "biggest deals"
    ]):

        return answer_top_deals(
            deals
        )

    # --------------------------------------------------------
    # WORK ORDERS
    # --------------------------------------------------------

    if (
        any(word in question for word in [
            "work order",
            "work orders",
            "execution"
        ])
        and "sector" not in question
    ):

        return answer_work_orders(
            work_orders
        )

    # --------------------------------------------------------
    # SECTORS
    # --------------------------------------------------------

    if (
        "sector" in question
        or "sectors" in question
    ):

        if (
            "deal" in question
            or "pipeline" in question
        ):

            return answer_pipeline_by_sector(
                deals
            )

        else:

            return answer_work_orders_by_sector(
                work_orders
            )

    # --------------------------------------------------------
    # FINANCIALS
    # --------------------------------------------------------

    if any(word in question for word in [
        "receivable",
        "receivables",
        "billing",
        "billed",
        "collected",
        "collection",
        "financial",
        "outstanding"
    ]):

        return answer_financials(
            work_orders
        )

    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    if any(word in question for word in [
        "data quality",
        "missing data",
        "data issues",
        "missing values"
    ]):

        return answer_data_quality(
            deals,
            work_orders
        )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return (
        "I can currently answer questions about:\n\n"
        "- Sales pipeline\n"
        "- Top deals\n"
        "- Pipeline by sector\n"
        "- Work order execution\n"
        "- Work orders by sector\n"
        "- Cross-board sector performance\n"
        "- Operational performance\n"
        "- Billing and receivables\n"
        "- Data quality\n\n"
        "Try asking something like:\n"
        "\"How is Mining doing?\"\n"
        "or\n"
        "\"Where are we strongest operationally?\"\n"
        "or\n"
        "\"Which sectors have strong pipeline but execution risk?\""
    )


# ============================================================
# MAIN PUBLIC FUNCTION
# ============================================================

def answer_question(question):

    """
    Main entry point used by app.py.

    Strategy:

    1. Load live Monday.com data.
    2. Ask OpenAI to interpret the question.
    3. Route the interpretation to deterministic BI functions.
    4. If OpenAI is unavailable or fails, use the deterministic
       keyword router as a fallback.
    """

    if not question or not question.strip():

        return (
            "Please enter a business question."
        )

    # --------------------------------------------------------
    # Load data once
    # --------------------------------------------------------

    deals, work_orders = load_data()

    # --------------------------------------------------------
    # Try OpenAI semantic interpretation
    # --------------------------------------------------------

    intent_data = understand_question(
        question
    )

    if intent_data:

        try:

            semantic_answer = answer_from_intent(
                intent_data,
                question,
                deals,
                work_orders
            )

            if semantic_answer:

                return semantic_answer

        except Exception:
            pass

    # --------------------------------------------------------
    # Safe fallback
    # --------------------------------------------------------

    return keyword_answer_question(
        question
    )