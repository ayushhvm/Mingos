from django.db import models
from django.utils.timezone import now


class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    ingredient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    unit_of_measure = models.CharField(max_length=20)
    current_stock_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    safety_stock_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_perishable = models.BooleanField(default=False)
    status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class MenuCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    menu_item_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    spice_level = models.CharField(max_length=20, blank=True, null=True)
    is_vegetarian = models.BooleanField(default=False)
    category = models.ForeignKey(MenuCategory, on_delete=models.SET_NULL, null=True, related_name="items")

    def __str__(self):
        return self.name


class SupplierIngredient(models.Model):
    """Equivalent to SUPPLIES (Supplier ↔ Ingredient)."""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('supplier', 'ingredient')

    def __str__(self):
        return f"{self.supplier} supplies {self.ingredient}"


class PurchaseOrder(models.Model):
    po_id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchase_orders")
    order_date = models.DateField()
    received_date = models.DateField(blank=True, null=True)
    expected_delivery_date = models.DateField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"PO #{self.po_id} - {self.supplier.name}"


class PurchaseOrderLine(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="lines")
    line_no = models.IntegerField()
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    ordered_qty = models.DecimalField(max_digits=10, decimal_places=2)
    received_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('purchase_order', 'line_no')

    def __str__(self):
        return f"PO #{self.purchase_order.po_id} Line {self.line_no}"


class Recipe(models.Model):
    """MenuItem ↔ Ingredient with quantity."""
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="recipe_items")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="used_in_recipes")
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('menu_item', 'ingredient')

    def __str__(self):
        return f"{self.quantity_required} {self.ingredient.unit_of_measure} {self.ingredient.name} for {self.menu_item.name}"


class CustomerOrder(models.Model):
    ORDER_TYPES = (
        ('DINE_IN', 'Dine In'),
        ('TAKEAWAY', 'Take Away'),
        ('ONLINE', 'Online'),
    )

    ORDER_STATUS = (
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('SERVED', 'Served'),
        ('CANCELLED', 'Cancelled'),
    )

    order_id = models.AutoField(primary_key=True)
    order_datetime = models.DateTimeField(auto_now_add=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES, default='DINE_IN')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING')
    payment_mode = models.CharField(max_length=50, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.order_id} ({self.order_status})"


class OrderItem(models.Model):
    customer_order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('customer_order', 'menu_item')

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} (Order #{self.customer_order.order_id})"
