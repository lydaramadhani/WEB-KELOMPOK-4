from django import template

register = template.Library()

@register.filter(name='rupiah')
def rupiah(value):
    """
    Format numeric value into Indonesian Rupiah string with dot thousand separator.
    Example: 250000 -> "250.000"
    """
    if value is None or value == '':
        return '0'
    try:
        val = int(round(float(value)))
        return f"{val:,}".replace(',', '.')
    except (ValueError, TypeError):
        return str(value)
