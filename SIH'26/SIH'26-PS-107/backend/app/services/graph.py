# backend/app/services/graph.py
"""GraphService provides high‑level graph‑style lookups over the relational
schema. It abstracts the underlying PostgreSQL tables so that a future Neo4j
implementation can be swapped in without changing callers.
All methods return lists of ORM objects; the calling router will transform
them into the API response models.
"""
import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models

logger = logging.getLogger(__name__)

class GraphService:
    """Service layer for structured BIS relationship reasoning.
    The methods are deliberately simple – they perform straightforward joins
    based on the foreign‑key / association tables defined in ``models``.
    """

    @staticmethod
    async def find_standards_for_product(session: AsyncSession, product_id: int) -> List[models.Standard]:
        stmt = select(models.Standard).join(models.product_standard_association).join(models.Product).where(models.Product.id == product_id)
        result = await session.execute(stmt)
        return result.scalars().unique().all()

    @staticmethod
    async def find_requirements_for_standard(session: AsyncSession, standard_id: int) -> List[models.Requirement]:
        stmt = select(models.Requirement).where(models.Requirement.standard_id == standard_id)
        result = await session.execute(stmt)
        return result.scalars().unique().all()

    @staticmethod
    async def find_schemes_for_product(session: AsyncSession, product_id: int) -> List[models.CertificationScheme]:
        stmt = (
            select(models.CertificationScheme)
            .join(models.product_scheme_association)
            .join(models.Product)
            .where(models.Product.id == product_id)
        )
        result = await session.execute(stmt)
        return result.scalars().unique().all()

    @staticmethod
    async def find_tests_for_requirement(session: AsyncSession, requirement_id: int) -> List[models.Test]:
        stmt = (
            select(models.Test)
            .join(models.requirement_test_association)
            .join(models.Requirement)
            .where(models.Requirement.id == requirement_id)
        )
        result = await session.execute(stmt)
        return result.scalars().unique().all()

    @staticmethod
    async def find_labs_for_test(session: AsyncSession, test_id: int) -> List[models.Laboratory]:
        stmt = (
            select(models.Laboratory)
            .join(models.test_lab_association)
            .join(models.Test)
            .where(models.Test.id == test_id)
        )
        result = await session.execute(stmt)
        return result.scalars().unique().all()

    @staticmethod
    async def find_related_standards(session: AsyncSession, standard_id: int) -> List[models.Standard]:
        # Related standards are linked via clause_related_standard association.
        # We find any clauses of the given standard, then any standards linked to
        # those clauses.
        stmt = (
            select(models.Standard)
            .join(models.clause_related_standard)
            .join(models.StandardClause)
            .where(models.StandardClause.standard_id == standard_id)
        )
        result = await session.execute(stmt)
        # Remove the original standard from results if present.
        related = [s for s in result.scalars().unique().all() if s.id != standard_id]
        return related
