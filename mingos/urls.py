from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analytics/sales/', views.sales_analytics, name='sales_analytics'),
    path('analytics/inventory/', views.inventory_analytics, name='inventory_analytics'),
    path('menu/', views.menu_list, name='menu_list'),
    path('order/new/', views.create_order, name='create_order'),
    path('orders/recent/', views.recent_orders, name='recent_orders'),
    path('menu/<int:item_id>/recipe/', views.recipe_view_edit, name='recipe_view_edit'),
    path('menu/<int:item_id>/recipe/view/', views.recipe_detail, name='recipe_detail'),
    path('reports/', views.report_generation, name='report_generation'),
    path('reports/generate-pdf/', views.generate_report_pdf, name='generate_report_pdf'),
]
