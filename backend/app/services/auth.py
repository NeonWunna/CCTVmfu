"""
Authentication Service
Service for handling Google OAuth and user management.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.jwt import create_access_token


# Initialize OAuth
config = Config(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
})

oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: Session):
        """Initialize auth service with database session."""
        self.db = db

    async def get_google_oauth_url(self, redirect_uri: str) -> str:
        """
        Generate Google OAuth authorization URL.

        Args:
            redirect_uri: Callback URL for OAuth flow

        Returns:
            Authorization URL string
        """
        # This is handled by authlib, return redirect_uri for reference
        return settings.GOOGLE_REDIRECT_URI

    def get_or_create_user(self, google_user: Dict[str, Any]) -> User:
        """
        Find existing user or create new one from Google user info.

        Args:
            google_user: User information from Google OAuth

        Returns:
            User model instance
        """
        google_id = google_user.get("sub")
        email = google_user.get("email")
        name = google_user.get("name", email)
        picture = google_user.get("picture")

        # Determine if this email is a superadmin
        superadmin_emails = [e.strip() for e in settings.SUPERADMIN_EMAILS.split(",") if e.strip()]
        is_superadmin_email = email in superadmin_emails

        # Try to find existing user by Google ID
        user = self.db.query(User).filter(User.google_id == google_id).first()

        if user:
            # Update user info in case it changed
            user.name = name
            user.email = email
            user.picture = picture
            # Only force-apply superadmin role if email is in the superadmin list.
            # Otherwise, preserve the manually-assigned role (e.g., 'admin')
            # so that promotions done via Admin Panel survive across logins.
            if is_superadmin_email:
                user.role = "superadmin"
            # else: keep existing role unchanged
            self.db.commit()
            self.db.refresh(user)
        else:
            # Create new user — default is 'user', or 'superadmin' if in list
            new_role = "superadmin" if is_superadmin_email else "user"
            user = User(
                google_id=google_id,
                email=email,
                name=name,
                picture=picture,
                role=new_role
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        return user

    def create_user_token(self, user: User) -> str:
        """
        Generate JWT token for user.

        Args:
            user: User model instance

        Returns:
            JWT token string
        """
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
        access_token = create_access_token(data=token_data)
        return access_token

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User model instance or None
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User model instance or None
        """
        return self.db.query(User).filter(User.email == email).first()
