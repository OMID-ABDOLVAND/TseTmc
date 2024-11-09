from django.db import models


class Fund(models.Model):
    fund_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FundPrice(models.Model):
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField()
    closing_price = models.FloatField()

    class Meta:
        unique_together = ('fund', 'date')

    def __str__(self):
        return f"{self.fund.name} - {self.date}"
