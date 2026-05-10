"""Privacy-first IP geolocation service.

History. Earlier iterations of this service called the free ip-api.com
HTTP endpoint to resolve a request's IP to a country and region for
aggregate stats. That call was a cross-border disclosure of personal
information under IPP 12 of the Privacy Act 2020, and it ran over
plain HTTP. It has been removed.

Current behaviour. The service NEVER sends the IP off the host. It
returns ``("Local", "NZ")`` for loopback and RFC 1918 addresses, and
``("Unknown", "XX")`` for everything else. Aggregate counts therefore
mostly fall into the "Unknown" bucket, which is the right default
until an in-process, NZ-resident offline geolocation database
(eg. MaxMind GeoLite2) is provisioned and a fresh privacy impact
assessment signs off on its use.

Re-enabling. Add a MaxMind GeoLite2 database, gate it on the
``settings.GEO_LOOKUP_ENABLED`` flag, and resolve in-process only.
Do not re-introduce the HTTP call.
"""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def _is_private_ip(ip: str) -> bool:
    if ip in ("127.0.0.1", "::1", "localhost"):
        return True
    return (
        ip.startswith("10.")
        or ip.startswith("192.168.")
        or ip.startswith("172.16.")
        or ip.startswith("172.17.")
        or ip.startswith("172.18.")
        or ip.startswith("172.19.")
        or ip.startswith("172.2")  # covers 172.20-172.29
        or ip.startswith("172.30.")
        or ip.startswith("172.31.")
        or ip.startswith("169.254.")  # link-local
    )


async def resolve_location(ip: str) -> tuple[str, str]:
    """Resolve an IP to (region, country_code) without leaving the host.

    The IP address is never logged, never stored, and never sent off
    the host. Only aggregate counts are persisted upstream of this call.
    """
    if not ip:
        return ("Unknown", "XX")

    if _is_private_ip(ip):
        return ("Local", "NZ")

    if not settings.GEO_LOOKUP_ENABLED:
        # The feature is dormant pending an offline NZ-resident database.
        # The IP is treated as unresolved so the aggregate "Unknown"
        # bucket grows but no cross-border disclosure occurs.
        return ("Unknown", "XX")

    # Future home of an in-process MaxMind GeoLite2 lookup. Until that
    # database is provisioned the feature is forced off above.
    logger.warning(
        "GEO_LOOKUP_ENABLED is true but no offline geolocation backend "
        "is installed; returning Unknown."
    )
    return ("Unknown", "XX")
