from monday_client import get_work_orders
from data_cleaner import clean_work_orders

work_orders = clean_work_orders(
    get_work_orders()
)

financial_columns = [
    "Amount in Rupees (Incl of GST) (Masked)",
    "Billed Value in Rupees (Excl. of GST.) (Masked)",
    "Billed Value in Rupees (Incl. of GST.) (Masked)",
    "Collected Amount in Rupees (Incl. of GST.) (Masked)",
    "Amount to be billed in Rs. (Incl. of GST) (Masked)",
    "Amount Receivable (Masked)"
]

for column in financial_columns:

    print("\n" + "=" * 70)
    print(column)

    if column in work_orders.columns:

        print("Non-null:", work_orders[column].notna().sum())
        print("Sum:", work_orders[column].sum())
        print("Non-zero:", (work_orders[column].fillna(0) != 0).sum())

        print("\nSample values:")
        print(
            work_orders[column]
            .dropna()
            .head(10)
            .to_list()
        )

    else:

        print("COLUMN NOT FOUND")