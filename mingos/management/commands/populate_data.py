from django.core.management.base import BaseCommand
from mingos.models import (
    MenuCategory, MenuItem, Ingredient, Recipe, 
    CustomerOrder, OrderItem, Supplier, SupplierIngredient
)
from datetime import datetime, timedelta
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Populate database with mock data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data population...')
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        OrderItem.objects.all().delete()
        CustomerOrder.objects.all().delete()
        Recipe.objects.all().delete()
        MenuItem.objects.all().delete()
        MenuCategory.objects.all().delete()
        SupplierIngredient.objects.all().delete()
        Ingredient.objects.all().delete()
        Supplier.objects.all().delete()
        
        # Create Categories
        self.stdout.write('Creating categories...')
        categories = {
            'Burgers': MenuCategory.objects.create(name='Burgers', description='Delicious burgers'),
            'Pizzas': MenuCategory.objects.create(name='Pizzas', description='Fresh pizzas'),
            'Sandwiches': MenuCategory.objects.create(name='Sandwiches', description='Tasty sandwiches'),
            'Beverages': MenuCategory.objects.create(name='Beverages', description='Refreshing drinks'),
            'Desserts': MenuCategory.objects.create(name='Desserts', description='Sweet treats'),
        }
        
        # Create Ingredients
        self.stdout.write('Creating ingredients...')
        ingredients_data = [
            # Breads & Bases
            ('Burger Bun', 'piece', 100, 50, 10),
            ('Pizza Dough', 'piece', 80, 40, 8),
            ('White Bread', 'slice', 200, 100, 20),
            ('Whole Wheat Bread', 'slice', 150, 75, 15),
            
            # Proteins
            ('Chicken Patty', 'piece', 60, 30, 5),
            ('Beef Patty', 'piece', 50, 25, 5),
            ('Paneer', 'grams', 2000, 1000, 200),
            ('Chicken Tikka', 'grams', 1500, 750, 150),
            
            # Vegetables
            ('Lettuce', 'grams', 1000, 500, 100),
            ('Tomato', 'piece', 100, 50, 10),
            ('Onion', 'piece', 120, 60, 12),
            ('Bell Pepper', 'piece', 80, 40, 8),
            ('Mushroom', 'grams', 800, 400, 80),
            
            # Cheese & Dairy
            ('Cheese Slice', 'piece', 150, 75, 15),
            ('Mozzarella Cheese', 'grams', 2000, 1000, 200),
            ('Milk', 'ml', 5000, 2500, 500),
            ('Ice Cream', 'ml', 3000, 1500, 300),
            
            # Sauces & Condiments
            ('Mayo', 'grams', 1000, 500, 100),
            ('Ketchup', 'grams', 1000, 500, 100),
            ('Pizza Sauce', 'grams', 1500, 750, 150),
            ('BBQ Sauce', 'grams', 800, 400, 80),
            
            # Beverages
            ('Coffee Powder', 'grams', 500, 250, 50),
            ('Tea Leaves', 'grams', 400, 200, 40),
            ('Coke Syrup', 'ml', 2000, 1000, 200),
            ('Orange Juice', 'ml', 3000, 1500, 300),
            
            # Desserts
            ('Chocolate Sauce', 'grams', 800, 400, 80),
            ('Vanilla Extract', 'ml', 200, 100, 20),
            ('Sugar', 'grams', 3000, 1500, 300),
        ]
        
        ingredients = {}
        for name, unit, stock, reorder, safety in ingredients_data:
            ingredients[name] = Ingredient.objects.create(
                name=name,
                unit_of_measure=unit,
                current_stock_qty=stock,
                reorder_level=reorder,
                safety_stock_qty=safety
            )
        
        # Create Menu Items with Recipes
        self.stdout.write('Creating menu items and recipes...')
        
        menu_items_data = [
            # Burgers
            ('Classic Chicken Burger', 'Burgers', 120, [
                ('Burger Bun', 1), ('Chicken Patty', 1), ('Lettuce', 20), 
                ('Tomato', 1), ('Mayo', 15), ('Cheese Slice', 1)
            ]),
            ('Beef Burger', 'Burgers', 150, [
                ('Burger Bun', 1), ('Beef Patty', 1), ('Lettuce', 20),
                ('Onion', 0.5), ('Ketchup', 15), ('Cheese Slice', 1)
            ]),
            ('Paneer Burger', 'Burgers', 110, [
                ('Burger Bun', 1), ('Paneer', 50), ('Lettuce', 15),
                ('Tomato', 1), ('Mayo', 10)
            ]),
            ('BBQ Chicken Burger', 'Burgers', 140, [
                ('Burger Bun', 1), ('Chicken Patty', 1), ('BBQ Sauce', 20),
                ('Onion', 0.5), ('Cheese Slice', 1)
            ]),
            
            # Pizzas
            ('Margherita Pizza', 'Pizzas', 200, [
                ('Pizza Dough', 1), ('Pizza Sauce', 50), ('Mozzarella Cheese', 100),
                ('Tomato', 2)
            ]),
            ('Chicken Tikka Pizza', 'Pizzas', 280, [
                ('Pizza Dough', 1), ('Pizza Sauce', 50), ('Mozzarella Cheese', 120),
                ('Chicken Tikka', 80), ('Onion', 1), ('Bell Pepper', 1)
            ]),
            ('Veggie Supreme Pizza', 'Pizzas', 250, [
                ('Pizza Dough', 1), ('Pizza Sauce', 50), ('Mozzarella Cheese', 100),
                ('Mushroom', 40), ('Bell Pepper', 1), ('Onion', 1), ('Tomato', 2)
            ]),
            ('Paneer Pizza', 'Pizzas', 240, [
                ('Pizza Dough', 1), ('Pizza Sauce', 50), ('Mozzarella Cheese', 100),
                ('Paneer', 60), ('Bell Pepper', 1)
            ]),
            ('BBQ Chicken Pizza', 'Pizzas', 290, [
                ('Pizza Dough', 1), ('BBQ Sauce', 50), ('Mozzarella Cheese', 100),
                ('Chicken Tikka', 80), ('Onion', 1)
            ]),
            
            # Sandwiches
            ('Grilled Chicken Sandwich', 'Sandwiches', 90, [
                ('White Bread', 2), ('Chicken Tikka', 60), ('Lettuce', 15),
                ('Tomato', 1), ('Mayo', 10), ('Cheese Slice', 1)
            ]),
            ('Veg Sandwich', 'Sandwiches', 70, [
                ('Whole Wheat Bread', 2), ('Tomato', 2), ('Onion', 0.5),
                ('Lettuce', 15), ('Mayo', 10)
            ]),
            ('Paneer Sandwich', 'Sandwiches', 85, [
                ('White Bread', 2), ('Paneer', 50), ('Onion', 0.5),
                ('Tomato', 1), ('Mayo', 10), ('Cheese Slice', 1)
            ]),
            ('Club Sandwich', 'Sandwiches', 110, [
                ('White Bread', 3), ('Chicken Tikka', 50), ('Lettuce', 20),
                ('Tomato', 2), ('Mayo', 15), ('Cheese Slice', 2)
            ]),
            
            # Beverages
            ('Coffee', 'Beverages', 40, [
                ('Coffee Powder', 10), ('Milk', 150), ('Sugar', 10)
            ]),
            ('Tea', 'Beverages', 30, [
                ('Tea Leaves', 5), ('Milk', 150), ('Sugar', 10)
            ]),
            ('Cold Coffee', 'Beverages', 60, [
                ('Coffee Powder', 15), ('Milk', 200), ('Sugar', 15), ('Ice Cream', 50)
            ]),
            ('Coke', 'Beverages', 40, [
                ('Coke Syrup', 50)
            ]),
            ('Orange Juice', 'Beverages', 50, [
                ('Orange Juice', 200), ('Sugar', 5)
            ]),
            
            # Desserts
            ('Chocolate Ice Cream', 'Desserts', 80, [
                ('Ice Cream', 150), ('Chocolate Sauce', 30)
            ]),
            ('Vanilla Ice Cream', 'Desserts', 70, [
                ('Ice Cream', 150), ('Vanilla Extract', 5)
            ]),
            ('Brownie with Ice Cream', 'Desserts', 120, [
                ('Ice Cream', 100), ('Chocolate Sauce', 40), ('Sugar', 20)
            ]),
            ('Chocolate Shake', 'Desserts', 90, [
                ('Milk', 250), ('Ice Cream', 100), ('Chocolate Sauce', 30), ('Sugar', 15)
            ]),
            ('Vanilla Shake', 'Desserts', 85, [
                ('Milk', 250), ('Ice Cream', 100), ('Vanilla Extract', 5), ('Sugar', 15)
            ]),
            
            # Additional items to reach 25
            ('Cheese Burger', 'Burgers', 130, [
                ('Burger Bun', 1), ('Beef Patty', 1), ('Cheese Slice', 2),
                ('Lettuce', 15), ('Tomato', 1), ('Mayo', 10)
            ]),
            ('Mushroom Pizza', 'Pizzas', 260, [
                ('Pizza Dough', 1), ('Pizza Sauce', 50), ('Mozzarella Cheese', 120),
                ('Mushroom', 80), ('Onion', 1)
            ]),
        ]
        
        menu_items = {}
        for item_name, category_name, price, recipe_data in menu_items_data:
            menu_item = MenuItem.objects.create(
                name=item_name,
                category=categories[category_name],
                price=price,
                is_available=True
            )
            menu_items[item_name] = menu_item
            
            # Create recipes
            for ingredient_name, quantity in recipe_data:
                Recipe.objects.create(
                    menu_item=menu_item,
                    ingredient=ingredients[ingredient_name],
                    quantity_required=quantity
                )
        
        self.stdout.write(f'Created {len(menu_items)} menu items with recipes')
        
        # Create Orders (100 orders spread over last 7 days for better analytics)
        self.stdout.write('Creating customer orders...')
        
        all_items = list(menu_items.values())
        today = timezone.now()
        
        for i in range(100):
            # Random date in last 7 days (focused on recent data)
            days_ago = random.randint(0, 7)
            order_date = today - timedelta(days=days_ago, hours=random.randint(8, 20), minutes=random.randint(0, 59))
            
            # Random number of items per order (1-5)
            num_items = random.randint(1, 5)
            selected_items = random.sample(all_items, num_items)
            
            total_amount = 0
            order_items_data = []
            
            for menu_item in selected_items:
                quantity = random.randint(1, 3)
                line_amount = menu_item.price * quantity
                total_amount += line_amount
                order_items_data.append((menu_item, quantity, line_amount))
            
            # Create order
            order = CustomerOrder.objects.create(
                total_amount=total_amount,
                order_status=random.choice(['PENDING', 'COMPLETED', 'COMPLETED', 'COMPLETED']),  # 75% completed
                order_datetime=order_date
            )
            
            # Create order items
            for menu_item, quantity, line_amount in order_items_data:
                OrderItem.objects.create(
                    customer_order=order,
                    menu_item=menu_item,
                    quantity=quantity,
                    unit_price=menu_item.price,
                    line_amount=line_amount
                )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created 100 orders'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Data Population Complete ==='))
        self.stdout.write(f'Categories: {MenuCategory.objects.count()}')
        self.stdout.write(f'Ingredients: {Ingredient.objects.count()}')
        self.stdout.write(f'Menu Items: {MenuItem.objects.count()}')
        self.stdout.write(f'Recipes: {Recipe.objects.count()}')
        self.stdout.write(f'Orders: {CustomerOrder.objects.count()}')
        self.stdout.write(f'Order Items: {OrderItem.objects.count()}')
        self.stdout.write(self.style.SUCCESS('Dashboard analytics should now have plenty of data!'))
