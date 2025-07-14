from django import template
from django.utils.formats import number_format
from django.utils.translation import gettext as _


register = template.Library()

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None
    
@register.filter
def custom_intcomma(value):
    return number_format(value, use_l10n=True)

@register.filter
def format_large_number(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    
    abs_value = abs(value)
    sign = '-' if value < 0 else ''
    
    if abs_value >= 1e9:
        return f'{sign}{abs_value/1e9:.1f}B'
    if abs_value >= 1e6:
        return f'{sign}{abs_value/1e6:.1f}M'
    if abs_value >= 1e3:
        return f'{sign}{abs_value/1e3:.1f}K'
    return f'{sign}{abs_value:.2f}'

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

@register.simple_tag
def get_risk_color(score):
    if score >= 80:
        return 0xFF0000
    elif score >= 60:
        return 0xFFA500
    elif score >= 40:
        return 0xffdc00
    elif score >= 20:
        return 0x008000
    else:
        return 0x00A8FF

@register.simple_tag
def get_risk_text(score):
    if score >= 80:
        return _("Critical")
    elif score >= 60:
        return _("Dangerous")
    elif score >= 40:
        return _("Caution")
    elif score >= 20:
        return _("Normal")
    else:
        return _("Healthy")

def risk_color(value, inverted=False):
    """
    Retorna a cor baseada no valor para barras de risco e resiliência.
    Se 'inverted' for True, inverte as cores (valores mais altos representam menos risco).
    """
    value = int(value)
    colors = {
        1: 'color-risk-1',
        2: 'color-risk-2',
        3: 'color-risk-3',
        4: 'color-risk-4',
        5: 'color-risk-5'
    }
    if inverted:
        return colors[6 - value]  # Inverte as cores
    return colors[value]

@register.filter
def int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0  # Retorna 0 se a conversão falhar
    

@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr, False)