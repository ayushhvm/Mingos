from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from django.contrib import messages
import json
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Sum, Count, F
from django.shortcuts import render
from .models import CustomerOrder, OrderItem, Ingredient, MenuItem, MenuCategory, PurchaseOrder, Recipe


def _get_last_7_days_sales():
    today = now().date()
    start_date = today - timedelta(days=6)

    qs = (
        CustomerOrder.objects
        .filter(order_datetime__date__gte=start_date)
        .values('order_datetime__date')
        .annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('order_id')
        )
        .order_by('order_datetime__date')
    )

    labels = []
    totals = []
    counts = []

    for row in qs:
        labels.append(row['order_datetime__date'].strftime('%d %b'))
        totals.append(float(row['total_sales'] or 0))
        counts.append(row['order_count'] or 0)

    return labels, totals, counts


def dashboard(request):
    # High-level KPIs
    total_revenue = CustomerOrder.objects.aggregate(s=Sum('total_amount'))['s'] or 0
    total_orders = CustomerOrder.objects.count()
    total_menu_items = MenuItem.objects.count()
    low_stock_count = Ingredient.objects.filter(current_stock_qty__lt=F('reorder_level')).count()

    # Daily sales (last 7 days)
    daily_labels, daily_totals, daily_counts = _get_last_7_days_sales()

    # Top 5 selling items by revenue
    top_items = (
        OrderItem.objects
        .values('menu_item__name')
        .annotate(
            total_qty=Sum('quantity'),
            total_sales=Sum('line_amount')
        )
        .order_by('-total_sales')[:5]
    )
    top_items_labels = [row['menu_item__name'] for row in top_items]
    top_items_sales = [float(row['total_sales'] or 0) for row in top_items]

    # Category-wise revenue
    category_sales_qs = (
        OrderItem.objects
        .values('menu_item__category__name')
        .annotate(total_sales=Sum('line_amount'))
        .order_by('-total_sales')
    )
    category_labels = [row['menu_item__category__name'] or 'Uncategorized' for row in category_sales_qs]
    category_values = [float(row['total_sales'] or 0) for row in category_sales_qs]
    category_data = [
        {"label": label, "value": value}
        for label, value in zip(category_labels, category_values)
    ]

    context = {
        "total_revenue": float(total_revenue),
        "total_orders": total_orders,
        "total_menu_items": total_menu_items,
        "low_stock_count": low_stock_count,
        "category_data": category_data,
        "daily_labels_json": json.dumps(daily_labels),
        "daily_totals_json": json.dumps(daily_totals),
        "top_items_labels_json": json.dumps(top_items_labels),
        "top_items_sales_json": json.dumps(top_items_sales),
        "category_labels_json": json.dumps(category_labels),
        "category_values_json": json.dumps(category_values),
    }
    return render(request, "mingos/dashboard.html", context)


def sales_analytics(request):
    daily_labels, daily_totals, daily_counts = _get_last_7_days_sales()

    top_items = (
        OrderItem.objects
        .values('menu_item__name')
        .annotate(
            total_qty=Sum('quantity'),
            total_sales=Sum('line_amount')
        )
        .order_by('-total_sales')[:10]
    )

    context = {
        "top_items": top_items,
        "daily_labels_json": json.dumps(daily_labels),
        "daily_totals_json": json.dumps(daily_totals),
    }
    return render(request, "mingos/sales_analytics.html", context)


def inventory_analytics(request):
    low_stock = (
        Ingredient.objects
        .filter(current_stock_qty__lt=F('reorder_level'))
        .order_by('current_stock_qty')[:20]
    )

    recent_pos = (
        PurchaseOrder.objects
        .select_related('supplier')
        .order_by('-order_date')[:10]
    )

    context = {
        "low_stock": low_stock,
        "recent_pos": recent_pos,
    }
    return render(request, "mingos/inventory_analytics.html", context)


def menu_list(request):
    """
    Show all menu categories and items in a clean list.
    """
    categories = MenuCategory.objects.prefetch_related('items').all().order_by('name')
    return render(request, 'mingos/menu_list.html', {'categories': categories})


@transaction.atomic
def create_order(request):
    """
    Simple order creation
    - GET: show a form with all menu items and quantity fields
    - POST: read selected quantities, create CustomerOrder + OrderItem rows
    """
    if request.method == 'POST':
        items = []
        total_amount = 0

        for key, value in request.POST.items():
            if key.startswith('item_') and value.strip():
                try:
                    qty = int(value)
                except ValueError:
                    continue
                if qty <= 0:
                    continue

                menu_item_id = key.split('_', 1)[1]
                try:
                    menu_item = MenuItem.objects.get(pk=menu_item_id)
                except MenuItem.DoesNotExist:
                    continue

                line_amount = menu_item.price * qty
                items.append((menu_item, qty, line_amount))
                total_amount += line_amount

        if items:
            # Create order
            order = CustomerOrder.objects.create(
                total_amount=total_amount,
                order_status='PENDING'
            )
            
            # Add order items
            for menu_item, qty, line_amount in items:
                OrderItem.objects.create(
                    customer_order=order,
                    menu_item=menu_item,
                    quantity=qty,
                    unit_price=menu_item.price,
                    line_amount=line_amount,
                )

            messages.success(request, f"✅ Order #{order.order_id} created successfully!")
            return redirect('dashboard')

        # If no items selected
        categories = MenuCategory.objects.prefetch_related('items').all().order_by('name')
        messages.warning(request, "Please select at least one item with quantity > 0.")
        return render(
            request,
            'mingos/create_order.html',
            {
                'categories': categories,
                'error': "Please select at least one item with quantity > 0.",
            },
        )

    # GET: show form
    categories = MenuCategory.objects.prefetch_related('items').all().order_by('name')
    return render(request, 'mingos/create_order.html', {'categories': categories})


def recent_orders(request):
    """
    Show the most recent customer orders with a quick breakdown of items.
    """
    orders = (
        CustomerOrder.objects
        .annotate(
            item_count=Count('items'),
            total_qty=Sum('items__quantity'),
        )
        .order_by('-order_datetime')
        .prefetch_related('items__menu_item')[:20]
    )

    context = {
        "orders": orders,
    }
    return render(request, "mingos/recent_orders.html", context)


@transaction.atomic
def recipe_view_edit(request, item_id):
    menu_item = get_object_or_404(MenuItem, pk=item_id)
    ingredients = list(Ingredient.objects.all().order_by("name"))

    # Map existing recipe
    existing_recipe = {
        r.ingredient_id: float(r.quantity_required)
        for r in Recipe.objects.filter(menu_item=menu_item)
    }

    if request.method == "POST":
        # Remove old recipe rows
        Recipe.objects.filter(menu_item=menu_item).delete()

        # Rebuild recipe rows from POST
        for ing in ingredients:
            field_name = f"ing_{ing.pk}"
            qty_str = request.POST.get(field_name)

            if qty_str and qty_str.strip():
                try:
                    qty_val = float(qty_str)
                except ValueError:
                    continue
                if qty_val > 0:
                    Recipe.objects.create(
                        menu_item=menu_item,
                        ingredient=ing,
                        quantity_required=qty_val,
                    )

        return redirect("recipe_view_edit", item_id=item_id)

    # Attach current qty to each ingredient object
    for ing in ingredients:
        ing.current_qty = existing_recipe.get(ing.pk, 0)

    return render(
        request,
        "mingos/recipe_view_edit.html",
        {
            "menu_item": menu_item,
            "ingredients": ingredients,
        },
    )


def recipe_detail(request, item_id):
    menu_item = get_object_or_404(MenuItem, pk=item_id)
    recipe_rows = Recipe.objects.filter(menu_item=menu_item).select_related("ingredient")

    return render(request, "mingos/recipe_detail.html", {
        "menu_item": menu_item,
        "recipe_rows": recipe_rows,
    })
