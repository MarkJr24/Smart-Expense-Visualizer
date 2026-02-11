def is_valid_expense(date, category, amount):
    if not date or not category or amount <= 0:
        return False
    return True
