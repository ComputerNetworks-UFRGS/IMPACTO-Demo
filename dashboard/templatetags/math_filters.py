# dashboard/templatetags/math_filters.py

from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """Subtrai arg de value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def divide(value, arg):
    """Divide value por arg."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return ''

@register.filter
def multiply(value, arg):
    """Multiplica value por arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def to_percentage(value):
    """Converte um valor numérico para uma string de porcentagem."""
    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return ""