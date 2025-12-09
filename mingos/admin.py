from django.contrib import admin
from .models import (
    Supplier, Ingredient, MenuCategory, MenuItem, 
    CustomerOrder, OrderItem, Recipe, PurchaseOrder, 
    PurchaseOrderLine, SupplierIngredient
)

admin.site.register(Supplier)
admin.site.register(Ingredient)
admin.site.register(MenuCategory)
admin.site.register(MenuItem)
admin.site.register(SupplierIngredient)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderLine)
admin.site.register(Recipe)
admin.site.register(CustomerOrder)
admin.site.register(OrderItem)
