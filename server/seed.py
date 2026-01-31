"""
Seed script: creates initial admin user and sample parties for development.
Run with: python -m seed
"""

import asyncio

from sqlalchemy import select

from app.core.auth import hash_password
from app.core.config import settings
from app.core.database import async_session, init_db
from app.models.party import Party, PartyUser, PartyStatus, UserRole
from app.services.encryption import encrypt_string


NZ_PARTIES = [
    ("New Zealand Labour Party", "Labour"),
    ("New Zealand National Party", "National"),
    ("Green Party of Aotearoa New Zealand", "Greens"),
    ("ACT New Zealand", "ACT"),
    ("New Zealand First", "NZ First"),
    ("Te Pāti Māori", "Te Pāti Māori"),
    ("The Opportunities Party", "TOP"),
]


async def seed():
    await init_db()

    async with async_session() as db:
        # Check if already seeded
        result = await db.execute(select(Party).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded. Skipping.")
            return

        # Create parties
        parties = []
        for name, short_name in NZ_PARTIES:
            party = Party(
                name=name,
                short_name=short_name,
                status=PartyStatus.ACTIVE,
                contact_email_encrypted=encrypt_string(
                    f"admin@{short_name.lower().replace(' ', '')}.org.nz"
                ),
            )
            db.add(party)
            parties.append(party)

        await db.flush()

        # Create an admin user for each party
        for party in parties:
            username = f"admin_{party.short_name.lower().replace(' ', '_')}"
            user = PartyUser(
                party_id=party.id,
                username=username,
                email_encrypted=encrypt_string(f"{username}@example.com"),
                hashed_password=hash_password("changeme123"),
                role=UserRole.ADMIN,
            )
            db.add(user)
            print(f"  Created: {username} / changeme123 (party: {party.short_name})")

        # Create a system admin (not tied to a specific party -- uses first party)
        system_admin = PartyUser(
            party_id=parties[0].id,
            username="sysadmin",
            email_encrypted=encrypt_string("sysadmin@verify.nz"),
            hashed_password=hash_password("admin_changeme"),
            role=UserRole.ADMIN,
        )
        db.add(system_admin)
        print("  Created: sysadmin / admin_changeme (system admin)")

        await db.commit()
        print(f"\nSeeded {len(parties)} parties with admin accounts.")
        print("NOTE: Change all passwords before any non-development use!")


if __name__ == "__main__":
    asyncio.run(seed())
