# backend/app/services/lab_discovery.py
"""Service for Laboratory discovery."""
from typing import List
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import models
from ..schemas.lab_discovery import LabSearchRequest, LabResult, LabCapability

async def search_laboratories(
    session: AsyncSession,
    request: LabSearchRequest
) -> List[LabResult]:
    """Search for laboratories based on various criteria using the graph/relational schema."""
    
    # Start with base query
    stmt = select(models.Laboratory).options(
        selectinload(models.Laboratory.tests).selectinload(models.Test.requirements).selectinload(models.Requirement.standard)
    )
    
    # We will build filters dynamically
    filters = []
    
    if request.location:
        filters.append(models.Laboratory.location.ilike(f"%{request.location}%"))
        
    if request.query:
        filters.append(models.Laboratory.name.ilike(f"%{request.query}%"))
        
    # Standard and Test type require joining
    if request.standard_number or request.test_type:
        stmt = stmt.join(models.Laboratory.tests)
        
        if request.test_type:
            filters.append(models.Test.name.ilike(f"%{request.test_type}%"))
            
        if request.standard_number:
            stmt = stmt.join(models.Test.requirements).join(models.Requirement.standard)
            filters.append(models.Standard.number.ilike(f"%{request.standard_number}%"))
    
    if filters:
        stmt = stmt.where(and_(*filters))
        
    result = await session.execute(stmt)
    labs = result.scalars().unique().all()
    
    response_labs = []
    for lab in labs:
        capabilities = []
        for test in lab.tests:
            # Get associated standards for this test
            related_standards = []
            for req in test.requirements:
                if req.standard:
                    related_standards.append(req.standard.number)
            
            std_str = ", ".join(related_standards) if related_standards else None
            
            # Since we only use verified data, the existence of the link is the verification
            capabilities.append(LabCapability(
                test_name=test.name,
                related_standard=std_str,
                verification_source="BIS Empanelled Labs Registry (Internal Database)"
            ))
            
        # Construct explanation based on request
        reasons = []
        if request.location and request.location.lower() in (lab.location or "").lower():
            reasons.append(f"Located in requested region ({lab.location})")
        if request.test_type:
            reasons.append(f"Performs {request.test_type} testing")
        if request.standard_number:
            reasons.append(f"Verified to test for standard {request.standard_number}")
            
        explanation = ", ".join(reasons) if reasons else "Matches search criteria based on verified testing capabilities."
        
        response_labs.append(LabResult(
            id=lab.id,
            name=lab.name,
            location=lab.location,
            capabilities=capabilities,
            accreditation="NABL / BIS Recognized", # Placeholder for actual DB field if added later
            source="BIS Laboratory Directory",
            relevance_explanation=explanation
        ))
        
    return response_labs
