"""WHOIS lookup service for domain information."""
import logging
from datetime import datetime
from typing import Dict, Optional, Any
import whois
from whois.parser import PywhoisError

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.config import settings
from ..crud import crud_domain
from ..models.domain import DomainStatus
from ..schemas.domain import DomainCreate, DomainUpdate

logger = logging.getLogger(__name__)

class WHOISService:
    """Service for performing WHOIS lookups and processing results."""
    
    @staticmethod
    def _parse_whois_data(whois_data: Dict) -> Dict[str, Any]:
        """Parse raw WHOIS data into a structured format."""
        return {
            "domain_name": whois_data.get("domain_name"),
            "registrar": whois_data.get("registrar"),
            "whois_server": whois_data.get("whois_server"),
            "referral_url": whois_data.get("referral_url"),
            "updated_date": whois_data.get("updated_date"),
            "creation_date": whois_data.get("creation_date"),
            "expiration_date": whois_data.get("expiration_date"),
            "name_servers": whois_data.get("name_servers", []),
            "status": whois_data.get("status"),
            "emails": whois_data.get("emails", []),
            "dnssec": whois_data.get("dnssec"),
            "name": whois_data.get("name"),
            "org": whois_data.get("org"),
            "address": whois_data.get("address"),
            "city": whois_data.get("city"),
            "state": whois_data.get("state"),
            "zipcode": whois_data.get("zipcode"),
            "country": whois_data.get("country"),
        }
    
    @staticmethod
    def _determine_domain_status(whois_data: Dict) -> DomainStatus:
        """
        Determine the status of a domain based on WHOIS data.
        Handles TLD-specific status messages and common patterns.
        """
        domain_name = whois_data.get("domain_name", "").lower()
        if not domain_name:
            return DomainStatus.UNKNOWN
            
        # Convert status to list if it's not already
        statuses = whois_data.get("status", [])
        if not isinstance(statuses, list):
            statuses = [statuses] if statuses else []
            
        status_lower = [str(s).lower() for s in statuses if s]
        whois_str = str(whois_data).lower()
        
        # TLD-specific handling
        if domain_name.endswith(".ng"):
            # .ng domains return "Not found" when available
            if "not found" in whois_str:
                return DomainStatus.AVAILABLE
            return DomainStatus.REGISTERED
            
        # Common availability indicators across TLDs
        availability_indicators = [
            "no match", 
            "no data found", 
            "not found",
            "no entries found",
            "no object found",
            "no such domain",
            "domain not found"
        ]
        
        if any(indicator in whois_str for indicator in availability_indicators):
            return DomainStatus.AVAILABLE
            
        # Check for registered domain indicators
        registered_indicators = [
            "clientdeleteprohibited", 
            "clienttransferprohibited",
            "clientupdateprohibited",
            "serverdeleteprohibited",
            "servertransferprohibited",
            "serverupdateprohibited",
            "active",
            "registered",
            "ok",
            "paid-till"
        ]
        
        # If we have any registered indicators or statuses, domain is registered
        if any(indicator in status_lower for indicator in registered_indicators):
            return DomainStatus.REGISTERED
            
        # Check expiration date if available
        if whois_data.get("expiration_date"):
            exp_date = whois_data.get("expiration_date")
            if isinstance(exp_date, list):
                exp_date = exp_date[0] if exp_date else None
                
            if exp_date and isinstance(exp_date, datetime) and exp_date < datetime.now():
                return DomainStatus.AVAILABLE
                
        # If we have a creation date but no explicit status, assume registered
        if whois_data.get("creation_date"):
            return DomainStatus.REGISTERED
            
        # If we have name servers, domain is likely registered
        if whois_data.get("name_servers"):
            return DomainStatus.REGISTERED
            
        # Default to unknown if we can't determine status
        return DomainStatus.UNKNOWN
    
    @classmethod
    def lookup_domain(cls, domain_name: str) -> Dict[str, Any]:
        """
        Perform a WHOIS lookup for a domain.
        
        Args:
            domain_name: The domain name to look up
            
        Returns:
            Dict containing the parsed WHOIS data
            
        Raises:
            HTTPException: If the WHOIS lookup fails
        """
        try:
            logger.info(f"Performing WHOIS lookup for domain: {domain_name}")
            whois_data = whois.whois(domain_name)
            parsed_data = cls._parse_whois_data(whois_data)
            parsed_data["status"] = cls._determine_domain_status(whois_data)
            return parsed_data
            
        except PywhoisError as e:
            if "No match" in str(e):
                return {
                    "domain_name": domain_name,
                    "status": DomainStatus.AVAILABLE,
                    "is_available": True
                }
            logger.error(f"WHOIS lookup failed for {domain_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"WHOIS lookup failed: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during WHOIS lookup for {domain_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during WHOIS lookup"
            )
    
    @classmethod
    def check_domain_availability(cls, domain_name: str) -> Dict[str, Any]:
        """
        Check if a domain is available.
        
        Args:
            domain_name: The domain name to check
            
        Returns:
            Dict containing availability information
        """
        try:
            data = cls.lookup_domain(domain_name)
            is_available = data.get("status") == DomainStatus.AVAILABLE
            return {
                "domain": domain_name,
                "is_available": is_available,
                "status": data.get("status"),
                "whois_data": data if not is_available else None
            }
        except Exception as e:
            logger.error(f"Error checking domain availability for {domain_name}: {str(e)}")
            return {
                "domain": domain_name,
                "is_available": False,
                "status": DomainStatus.UNKNOWN,
                "error": str(e)
            }
    
    @classmethod
    def update_domain_from_whois(
        cls, 
        db: Session, 
        domain_name: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update domain information from WHOIS and save to database.
        
        Args:
            db: Database session
            domain_name: Domain name to update
            user_id: Optional user ID for tracking
            
        Returns:
            Updated domain information
        """
        try:
            # Get current domain info from database if it exists
            db_domain = crud_domain.domain.get_by_name(db, name=domain_name)
            
            # Perform WHOIS lookup
            whois_data = cls.lookup_domain(domain_name)
            
            # Prepare domain data for create/update
            domain_data = {
                "name": domain_name,
                "tld": domain_name.split('.')[-1],
                "tld_type": "gtld",  # This should be determined from a TLD database
                "status": whois_data.get("status", DomainStatus.UNKNOWN),
                "is_available": whois_data.get("is_available", False),
                "whois_data": whois_data,
                "whois_last_updated": datetime.utcnow(),
            }
            
            # Create or update domain in database
            if db_domain:
                domain = crud_domain.domain.update(
                    db, 
                    db_obj=db_domain, 
                    obj_in=DomainUpdate(**domain_data)
                )
            else:
                domain = crud_domain.domain.create(
                    db, 
                    obj_in=DomainCreate(**domain_data)
                )
            
            return {
                "domain": domain.name,
                "status": domain.status,
                "is_available": domain.is_available,
                "whois_last_updated": domain.whois_last_updated,
            }
            
        except Exception as e:
            logger.error(f"Error updating domain {domain_name} from WHOIS: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update domain information: {str(e)}"
            )

# Create singleton instance
whois_service = WHOISService()
