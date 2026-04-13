from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.db.models import User, UserRole


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def create_user(db: Session, email: str, password: str, role: UserRole = UserRole.user) -> User:
    if not isinstance(role, UserRole):
        role = UserRole(role)
    user = User(email=email.lower(), password_hash=get_password_hash(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def ensure_default_admin(db: Session, email: str, password: str) -> None:
    if get_user_by_email(db, email):
        return
    create_user(db, email=email, password=password, role=UserRole.admin)

