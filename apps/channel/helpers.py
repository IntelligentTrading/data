from settings import SOURCE_CHOICES, COUNTER_CURRENCY_CHOICES



def source_code_from_name(name):
    "return 0 for poloniex"
    name = name.lower()
    return next((source_code for source_code, source_name in SOURCE_CHOICES if source_name==name), None)

def source_name_from_code(code):
    "return poloniex for 0"
    return next((source_name for source_code, source_name in SOURCE_CHOICES if source_code==code), None)

def counter_currency_code_from_name(name):
    name = name.upper()
    return next((cc_code for cc_code, cc_name in COUNTER_CURRENCY_CHOICES if cc_name==name), None)