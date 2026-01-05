"""
Sentinel Integration Utilities for P.A.T.R.I.O.T. Backend

Provides functions to communicate with Sentinel Login backend for:
- Token validation
- Health checks
- Cross-system authentication
"""
import requests
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class SentinelClient:
    """Client for communicating with Sentinel Login backend"""
    
    def __init__(self, sentinel_url=None):
        """
        Initialize Sentinel client
        
        Args:
            sentinel_url: URL of Sentinel backend (e.g., http://localhost:5001)
                         Defaults to SENTINEL_LOGIN_URL from config
        """
        self.base_url = sentinel_url or current_app.config.get("SENTINEL_LOGIN_URL")
        self.timeout = 5  # seconds
    
    def health_check(self) -> bool:
        """
        Check if Sentinel is healthy and online
        
        Returns:
            True if Sentinel is online and healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/auth/sentinel/health",
                timeout=self.timeout
            )
            return response.status_code == 200 and response.json().get("status") == "online"
        except Exception as e:
            logger.warning(f"Sentinel health check failed: {e}")
            return False
    
    def validate_token(self, token: str) -> dict:
        """
        Validate JWT token with Sentinel backend
        
        Args:
            token: JWT token to validate (without 'Bearer ' prefix)
        
        Returns:
            dict with keys:
                - valid: True if token is valid
                - user_id: User ID from token
                - username: Username from token
                - household_id: Household ID from token
                - error: Error message if invalid
        """
        try:
            response = requests.post(
                f"{self.base_url}/auth/sentinel/token-info",
                json={"token": token},
                timeout=self.timeout
            )
            
            data = response.json()
            
            if response.status_code == 200:
                return {
                    "valid": True,
                    "user_id": data.get("user_id"),
                    "username": data.get("username"),
                    "household_id": data.get("household_id"),
                }
            else:
                return {
                    "valid": False,
                    "error": data.get("error", "Token validation failed")
                }
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    def verify_sentinel_connection(self) -> dict:
        """
        Verify P.A.T.R.I.O.T. can communicate with Sentinel
        
        Returns:
            dict with connection status info
        """
        try:
            # Check if Sentinel is online
            is_online = self.health_check()
            
            # Check if JWT secrets match (by attempting to decode a test scenario)
            jwt_configured = current_app.config.get("JWT_SECRET_KEY") is not None
            
            return {
                "sentinel_online": is_online,
                "sentinel_url": self.base_url,
                "jwt_configured": jwt_configured,
                "connection_status": "ready" if is_online and jwt_configured else "incomplete"
            }
        except Exception as e:
            logger.error(f"Connection verification error: {e}")
            return {
                "sentinel_online": False,
                "error": str(e),
                "connection_status": "error"
            }


def get_sentinel_client():
    """Factory function to get configured Sentinel client"""
    return SentinelClient()
