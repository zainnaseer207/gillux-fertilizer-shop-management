"""
utils/permissions.py

Simple role check — is_admin() poore app mein reuse hoga jahan bhi
koi action sirf Admin ke liye restrict karni ho.
"""

def is_admin(user) -> bool:
    return bool(user and user.role and user.role.name == "Admin")