"""
Sentinel Systems - User Sync Service

This service allows Sentinel apps to share user accounts.
When a user tries to login to App B after registering on App A,
this service automatically syncs their account.

Configuration:
- Set SENTINEL_APPS in .env as comma-separated URLs
- Example: SENTINEL_APPS=http://localhost:5001,http://localhost:5002,http://localhost:5003
"""

import requests
import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SentinelUserSync:
    """Handles user synchronization across Sentinel System apps"""
    
    def __init__(self, app_urls: List[str], current_app_url: str):
        """
        Initialize the sync service.
        
        Args:
            app_urls: List of URLs for all Sentinel apps
            current_app_url: URL of the current app (to exclude from sync)
        """
        self.app_urls = [url for url in app_urls if url != current_app_url]
        self.timeout = 5  # seconds
    
    def find_user_in_apps(self, identifier: str) -> Optional[Dict]:
        """
        Search for a user across all Sentinel apps.
        
        Args:
            identifier: Username or email to search for
            
        Returns:
            User data dict if found, None otherwise
        """
        for app_url in self.app_urls:
            try:
                response = requests.get(
                    f"{app_url}/api/sentinel/user-lookup",
                    params={"identifier": identifier},
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    logger.info(f"Found user {identifier} in app: {app_url}")
                    return user_data
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to connect to {app_url}: {str(e)}")
                continue
        
        logger.info(f"User {identifier} not found in any Sentinel app")
        return None
    
    def sync_user_to_local(self, user_data: Dict, db_session, User):
        """
        Create a local copy of a user from another Sentinel app.
        
        Args:
            user_data: User information from another app
            db_session: SQLAlchemy database session
            User: User model class
            
        Returns:
            Created user object
        """
        try:
            # Check if user already exists locally
            existing = User.query.filter(
                (User.username == user_data['username']) | 
                (User.email == user_data['email'])
            ).first()
            
            if existing:
                logger.info(f"User {user_data['username']} already exists locally")
                return existing
            
            # Create new user with synced data
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],  # Already hashed
                is_verified=user_data.get('is_verified', True),  # Trust verified status
                verification_token=None,  # Don't copy tokens
                token_expiration=None
            )
            
            db_session.add(new_user)
            db_session.commit()
            
            logger.info(f"Successfully synced user {user_data['username']} to local database")
            return new_user
            
        except Exception as e:
            db_session.rollback()
            logger.error(f"Failed to sync user {user_data.get('username')}: {str(e)}")
            raise
    
    def auto_sync_on_login(self, identifier: str, db_session, User) -> Optional[object]:
        """
        Automatically sync a user from another app when they try to login.
        This is called when a login attempt fails locally.
        
        Args:
            identifier: Username or email attempting to login
            db_session: SQLAlchemy database session
            User: User model class
            
        Returns:
            User object if sync successful, None otherwise
        """
        # Try to find user in other Sentinel apps
        user_data = self.find_user_in_apps(identifier)
        
        if not user_data:
            return None
        
        # Sync user to local database
        try:
            return self.sync_user_to_local(user_data, db_session, User)
        except Exception as e:
            logger.error(f"Auto-sync failed for {identifier}: {str(e)}")
            return None


def get_sync_service(config) -> Optional[SentinelUserSync]:
    """
    Create a SentinelUserSync instance from Flask config.
    
    Args:
        config: Flask app config
        
    Returns:
        SentinelUserSync instance or None if not configured
    """
    sentinel_apps = config.get('SENTINEL_APPS', '')
    current_app_url = config.get('CURRENT_APP_URL', '')
    
    if not sentinel_apps or not current_app_url:
        logger.info("Sentinel user sync not configured (SENTINEL_APPS or CURRENT_APP_URL missing)")
        return None
    
    app_urls = [url.strip() for url in sentinel_apps.split(',') if url.strip()]
    
    if not app_urls:
        logger.warning("SENTINEL_APPS is empty, user sync disabled")
        return None
    
    return SentinelUserSync(app_urls, current_app_url)
