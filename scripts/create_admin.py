import getpass
import sys
from pathlib import Path

# Let this script import the app's code
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from database import Base, engine, session  # noqa: E402
from models import category, supplier, product, user, customer, sale, sale_item, payment, receipt  # noqa: E402,F401  (registers all tables)
from models.user import User  # noqa: E402
from core.security import hash_password  # noqa: E402


def main():
    Base.metadata.create_all(bind=engine)  # makes the tables in pos_db if they don't exist yet

    username = input("Admin username: ").strip()
    full_name = input("Full name: ").strip()
    password = getpass.getpass("Password (min 12 characters, hidden while typing): ")  # never shown on screen
    if len(password) < 12:
        sys.exit("Password too short. Use at least 12 characters.")
    if password != getpass.getpass("Repeat password: "):
        sys.exit("Passwords do not match.")

    db = session()
    try:
        if db.query(User).filter(User.username == username).first():
            sys.exit("That username already exists.")
        db.add(User(
            full_name=full_name,
            username=username,
            password_hash=hash_password(password),  # only the hash is stored, never the password
            role="Admin",
            is_active=True,
        ))
        db.commit()
        print(f"Admin '{username}' created.")
    finally:
        db.close()


if __name__ == "__main__":
    main()