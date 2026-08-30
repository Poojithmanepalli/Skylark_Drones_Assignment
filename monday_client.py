import os
import requests
import pandas as pd
from dotenv import load_dotenv

from data_cleaner import (
    clean_deals,
    clean_work_orders,
    get_data_quality_report
)

load_dotenv()

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")

API_URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": MONDAY_API_TOKEN,
    "Content-Type": "application/json"
}


def fetch_all_items(board_id):
    """
    Fetch all items and column metadata from a Monday.com board.

    Includes error handling for:
    - Missing API credentials
    - Request timeouts
    - Connection/request failures
    - Monday.com GraphQL errors
    - Unexpected empty board responses
    """

    if not MONDAY_API_TOKEN:
        raise Exception(
            "Monday.com API token is missing. "
            "Please check your .env file."
        )

    if not board_id:
        raise Exception(
            "Monday.com board ID is missing. "
            "Please check your .env file."
        )

    all_items = []
    cursor = None
    board_name = None
    columns = None

    # --------------------------------
    # FIRST API REQUEST
    # --------------------------------

    query = """
    query ($board_id: ID!) {
        boards(ids: [$board_id]) {
            id
            name

            columns {
                id
                title
                type
            }

            items_page(limit: 100) {
                cursor

                items {
                    id
                    name

                    column_values {
                        id
                        text
                        value
                    }
                }
            }
        }
    }
    """

    variables = {
        "board_id": board_id
    }

    try:

        response = requests.post(
            API_URL,
            json={
                "query": query,
                "variables": variables
            },
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:

        raise Exception(
            "Monday.com request timed out. "
            "Please try again shortly."
        )

    except requests.exceptions.ConnectionError:

        raise Exception(
            "Unable to connect to Monday.com. "
            "Please check your internet connection "
            "and try again."
        )

    except requests.exceptions.RequestException as e:

        raise Exception(
            f"Unable to retrieve data from Monday.com: {e}"
        )

    try:

        result = response.json()

    except ValueError:

        raise Exception(
            "Monday.com returned an invalid response."
        )

    if "errors" in result:

        raise Exception(
            f"Monday.com API error: {result['errors']}"
        )

    if (
        "data" not in result
        or not result["data"].get("boards")
    ):

        raise Exception(
            f"No Monday.com board was found for "
            f"board ID: {board_id}"
        )

    board = result["data"]["boards"][0]

    board_name = board["name"]
    columns = board["columns"]

    items_page = board["items_page"]

    all_items.extend(
        items_page["items"]
    )

    cursor = items_page.get("cursor")


    # --------------------------------
    # PAGINATION
    # --------------------------------

    while cursor:

        query = """
        query ($cursor: String!) {
            next_items_page(limit: 100, cursor: $cursor) {

                cursor

                items {
                    id
                    name

                    column_values {
                        id
                        text
                        value
                    }
                }
            }
        }
        """

        variables = {
            "cursor": cursor
        }

        try:

            response = requests.post(
                API_URL,
                json={
                    "query": query,
                    "variables": variables
                },
                headers=HEADERS,
                timeout=30
            )

            response.raise_for_status()

        except requests.exceptions.Timeout:

            raise Exception(
                "Monday.com pagination request timed out. "
                "Please try again shortly."
            )

        except requests.exceptions.ConnectionError:

            raise Exception(
                "Connection to Monday.com was lost "
                "while retrieving additional data."
            )

        except requests.exceptions.RequestException as e:

            raise Exception(
                f"Unable to retrieve additional Monday.com "
                f"data: {e}"
            )

        try:

            result = response.json()

        except ValueError:

            raise Exception(
                "Monday.com returned an invalid pagination response."
            )

        if "errors" in result:

            raise Exception(
                f"Monday.com API error during pagination: "
                f"{result['errors']}"
            )

        if (
            "data" not in result
            or not result["data"].get("next_items_page")
        ):

            raise Exception(
                "Monday.com returned an unexpected pagination response."
            )

        items_page = result["data"]["next_items_page"]

        all_items.extend(
            items_page["items"]
        )

        cursor = items_page.get("cursor")


    return board_name, columns, all_items


def items_to_dataframe(items, columns):
    """
    Convert Monday.com items into a pandas DataFrame.
    """

    column_map = {
        column["id"]: column["title"]
        for column in columns
    }

    rows = []

    for item in items:

        row = {
            "item_id": item["id"],
            "item_name": item["name"]
        }

        for column in item["column_values"]:

            column_id = column["id"]

            column_name = column_map.get(
                column_id,
                column_id
            )

            row[column_name] = column["text"]

        rows.append(row)

    return pd.DataFrame(rows)


def get_deals():
    """
    Retrieve and return the Deals board data.
    """

    board_name, columns, items = fetch_all_items(
        DEALS_BOARD_ID
    )

    df = items_to_dataframe(
        items,
        columns
    )

    return df


def get_work_orders():
    """
    Retrieve and return the Work Orders board data.
    """

    board_name, columns, items = fetch_all_items(
        WORK_ORDERS_BOARD_ID
    )

    df = items_to_dataframe(
        items,
        columns
    )

    return df


if __name__ == "__main__":

    print("Fetching Deals...")

    deals_df = get_deals()

    print(
        "Raw Deals rows:",
        len(deals_df)
    )

    deals_df = clean_deals(
        deals_df
    )

    print(
        "Cleaned Deals rows:",
        len(deals_df)
    )

    print("\nDeals columns:")
    print(
        list(deals_df.columns)
    )

    print("\nDeals data types:")
    print(
        deals_df.dtypes
    )


    print("\nFetching Work Orders...")

    work_orders_df = get_work_orders()

    print(
        "Raw Work Orders rows:",
        len(work_orders_df)
    )

    work_orders_df = clean_work_orders(
        work_orders_df
    )

    print(
        "Cleaned Work Orders rows:",
        len(work_orders_df)
    )

    print("\nWork Orders columns:")
    print(
        list(work_orders_df.columns)
    )

    print("\nWork Orders data types:")
    print(
        work_orders_df.dtypes
    )


    print("\nDeals Data Quality:")

    print(
        get_data_quality_report(
            deals_df
        )
    )


    print("\nWork Orders Data Quality:")

    print(
        get_data_quality_report(
            work_orders_df
        )
    )


    print("\nData cleaning successful!")