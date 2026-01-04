from mingos.models import CustomerOrder
from django.db.models import Count

orders_by_date = CustomerOrder.objects.extra({'date': 'DATE(order_datetime)'}).values('date').annotate(count=Count('order_id')).order_by('-date')[:8]

for o in orders_by_date:
    print(f"{o['date']}: {o['count']} orders")
