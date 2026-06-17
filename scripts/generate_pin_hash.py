"""
generate_pin_hash.py - TITAN Wave 1
Utility to generate bcrypt hash for the admin PIN.
"""
import bcrypt
import getpass
import sys

def generate():
    print("=== TITAN PIN HASH GENERATOR ===")
    pin = getpass.getpass("Enter 6-digit Admin PIN: ")
    
    if len(pin) != 6 or not pin.isdigit():
        print("Error: PIN must be exactly 6 digits.")
        sys.exit(1)
        
    confirm = getpass.getpass("Confirm Admin PIN: ")
    if pin != confirm:
        print("Error: PINs do not match.")
        sys.exit(1)
        
    hashed = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
    
    print("\\n=== TITAN ADMIN PIN HASH ===")
    print(hashed)
    print("=== COPY EVERYTHING ABOVE FROM $2b$ ===\\n")
    print("Paste this value into your .env file as ADMIN_PIN_HASH")

if __name__ == "__main__":
    generate()
