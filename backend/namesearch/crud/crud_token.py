"""CRUD operations for refresh tokens."""
from datetime import datetime
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from ..models.token import Token
from .base import CRUDBase
from ..schemas.token import TokenCreate, TokenUpdate


class CRUDToken(CRUDBase[Token, TokenCreate, TokenUpdate]):
    """CRUD operations for refresh tokens."""
    
    def get_by_token(self, db: Session, *, token: str) -> Optional[Token]:
        """Get a token by its value."""
        return db.query(Token).filter(Token.token == token).first()
    
    def get_active_tokens_for_user(
        self, db: Session, *, user_id: int
    ) -> list[Token]:
        """Get all active refresh tokens for a user."""
        return (
            db.query(Token)
            .filter(
                Token.user_id == user_id,
                Token.revoked.is_(False),
                Token.expires_at > datetime.utcnow()
            )
            .all()
        )
    
    def revoke_token(self, db: Session, *, token: str) -> Optional[Token]:
        """Revoke a refresh token."""
        db_token = self.get_by_token(db, token=token)
        if not db_token:
            return None
        db_token.revoked = True
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token
    
    def revoke_all_tokens_for_user(
        self, db: Session, *, user_id: int
    ) -> int:
        """Revoke all refresh tokens for a user."""
        result = (
            db.query(Token)
            .filter(
                Token.user_id == user_id,
                Token.revoked.is_(False)
            )
            .update({Token.revoked: True}, synchronize_session=False)
        )
        db.commit()
        return result
    
    def cleanup_expired_tokens(self, db: Session) -> int:
        """Remove expired refresh tokens from the database."""
        result = (
            db.query(Token)
            .filter(Token.expires_at < datetime.utcnow())
            .delete(synchronize_session=False)
        )
        db.commit()
        return result


# Create a singleton instance
token = CRUDToken(Token)
