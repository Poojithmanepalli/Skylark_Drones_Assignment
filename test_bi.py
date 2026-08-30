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


print("Loading data...")

deals = clean_deals(
    get_deals()
)

work_orders = clean_work_orders(
    get_work_orders()
)


print("\n========== PIPELINE SUMMARY ==========")

print(
    pipeline_summary(deals)
)


print("\n========== PIPELINE BY SECTOR ==========")

print(
    pipeline_by_sector(deals)
)


print("\n========== TOP DEALS ==========")

print(
    top_deals(deals, 5)
)


print("\n========== WORK ORDER SUMMARY ==========")

print(
    work_order_summary(work_orders)
)


print("\n========== WORK ORDERS BY SECTOR ==========")

print(
    work_orders_by_sector(work_orders)
)


print("\n========== FINANCIAL SUMMARY ==========")

print(
    financial_summary(work_orders)
)


print("\n========== DATA QUALITY ==========")

for issue in data_quality_summary(
    deals,
    work_orders
):

    print("-", issue)

print("\n========== CROSS-BOARD SECTOR ANALYSIS ==========")

print(
    cross_board_sector_analysis(
        deals,
        work_orders
    ).head(10)
)