
def is_float(value: str):
    try:
        float(value)
        return True
    except ValueError:
        return False


def starts_with_digit(name: str):
    return name[0].isdigit()


def starts_with_lower_case(name: str):
    return name[0].islower()


def starts_with_upper_case(name: str):
    return name[0].isupper()


def starts_with_underscore(name: str):
    return name[0] == '_'


def is_surrounded_by_single_quotes(name: str):
    quote_char = "'"
    return len(name) >= 3 and name[0] == quote_char and name[-1] == quote_char and quote_char not in name[1:-1]


def is_valid_variable(name: str):
    if len(name) == 0:
        return False

    return (starts_with_upper_case(name)
            or starts_with_underscore(name)
            )


def is_valid_constant(name: str):
    if len(name) == 0:
        return False

    return (starts_with_digit(name)
            or starts_with_lower_case(name)
            or is_float(name)
            or is_surrounded_by_single_quotes(name)
            )