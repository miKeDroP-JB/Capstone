#!/usr/bin/env python3
"""
LEAD SCRAPER - Multi-source lead generation
Scrapes Google Maps, Yelp, BBB, Yellow Pages, and more.

Love - Loyalty - Honor - Everybody Eats
"""

import asyncio
import aiohttp
import json
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import quote_plus, urljoin
import random

# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

class LeadSource(Enum):
    GOOGLE_MAPS = "google_maps"
    YELP = "yelp"
    BBB = "bbb"
    YELLOW_PAGES = "yellow_pages"
    HOMEADVISOR = "homeadvisor"
    ANGIES_LIST = "angies_list"
    THUMBTACK = "thumbtack"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    WEBSITE = "website"
    MANUAL = "manual"


class LeadQuality(Enum):
    HOT = "hot"          # High intent signals
    WARM = "warm"        # Some engagement
    COLD = "cold"        # No signals
    DEAD = "dead"        # Do not contact


@dataclass
class ContactInfo:
    """Contact information for a lead"""
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None


@dataclass
class Lead:
    """A sales lead"""
    id: str
    business_name: str
    industry: str
    contact: ContactInfo
    source: LeadSource
    quality: LeadQuality = LeadQuality.COLD

    # Enrichment data
    owner_name: Optional[str] = None
    employee_count: Optional[int] = None
    revenue_estimate: Optional[str] = None
    years_in_business: Optional[int] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None

    # Metadata
    scraped_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    # Tracking
    times_contacted: int = 0
    last_contacted: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "business_name": self.business_name,
            "industry": self.industry,
            "contact": {
                "phone": self.contact.phone,
                "email": self.contact.email,
                "website": self.contact.website,
                "address": self.contact.address,
                "city": self.contact.city,
                "state": self.contact.state,
                "zip_code": self.contact.zip_code,
            },
            "source": self.source.value,
            "quality": self.quality.value,
            "owner_name": self.owner_name,
            "rating": self.rating,
            "review_count": self.review_count,
            "scraped_at": self.scraped_at.isoformat(),
        }


@dataclass
class ScraperConfig:
    """Configuration for the lead scraper"""
    industry: str = "hvac"
    location: str = ""
    radius_miles: int = 50
    max_results: int = 100
    sources: List[LeadSource] = field(default_factory=lambda: [
        LeadSource.GOOGLE_MAPS,
        LeadSource.YELP,
        LeadSource.BBB,
    ])
    min_rating: float = 0.0
    max_rating: float = 5.0
    exclude_chains: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


# ═══════════════════════════════════════════════════════════════
# SCRAPER ENGINE
# ═══════════════════════════════════════════════════════════════

class LeadScraper:
    """
    Multi-source lead scraper.
    Finds businesses, extracts contact info, enriches data.
    """

    # Common HVAC-related search terms
    HVAC_KEYWORDS = [
        "hvac contractor",
        "hvac repair",
        "air conditioning repair",
        "heating repair",
        "furnace repair",
        "ac installation",
        "heating and cooling",
        "hvac service",
        "air conditioning contractor",
        "heating contractor",
    ]

    # Known chains to exclude
    CHAIN_NAMES = [
        "home depot", "lowes", "sears", "costco",
        "walmart", "best buy", "amazon",
    ]

    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.leads: Dict[str, Lead] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self._request_count = 0
        self._last_request = datetime.now()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": self.config.user_agent}
        )
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    def _generate_lead_id(self, business_name: str, phone: str = "") -> str:
        """Generate unique lead ID"""
        content = f"{business_name.lower()}{phone}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _is_chain(self, business_name: str) -> bool:
        """Check if business is a known chain"""
        name_lower = business_name.lower()
        return any(chain in name_lower for chain in self.CHAIN_NAMES)

    def _clean_phone(self, phone: str) -> Optional[str]:
        """Clean and validate phone number"""
        if not phone:
            return None
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return None

    async def _rate_limit(self):
        """Simple rate limiting"""
        self._request_count += 1
        if self._request_count % 10 == 0:
            await asyncio.sleep(random.uniform(1, 3))

    # ═══════════════════════════════════════════════════════════
    # GOOGLE MAPS SCRAPER
    # ═══════════════════════════════════════════════════════════

    async def scrape_google_maps(self, query: str, location: str) -> List[Lead]:
        """
        Scrape Google Maps for businesses.
        Uses the unofficial places data endpoint.
        """
        leads = []

        # Build search URL (using Google's internal API pattern)
        search_query = f"{query} near {location}"

        # Note: In production, you'd use:
        # 1. Google Places API (official, paid)
        # 2. SerpAPI (unofficial, paid)
        # 3. Custom Selenium/Playwright scraper

        # Simulated scrape structure for now
        # Replace with actual scraping logic

        print(f"  [Google Maps] Searching: {search_query}")

        # Placeholder - in production, implement actual scraping
        # This would use aiohttp to fetch and parse Google Maps results

        return leads

    # ═══════════════════════════════════════════════════════════
    # YELP SCRAPER
    # ═══════════════════════════════════════════════════════════

    async def scrape_yelp(self, query: str, location: str) -> List[Lead]:
        """
        Scrape Yelp for businesses.
        Extracts business info, ratings, contact details.
        """
        leads = []

        # Yelp search URL
        base_url = "https://www.yelp.com/search"
        params = {
            "find_desc": query,
            "find_loc": location,
        }

        print(f"  [Yelp] Searching: {query} in {location}")

        try:
            await self._rate_limit()

            if self.session:
                url = f"{base_url}?find_desc={quote_plus(query)}&find_loc={quote_plus(location)}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        leads = self._parse_yelp_results(html)
        except Exception as e:
            print(f"  [Yelp] Error: {e}")

        return leads

    def _parse_yelp_results(self, html: str) -> List[Lead]:
        """Parse Yelp search results HTML"""
        leads = []

        # Extract business data using regex patterns
        # In production, use BeautifulSoup or lxml

        # Business name pattern
        name_pattern = r'"name":"([^"]+)"'
        phone_pattern = r'"phone":"([^"]+)"'
        rating_pattern = r'"rating":(\d+\.?\d*)'
        review_pattern = r'"reviewCount":(\d+)'
        address_pattern = r'"addressLines":\["([^"]+)"'

        names = re.findall(name_pattern, html)
        phones = re.findall(phone_pattern, html)
        ratings = re.findall(rating_pattern, html)
        reviews = re.findall(review_pattern, html)

        for i, name in enumerate(names[:self.config.max_results]):
            if self.config.exclude_chains and self._is_chain(name):
                continue

            phone = self._clean_phone(phones[i]) if i < len(phones) else None
            rating = float(ratings[i]) if i < len(ratings) else None
            review_count = int(reviews[i]) if i < len(reviews) else None

            # Filter by rating
            if rating and (rating < self.config.min_rating or rating > self.config.max_rating):
                continue

            lead = Lead(
                id=self._generate_lead_id(name, phone or ""),
                business_name=name,
                industry=self.config.industry,
                contact=ContactInfo(phone=phone),
                source=LeadSource.YELP,
                rating=rating,
                review_count=review_count,
            )

            leads.append(lead)

        return leads

    # ═══════════════════════════════════════════════════════════
    # BBB SCRAPER
    # ═══════════════════════════════════════════════════════════

    async def scrape_bbb(self, query: str, location: str) -> List[Lead]:
        """
        Scrape Better Business Bureau for accredited businesses.
        BBB businesses tend to be higher quality leads.
        """
        leads = []

        print(f"  [BBB] Searching: {query} in {location}")

        # BBB search URL
        base_url = "https://www.bbb.org/search"

        try:
            await self._rate_limit()

            if self.session:
                url = f"{base_url}?find_country=USA&find_text={quote_plus(query)}&find_loc={quote_plus(location)}&find_type=Category"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        leads = self._parse_bbb_results(html)
        except Exception as e:
            print(f"  [BBB] Error: {e}")

        return leads

    def _parse_bbb_results(self, html: str) -> List[Lead]:
        """Parse BBB search results"""
        leads = []

        # BBB results parsing
        # BBB accredited businesses are higher quality

        name_pattern = r'data-business-name="([^"]+)"'
        phone_pattern = r'data-phone="([^"]+)"'
        rating_pattern = r'data-rating="([^"]+)"'

        names = re.findall(name_pattern, html)
        phones = re.findall(phone_pattern, html)
        ratings = re.findall(rating_pattern, html)

        for i, name in enumerate(names[:self.config.max_results]):
            if self.config.exclude_chains and self._is_chain(name):
                continue

            phone = self._clean_phone(phones[i]) if i < len(phones) else None

            lead = Lead(
                id=self._generate_lead_id(name, phone or ""),
                business_name=name,
                industry=self.config.industry,
                contact=ContactInfo(phone=phone),
                source=LeadSource.BBB,
                quality=LeadQuality.WARM,  # BBB businesses are warmer leads
                tags=["bbb_accredited"],
            )

            leads.append(lead)

        return leads

    # ═══════════════════════════════════════════════════════════
    # YELLOW PAGES SCRAPER
    # ═══════════════════════════════════════════════════════════

    async def scrape_yellow_pages(self, query: str, location: str) -> List[Lead]:
        """Scrape Yellow Pages directory"""
        leads = []

        print(f"  [Yellow Pages] Searching: {query} in {location}")

        base_url = "https://www.yellowpages.com/search"

        try:
            await self._rate_limit()

            if self.session:
                url = f"{base_url}?search_terms={quote_plus(query)}&geo_location_terms={quote_plus(location)}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        leads = self._parse_yp_results(html)
        except Exception as e:
            print(f"  [Yellow Pages] Error: {e}")

        return leads

    def _parse_yp_results(self, html: str) -> List[Lead]:
        """Parse Yellow Pages results"""
        leads = []

        # YP uses structured data
        name_pattern = r'class="business-name"[^>]*>([^<]+)<'
        phone_pattern = r'class="phones phone primary"[^>]*>([^<]+)<'

        names = re.findall(name_pattern, html)
        phones = re.findall(phone_pattern, html)

        for i, name in enumerate(names[:self.config.max_results]):
            if self.config.exclude_chains and self._is_chain(name):
                continue

            phone = self._clean_phone(phones[i]) if i < len(phones) else None

            lead = Lead(
                id=self._generate_lead_id(name, phone or ""),
                business_name=name,
                industry=self.config.industry,
                contact=ContactInfo(phone=phone),
                source=LeadSource.YELLOW_PAGES,
            )

            leads.append(lead)

        return leads

    # ═══════════════════════════════════════════════════════════
    # MAIN SCRAPE FUNCTION
    # ═══════════════════════════════════════════════════════════

    async def scrape(self, location: str = None) -> List[Lead]:
        """
        Run full scrape across all configured sources.
        Deduplicates and enriches leads.
        """
        location = location or self.config.location
        all_leads: Dict[str, Lead] = {}

        print(f"\n{'='*60}")
        print(f"  LEAD SCRAPER - {self.config.industry.upper()}")
        print(f"  Location: {location}")
        print(f"  Sources: {[s.value for s in self.config.sources]}")
        print(f"{'='*60}\n")

        async with self:
            for keyword in self.HVAC_KEYWORDS[:3]:  # Limit keywords for speed
                for source in self.config.sources:
                    try:
                        if source == LeadSource.GOOGLE_MAPS:
                            leads = await self.scrape_google_maps(keyword, location)
                        elif source == LeadSource.YELP:
                            leads = await self.scrape_yelp(keyword, location)
                        elif source == LeadSource.BBB:
                            leads = await self.scrape_bbb(keyword, location)
                        elif source == LeadSource.YELLOW_PAGES:
                            leads = await self.scrape_yellow_pages(keyword, location)
                        else:
                            leads = []

                        # Deduplicate by ID
                        for lead in leads:
                            if lead.id not in all_leads:
                                all_leads[lead.id] = lead
                            else:
                                # Merge data from multiple sources
                                existing = all_leads[lead.id]
                                if lead.rating and not existing.rating:
                                    existing.rating = lead.rating
                                if lead.contact.phone and not existing.contact.phone:
                                    existing.contact.phone = lead.contact.phone
                                existing.tags.extend(lead.tags)

                    except Exception as e:
                        print(f"  [!] Error scraping {source.value}: {e}")

        self.leads = all_leads

        print(f"\n{'='*60}")
        print(f"  SCRAPE COMPLETE: {len(all_leads)} unique leads")
        print(f"{'='*60}\n")

        return list(all_leads.values())

    def export_csv(self, filepath: str):
        """Export leads to CSV"""
        import csv

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID', 'Business Name', 'Phone', 'Email', 'Website',
                'Address', 'City', 'State', 'Zip', 'Source',
                'Quality', 'Rating', 'Reviews', 'Tags'
            ])

            for lead in self.leads.values():
                writer.writerow([
                    lead.id,
                    lead.business_name,
                    lead.contact.phone,
                    lead.contact.email,
                    lead.contact.website,
                    lead.contact.address,
                    lead.contact.city,
                    lead.contact.state,
                    lead.contact.zip_code,
                    lead.source.value,
                    lead.quality.value,
                    lead.rating,
                    lead.review_count,
                    ','.join(lead.tags),
                ])

    def export_json(self, filepath: str):
        """Export leads to JSON"""
        data = [lead.to_dict() for lead in self.leads.values()]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

async def main():
    """Demo the scraper"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                      LEAD SCRAPER                             ║
║                                                               ║
║   Multi-source lead generation for HVAC sales                 ║
║                                                               ║
║          Love  -  Loyalty  -  Honor  -  Everybody Eats        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    config = ScraperConfig(
        industry="hvac",
        location="Phoenix, AZ",
        max_results=50,
        sources=[
            LeadSource.YELP,
            LeadSource.BBB,
            LeadSource.YELLOW_PAGES,
        ],
    )

    scraper = LeadScraper(config)
    leads = await scraper.scrape()

    print("\nSample leads:")
    for lead in leads[:5]:
        print(f"  - {lead.business_name}: {lead.contact.phone} ({lead.source.value})")

    # Export
    scraper.export_json("leads.json")
    print(f"\nExported to leads.json")


if __name__ == "__main__":
    asyncio.run(main())
