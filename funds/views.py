import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from io import BytesIO
from rest_framework.viewsets import ReadOnlyModelViewSet
from funds.models import Fund
from funds.serializers import FundSerializer


class FundListDetail(ReadOnlyModelViewSet):
    queryset = Fund.objects.all()
    serializer_class = FundSerializer
    lookup_field = 'fund_code'


class FundReturnsView(APIView):
    def get(self, request):
        # Get ids from query params
        fund_ids = request.query_params.getlist('fund_ids')
        if not fund_ids:
            return Response({"error": "No fund IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        fund_dataframes = {}

        # time frames for returns
        timeframes = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30,
            'seasonal': 90,
            'semi_annual': 180,
            'annual': 365
        }

        def calculate_returns(df, period):
            df[f'{period}_return'] = (df['closing_price'] / df['closing_price'].shift(period)) - 1

            return df

        # Fetch and calculate returns
        for fund_id in fund_ids:
            try:
                # Retrieve the fund and related price data
                fund = Fund.objects.get(fund_code=fund_id)
                prices_qs = fund.prices.all().order_by('date')

                # Convert queryset to DataFrame
                prices_data = [{'date': p.date, 'closing_price': p.closing_price} for p in prices_qs]
                df = pd.DataFrame(prices_data)

                # Ensure 'date' column is datetime type
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date').sort_index()

                # Calculate returns for each timeframe
                for name, days in timeframes.items():
                    df = calculate_returns(df, days)

                # Store the DataFrame for this fund
                fund_dataframes[fund_id] = df

            except Fund.DoesNotExist:
                return Response({'error': f'Fund with ID {fund_id} not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create an Excel file
        with BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                for fund_id, fund_df in fund_dataframes.items():
                    fund_df.to_excel(writer, sheet_name=f'Fund_{fund_id}', index=True)
            buffer.seek(0)

            # Serve Excel file as response
            response = HttpResponse(
                buffer,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="multi_fund_returns.xlsx"'
            return response