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
    ("Independent Candidates", "Independent"),
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

        # Create an Electoral Commission user (for EC dashboard)
        ec_user = PartyUser(
            party_id=parties[0].id,
            username="ec_admin",
            email_encrypted=encrypt_string("admin@elections.govt.nz"),
            hashed_password=hash_password("ec_changeme"),
            role=UserRole.ELECTORAL_COMMISSION,
        )
        db.add(ec_user)
        print("  Created: ec_admin / ec_changeme (Electoral Commission)")

        # Create a sample candidate in the Labour party
        candidate_user = PartyUser(
            party_id=parties[0].id,
            username="candidate_labour",
            email_encrypted=encrypt_string("candidate@labour.org.nz"),
            hashed_password=hash_password("candidate_changeme"),
            role=UserRole.CANDIDATE,
            promoter_statement="Authorised by J. Smith, 42 Queen St, Wellington",
        )
        db.add(candidate_user)
        print("  Created: candidate_labour / candidate_changeme (Candidate, Labour)")

        # Create a sample independent candidate
        independent_party = [p for p in parties if p.short_name == "Independent"][0]
        independent_user = PartyUser(
            party_id=independent_party.id,
            username="independent_jones",
            email_encrypted=encrypt_string("jones@independent.nz"),
            hashed_password=hash_password("indie_changeme"),
            role=UserRole.CANDIDATE,
            promoter_statement="Authorised by M. Jones, 10 Main Rd, Auckland",
        )
        db.add(independent_user)
        print("  Created: independent_jones / indie_changeme (Independent Candidate)")

        await db.commit()
        print(f"\nSeeded {len(parties)} parties with admin accounts.")
        print("NOTE: Change all passwords before any non-development use!")


if __name__ == "__main__":
    asyncio.run(seed())
