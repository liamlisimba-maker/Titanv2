import bcrypt

pin = "474923"
h = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
print("=== TITAN ADMIN PIN HASH ===")
print(h)
print("=== COPY EVERYTHING ABOVE FROM $2b$ ===")
