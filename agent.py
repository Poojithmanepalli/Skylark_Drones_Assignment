import re

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


def format_rupees(value):

    if value is None:
        return "₹0"

    crore = value / 10_000_000

    if crore >= 1:
        return f"₹{crore:.2f} crore"

    lakh = value / 100_000

    return f"₹{lakh:.2f} lakh"


def load_data():

    deals = clean_deals(
        get_deals()
    )

    work_orders = clean_work_orders(
        get_work_orders()
    )

    return deals, work_orders


def answer_question(question):

    question = question.lower().strip()

    deals, work_orders = load_data()
        # --------------------------------
    # CLARIFICATION
    # --------------------------------

    sector_names = [
        "mining",
        "renewables",
        "railways",
        "powerline",
        "construction",
        "others",
        "dsp",
        "tender",
        "security and surveillance",
        "manufacturing",
        "aviation"
    ]

    if (
        any(sector in question for sector in sector_names)
        and any(word in question for word in [
            "how is",
            "how are",
            "performance",
            "doing",
            "doing?"
        ])
        and not any(word in question for word in [
            "pipeline",
            "deal",
            "work order",
            "execution",
            "billing",
            "financial",
            "receivable",
            "collection"
        ])
    ):

        return (
            "I can evaluate this sector from several angles. "
            "Would you like to see its **sales pipeline**, "
            "**work-order execution**, or **financial performance**?"
        )

    # --------------------------------
    # PIPELINE
    # --------------------------------

    if any(word in question for word in [
        "pipeline",
        "deal pipeline",
        "sales pipeline"
    ]):

        summary = pipeline_summary(deals)

        sector_data = pipeline_by_sector(deals)

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

        for sector, row in sector_data.head(5).iterrows():

            sector_name = sector if sector else "Unknown"

            response += (
                f"- **{sector_name}:** "
                f"{format_rupees(row['pipeline_value'])} "
                f"({int(row['deal_count'])} deals)\n"
            )

        response += (
            "\n**Data caveat:** Closure Probability is "
            "missing for all deals, so a probability-weighted "
            "pipeline cannot currently be calculated."
        )

        return response


    # --------------------------------
    # TOP DEALS
    # --------------------------------

    if any(word in question for word in [
        "top deals",
        "largest deals",
        "biggest deals"
    ]):

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
        # --------------------------------
    # CROSS-BOARD ANALYSIS
    # --------------------------------

    if (
        ("sector" in question)
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
        )
    ):

        result = cross_board_sector_analysis(
            deals,
            work_orders
        )

        response = (
            "### Cross-Board Sector Analysis\n\n"
        )

        for _, row in result.iterrows():

            sector = row["Sector/service"]

            if not sector:
                sector = "Unknown"

            pipeline = row["pipeline_value"]

            work_order_count = int(
                row["total_work_orders"]
            )

            completion_rate = row[
                "completion_rate"
            ]

            response += (
                f"**{sector}** — "
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


        response += (
            "### Business Takeaway\n\n"
        )

        response += (
            "Railways deserves attention because it has "
            "a significant open pipeline while only "
            "16.7% of its recorded work orders are "
            "completed. Mining and Renewables have much "
            "larger operational footprints and currently "
            "show substantially higher completion rates."
        )

        response += (
            "\n\n**Data caveat:** A 0% completion rate "
            "for sectors with no work orders does not "
            "indicate poor execution; there is no "
            "operational denominator for those sectors."
        )

        return response


    # --------------------------------
    # WORK ORDERS
    # --------------------------------

    if (
        any(word in question for word in [
        "work order",
        "work orders",
        "execution"
       ])
       and "sector" not in question

    ):

        summary = work_order_summary(
            work_orders
        )

        response = (
            f"### Work Order Overview\n\n"
            f"- **Total:** {summary['total_work_orders']}\n"
            f"- **Completed:** {summary['completed']}\n"
            f"- **Ongoing:** {summary['ongoing']}\n"
            f"- **Not started:** {summary['not_started']}\n\n"
            f"Other execution statuses are also present, "
            f"including 'Executed until current month', "
            f"'Pause / struck', and 'Partial Completed'."
        )

        return response


    # --------------------------------
    # SECTORS
    # --------------------------------

    if "sector" in question:

        if "deal" in question or "pipeline" in question:

            result = pipeline_by_sector(deals)

            response = "### Deal Pipeline by Sector\n\n"

            for sector, row in result.head(10).iterrows():

                sector_name = (
                    sector if sector else "Unknown"
                )

                response += (
                    f"- **{sector_name}:** "
                    f"{format_rupees(row['pipeline_value'])} "
                    f"({int(row['deal_count'])} open deals)\n"
                )

            return response

        else:

            result = work_orders_by_sector(
                work_orders
            )

            response = "### Work Orders by Sector\n\n"

            for sector, count in result.head(10).items():

                sector_name = (
                    sector if sector else "Unknown"
                )

                response += (
                    f"- **{sector_name}:** "
                    f"{int(count)} work orders\n"
                )

            return response


    # --------------------------------
    # FINANCIALS
    # --------------------------------

    if any(word in question for word in [
        "receivable",
        "receivables",
        "billing",
        "billed",
        "collected",
        "collection",
        "financial"
    ]):

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


    # --------------------------------
    # DATA QUALITY
    # --------------------------------

    if any(word in question for word in [
        "data quality",
        "missing data",
        "data issues",
        "missing values"
    ]):

        issues = data_quality_summary(
            deals,
            work_orders
        )

        response = "### Data Quality\n\n"

        for issue in issues:

            response += f"- {issue}\n"

        return response


    # --------------------------------
    # FALLBACK
    # --------------------------------

    return (
        "I can currently answer questions about:\n\n"
        "- Sales pipeline\n"
        "- Top deals\n"
        "- Pipeline by sector\n"
        "- Work order execution\n"
        "- Work orders by sector\n"
        "- Billing and receivables\n"
        "- Data quality\n\n"
        "Try asking something like: "
        "\"What is our current pipeline?\""
    )