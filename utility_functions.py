# A function for determining whether a value is an accounting
def is_accounting_code(value):
    if value:
        try:
            parts = str(value).split('.')
            has_digit = any(part.isdigit() for part in parts)
            # Checking whether each part consists only of numbers or (if the length is less than 3) only of letters
            return has_digit and all(part.isdigit() or (len(part) < 3 and part.isalpha()) for part in parts)
        except TypeError:
            return False
    else:
        return False


# A function to check whether the account is a parent account
def is_parent(account, accounts):
    for acc in accounts:
        if acc.startswith(account + '.') and acc != account:
            return True
    return False

