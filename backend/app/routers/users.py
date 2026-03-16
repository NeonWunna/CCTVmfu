"""
Users Router
API endpoints for user management (superadmin only).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.dependencies import require_superadmin

router = APIRouter(prefix="/users")


@router.get("", response_model=List[UserResponse])
def list_users(
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    """
    List all users in the system.
    Superadmin only.
    """
    return db.query(User).order_by(User.created_at.desc()).all()


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    """
    Delete a user by ID.
    Superadmin only. Cannot delete yourself.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()
    return {"message": f"User {user.email} deleted successfully"}


@router.put("/{user_id}/role")
def update_user_role(
    user_id: int,
    role_data: dict,
    current_user: User = Depends(require_superadmin),
    db: Session = Depends(get_db)
):
    """
    Update a user's role.
    Superadmin only. Valid roles: 'user', 'superadmin'.
    """
    new_role = role_data.get("role")
    if new_role not in ("user", "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'user' or 'superadmin'"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.role = new_role
    db.commit()
    db.refresh(user)
    return {"message": f"Role updated to '{new_role}' for {user.email}"}
