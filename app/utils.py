import string

ALPHABET = string.ascii_letters + string.digits

def encode_base62(num):
    base = len(ALPHABET)
    result = []

    while num:
        num, rem = divmod(num, base)
        result.append(ALPHABET[rem])

    return ''.join(reversed(result))