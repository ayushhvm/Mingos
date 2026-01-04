from django.core.management.base import BaseCommand
from mingos.models import CustomerOrder
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Redistribute order dates across last 7 days'

    def handle(self, *args, **kwargs):
        self.stdout.write('Updating order dates...')
        
        # Get first 50 orders
        orders = CustomerOrder.objects.all().order_by('order_id')[:50]
        
        today = timezone.now()
        
        for order in orders:
            # Random date in last 7 days
            days_ago = random.randint(0, 6)
            new_date = today - timedelta(days=days_ago, hours=random.randint(8, 20), minutes=random.randint(0, 59))
            
            order.order_datetime = new_date
            order.save(update_fields=['order_datetime'])
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {len(orders)} order dates'))
