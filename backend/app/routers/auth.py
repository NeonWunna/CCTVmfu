"""
Authentication Router
API endpoints for authentication operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth import AuthService, oauth
from app.schemas.user import UserResponse, TokenResponse
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/auth/google")
async def google_login(request: Request):
    """
    Initiate Google OAuth flow.
    Redirects user to Google consent screen.
    """
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback.
    Exchange authorization code for user info and create JWT token.
    """
    try:
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)

        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")

        # Create or update user in database
        auth_service = AuthService(db)
        user = auth_service.get_or_create_user(user_info)

        # Generate JWT token
        access_token = auth_service.create_user_token(user)

        # Redirect to frontend with token
        # Frontend will handle storing the token and redirecting to dashboard
        frontend_url = f"http://localhost:5173/login?token={access_token}"

        return RedirectResponse(url=frontend_url)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Requires: Valid JWT token in Authorization header
    """
    return current_user


@router.post("/auth/logout")
async def logout():
    """
    Logout endpoint.

    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token from storage. This endpoint is here for
    consistency and future enhancements (e.g., token blacklisting).
    """
    return {"message": "Logged out successfully"}


@router.get("/auth/status")
async def auth_status():
    """
    Check if authentication system is configured properly.
    """
    from app.core.config import settings

    has_google_client_id = bool(settings.GOOGLE_CLIENT_ID and
                                settings.GOOGLE_CLIENT_ID != "your-client-id-here.apps.googleusercontent.com")
    has_google_client_secret = bool(settings.GOOGLE_CLIENT_SECRET and
                                   settings.GOOGLE_CLIENT_SECRET != "your-client-secret-here")
    has_jwt_secret = bool(settings.JWT_SECRET_KEY and
                         "generate" not in settings.JWT_SECRET_KEY.lower())

    return {
        "google_oauth_configured": has_google_client_id and has_google_client_secret,
        "jwt_configured": has_jwt_secret,
        "ready": has_google_client_id and has_google_client_secret and has_jwt_secret,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }
