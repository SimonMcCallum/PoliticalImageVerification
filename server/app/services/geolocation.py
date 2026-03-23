"""Privacy-first IP geolocation service.

Resolves IP addresses to region/country in memory only.
Only aggregated counts are persisted -- individual IPs are NEVER stored.

Uses the free ip-api.com service for the test environment.
For production, replace with MaxMind GeoLite2 offline database.
"""

import logging

import httpx

logger = logging.getLogger(__name__)

# In-memory cache to reduce API calls (IP -> (region, country))
_cache: dict[str, tuple[str, str]] = {}
_CACHE_MAX_SIZE = 1000


def _evict_cache() -> None:
    """Simple cache eviction: clear when too large."""
    global _cache
    if len(_cache) > _CACHE_MAX_SIZE:
        _cache = {}


async def resolve_location(ip: str) -> tuple[str, str]:
    """Resolve an IP address to (region, country_code).

    Returns ("Unknown", "XX") if resolution fails.
    The IP address is NOT stored or logged.
    """
    # Skip private/localhost IPs
    if ip in ("127.0.0.1", "::1", "localhost") or ip.startswith("192.168.") or ip.startswith("10."):
        return ("Local", "NZ")

    # Check cache
    if ip in _cache:
        return _cache[ip]

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            # ip-api.com free tier: 45 req/min, no API key needed
            resp = await client.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": "status,country,countryCode,regionName"},
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    country = data.get("countryCode", "XX")
                    # For NZ, use region name; for others, use country name
                    if country == "NZ":
                        region = data.get("regionName", "Unknown")
                    else:
                        region = data.get("country", "Unknown")

                    result = (region, country)
                    _evict_cache()
                    _cache[ip] = result
                    return result
    except Exception:
        logger.debug("Geolocation lookup failed for request (IP not logged)")

    return ("Unknown", "XX")
