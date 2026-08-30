from monday_client import get_deals, get_work_orders
from data_cleaner import clean_deals, clean_work_orders


print("Loading Deals...")

deals = get_deals()
deals = clean_deals(deals)

print("\n===== DEALS =====")

columns_to_inspect = [
    "Deal Status",
    "Deal Stage",
    "Product deal",
    "Sector/service",
    "Closure Probability"
]

for column in columns_to_inspect:

    if column in deals.columns:

        print(f"\n--- {column} ---")

        print(
            deals[column]
            .value_counts(dropna=False)
            .head(20)
        )


print("\n\nLoading Work Orders...")

work_orders = get_work_orders()
work_orders = clean_work_orders(work_orders)

print("\n===== WORK ORDERS =====")

columns_to_inspect = [
    "Execution Status",
    "Sector",
    "Type of Work",
    "Invoice Status",
    "WO Status (billed)",
    "Collection status",
    "Billing Status"
]

for column in columns_to_inspect:

    if column in work_orders.columns:

        print(f"\n--- {column} ---")

        print(
            work_orders[column]
            .value_counts(dropna=False)
            .head(20)
        )