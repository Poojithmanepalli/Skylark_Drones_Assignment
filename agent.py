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

    for name, display_name in sector_names.items():

        if name in question:
            return display_name

    return None


def answer_question(question):

    question = question.lower().strip()

    deals, work_orders = load_data()

    sector = find_sector(question)


    # --------------------------------
    # SECTOR BUSINESS OVERVIEW
    # --------------------------------

    # Handles questions such as:
    #
    # "How is Mining doing?"
    # "How is Mining performing?"
    # "Give me an overview of Mining"
    # "Tell me about Renewables"
    # "What's happening in Railways?"
    #
    # These questions combine information
    # from both Deals and Work Orders.

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

        cross_data = cross_board_sector_analysis(
            deals,
            work_orders
        )

        sector_data = cross_data[
            cross_data["Sector/service"].astype(str).str.lower()
            == sector.lower()
        ]

        response = f"### {sector} — Business Overview\n\n"

        if sector_data.empty:

            response += (
                f"No matching data was found for **{sector}** "
                "across the Deals and Work Orders boards."
            )

            return response

        row = sector_data.iloc[0]

        pipeline = row["pipeline_value"]
        open_deals = int(row["open_deals"])

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


    # --------------------------------
    # CROSS-BOARD ANALYSIS
    # --------------------------------

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


        # Find sectors that have both meaningful
        # pipeline and relatively weak execution.

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


    # --------------------------------
    # SECTORS
    # --------------------------------

    if (
        "sector" in question
        or "sectors" in question
    ):

        if (
            "deal" in question
            or "pipeline" in question
        ):

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

        else:

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
        "- Cross-board sector performance\n"
        "- Billing and receivables\n"
        "- Data quality\n\n"
        "Try asking something like:\n"
        "\"How is Mining doing?\"\n"
        "or\n"
        "\"Which sectors have strong pipeline but execution risk?\""
    )