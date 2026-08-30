import pandas as pd


def format_currency(value):
    """Format a number as Indian Rupees."""

    if pd.isna(value):
        return "₹0"

    return f"₹{value:,.0f}"


def pipeline_summary(deals):

    total_deals = len(deals)

    open_deals = deals[
        deals["Deal Status"].str.lower() == "open"
    ]

    won_deals = deals[
        deals["Deal Status"].str.lower() == "won"
    ]

    dead_deals = deals[
        deals["Deal Status"].str.lower() == "dead"
    ]

    open_pipeline = open_deals[
        "Masked Deal value"
    ].sum()

    won_value = won_deals[
        "Masked Deal value"
    ].sum()

    return {
        "total_deals": total_deals,
        "open_deals": len(open_deals),
        "won_deals": len(won_deals),
        "dead_deals": len(dead_deals),
        "open_pipeline": open_pipeline,
        "won_value": won_value
    }


def pipeline_by_sector(deals):

    open_deals = deals[
        deals["Deal Status"].str.lower() == "open"
    ]

    result = (
        open_deals
        .groupby("Sector/service", dropna=False)
        ["Masked Deal value"]
        .agg(
            deal_count="count",
            pipeline_value="sum"
        )
        .sort_values(
            "pipeline_value",
            ascending=False
        )
    )

    return result


def top_deals(deals, n=10):

    open_deals = deals[
        deals["Deal Status"].str.lower() == "open"
    ]

    result = (
        open_deals[
            [
                "item_name",
                "Client Code",
                "Masked Deal value",
                "Sector/service",
                "Deal Stage"
            ]
        ]
        .dropna(
            subset=["Masked Deal value"]
        )
        .sort_values(
            "Masked Deal value",
            ascending=False
        )
        .head(n)
    )

    return result


def work_order_summary(work_orders):

    total = len(work_orders)

    execution_counts = (
        work_orders["Execution Status"]
        .value_counts()
    )

    completed = execution_counts.get(
        "Completed",
        0
    )

    ongoing = execution_counts.get(
        "Ongoing",
        0
    )

    not_started = execution_counts.get(
        "Not Started",
        0
    )

    return {
        "total_work_orders": total,
        "completed": completed,
        "ongoing": ongoing,
        "not_started": not_started,
        "execution_status_counts":
            execution_counts.to_dict()
    }


def work_orders_by_sector(work_orders):

    result = (
        work_orders
        .groupby(
            "Sector",
            dropna=False
        )
        .size()
        .sort_values(
            ascending=False
        )
    )

    return result


def financial_summary(work_orders):

    def normalize_column_name(name):
        """
        Normalize a column name so minor punctuation and
        spacing differences do not affect matching.
        """
        return (
            str(name)
            .lower()
            .replace(".", "")
            .replace(",", "")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace("_", "")
            .replace(" ", "")
        )


    def find_column(keywords):

        normalized_columns = {
            normalize_column_name(column): column
            for column in work_orders.columns
        }

        normalized_keywords = [
            normalize_column_name(keyword)
            for keyword in keywords
        ]

        for normalized_column, original_column in normalized_columns.items():

            if all(
                keyword in normalized_column
                for keyword in normalized_keywords
            ):
                return original_column

        return None


    def sum_column(keywords):

        column = find_column(keywords)

        if column is None:
            return 0

        return work_orders[column].fillna(0).sum()


    total_amount = sum_column([
        "Amount in Rupees",
        "Incl",
        "GST"
    ])


    billed_amount = sum_column([
        "Billed Value in Rupees",
        "Incl",
        "GST"
    ])


    collected_amount = sum_column([
        "Collected Amount in Rupees",
        "Incl",
        "GST"
    ])


    receivable = sum_column([
        "Amount Receivable"
    ])


    to_be_billed = sum_column([
        "Amount to be billed in Rs",
        "Incl",
        "GST"
    ])


    return {
        "total_amount": total_amount,
        "billed_amount": billed_amount,
        "collected_amount": collected_amount,
        "receivable": receivable,
        "to_be_billed": to_be_billed
    }

def data_quality_summary(deals, work_orders):

    issues = []

    # Deals
    if deals["Closure Probability"].isna().all():
        issues.append(
            "Closure Probability is missing for all deals."
        )

    if deals["Masked Deal value"].isna().any():
        missing = deals[
            "Masked Deal value"
        ].isna().sum()

        issues.append(
            f"Deal value is missing for {missing} deals."
        )

    # Work orders
    if work_orders["Collection status"].isna().all():

        issues.append(
            "Collection status is missing for all work orders."
        )

    if work_orders[
        "Amount Receivable (Masked)"
    ].isna().any():

        missing = work_orders[
            "Amount Receivable (Masked)"
        ].isna().sum()

        issues.append(
            f"Amount receivable is missing for {missing} work orders."
        )

    return issues

def cross_board_sector_analysis(deals, work_orders):
    """
    Compare sales pipeline with work-order execution
    for each sector.
    """

    # Open deal pipeline by sector
    open_deals = deals[
        deals["Deal Status"].str.lower() == "open"
    ].copy()

    pipeline = (
        open_deals
        .groupby("Sector/service")
        ["Masked Deal value"]
        .agg(
            pipeline_value="sum",
            open_deals="count"
        )
        .reset_index()
    )

    # Work-order execution by sector
    work_orders_copy = work_orders.copy()

    work_orders_copy["is_completed"] = (
        work_orders_copy["Execution Status"]
        .str.lower()
        == "completed"
    )

    execution = (
        work_orders_copy
        .groupby("Sector")
        .agg(
            total_work_orders=("item_id", "count"),
            completed_work_orders=("is_completed", "sum")
        )
        .reset_index()
    )

    # Calculate completion rate
    execution["completion_rate"] = (
        execution["completed_work_orders"]
        / execution["total_work_orders"]
        * 100
    )

    # Rename sector so the two datasets can be merged
    execution = execution.rename(
        columns={
            "Sector": "Sector/service"
        }
    )

    # Combine Deals + Work Orders
    result = pipeline.merge(
        execution,
        on="Sector/service",
        how="outer"
    )

    result["pipeline_value"] = (
        result["pipeline_value"].fillna(0)
    )

    result["open_deals"] = (
        result["open_deals"].fillna(0)
    )

    result["total_work_orders"] = (
        result["total_work_orders"].fillna(0)
    )

    result["completed_work_orders"] = (
        result["completed_work_orders"].fillna(0)
    )

    result["completion_rate"] = (
        result["completion_rate"].fillna(0)
    )

    return result.sort_values(
        "pipeline_value",
        ascending=False
    )