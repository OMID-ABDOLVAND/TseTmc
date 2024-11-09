import requests
from datetime import datetime
from funds.models import Fund, FundPrice
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load countries and their provinces into the database'

    def handle(self, *args, **kwargs):
        fund_code = Fund.objects.values_list('fund_code', flat=True)
        for fund_code in fund_code:

            url = f"http://old.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={fund_code}&Top=360&Persian=1"

            # Send a request to the API
            response = requests.get(url)
            data = response.text

            daily_close_prices = []

            # Split each record by `;`
            records = data.split(";")
            fund = Fund.objects.get(fund_code=fund_code)

            for record in records:
                fields = record.split("@")

                if len(fields) > 5:
                    date = fields[0]  # Date
                    date_obj = datetime.strptime(date, "%Y%m%d").date()
                    close_price = fields[5]  # Closing price

                    daily_close_prices.append((date_obj, close_price))

                    # Update or create Fund entry
                    FundPrice.objects.update_or_create(
                        fund=fund,
                        date=date_obj,
                        defaults={'closing_price': float(close_price)}
                    )

                    self.stdout.write(self.style.SUCCESS(f'Updated data for fund ID {fund_code}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to fetch data for fund ID {fund_code}'))

