import pandas as pd

def generate_forecast(request):
    business_unit = request.business_unit.lower()
    months = request.months

    if business_unit == "large":
        df = pd.DataFrame({
            "Month": list(range(1, months + 1)),
            "Revenue": [
                request.revenue_per_customer * request.sales_per_executive * m
                for m in range(1, months + 1)
            ]
        })

    elif business_unit == "small_medium":
        paying_customers_per_month = int((request.marketing_cost / request.cac) * request.conversion_rate)
        df = pd.DataFrame({
            "Month": list(range(1, months + 1)),
            "Paying_Customers": [paying_customers_per_month * m for m in range(1, months + 1)],
            "Revenue": [
                paying_customers_per_month * request.small_medium_revenue_per_customer * m
                for m in range(1, months + 1)
            ]
        })

    else:
        raise ValueError("Invalid business unit. Use 'large' or 'small_medium'")

    return df
