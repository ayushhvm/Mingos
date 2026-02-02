from django.core.management.base import BaseCommand
from mingos.models import (
    MenuCategory, MenuItem, Ingredient, Recipe, 
    CustomerOrder, OrderItem, Supplier, SupplierIngredient,
    PurchaseOrder, PurchaseOrderLine
)
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Populate database with comprehensive mock data (50-70 entries per table)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting comprehensive data population...')
        
        # Clear existing data in proper order (respecting foreign keys)
        self.stdout.write('Clearing existing data...')
        OrderItem.objects.all().delete()
        CustomerOrder.objects.all().delete()
        PurchaseOrderLine.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        Recipe.objects.all().delete()
        MenuItem.objects.all().delete()
        MenuCategory.objects.all().delete()
        SupplierIngredient.objects.all().delete()
        Ingredient.objects.all().delete()
        Supplier.objects.all().delete()
        
        # ==========================================
        # CREATE SUPPLIERS (60 entries)
        # ==========================================
        self.stdout.write('Creating 60 suppliers...')
        suppliers_data = [
            ('Fresh Farms Produce', '555-0101', 'contact@freshfarms.com', '123 Farm Road, Greenville', 'GST001FRESH', 'Active'),
            ('Metro Meats Inc', '555-0102', 'orders@metromeats.com', '456 Butcher Lane, Meattown', 'GST002METRO', 'Active'),
            ('Dairy Delights Co', '555-0103', 'sales@dairydelights.com', '789 Milk Street, Creamville', 'GST003DAIRY', 'Active'),
            ('Bakery Supplies Ltd', '555-0104', 'info@bakerysupplies.com', '321 Bread Ave, Flourtown', 'GST004BAKER', 'Active'),
            ('Spice World Trading', '555-0105', 'spices@spiceworld.com', '654 Spice Market, Aromaville', 'GST005SPICE', 'Active'),
            ('Ocean Fresh Seafood', '555-0106', 'catch@oceanfresh.com', '987 Harbor Blvd, Fishport', 'GST006OCEAN', 'Active'),
            ('Green Valley Organics', '555-0107', 'organic@greenvalley.com', '147 Organic Way, Natureton', 'GST007GREEN', 'Active'),
            ('Quick Beverage Dist', '555-0108', 'drinks@quickbev.com', '258 Soda Street, Refreshton', 'GST008QUICK', 'Active'),
            ('Premium Poultry Farm', '555-0109', 'orders@premiumpoultry.com', '369 Chicken Road, Eggville', 'GST009PREMI', 'Active'),
            ('Sauce Masters Inc', '555-0110', 'sauces@saucemasters.com', '741 Condiment Lane, Flavortown', 'GST010SAUCE', 'Active'),
            ('Frozen Foods Express', '555-0111', 'frozen@ffexpress.com', '852 Ice Road, Coldville', 'GST011FROZE', 'Active'),
            ('Veggie Paradise', '555-0112', 'veggies@veggieparadise.com', '963 Garden Street, Vegtown', 'GST012VEGGI', 'Active'),
            ('Cheese Heaven Ltd', '555-0113', 'cheese@cheeseheaven.com', '174 Cheddar Blvd, Gouda City', 'GST013CHEES', 'Active'),
            ('Grain Central', '555-0114', 'grains@graincentral.com', '285 Wheat Ave, Riceville', 'GST014GRAIN', 'Active'),
            ('Sweet Treats Supplier', '555-0115', 'sweets@sweettreats.com', '396 Sugar Lane, Candyton', 'GST015SWEET', 'Active'),
            ('Fresh Herbs Garden', '555-0116', 'herbs@freshherbs.com', '417 Basil Road, Herbville', 'GST016HERBS', 'Active'),
            ('Oil & Fats Co', '555-0117', 'oils@oilfats.com', '528 Olive Street, Oilton', 'GST017OILFA', 'Active'),
            ('Tropical Fruits Inc', '555-0118', 'fruits@tropicalfruits.com', '639 Mango Blvd, Fruitville', 'GST018TROPI', 'Active'),
            ('Nut House Trading', '555-0119', 'nuts@nuthouse.com', '741 Almond Way, Nutberg', 'GST019NUTHS', 'Active'),
            ('Coffee Bean Imports', '555-0120', 'beans@coffeeimports.com', '852 Java Street, Brewton', 'GST020COFFE', 'Active'),
            ('Tea Leaf Traders', '555-0121', 'tea@tealeaf.com', '963 Earl Grey Lane, Teaburg', 'GST021TEALE', 'Active'),
            ('Pasta Perfect Ltd', '555-0122', 'pasta@pastaperfect.com', '174 Noodle Road, Pastaville', 'GST022PASTA', 'Active'),
            ('Mushroom Kingdom', '555-0123', 'fungi@mushroomkingdom.com', '285 Portobello Ave, Shroomton', 'GST023MUSHR', 'Active'),
            ('Egg Excellence', '555-0124', 'eggs@eggexcellence.com', '396 Hen House Lane, Eggburg', 'GST024EGGEX', 'Active'),
            ('Honey Bee Farms', '555-0125', 'honey@honeybeefarms.com', '417 Hive Road, Sweetville', 'GST025HONEY', 'Active'),
            ('Pickle Palace', '555-0126', 'pickles@picklepalace.com', '528 Brine Street, Sourton', 'GST026PICKL', 'Active'),
            ('Butter & Cream Co', '555-0127', 'butter@buttercream.com', '639 Churn Blvd, Butterburg', 'GST027BUTTE', 'Active'),
            ('Rice Masters', '555-0128', 'rice@ricemasters.com', '741 Paddy Lane, Riceton', 'GST028RICEM', 'Active'),
            ('Flour Power Inc', '555-0129', 'flour@flourpower.com', '852 Mill Street, Flourville', 'GST029FLOUR', 'Active'),
            ('Chocolate Dreams', '555-0130', 'cocoa@chocolatedreams.com', '963 Cocoa Road, Chocotown', 'GST030CHOCO', 'Active'),
            ('Vinegar Valley', '555-0131', 'vinegar@vinegarvalley.com', '174 Acid Ave, Sourville', 'GST031VINEG', 'Active'),
            ('Lemon Lime Ltd', '555-0132', 'citrus@lemonlime.com', '285 Citrus Lane, Zestburg', 'GST032LEMON', 'Active'),
            ('Garlic Grove', '555-0133', 'garlic@garlicgrove.com', '396 Clove Street, Garlicton', 'GST033GARLI', 'Active'),
            ('Pepper Palace', '555-0134', 'peppers@pepperpalace.com', '417 Capsicum Road, Spiceville', 'GST034PEPPE', 'Active'),
            ('Tofu Town', '555-0135', 'tofu@tofutown.com', '528 Soy Blvd, Beanburg', 'GST035TOFUT', 'Active'),
            ('Maple Syrup Farms', '555-0136', 'maple@maplesyrup.com', '639 Tree Tap Lane, Mapleville', 'GST036MAPLE', 'Active'),
            ('Vanilla Ventures', '555-0137', 'vanilla@vanillaventures.com', '741 Bean Pod Ave, Vanillatown', 'GST037VANIL', 'Active'),
            ('Cinnamon Central', '555-0138', 'cinnamon@cinnamoncentral.com', '852 Bark Street, Spiceburg', 'GST038CINNA', 'Active'),
            ('Bacon Brothers', '555-0139', 'bacon@baconbros.com', '963 Smoky Lane, Porkville', 'GST039BACON', 'Active'),
            ('Sausage Supreme', '555-0140', 'links@sausagesupreme.com', '174 Casing Road, Wurstburg', 'GST040SAUSA', 'Active'),
            ('Lettuce Land', '555-0141', 'greens@lettuceland.com', '285 Salad Ave, Leafton', 'GST041LETTU', 'Active'),
            ('Tomato Territory', '555-0142', 'tomatoes@tomatoterritory.com', '396 Vine Street, Tomatoville', 'GST042TOMAT', 'Active'),
            ('Onion Outpost', '555-0143', 'onions@onionoutpost.com', '417 Layer Lane, Tearburg', 'GST043ONION', 'Active'),
            ('Carrot Country', '555-0144', 'carrots@carrotcountry.com', '528 Root Road, Orangeville', 'GST044CARRO', 'Active'),
            ('Potato Partners', '555-0145', 'spuds@potatopartners.com', '639 Tuber Blvd, Mashton', 'GST045POTAT', 'Active'),
            ('Celery Central', '555-0146', 'celery@celerycentral.com', '741 Stalk Street, Crunchburg', 'GST046CELER', 'Active'),
            ('Cucumber Corner', '555-0147', 'cukes@cucumbercorner.com', '852 Cool Ave, Pickleton', 'GST047CUCUM', 'Active'),
            ('Avocado Avenue', '555-0148', 'avocados@avocadoave.com', '963 Green Gold Lane, Guacville', 'GST048AVOCA', 'Active'),
            ('Broccoli Base', '555-0149', 'broccoli@broccolibase.com', '174 Floret Road, Treetown', 'GST049BROCC', 'Active'),
            ('Spinach Suppliers', '555-0150', 'spinach@spinachsuppliers.com', '285 Iron Leaf Ave, Popeyeton', 'GST050SPINA', 'Active'),
            ('Corn Connection', '555-0151', 'corn@cornconnection.com', '396 Kernel Street, Cobburg', 'GST051CORNC', 'Active'),
            ('Bean Brigade', '555-0152', 'beans@beanbrigade.com', '417 Pod Lane, Legumeville', 'GST052BEANB', 'Active'),
            ('Pea Producers', '555-0153', 'peas@peaproducers.com', '528 Pod Blvd, Peaton', 'GST053PEAPR', 'Active'),
            ('Cabbage Collective', '555-0154', 'cabbage@cabbagecollective.com', '639 Head Road, Colesburg', 'GST054CABBA', 'Active'),
            ('Radish Ranch', '555-0155', 'radish@radishranch.com', '741 Root Ave, Spicyville', 'GST055RADIS', 'Active'),
            ('Asparagus Acres', '555-0156', 'asparagus@asparagusacres.com', '852 Spear Street, Stalkburg', 'GST056ASPAR', 'Active'),
            ('Artichoke Alliance', '555-0157', 'artichoke@artichokealliance.com', '963 Heart Lane, Thistleton', 'GST057ARTIC', 'Active'),
            ('Cauliflower Corp', '555-0158', 'cauli@cauliflowercorp.com', '174 White Head Road, Floretville', 'GST058CAULI', 'Active'),
            ('Zucchini Zone', '555-0159', 'zucchini@zucchinizone.com', '285 Squash Ave, Greensburg', 'GST059ZUCCH', 'Active'),
            ('Eggplant Empire', '555-0160', 'eggplant@eggplantempire.com', '396 Purple Blvd, Aubergineton', 'GST060EGGPL', 'Active'),
        ]
        
        suppliers = {}
        for name, phone, email, address, gst, status in suppliers_data:
            suppliers[name] = Supplier.objects.create(
                name=name,
                phone=phone,
                email=email,
                address=address,
                gst_number=gst,
                status=status
            )
        self.stdout.write(f'Created {len(suppliers)} suppliers')
        
        # ==========================================
        # CREATE INGREDIENTS (70 entries)
        # ==========================================
        self.stdout.write('Creating 70 ingredients...')
        ingredients_data = [
            # Breads & Bases (7)
            ('Burger Bun', 'piece', 500, 100, 50, True),
            ('Pizza Dough', 'piece', 400, 80, 40, True),
            ('White Bread', 'slice', 1000, 200, 100, True),
            ('Whole Wheat Bread', 'slice', 800, 160, 80, True),
            ('Ciabatta Roll', 'piece', 300, 60, 30, True),
            ('Pita Bread', 'piece', 400, 80, 40, True),
            ('Tortilla Wrap', 'piece', 600, 120, 60, True),
            
            # Proteins (10)
            ('Chicken Patty', 'piece', 350, 70, 35, True),
            ('Beef Patty', 'piece', 300, 60, 30, True),
            ('Paneer', 'grams', 10000, 2000, 1000, True),
            ('Chicken Tikka', 'grams', 8000, 1600, 800, True),
            ('Grilled Chicken', 'grams', 7000, 1400, 700, True),
            ('Fish Fillet', 'piece', 200, 40, 20, True),
            ('Shrimp', 'grams', 5000, 1000, 500, True),
            ('Lamb Keema', 'grams', 4000, 800, 400, True),
            ('Turkey Slices', 'grams', 3000, 600, 300, True),
            ('Bacon Strips', 'piece', 500, 100, 50, True),
            
            # Vegetables (15)
            ('Lettuce', 'grams', 5000, 1000, 500, True),
            ('Tomato', 'piece', 600, 120, 60, True),
            ('Onion', 'piece', 700, 140, 70, False),
            ('Bell Pepper', 'piece', 400, 80, 40, True),
            ('Mushroom', 'grams', 4000, 800, 400, True),
            ('Jalapeno', 'piece', 300, 60, 30, True),
            ('Cucumber', 'piece', 400, 80, 40, True),
            ('Spinach', 'grams', 3000, 600, 300, True),
            ('Corn Kernels', 'grams', 5000, 1000, 500, False),
            ('Olives', 'grams', 2000, 400, 200, False),
            ('Pickles', 'piece', 500, 100, 50, False),
            ('Avocado', 'piece', 200, 40, 20, True),
            ('Capsicum', 'piece', 350, 70, 35, True),
            ('Green Chili', 'piece', 400, 80, 40, True),
            ('Cabbage', 'grams', 4000, 800, 400, True),
            
            # Cheese & Dairy (8)
            ('Cheese Slice', 'piece', 800, 160, 80, True),
            ('Mozzarella Cheese', 'grams', 10000, 2000, 1000, True),
            ('Cheddar Cheese', 'grams', 8000, 1600, 800, True),
            ('Parmesan Cheese', 'grams', 3000, 600, 300, True),
            ('Milk', 'ml', 25000, 5000, 2500, True),
            ('Cream', 'ml', 10000, 2000, 1000, True),
            ('Butter', 'grams', 5000, 1000, 500, True),
            ('Yogurt', 'grams', 6000, 1200, 600, True),
            
            # Sauces & Condiments (10)
            ('Mayo', 'grams', 5000, 1000, 500, False),
            ('Ketchup', 'grams', 5000, 1000, 500, False),
            ('Pizza Sauce', 'grams', 8000, 1600, 800, False),
            ('BBQ Sauce', 'grams', 4000, 800, 400, False),
            ('Mustard Sauce', 'grams', 3000, 600, 300, False),
            ('Hot Sauce', 'grams', 2000, 400, 200, False),
            ('Ranch Dressing', 'grams', 3000, 600, 300, False),
            ('Soy Sauce', 'ml', 4000, 800, 400, False),
            ('Garlic Sauce', 'grams', 3000, 600, 300, False),
            ('Pesto Sauce', 'grams', 2000, 400, 200, True),
            
            # Beverages (8)
            ('Coffee Powder', 'grams', 3000, 600, 300, False),
            ('Tea Leaves', 'grams', 2000, 400, 200, False),
            ('Coke Syrup', 'ml', 10000, 2000, 1000, False),
            ('Orange Juice', 'ml', 15000, 3000, 1500, True),
            ('Lemon Juice', 'ml', 5000, 1000, 500, True),
            ('Apple Juice', 'ml', 10000, 2000, 1000, True),
            ('Mango Pulp', 'grams', 8000, 1600, 800, True),
            ('Mint Leaves', 'grams', 1000, 200, 100, True),
            
            # Desserts & Sweets (8)
            ('Ice Cream', 'ml', 15000, 3000, 1500, True),
            ('Chocolate Sauce', 'grams', 4000, 800, 400, False),
            ('Vanilla Extract', 'ml', 1000, 200, 100, False),
            ('Sugar', 'grams', 15000, 3000, 1500, False),
            ('Honey', 'grams', 3000, 600, 300, False),
            ('Whipped Cream', 'grams', 4000, 800, 400, True),
            ('Brownie Base', 'piece', 300, 60, 30, True),
            ('Caramel Sauce', 'grams', 3000, 600, 300, False),
            
            # Seasonings & Spices (4)
            ('Salt', 'grams', 10000, 2000, 1000, False),
            ('Black Pepper', 'grams', 2000, 400, 200, False),
            ('Oregano', 'grams', 1500, 300, 150, False),
            ('Chili Flakes', 'grams', 1500, 300, 150, False),
        ]
        
        ingredients = {}
        for name, unit, stock, reorder, safety, perishable in ingredients_data:
            ingredients[name] = Ingredient.objects.create(
                name=name,
                unit_of_measure=unit,
                current_stock_qty=stock,
                reorder_level=reorder,
                safety_stock_qty=safety,
                is_perishable=perishable,
                status='Active'
            )
        self.stdout.write(f'Created {len(ingredients)} ingredients')
        
        # ==========================================
        # CREATE MENU CATEGORIES (10 entries)
        # ==========================================
        self.stdout.write('Creating 10 menu categories...')
        categories_data = [
            ('Burgers', 'Juicy and delicious burgers with various toppings'),
            ('Pizzas', 'Freshly baked pizzas with premium toppings'),
            ('Sandwiches', 'Classic and gourmet sandwiches'),
            ('Wraps', 'Healthy and filling wraps'),
            ('Beverages', 'Hot and cold refreshing drinks'),
            ('Desserts', 'Sweet treats and indulgences'),
            ('Sides', 'Perfect accompaniments to your meal'),
            ('Salads', 'Fresh and healthy salad options'),
            ('Appetizers', 'Start your meal right'),
            ('Specials', 'Chef\'s special creations'),
        ]
        
        categories = {}
        for name, desc in categories_data:
            categories[name] = MenuCategory.objects.create(name=name, description=desc)
        self.stdout.write(f'Created {len(categories)} categories')
        
        # ==========================================
        # CREATE MENU ITEMS (50 entries) with RECIPES
        # ==========================================
        self.stdout.write('Creating 50 menu items with recipes...')
        
        menu_items_data = [
            # Burgers (8)
            ('Classic Chicken Burger', 'Burgers', 120, True, 'Medium', False, [
                ('Burger Bun', 1), ('Chicken Patty', 1), ('Lettuce', 20), 
                ('Tomato', 1), ('Mayo', 15), ('Cheese Slice', 1)
            ]),
            ('Beef Burger', 'Burgers', 150, True, 'Medium', False, [
                ('Burger Bun', 1), ('Beef Patty', 1), ('Lettuce', 20),
                ('Onion', 0.5), ('Ketchup', 15), ('Cheese Slice', 1)
            ]),
            ('Paneer Burger', 'Burgers', 110, True, 'Mild', True, [
                ('Burger Bun', 1), ('Paneer', 50), ('Lettuce', 15),
                ('Tomato', 1), ('Mayo', 10)
            ]),
            ('BBQ Chicken Burger', 'Burgers', 140, True, 'Medium', False, [
                ('Burger Bun', 1), ('Chicken Patty', 1), ('BBQ Sauce', 20),
                ('Onion', 0.5), ('Cheese Slice', 1)
            ]),
            ('Double Cheese Burger', 'Burgers', 180, True, 'Mild', False, [
                ('Burger Bun', 1), ('Beef Patty', 2), ('Cheese Slice', 3),
                ('Lettuce', 15), ('Tomato', 1), ('Mayo', 10)
            ]),
            ('Spicy Chicken Burger', 'Burgers', 135, True, 'Hot', False, [
                ('Burger Bun', 1), ('Chicken Patty', 1), ('Jalapeno', 2),
                ('Hot Sauce', 15), ('Lettuce', 15), ('Cheese Slice', 1)
            ]),
            ('Fish Burger', 'Burgers', 160, True, 'Mild', False, [
                ('Burger Bun', 1), ('Fish Fillet', 1), ('Lettuce', 20),
                ('Tomato', 1), ('Mayo', 20)
            ]),
            ('Veggie Supreme Burger', 'Burgers', 100, True, 'Mild', True, [
                ('Burger Bun', 1), ('Lettuce', 25), ('Tomato', 2),
                ('Onion', 0.5), ('Cheese Slice', 1), ('Mayo', 15)
            ]),
            
            # Pizzas (8)
            ('Margherita Pizza', 'Pizzas', 200, True, 'Mild', True, [
                ('Pizza Dough', 1), ('Pizza Sauce', 50), ('Mozzarella Cheese', 100),
                ('Tomato', 2), ('Oregano', 2)
            ]),
            ('Chicken Tikka Pizza', 'Pizzas', 280, True, 'Medium', False, [
                ('Pizza Dough', 1), ('Pizza Sauce', 50), ('Mozzarella Cheese', 120),
                ('Chicken Tikka', 80), ('Onion', 1), ('Bell Pepper', 1)
            ]),
            ('Veggie Supreme Pizza', 'Pizzas', 250, True, 'Mild', True, [
                ('Pizza Dough', 1), ('Pizza Sauce', 50), ('Mozzarella Cheese', 100),
                ('Mushroom', 40), ('Bell Pepper', 1), ('Onion', 1), ('Tomato', 2), ('Olives', 20)
            ]),
            ('Paneer Pizza', 'Pizzas', 240, True, 'Medium', True, [
                ('Pizza Dough', 1), ('Pizza Sauce', 50), ('Mozzarella Cheese', 100),
                ('Paneer', 60), ('Bell Pepper', 1), ('Capsicum', 1)
            ]),
            ('BBQ Chicken Pizza', 'Pizzas', 290, True, 'Medium', False, [
                ('Pizza Dough', 1), ('BBQ Sauce', 50), ('Mozzarella Cheese', 100),
                ('Chicken Tikka', 80), ('Onion', 1)
            ]),
            ('Pepperoni Pizza', 'Pizzas', 300, True, 'Medium', False, [
                ('Pizza Dough', 1), ('Pizza Sauce', 50), ('Mozzarella Cheese', 120),
                ('Bacon Strips', 10), ('Chili Flakes', 2)
            ]),
            ('Four Cheese Pizza', 'Pizzas', 320, True, 'Mild', True, [
                ('Pizza Dough', 1), ('Pizza Sauce', 40), ('Mozzarella Cheese', 80),
                ('Cheddar Cheese', 60), ('Parmesan Cheese', 30), ('Oregano', 3)
            ]),
            ('Mushroom Pizza', 'Pizzas', 260, True, 'Mild', True, [
                ('Pizza Dough', 1), ('Pizza Sauce', 50), ('Mozzarella Cheese', 120),
                ('Mushroom', 80), ('Onion', 1), ('Garlic Sauce', 15)
            ]),
            
            # Sandwiches (6)
            ('Grilled Chicken Sandwich', 'Sandwiches', 90, True, 'Mild', False, [
                ('White Bread', 2), ('Grilled Chicken', 60), ('Lettuce', 15),
                ('Tomato', 1), ('Mayo', 10), ('Cheese Slice', 1)
            ]),
            ('Veg Sandwich', 'Sandwiches', 70, True, 'Mild', True, [
                ('Whole Wheat Bread', 2), ('Tomato', 2), ('Onion', 0.5),
                ('Lettuce', 15), ('Mayo', 10), ('Cucumber', 0.5)
            ]),
            ('Paneer Sandwich', 'Sandwiches', 85, True, 'Medium', True, [
                ('White Bread', 2), ('Paneer', 50), ('Onion', 0.5),
                ('Tomato', 1), ('Mayo', 10), ('Cheese Slice', 1)
            ]),
            ('Club Sandwich', 'Sandwiches', 130, True, 'Mild', False, [
                ('White Bread', 3), ('Grilled Chicken', 50), ('Bacon Strips', 3),
                ('Lettuce', 20), ('Tomato', 2), ('Mayo', 15), ('Cheese Slice', 2)
            ]),
            ('BLT Sandwich', 'Sandwiches', 95, True, 'Mild', False, [
                ('White Bread', 2), ('Bacon Strips', 4), ('Lettuce', 20),
                ('Tomato', 2), ('Mayo', 15)
            ]),
            ('Turkey Club', 'Sandwiches', 110, True, 'Mild', False, [
                ('Ciabatta Roll', 1), ('Turkey Slices', 60), ('Lettuce', 15),
                ('Tomato', 1), ('Mustard Sauce', 10), ('Cheese Slice', 1)
            ]),
            
            # Wraps (5)
            ('Chicken Wrap', 'Wraps', 100, True, 'Medium', False, [
                ('Tortilla Wrap', 1), ('Grilled Chicken', 70), ('Lettuce', 20),
                ('Tomato', 1), ('Ranch Dressing', 20)
            ]),
            ('Paneer Wrap', 'Wraps', 95, True, 'Medium', True, [
                ('Tortilla Wrap', 1), ('Paneer', 60), ('Onion', 0.5),
                ('Bell Pepper', 0.5), ('Mayo', 15)
            ]),
            ('Falafel Wrap', 'Wraps', 90, True, 'Medium', True, [
                ('Pita Bread', 1), ('Lettuce', 20), ('Tomato', 1),
                ('Onion', 0.5), ('Yogurt', 30)
            ]),
            ('Lamb Keema Wrap', 'Wraps', 120, True, 'Hot', False, [
                ('Tortilla Wrap', 1), ('Lamb Keema', 80), ('Onion', 0.5),
                ('Green Chili', 2), ('Yogurt', 20)
            ]),
            ('Veggie Wrap', 'Wraps', 80, True, 'Mild', True, [
                ('Tortilla Wrap', 1), ('Lettuce', 25), ('Tomato', 1),
                ('Cucumber', 0.5), ('Avocado', 0.5), ('Ranch Dressing', 15)
            ]),
            
            # Beverages (8)
            ('Coffee', 'Beverages', 40, True, None, True, [
                ('Coffee Powder', 10), ('Milk', 150), ('Sugar', 10)
            ]),
            ('Tea', 'Beverages', 30, True, None, True, [
                ('Tea Leaves', 5), ('Milk', 150), ('Sugar', 10)
            ]),
            ('Cold Coffee', 'Beverages', 60, True, None, True, [
                ('Coffee Powder', 15), ('Milk', 200), ('Sugar', 15), ('Ice Cream', 50)
            ]),
            ('Coke', 'Beverages', 40, True, None, True, [
                ('Coke Syrup', 50)
            ]),
            ('Fresh Orange Juice', 'Beverages', 60, True, None, True, [
                ('Orange Juice', 250)
            ]),
            ('Mango Lassi', 'Beverages', 70, True, None, True, [
                ('Mango Pulp', 80), ('Yogurt', 100), ('Sugar', 15), ('Milk', 50)
            ]),
            ('Lemonade', 'Beverages', 45, True, None, True, [
                ('Lemon Juice', 50), ('Sugar', 20), ('Mint Leaves', 5)
            ]),
            ('Apple Juice', 'Beverages', 55, True, None, True, [
                ('Apple Juice', 250)
            ]),
            
            # Desserts (8)
            ('Chocolate Ice Cream', 'Desserts', 80, True, None, True, [
                ('Ice Cream', 150), ('Chocolate Sauce', 30)
            ]),
            ('Vanilla Ice Cream', 'Desserts', 70, True, None, True, [
                ('Ice Cream', 150), ('Vanilla Extract', 5)
            ]),
            ('Brownie with Ice Cream', 'Desserts', 120, True, None, True, [
                ('Brownie Base', 1), ('Ice Cream', 100), ('Chocolate Sauce', 40)
            ]),
            ('Chocolate Shake', 'Desserts', 90, True, None, True, [
                ('Milk', 250), ('Ice Cream', 100), ('Chocolate Sauce', 30), ('Sugar', 15)
            ]),
            ('Vanilla Shake', 'Desserts', 85, True, None, True, [
                ('Milk', 250), ('Ice Cream', 100), ('Vanilla Extract', 5), ('Sugar', 15)
            ]),
            ('Caramel Sundae', 'Desserts', 100, True, None, True, [
                ('Ice Cream', 150), ('Caramel Sauce', 40), ('Whipped Cream', 30)
            ]),
            ('Fruit Salad with Cream', 'Desserts', 95, True, None, True, [
                ('Cream', 50), ('Honey', 15), ('Sugar', 10)
            ]),
            ('Chocolate Lava Cake', 'Desserts', 140, True, None, True, [
                ('Brownie Base', 1), ('Chocolate Sauce', 50), ('Ice Cream', 80)
            ]),
            
            # Sides (4)
            ('French Fries', 'Sides', 60, True, None, True, [
                ('Salt', 5), ('Ketchup', 20)
            ]),
            ('Onion Rings', 'Sides', 70, True, None, True, [
                ('Onion', 2), ('Salt', 3)
            ]),
            ('Coleslaw', 'Sides', 50, True, None, True, [
                ('Cabbage', 80), ('Mayo', 30), ('Cream', 20)
            ]),
            ('Garlic Bread', 'Sides', 55, True, None, True, [
                ('White Bread', 4), ('Butter', 30), ('Garlic Sauce', 15)
            ]),
            
            # Salads (3)
            ('Caesar Salad', 'Salads', 110, True, None, True, [
                ('Lettuce', 100), ('Parmesan Cheese', 20), ('Cream', 30)
            ]),
            ('Greek Salad', 'Salads', 100, True, None, True, [
                ('Lettuce', 80), ('Tomato', 2), ('Cucumber', 1), ('Olives', 30), ('Cheese Slice', 2)
            ]),
            ('Garden Salad', 'Salads', 80, True, None, True, [
                ('Lettuce', 60), ('Tomato', 2), ('Cucumber', 1), ('Onion', 0.5), ('Bell Pepper', 0.5)
            ]),
        ]
        
        menu_items = {}
        for item_data in menu_items_data:
            item_name, category_name, price, available, spice, veg, recipe_data = item_data
            menu_item = MenuItem.objects.create(
                name=item_name,
                category=categories[category_name],
                price=price,
                is_available=available,
                spice_level=spice,
                is_vegetarian=veg
            )
            menu_items[item_name] = menu_item
            
            # Create recipes
            for ingredient_name, quantity in recipe_data:
                Recipe.objects.create(
                    menu_item=menu_item,
                    ingredient=ingredients[ingredient_name],
                    quantity_required=Decimal(str(quantity))
                )
        
        self.stdout.write(f'Created {len(menu_items)} menu items with recipes')
        self.stdout.write(f'Created {Recipe.objects.count()} recipe entries')
        
        # ==========================================
        # CREATE SUPPLIER-INGREDIENT RELATIONSHIPS (70+ entries)
        # ==========================================
        self.stdout.write('Creating supplier-ingredient relationships...')
        supplier_ingredient_mapping = [
            ('Fresh Farms Produce', ['Lettuce', 'Tomato', 'Onion', 'Bell Pepper', 'Cucumber', 'Spinach', 'Cabbage', 'Capsicum']),
            ('Metro Meats Inc', ['Chicken Patty', 'Beef Patty', 'Lamb Keema', 'Bacon Strips']),
            ('Dairy Delights Co', ['Milk', 'Cream', 'Butter', 'Yogurt', 'Cheese Slice']),
            ('Bakery Supplies Ltd', ['Burger Bun', 'Pizza Dough', 'White Bread', 'Whole Wheat Bread', 'Ciabatta Roll', 'Pita Bread', 'Tortilla Wrap']),
            ('Spice World Trading', ['Salt', 'Black Pepper', 'Oregano', 'Chili Flakes', 'Green Chili']),
            ('Ocean Fresh Seafood', ['Fish Fillet', 'Shrimp']),
            ('Green Valley Organics', ['Avocado', 'Mushroom', 'Corn Kernels', 'Olives', 'Mint Leaves']),
            ('Quick Beverage Dist', ['Coke Syrup', 'Orange Juice', 'Apple Juice', 'Lemon Juice']),
            ('Premium Poultry Farm', ['Chicken Tikka', 'Grilled Chicken', 'Turkey Slices']),
            ('Sauce Masters Inc', ['Mayo', 'Ketchup', 'Pizza Sauce', 'BBQ Sauce', 'Mustard Sauce', 'Hot Sauce', 'Ranch Dressing', 'Soy Sauce', 'Garlic Sauce', 'Pesto Sauce']),
            ('Frozen Foods Express', ['Ice Cream', 'Brownie Base']),
            ('Veggie Paradise', ['Jalapeno', 'Pickles', 'Corn Kernels']),
            ('Cheese Heaven Ltd', ['Mozzarella Cheese', 'Cheddar Cheese', 'Parmesan Cheese']),
            ('Grain Central', ['Sugar', 'Coffee Powder', 'Tea Leaves']),
            ('Sweet Treats Supplier', ['Chocolate Sauce', 'Vanilla Extract', 'Honey', 'Whipped Cream', 'Caramel Sauce']),
            ('Fresh Herbs Garden', ['Mint Leaves', 'Oregano']),
            ('Tropical Fruits Inc', ['Mango Pulp', 'Orange Juice', 'Lemon Juice', 'Apple Juice']),
            ('Coffee Bean Imports', ['Coffee Powder']),
            ('Tea Leaf Traders', ['Tea Leaves']),
            ('Mushroom Kingdom', ['Mushroom']),
            ('Lettuce Land', ['Lettuce', 'Spinach', 'Cabbage']),
            ('Tomato Territory', ['Tomato']),
            ('Onion Outpost', ['Onion']),
            ('Pepper Palace', ['Bell Pepper', 'Capsicum', 'Jalapeno', 'Green Chili']),
            ('Cucumber Corner', ['Cucumber', 'Pickles']),
            ('Avocado Avenue', ['Avocado']),
        ]
        
        supplier_ingredient_count = 0
        for supplier_name, ingredient_names in supplier_ingredient_mapping:
            if supplier_name in suppliers:
                for ing_name in ingredient_names:
                    if ing_name in ingredients:
                        SupplierIngredient.objects.create(
                            supplier=suppliers[supplier_name],
                            ingredient=ingredients[ing_name]
                        )
                        supplier_ingredient_count += 1
        
        self.stdout.write(f'Created {supplier_ingredient_count} supplier-ingredient relationships')
        
        # ==========================================
        # CREATE PURCHASE ORDERS (60 entries) with PURCHASE ORDER LINES
        # ==========================================
        self.stdout.write('Creating 60 purchase orders with lines...')
        
        # Date range: Jan 20 to Feb 2, 2026
        base_date = datetime(2026, 1, 20, tzinfo=timezone.get_current_timezone())
        supplier_list = list(suppliers.values())
        ingredient_list = list(ingredients.values())
        
        po_statuses = ['Pending', 'Ordered', 'Shipped', 'Delivered', 'Delivered', 'Delivered']
        
        for i in range(60):
            order_date = base_date + timedelta(days=random.randint(0, 13))
            supplier = random.choice(supplier_list)
            status = random.choice(po_statuses)
            
            expected_delivery = order_date + timedelta(days=random.randint(2, 5))
            received_date = None
            if status == 'Delivered':
                received_date = expected_delivery + timedelta(days=random.randint(-1, 1))
            
            po = PurchaseOrder.objects.create(
                supplier=supplier,
                order_date=order_date.date(),
                expected_delivery_date=expected_delivery.date(),
                received_date=received_date.date() if received_date else None,
                status=status,
                total_amount=0
            )
            
            # Add 2-5 lines per PO
            num_lines = random.randint(2, 5)
            selected_ingredients = random.sample(ingredient_list, num_lines)
            total_amount = Decimal('0')
            
            for line_no, ing in enumerate(selected_ingredients, 1):
                qty = Decimal(str(random.randint(50, 500)))
                unit_price = Decimal(str(random.randint(5, 50))) + Decimal(str(random.random())).quantize(Decimal('0.01'))
                line_amount = qty * unit_price
                received_qty = qty if status == 'Delivered' else Decimal('0')
                
                PurchaseOrderLine.objects.create(
                    purchase_order=po,
                    line_no=line_no,
                    ingredient=ing,
                    ordered_qty=qty,
                    received_qty=received_qty,
                    unit_price=unit_price,
                    line_amount=line_amount
                )
                total_amount += line_amount
            
            po.total_amount = total_amount
            po.save()
        
        self.stdout.write(f'Created {PurchaseOrder.objects.count()} purchase orders')
        self.stdout.write(f'Created {PurchaseOrderLine.objects.count()} purchase order lines')
        
        # ==========================================
        # CREATE CUSTOMER ORDERS (65 orders from Jan 28 - Feb 2)
        # ==========================================
        self.stdout.write('Creating 65 customer orders from Jan 28 - Feb 2, 2026...')
        
        all_items = list(menu_items.values())
        order_types = ['DINE_IN', 'TAKEAWAY', 'ONLINE']
        payment_modes = ['Cash', 'Card', 'UPI', 'Online']
        
        # Start date: Jan 28, 2026; End date: Feb 2, 2026 (6 days)
        start_date = datetime(2026, 1, 28, tzinfo=timezone.get_current_timezone())
        end_date = datetime(2026, 2, 2, 23, 59, 59, tzinfo=timezone.get_current_timezone())
        
        orders_created = 0
        # Distribute orders across the days (roughly 10-12 per day)
        for day_offset in range(6):  # Jan 28, 29, 30, 31, Feb 1, Feb 2
            current_date = start_date + timedelta(days=day_offset)
            num_orders_today = random.randint(10, 12)
            
            for _ in range(num_orders_today):
                # Random time during operating hours (10 AM to 10 PM)
                hour = random.randint(10, 22)
                minute = random.randint(0, 59)
                order_datetime = current_date.replace(hour=hour, minute=minute)
                
                # Random number of items per order (1-6)
                num_items = random.randint(1, 6)
                selected_items = random.sample(all_items, min(num_items, len(all_items)))
                
                total_amount = Decimal('0')
                order_items_data = []
                
                for menu_item in selected_items:
                    quantity = random.randint(1, 3)
                    line_amount = menu_item.price * quantity
                    total_amount += line_amount
                    order_items_data.append((menu_item, quantity, line_amount))
                
                # Create order
                order = CustomerOrder(
                    total_amount=total_amount,
                    order_status=random.choice(['PENDING', 'PREPARING', 'SERVED', 'SERVED', 'SERVED']),  # 60% served
                    order_type=random.choice(order_types),
                    payment_mode=random.choice(payment_modes)
                )
                order.save()
                # Override the auto-set datetime
                CustomerOrder.objects.filter(pk=order.pk).update(order_datetime=order_datetime)
                
                # Create order items
                for menu_item, quantity, line_amount in order_items_data:
                    OrderItem.objects.create(
                        customer_order=order,
                        menu_item=menu_item,
                        quantity=quantity,
                        unit_price=menu_item.price,
                        line_amount=line_amount
                    )
                
                orders_created += 1
        
        self.stdout.write(f'Created {CustomerOrder.objects.count()} customer orders')
        self.stdout.write(f'Created {OrderItem.objects.count()} order items')
        
        # ==========================================
        # SUMMARY
        # ==========================================
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('=== Comprehensive Data Population Complete ==='))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'Suppliers: {Supplier.objects.count()}')
        self.stdout.write(f'Ingredients: {Ingredient.objects.count()}')
        self.stdout.write(f'Supplier-Ingredient Links: {SupplierIngredient.objects.count()}')
        self.stdout.write(f'Menu Categories: {MenuCategory.objects.count()}')
        self.stdout.write(f'Menu Items: {MenuItem.objects.count()}')
        self.stdout.write(f'Recipes: {Recipe.objects.count()}')
        self.stdout.write(f'Purchase Orders: {PurchaseOrder.objects.count()}')
        self.stdout.write(f'Purchase Order Lines: {PurchaseOrderLine.objects.count()}')
        self.stdout.write(f'Customer Orders: {CustomerOrder.objects.count()}')
        self.stdout.write(f'Order Items: {OrderItem.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\nAll tables populated with 50-70 entries!'))
        self.stdout.write(self.style.SUCCESS('Customer orders are dated Jan 28 - Feb 2, 2026'))
