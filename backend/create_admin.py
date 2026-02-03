"""
Create Admin User Script
=========================
Run this script to create an initial admin user for the trading bot system.

Usage:
    python create_admin.py
"""

from core.database import user_db
from core.auth import get_password_hash
import sys


def create_admin_user():
    """Create an admin user interactively"""

    print("=" * 60)
    print("Create Admin User")
    print("=" * 60)

    # Get username
    while True:
        username = input("Username: ").strip()
        if not username:
            print("❌ Username cannot be empty")
            continue
        if user_db.get_user_by_username(username):
            print("❌ Username already exists")
            continue
        break

    # Get email
    while True:
        email = input("Email: ").strip()
        if not email:
            print("❌ Email cannot be empty")
            continue
        if "@" not in email:
            print("❌ Invalid email format")
            continue
        if user_db.get_user_by_email(email):
            print("❌ Email already exists")
            continue
        break

    # Get password
    while True:
        password = input("Password (min 6 characters): ").strip()
        if len(password) < 6:
            print("❌ Password must be at least 6 characters")
            continue
        password_confirm = input("Confirm password: ").strip()
        if password != password_confirm:
            print("❌ Passwords do not match")
            continue
        break

    # Get full name (optional)
    full_name = input("Full Name (optional): ").strip()
    if not full_name:
        full_name = None

    try:
        # Create admin user
        hashed_password = get_password_hash(password)
        user = user_db.create_user(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_admin=True
        )

        print("\n" + "=" * 60)
        print("✅ Admin user created successfully!")
        print("=" * 60)
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Full Name: {user.get('full_name', 'N/A')}")
        print(f"Admin: Yes")
        print("=" * 60)
        print("\nYou can now login with these credentials.")

        return 0

    except Exception as e:
        print(f"\n❌ Error creating admin user: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(create_admin_user())
