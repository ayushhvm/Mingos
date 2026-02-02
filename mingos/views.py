from django.shortcuts import render, redirect
from django.db import transaction, models
from django.db.models import Sum, Count, F, Case, When, Value, FloatField
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
import json
from datetime import timedelta, datetime
from django.utils.timezone import now
from .models import CustomerOrder, OrderItem, Ingredient, MenuItem, MenuCategory, PurchaseOrder, Recipe
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from io import BytesIO


def _get_last_7_days_sales():
    today = now().date()
    start_date = today - timedelta(days=6)

    # Get actual sales data
    qs = (
        CustomerOrder.objects
        .filter(order_datetime__date__gte=start_date, order_datetime__date__lte=today)
        .extra({'date': 'DATE(order_datetime)'})
        .values('date')
        .annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('order_id')
        )
        .order_by('date')
    )

    # Create a dict of sales by date
    sales_by_date = {row['date']: {'sales': float(row['total_sales'] or 0), 'count': row['order_count']} for row in qs}

    # Generate all 7 days
    labels = []
    totals = []
    counts = []
    
    for i in range(7):
        date = start_date + timedelta(days=i)
        labels.append(date.strftime('%d %b'))
        
        if date in sales_by_date:
            totals.append(sales_by_date[date]['sales'])
            counts.append(sales_by_date[date]['count'])
        else:
            totals.append(0)
            counts.append(0)

    return labels, totals, counts


def _predict_next_day_sales():
    """
    Use ML to predict quantities of each menu item for the next day.
    Returns a dict: {menu_item_id: predicted_quantity}
    """
    try:
        today = now().date()
        start_date = today - timedelta(days=30)  # Use last 30 days of data
        
        # Get historical daily sales by menu item
        daily_sales = (
            OrderItem.objects
            .filter(customer_order__order_datetime__date__gte=start_date)
            .values('menu_item_id', 'menu_item__name')
            .annotate(date=F('customer_order__order_datetime__date'))
            .values('date', 'menu_item_id', 'menu_item__name')
            .annotate(total_qty=Sum('quantity'))
            .order_by('date', 'menu_item_id')
        )
        
        predictions = {}
        
        # Group by menu item and predict
        menu_items_dict = {}
        for sale in daily_sales:
            item_id = sale['menu_item_id']
            date = sale['date']
            qty = sale['total_qty'] or 0
            
            if item_id not in menu_items_dict:
                menu_items_dict[item_id] = {
                    'name': sale['menu_item__name'],
                    'dates': [],
                    'quantities': []
                }
            
            menu_items_dict[item_id]['dates'].append(date)
            menu_items_dict[item_id]['quantities'].append(qty)
        
        # Train model for each menu item
        for item_id, data in menu_items_dict.items():
            if len(data['quantities']) < 3:  # Need at least 3 data points
                # Use average if not enough data
                predictions[item_id] = {
                    'predicted_qty': int(np.mean(data['quantities'])),
                    'name': data['name'],
                    'confidence': 'low'
                }
                continue
            
            try:
                # Prepare data for ML model
                X = np.arange(len(data['quantities'])).reshape(-1, 1)
                y = np.array(data['quantities'])
                
                # Use polynomial regression for better trend capture
                poly = PolynomialFeatures(degree=2)
                X_poly = poly.fit_transform(X)
                
                model = LinearRegression()
                model.fit(X_poly, y)
                
                # Predict for next day (index = len(data))
                next_day_X = np.array([[len(data['quantities'])]]).reshape(-1, 1)
                next_day_X_poly = poly.transform(next_day_X)
                predicted_qty = model.predict(next_day_X_poly)[0]
                
                # Ensure non-negative prediction
                predicted_qty = max(0, int(round(predicted_qty)))
                
                predictions[item_id] = {
                    'predicted_qty': predicted_qty,
                    'name': data['name'],
                    'confidence': 'high',
                    'avg_daily_sales': int(np.mean(data['quantities']))
                }
            except:
                # Fallback to average
                predictions[item_id] = {
                    'predicted_qty': int(np.mean(data['quantities'])),
                    'name': data['name'],
                    'confidence': 'low'
                }
        
        return predictions
    except Exception as e:
        print(f"Prediction error: {e}")
        return {}


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

    # ML Predictions for next day
    next_day_predictions = _predict_next_day_sales()
    predicted_items = []
    for item_id, pred_data in next_day_predictions.items():
        predicted_items.append({
            'id': item_id,
            'name': pred_data['name'],
            'predicted_qty': pred_data['predicted_qty'],
            'confidence': pred_data['confidence'],
            'avg_daily': pred_data.get('avg_daily_sales', 0)
        })
    predicted_items.sort(key=lambda x: x['predicted_qty'], reverse=True)

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
        "predicted_items": predicted_items,
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
    # Get all ingredients with stock status
    all_ingredients = (
        Ingredient.objects
        .annotate(
            stock_percentage=Case(
                When(reorder_level__gt=0, then=(
                    F('current_stock_qty') * 100 / F('reorder_level')
                )),
                default=Value(100),
                output_field=FloatField()
            )
        )
        .order_by('name')
    )
    
    low_stock = all_ingredients.filter(current_stock_qty__lt=F('reorder_level'))
    low_stock_count = low_stock.count()
    
    # Calculate total inventory value (you can add cost per unit later)
    total_items = all_ingredients.count()
    
    recent_pos = (
        PurchaseOrder.objects
        .select_related('supplier')
        .order_by('-order_date')[:10]
    )

    context = {
        "all_ingredients": all_ingredients,
        "low_stock_count": low_stock_count,
        "total_items": total_items,
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
           Also automatically reduces inventory based on recipes
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
            
            # Add order items and reduce inventory
            for menu_item, qty, line_amount in items:
                OrderItem.objects.create(
                    customer_order=order,
                    menu_item=menu_item,
                    quantity=qty,
                    unit_price=menu_item.price,
                    line_amount=line_amount,
                )
                
                # Reduce inventory based on recipe
                recipes = Recipe.objects.filter(menu_item=menu_item).select_related('ingredient')
                for recipe in recipes:
                    ingredient_qty_needed = recipe.quantity_required * qty
                    ingredient = recipe.ingredient
                    
                    # Deduct from inventory
                    ingredient.current_stock_qty = F('current_stock_qty') - ingredient_qty_needed
                    ingredient.save(update_fields=['current_stock_qty'])
                    ingredient.refresh_from_db()  # Reload to get actual value

            messages.success(request, f"✅ Order #{order.order_id} created successfully! Inventory updated.")
            return redirect('dashboard')

        # If no items selected
        categories = MenuCategory.objects.prefetch_related('items').all().order_by('name')
        messages.warning(request, "Please select at least one item with quantity > 0.")
        
        # Get all available menu items as JSON
        menu_items = MenuItem.objects.filter(is_available=True).values('pk', 'name', 'price', 'is_available')
        menu_items_json = json.dumps(list(menu_items), cls=json.JSONEncoder, default=str)
        menu_items_json = menu_items_json.replace('pk', 'id')
        
        return render(
            request,
            'mingos/create_order.html',
            {
                'categories': categories,
                'error': "Please select at least one item with quantity > 0.",
                'menu_items_json': menu_items_json,
            },
        )

    # GET: show form
    categories = MenuCategory.objects.prefetch_related('items').all().order_by('name')
    
    # Get all available menu items as JSON
    menu_items = MenuItem.objects.filter(is_available=True).values('pk', 'name', 'price', 'is_available')
    menu_items_json = json.dumps(list(menu_items), cls=json.JSONEncoder, default=str)
    menu_items_json = menu_items_json.replace('pk', 'id')
    
    return render(request, 'mingos/create_order.html', {
        'categories': categories,
        'menu_items_json': menu_items_json
    })


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


def report_generation(request):
    """Report generation page with date range selection"""
    today = now().date()
    default_start = today - timedelta(days=7)
    
    return render(request, 'mingos/report_generation.html', {
        'default_start_date': default_start.strftime('%Y-%m-%d'),
        'default_end_date': today.strftime('%Y-%m-%d'),
    })


def generate_report_pdf(request):
    """Generate comprehensive PDF report for custom date range"""
    # Get date range from parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    report_title = request.GET.get('report_title', 'Sales & Inventory Report')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except:
        # Default to last 7 days if invalid dates
        end_date = now().date()
        start_date = end_date - timedelta(days=7)
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="mingos_report_{start_date}_to_{end_date}.pdf"'
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#22c55e'),
        alignment=TA_CENTER,
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#3b82f6'),
        spaceAfter=10,
        spaceBefore=15
    )
    normal_style = styles['Normal']
    
    # Title
    elements.append(Paragraph(f"<b>{report_title}</b>", title_style))
    elements.append(Paragraph(f"<b>Mingos Canteen Management System</b>", styles['Heading3']))
    elements.append(Paragraph(f"Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}", normal_style))
    elements.append(Paragraph(f"Generated on: {now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Query data for date range
    orders = CustomerOrder.objects.filter(
        order_datetime__date__gte=start_date,
        order_datetime__date__lte=end_date
    )
    
    total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders.count()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Summary Section
    elements.append(Paragraph("<b>Executive Summary</b>", heading_style))
    summary_data = [
        ['Metric', 'Value'],
        ['Total Revenue', f'₹ {total_revenue:,.2f}'],
        ['Total Orders', f'{total_orders}'],
        ['Average Order Value', f'₹ {avg_order_value:,.2f}'],
        ['Number of Days', f'{(end_date - start_date).days + 1}'],
    ]
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Daily Revenue Data
    daily_sales = {}
    current_date = start_date
    while current_date <= end_date:
        daily_sales[current_date] = 0
        current_date += timedelta(days=1)
    
    daily_data = (
        orders.extra({'date': 'DATE(order_datetime)'})
        .values('date')
        .annotate(total=Sum('total_amount'))
        .order_by('date')
    )
    
    for row in daily_data:
        daily_sales[row['date']] = float(row['total'] or 0)
    
    # Daily Revenue Chart
    if len(daily_sales) > 0:
        elements.append(Paragraph("<b>Daily Revenue Analysis</b>", heading_style))
        
        drawing = Drawing(500, 200)
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = 125
        chart.width = 400
        chart.data = [list(daily_sales.values())]
        chart.categoryAxis.categoryNames = [d.strftime('%d %b') for d in daily_sales.keys()]
        chart.valueAxis.valueMin = 0
        chart.bars[0].fillColor = colors.HexColor('#22c55e')
        
        drawing.add(chart)
        elements.append(drawing)
        elements.append(Spacer(1, 0.2*inch))
    
    # Top Selling Items
    elements.append(Paragraph("<b>Top Selling Items</b>", heading_style))
    
    top_items = (
        OrderItem.objects.filter(customer_order__in=orders)
        .values('menu_item__name')
        .annotate(
            total_qty=Sum('quantity'),
            total_sales=Sum('line_amount')
        )
        .order_by('-total_sales')[:10]
    )
    
    if top_items:
        items_data = [['Rank', 'Item Name', 'Quantity Sold', 'Revenue (₹)']]
        for idx, item in enumerate(top_items, 1):
            items_data.append([
                str(idx),
                item['menu_item__name'],
                str(item['total_qty']),
                f"₹ {item['total_sales']:,.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[0.6*inch, 2.5*inch, 1.2*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#22c55e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(items_table)
    else:
        elements.append(Paragraph("No sales data available for this period.", normal_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Category-wise Revenue
    elements.append(Paragraph("<b>Category-wise Performance</b>", heading_style))
    
    category_data = (
        OrderItem.objects.filter(customer_order__in=orders)
        .values('menu_item__category__name')
        .annotate(total=Sum('line_amount'))
        .order_by('-total')
    )
    
    if category_data:
        cat_table_data = [['Category', 'Revenue (₹)', 'Percentage']]
        for cat in category_data:
            percentage = (float(cat['total']) / float(total_revenue) * 100) if total_revenue > 0 else 0
            cat_table_data.append([
                cat['menu_item__category__name'] or 'Uncategorized',
                f"₹ {cat['total']:,.2f}",
                f"{percentage:.1f}%"
            ])
        
        cat_table = Table(cat_table_data, colWidths=[2*inch, 1.8*inch, 1.2*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(cat_table)
    
    elements.append(PageBreak())
    
    # Inventory Status
    elements.append(Paragraph("<b>Current Inventory Status</b>", heading_style))
    
    all_ingredients = Ingredient.objects.annotate(
        stock_percentage=Case(
            When(reorder_level__gt=0, then=(
                F('current_stock_qty') * 100 / F('reorder_level')
            )),
            default=Value(100),
            output_field=FloatField()
        )
    ).order_by('current_stock_qty')[:15]  # Top 15 to fit on page
    
    if all_ingredients:
        inv_data = [['Ingredient', 'Current Stock', 'Reorder Level', 'Status']]
        for ing in all_ingredients:
            if ing.current_stock_qty < ing.safety_stock_qty:
                status = 'Critical'
            elif ing.current_stock_qty < ing.reorder_level:
                status = 'Low Stock'
            else:
                status = 'Healthy'
            
            inv_data.append([
                ing.name,
                f"{ing.current_stock_qty:.1f} {ing.unit_of_measure}",
                f"{ing.reorder_level:.1f}",
                status
            ])
        
        inv_table = Table(inv_data, colWidths=[2*inch, 1.5*inch, 1.2*inch, 1*inch])
        inv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(inv_table)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Low Stock Alerts
    low_stock = Ingredient.objects.filter(
        current_stock_qty__lt=F('reorder_level')
    ).count()
    
    elements.append(Paragraph(f"<b>Low Stock Alerts: {low_stock} items</b>", normal_style))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("─" * 100, normal_style))
    elements.append(Paragraph(
        "<i>This report was automatically generated by Mingos Canteen Management System</i>",
        ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF value and close buffer
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
