import random
import string

def generate_random_string(length=6) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def generate_temp_email() -> str:
    username = generate_random_string()
    domain = "1secmail.com"
    email_address = f"{username}@{domain}"
    return username, domain, email_address