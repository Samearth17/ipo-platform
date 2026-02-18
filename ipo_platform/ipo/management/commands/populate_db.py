from django.core.management.base import BaseCommand
from django.utils import timezone
from ipo.models import IPO
from datetime import timedelta
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populates the database with realistic IPO data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Cleaning existing IPO data...')
        IPO.objects.all().delete()

        # REAL IPO Data from 2023-2024
        real_ipos = [
            # --- 2023 Blockbusters ---
            {
                "company_name": "Tata Technologies",
                "symbol": "TATATECH",
                "sector": "Technology",
                "issue_size": 3042.51,
                "price_band": "475-500",
                "listing_price": 1200.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-11-22",
                "description": "Global engineering services company offering product development and digital solutions."
            },
            {
                "company_name": "IREDA",
                "symbol": "IREDA",
                "sector": "Finance",
                "issue_size": 2150.00,
                "price_band": "30-32",
                "listing_price": 50.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-11-21",
                "description": "Indian Renewable Energy Development Agency, a Mini Ratna (Category-I) Government of India Enterprise."
            },
            {
                "company_name": "DOMS Industries",
                "symbol": "DOMS",
                "sector": "Consumer Goods",
                "issue_size": 1200.00,
                "price_band": "750-790",
                "listing_price": 1400.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-12-13",
                "description": "Leading stationery and art product company in India."
            },
            {
                "company_name": "Inox India",
                "symbol": "INOXINDIA",
                "sector": "Industrial",
                "issue_size": 1459.32,
                "price_band": "627-660",
                "listing_price": 933.15,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-12-14",
                "description": "Leading cryogenic tank manufacturer."
            },
             {
                "company_name": "Happy Forgings",
                "symbol": "HAPPYFORGE",
                "sector": "Industrial",
                "issue_size": 1008.59,
                "price_band": "808-850",
                "listing_price": 1001.25,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-12-19",
                "description": "Heavy forging and high-precision machined components manufacturer."
            },
            {
                "company_name": "Azad Engineering",
                "symbol": "AZAD",
                "sector": "Industrial",
                "issue_size": 740.00,
                "price_band": "499-524",
                "listing_price": 720.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-12-20",
                "description": "Manufacturer of aerospace components and turbines."
            },
            {
                "company_name": "Motisons Jewellers",
                "symbol": "MOTISONS",
                "sector": "Consumer Goods",
                "issue_size": 151.09,
                "price_band": "52-55",
                "listing_price": 109.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-12-18",
                "description": "Jewellery retail player based in Jaipur."
            },
            {
                "company_name": "Muthoot Microfin",
                "symbol": "MUTHOOTMIC",
                "sector": "Finance",
                "issue_size": 960.00,
                "price_band": "277-291",
                "listing_price": 275.30,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-12-18",
                "description": "Microfinance institution providing micro-loans to women entrepreneurs."
            },
            {
                "company_name": "Suraj Estate Developers",
                "symbol": "SURAJEST",
                "sector": "Real Estate",
                "issue_size": 400.00,
                "price_band": "340-360",
                "listing_price": 340.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-12-18",
                "description": "Real estate developer focused on South Central Mumbai."
            },
            {
                "company_name": "Innova Captab",
                "symbol": "INNOVA",
                "sector": "Healthcare",
                "issue_size": 570.00,
                "price_band": "426-448",
                "listing_price": 545.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-12-21",
                "description": "Pharmaceutical company engaged in R&D and manufacturing."
            },
            
            # --- Early 2024 ---
             {
                "company_name": "Medi Assist Healthcare",
                "symbol": "MEDIASSIST",
                "sector": "Healthcare",
                "issue_size": 1171.58,
                "price_band": "397-418",
                "listing_price": 465.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-01-15",
                "description": "Health-tech and insurance administration services."
            },
            {
                "company_name": "Jyoti CNC Automation",
                "symbol": "JYOTICNC",
                "sector": "Industrial",
                "issue_size": 1000.00,
                "price_band": "315-331",
                "listing_price": 370.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-01-09",
                "description": "Manufacturer of metal cutting computer numerical control (CNC) machines."
            },
            {
                "company_name": "EPACK Durable",
                "symbol": "EPACK",
                "sector": "Consumer Goods",
                "issue_size": 640.05,
                "price_band": "218-230",
                "listing_price": 225.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-01-19",
                "description": "Outsourced Design and Manufacturing (ODM) of room air conditioners."
            },
             {
                "company_name": "Nova Agritech",
                "symbol": "NOVAAGRI",
                "sector": "Agriculture",
                "issue_size": 143.81,
                "price_band": "39-41",
                "listing_price": 56.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-01-23",
                "description": "Agri-input manufacturer focusing on soil health and crop nutrition."
            },
            {
                "company_name": "BLS E-Services",
                "symbol": "BLSE",
                "sector": "Technology",
                "issue_size": 310.91,
                "price_band": "129-135",
                "listing_price": 305.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-01-30",
                "description": "Digital service provider offering business correspondence and e-governance."
            },
            {
                "company_name": "Rashi Peripherals",
                "symbol": "RPTECH",
                "sector": "Technology",
                "issue_size": 600.00,
                "price_band": "295-311",
                "listing_price": 335.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-02-07",
                "description": "Information and communications technology (ICT) distributor."
            },
            {
                "company_name": "Capital Small Finance Bank",
                "symbol": "CAPITALSFB",
                "sector": "Finance",
                "issue_size": 523.00,
                "price_band": "445-468",
                "listing_price": 435.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-02-07",
                "description": "First small finance bank in India."
            },
            {
                "company_name": "Jana Small Finance Bank",
                "symbol": "JANABANK",
                "sector": "Finance",
                "issue_size": 570.00,
                "price_band": "393-414",
                "listing_price": 396.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-02-07",
                "description": "Small finance bank serving underbanked customers."
            },

            # --- Mid 2024 ---
            {
                "company_name": "Bharti Hexacom",
                "symbol": "BHARTIHEXA",
                "sector": "Telecommunication",
                "issue_size": 4275.00,
                "price_band": "542-570",
                "listing_price": 755.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-04-03",
                "description": "Communications solutions provider offering mobile, fixed-line and broadband."
            },
            {
                "company_name": "Go Digit General Insurance",
                "symbol": "GODIGIT",
                "sector": "Finance",
                "issue_size": 2614.65,
                "price_band": "258-272",
                "listing_price": 281.10,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-05-15",
                "description": "Digital full-stack insurance company."
            },
            {
                "company_name": "Aadhar Housing Finance",
                "symbol": "AADHARHFC",
                "sector": "Finance",
                "issue_size": 3000.00,
                "price_band": "300-315",
                "listing_price": 315.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-05-08",
                "description": "Housing finance company focused on low-income housing."
            },
            {
                "company_name": "TBO Tek",
                "symbol": "TBOTEK",
                "sector": "Technology",
                "issue_size": 1550.81,
                "price_band": "875-920",
                "listing_price": 1380.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-05-08",
                "description": "Global travel distribution platform."
            },
            {
                "company_name": "Indegene",
                "symbol": "INDEGENE",
                "sector": "Healthcare",
                "issue_size": 1841.76,
                "price_band": "430-452",
                "listing_price": 652.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-05-06",
                "description": "Digital commercialization partner for the life sciences industry."
            },
            {
                "company_name": "Awfis Space Solutions",
                "symbol": "AWFIS",
                "sector": "Real Estate",
                "issue_size": 598.93,
                "price_band": "364-383",
                "listing_price": 435.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-05-22",
                "description": "Largest flexible workspace solutions company in India."
            },
            {
                "company_name": "Ixigo (Le Travenues)",
                "symbol": "IXIGO",
                "sector": "Technology",
                "issue_size": 740.10,
                "price_band": "88-93",
                "listing_price": 135.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-06-10",
                "description": "AI-based travel app for booking trains, flights, and buses."
            },
            {
                "company_name": "DEE Development Engineers",
                "symbol": "DEEDEV",
                "sector": "Industrial",
                "issue_size": 418.01,
                "price_band": "193-203",
                "listing_price": 339.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-06-19",
                "description": "Engineering company providing specialized process piping solutions."
            },
             {
                "company_name": "Stanley Lifestyles",
                "symbol": "STANLEY",
                "sector": "Consumer Goods",
                "issue_size": 537.02,
                "price_band": "351-369",
                "listing_price": 494.95,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-06-21",
                "description": "Super-premium and luxury furniture brand."
            },
            {
                "company_name": "Emcure Pharmaceuticals",
                "symbol": "EMCURE",
                "sector": "Healthcare",
                "issue_size": 1952.03,
                "price_band": "960-1008",
                "listing_price": 1325.05,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-07-03",
                "description": "Research-driven pharmaceutical company."
            },
            {
                "company_name": "Bansal Wire",
                "symbol": "BANSALWIRE",
                "sector": "Industrial",
                "issue_size": 745.00,
                "price_band": "243-256",
                "listing_price": 356.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-07-03",
                "description": "Largest stainless steel wire manufacturing company in India."
            },
            {
                "company_name": "Ola Electric Mobility",
                "symbol": "OLAELEC",
                "sector": "Automobile",
                "issue_size": 6145.56,
                "price_band": "72-76",
                "listing_price": 75.99,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-08-02",
                "description": "India's leading electric two-wheeler manufacturer."
            },
            {
                "company_name": "FirstCry (Brainbees)",
                "symbol": "FIRSTCRY",
                "sector": "Technology",
                "issue_size": 4193.73,
                "price_band": "440-465",
                "listing_price": 651.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-08-06",
                "description": "India's largest online store for baby and kids products."
            },
             {
                "company_name": "Unicommerce eSolutions",
                "symbol": "UNICOM",
                "sector": "Technology",
                "issue_size": 276.57,
                "price_band": "102-108",
                "listing_price": 230.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2024-08-06",
                "description": "E-commerce enablement software-as-a-service (SaaS) platform."
            },
            
            # --- Upcoming / Ongoing (Hypothetical Dates for Demo) ---
            {
                "company_name": "Swiggy",
                "symbol": "SWIGGY",
                "sector": "Technology",
                "issue_size": 11327.43,
                "price_band": "371-390",
                "listing_price": None,
                "listing_at": "NSE",
                "status": "UPCOMING",
                "open_date": (timezone.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "description": "Leading food delivery and quick commerce platform in India."
            },
            {
                "company_name": "NTPC Green Energy",
                "symbol": "NTPCGREEN",
                "sector": "Energy",
                "issue_size": 10000.00,
                "price_band": "100-110",
                "listing_price": None,
                "listing_at": "NSE",
                "status": "UPCOMING",
                "open_date": (timezone.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
                "description": "Renewable energy arm of NTPC."
            },
             {
                "company_name": "Hyundai Motor India",
                "symbol": "HYUNDAI",
                "sector": "Automobile",
                "issue_size": 27870.16,
                "price_band": "1865-1960",
                "listing_price": None,
                "listing_at": "NSE",
                "status": "ONGOING",
                "open_date": (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "description": "Indian subsidiary of the South Korean automotive giant."
            },
             {
                "company_name": "Zinka Logistics (BlackBuck)",
                "symbol": "BLACKBUCK",
                "sector": "Technology",
                "issue_size": 1114.72,
                "price_band": "259-273",
                "listing_price": None,
                "listing_at": "NSE",
                "status": "UPCOMING",
                "open_date": (timezone.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
                "description": "Digital platform for truck operators."
            },
            
            # --- Additional 2023 IPOs ---
            {
                "company_name": "Ideaforge Technology",
                "symbol": "IDEAFORGE",
                "sector": "Technology",
                "issue_size": 567.03,
                "price_band": "638-672",
                "listing_price": 745.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-06-26",
                "description": "Leading drone manufacturer in India."
            },
            {
                "company_name": "Utkarsh Small Finance Bank",
                "symbol": "UTKARSH",
                "sector": "Finance",
                "issue_size": 2800.00,
                "price_band": "25-28",
                "listing_price": 35.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-07-10",
                "description": "Small finance bank focused on rural and semi-urban areas."
            },
            {
                "company_name": "Suraj Estate Developers",
                "symbol": "SURAJEST",
                "sector": "Real Estate",
                "issue_size": 400.00,
                "price_band": "340-360",
                "listing_price": 420.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-08-08",
                "description": "Real estate developer in Mumbai Metropolitan Region."
            },
            {
                "company_name": "Vishnu Prakash R Punglia",
                "symbol": "VPRL",
                "sector": "Industrial",
                "issue_size": 165.00,
                "price_band": "135-143",
                "listing_price": 180.00,
                "listing_at": "BSE",
                "status": "LISTED",
                "open_date": "2023-09-12",
                "description": "Manufacturer of specialty chemicals."
            },
            {
                "company_name": "Aeroflex Industries",
                "symbol": "AEROFLEX",
                "sector": "Industrial",
                "issue_size": 108.00,
                "price_band": "102-108",
                "listing_price": 145.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2023-10-03",
                "description": "Manufacturer of pre-insulated pipes and refrigeration components."
            },
            
            # --- 2022 IPOs ---
            {
                "company_name": "LIC India",
                "symbol": "LICI",
                "sector": "Finance",
                "issue_size": 21008.00,
                "price_band": "902-949",
                "listing_price": 875.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-05-04",
                "description": "Life Insurance Corporation of India - largest insurance company."
            },
            {
                "company_name": "Delhivery",
                "symbol": "DELHIVERY",
                "sector": "Logistics",
                "issue_size": 5235.00,
                "price_band": "462-487",
                "listing_price": 487.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-05-10",
                "description": "Leading logistics and supply chain services company."
            },
            {
                "company_name": "Aether Industries",
                "symbol": "AETHER",
                "sector": "Chemicals",
                "issue_size": 808.00,
                "price_band": "610-642",
                "listing_price": 730.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-05-24",
                "description": "Specialty chemicals manufacturer."
            },
            {
                "company_name": "Rainbow Children's Medicare",
                "symbol": "RAINBOW",
                "sector": "Healthcare",
                "issue_size": 1581.00,
                "price_band": "516-542",
                "listing_price": 605.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-04-27",
                "description": "Multi-specialty pediatric hospital chain."
            },
            {
                "company_name": "Campus Activewear",
                "symbol": "CAMPUS",
                "sector": "Consumer Goods",
                "issue_size": 1400.00,
                "price_band": "278-292",
                "listing_price": 330.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-05-02",
                "description": "Footwear brand manufacturer."
            },
            {
                "company_name": "Veranda Learning Solutions",
                "symbol": "VERANDA",
                "sector": "Education",
                "issue_size": 200.00,
                "price_band": "137-144",
                "listing_price": 165.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-03-29",
                "description": "Test preparation and skill development company."
            },
            {
                "company_name": "Ethos Limited",
                "symbol": "ETHOS",
                "sector": "Retail",
                "issue_size": 472.00,
                "price_band": "836-878",
                "listing_price": 950.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-05-18",
                "description": "Luxury watch retailer."
            },
            {
                "company_name": "Prudent Corporate Advisory",
                "symbol": "PRUDENT",
                "sector": "Finance",
                "issue_size": 630.00,
                "price_band": "614-630",
                "listing_price": 720.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-06-07",
                "description": "Wealth management and financial services."
            },
            {
                "company_name": "Syrma SGS Technology",
                "symbol": "SYRMA",
                "sector": "Technology",
                "issue_size": 840.00,
                "price_band": "209-220",
                "listing_price": 260.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-08-12",
                "description": "Electronics manufacturing services provider."
            },
            {
                "company_name": "Harsha Engineers International",
                "symbol": "HARSHA",
                "sector": "Industrial",
                "issue_size": 755.00,
                "price_band": "314-330",
                "listing_price": 395.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-09-14",
                "description": "Precision bearing cages manufacturer."
            },
            {
                "company_name": "Dreamfolks Services",
                "symbol": "DREAMFOLKS",
                "sector": "Services",
                "issue_size": 562.00,
                "price_band": "308-326",
                "listing_price": 380.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-08-24",
                "description": "Airport lounge aggregator platform."
            },
            {
                "company_name": "Tracxn Technologies",
                "symbol": "TRACXN",
                "sector": "Technology",
                "issue_size": 309.00,
                "price_band": "75-80",
                "listing_price": 85.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-10-10",
                "description": "Market intelligence platform for startups."
            },
            {
                "company_name": "Abans Holdings",
                "symbol": "ABANS",
                "sector": "Finance",
                "issue_size": 530.00,
                "price_band": "550-585",
                "listing_price": 640.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-12-19",
                "description": "Broking and financial services company."
            },
            {
                "company_name": "Archean Chemical Industries",
                "symbol": "ACI",
                "sector": "Chemicals",
                "issue_size": 1462.00,
                "price_band": "386-407",
                "listing_price": 480.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-11-09",
                "description": "Specialty marine chemicals manufacturer."
            },
            {
                "company_name": "Kaynes Technology India",
                "symbol": "KAYNES",
                "sector": "Technology",
                "issue_size": 858.00,
                "price_band": "559-587",
                "listing_price": 670.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-11-10",
                "description": "Electronics manufacturing services."
            },
            {
                "company_name": "Fusion Micro Finance",
                "symbol": "FUSION",
                "sector": "Finance",
                "issue_size": 1103.00,
                "price_band": "350-368",
                "listing_price": 420.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-11-02",
                "description": "Microfinance institution."
            },
            {
                "company_name": "Shriram Properties",
                "symbol": "SHRIRAMPROP",
                "sector": "Real Estate",
                "issue_size": 600.00,
                "price_band": "113-118",
                "listing_price": 125.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-12-08",
                "description": "Real estate developer in South India."
            },
            {
                "company_name": "Anand Rathi Wealth",
                "symbol": "ANANDRATHI",
                "sector": "Finance",
                "issue_size": 660.00,
                "price_band": "530-550",
                "listing_price": 620.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-12-06",
                "description": "Wealth management services."
            },
            {
                "company_name": "Sapphire Foods India",
                "symbol": "SAPPHIRE",
                "sector": "Food & Beverage",
                "issue_size": 2073.00,
                "price_band": "1120-1180",
                "listing_price": 1340.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-11-09",
                "description": "KFC and Pizza Hut franchisee."
            },
            {
                "company_name": "Nykaa (FSN E-Commerce)",
                "symbol": "NYKAA",
                "sector": "E-Commerce",
                "issue_size": 5352.00,
                "price_band": "1085-1125",
                "listing_price": 2018.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-10-28",
                "description": "Beauty and personal care e-commerce platform."
            },
            {
                "company_name": "Paytm (One97 Communications)",
                "symbol": "PAYTM",
                "sector": "Fintech",
                "issue_size": 18300.00,
                "price_band": "2080-2150",
                "listing_price": 1955.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-11-08",
                "description": "Digital payments and financial services platform."
            },
            {
                "company_name": "Policybazaar (PB Fintech)",
                "symbol": "POLICYBZR",
                "sector": "Fintech",
                "issue_size": 5710.00,
                "price_band": "940-980",
                "listing_price": 1150.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-11-01",
                "description": "Insurance aggregator platform."
            },
            {
                "company_name": "Fino Payments Bank",
                "symbol": "FINO",
                "sector": "Finance",
                "issue_size": 1200.00,
                "price_band": "560-577",
                "listing_price": 655.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-10-29",
                "description": "Payments bank focused on rural and semi-urban markets."
            },
            {
                "company_name": "Star Health Insurance",
                "symbol": "STARHEALTH",
                "sector": "Insurance",
                "issue_size": 6400.00,
                "price_band": "870-900",
                "listing_price": 845.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-11-30",
                "description": "Standalone health insurance company."
            },
            {
                "company_name": "Tarsons Products",
                "symbol": "TARSONS",
                "sector": "Healthcare",
                "issue_size": 1024.00,
                "price_band": "635-662",
                "listing_price": 780.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-11-15",
                "description": "Laboratory plastic ware manufacturer."
            },
            {
                "company_name": "Ami Organics",
                "symbol": "AMIORG",
                "sector": "Chemicals",
                "issue_size": 570.00,
                "price_band": "603-610",
                "listing_price": 720.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-09-01",
                "description": "Specialty chemicals for pharma and agrochemicals."
            },
            {
                "company_name": "Tatva Chintan Pharma Chem",
                "symbol": "TATVA",
                "sector": "Chemicals",
                "issue_size": 500.00,
                "price_band": "1073-1083",
                "listing_price": 1850.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-07-16",
                "description": "Specialty chemicals manufacturer."
            },
            {
                "company_name": "Windlas Biotech",
                "symbol": "WINDLAS",
                "sector": "Pharmaceuticals",
                "issue_size": 401.00,
                "price_band": "448-460",
                "listing_price": 520.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-08-04",
                "description": "Contract development and manufacturing organization."
            },
            {
                "company_name": "Glenmark Life Sciences",
                "symbol": "GLS",
                "sector": "Pharmaceuticals",
                "issue_size": 1513.00,
                "price_band": "695-720",
                "listing_price": 820.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-07-27",
                "description": "API manufacturer for generic drugs."
            },
            {
                "company_name": "Exxaro Tiles",
                "symbol": "EXXARO",
                "sector": "Building Materials",
                "issue_size": 161.00,
                "price_band": "118-120",
                "listing_price": 145.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-08-11",
                "description": "Ceramic tiles manufacturer."
            },
            {
                "company_name": "Chemplast Sanmar",
                "symbol": "CHEMPLAST",
                "sector": "Chemicals",
                "issue_size": 3850.00,
                "price_band": "530-541",
                "listing_price": 610.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-08-10",
                "description": "Specialty chemicals and custom manufacturing."
            },
            {
                "company_name": "Rolex Rings",
                "symbol": "ROLEXRINGS",
                "sector": "Industrial",
                "issue_size": 731.00,
                "price_band": "880-900",
                "listing_price": 1050.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-07-05",
                "description": "Forged and machined rings manufacturer."
            },
            {
                "company_name": "Dodla Dairy",
                "symbol": "DODLA",
                "sector": "Food & Beverage",
                "issue_size": 520.00,
                "price_band": "421-428",
                "listing_price": 495.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-06-16",
                "description": "Dairy products manufacturer."
            },
            {
                "company_name": "Krsnaa Diagnostics",
                "symbol": "KRSNAA",
                "sector": "Healthcare",
                "issue_size": 1213.00,
                "price_band": "933-954",
                "listing_price": 1050.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-08-04",
                "description": "Diagnostic services provider."
            },
            {
                "company_name": "Devyani International",
                "symbol": "DEVYANI",
                "sector": "Food & Beverage",
                "issue_size": 1838.00,
                "price_band": "86-90",
                "listing_price": 118.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-08-04",
                "description": "Pizza Hut and KFC franchisee."
            },
            {
                "company_name": "Zomato",
                "symbol": "ZOMATO",
                "sector": "Food Tech",
                "issue_size": 9375.00,
                "price_band": "72-76",
                "listing_price": 116.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-07-14",
                "description": "Food delivery and restaurant discovery platform."
            },
            {
                "company_name": "CarTrade Tech",
                "symbol": "CARTRADE",
                "sector": "E-Commerce",
                "issue_size": 2999.00,
                "price_band": "1618-1618",
                "listing_price": 1618.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-08-09",
                "description": "Online automotive marketplace."
            },
            {
                "company_name": "Clean Science and Technology",
                "symbol": "CLEAN",
                "sector": "Chemicals",
                "issue_size": 1546.00,
                "price_band": "880-900",
                "listing_price": 1784.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-07-07",
                "description": "Specialty chemicals using green chemistry."
            },
            {
                "company_name": "Aptus Value Housing Finance",
                "symbol": "APTUS",
                "sector": "Finance",
                "issue_size": 2780.00,
                "price_band": "346-353",
                "listing_price": 410.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-08-09",
                "description": "Housing finance company for low and middle income."
            },
            {
                "company_name": "Vijaya Diagnostic Centre",
                "symbol": "VIJAYA",
                "sector": "Healthcare",
                "issue_size": 1895.00,
                "price_band": "522-531",
                "listing_price": 605.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-09-01",
                "description": "Diagnostic services chain."
            },
            {
                "company_name": "Sansera Engineering",
                "symbol": "SANSERA",
                "sector": "Automobile",
                "issue_size": 1283.00,
                "price_band": "744-744",
                "listing_price": 850.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-09-14",
                "description": "Auto component manufacturer."
            },
            {
                "company_name": "Paras Defence and Space Technologies",
                "symbol": "PARAS",
                "sector": "Defense",
                "issue_size": 170.00,
                "price_band": "165-175",
                "listing_price": 280.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-09-21",
                "description": "Defense and space optics manufacturer."
            },
            {
                "company_name": "Supriya Lifescience",
                "symbol": "SUPRIYA",
                "sector": "Pharmaceuticals",
                "issue_size": 700.00,
                "price_band": "265-274",
                "listing_price": 340.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-12-16",
                "description": "API and intermediates manufacturer."
            },
            {
                "company_name": "Metro Brands",
                "symbol": "METROBRAND",
                "sector": "Retail",
                "issue_size": 1367.00,
                "price_band": "485-500",
                "listing_price": 575.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-12-10",
                "description": "Footwear retail chain."
            },
            {
                "company_name": "RateGain Travel Technologies",
                "symbol": "RATEGAIN",
                "sector": "Technology",
                "issue_size": 1335.00,
                "price_band": "405-425",
                "listing_price": 495.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-12-07",
                "description": "SaaS platform for travel and hospitality."
            },
            {
                "company_name": "Medplus Health Services",
                "symbol": "MEDPLUS",
                "sector": "Healthcare",
                "issue_size": 1398.00,
                "price_band": "780-796",
                "listing_price": 920.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-12-13",
                "description": "Pharmacy retail chain."
            },
            {
                "company_name": "Adani Wilmar",
                "symbol": "AWL",
                "sector": "FMCG",
                "issue_size": 3600.00,
                "price_band": "218-230",
                "listing_price": 260.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-01-27",
                "description": "Edible oil and FMCG products."
            },
            {
                "company_name": "AGS Transact Technologies",
                "symbol": "AGS",
                "sector": "Technology",
                "issue_size": 680.00,
                "price_band": "166-175",
                "listing_price": 195.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-01-19",
                "description": "Payment solutions and ATM management."
            },
            {
                "company_name": "CMS Info Systems",
                "symbol": "CMS",
                "sector": "Services",
                "issue_size": 1100.00,
                "price_band": "205-216",
                "listing_price": 245.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2021-12-21",
                "description": "Cash management and ATM services."
            },
            {
                "company_name": "Vedant Fashions (Manyavar)",
                "symbol": "MANYAVAR",
                "sector": "Retail",
                "issue_size": 3149.00,
                "price_band": "824-866",
                "listing_price": 1050.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-02-04",
                "description": "Ethnic wear brand Manyavar."
            },
            {
                "company_name": "Hariom Pipe Industries",
                "symbol": "HARIOMPIPE",
                "sector": "Industrial",
                "issue_size": 142.00,
                "price_band": "144-153",
                "listing_price": 185.00,
                "listing_at": "BSE",
                "status": "LISTED",
                "open_date": "2022-03-23",
                "description": "MS pipes and tubes manufacturer."
            },
            {
                "company_name": "Shivalik Bimetal Controls",
                "symbol": "SBCL",
                "sector": "Industrial",
                "issue_size": 214.00,
                "price_band": "428-450",
                "listing_price": 520.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-04-06",
                "description": "Bimetallic components manufacturer."
            },
            {
                "company_name": "Hariom Pipe Industries",
                "symbol": "HARIOMPIPE",
                "sector": "Industrial",
                "issue_size": 142.00,
                "price_band": "144-153",
                "listing_price": 185.00,
                "listing_at": "BSE",
                "status": "LISTED",
                "open_date": "2022-03-23",
                "description": "MS pipes and tubes manufacturer."
            },
            {
                "company_name": "Prudent Corporate Advisory",
                "symbol": "PRUDENT",
                "sector": "Finance",
                "issue_size": 630.00,
                "price_band": "614-630",
                "listing_price": 720.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-06-07",
                "description": "Wealth management and financial services."
            },
            {
                "company_name": "Paradeep Phosphates",
                "symbol": "PARADEEP",
                "sector": "Chemicals",
                "issue_size": 1501.00,
                "price_band": "39-42",
                "listing_price": 48.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-05-17",
                "description": "Fertilizer manufacturer."
            },
            {
                "company_name": "Sah Polymers",
                "symbol": "SAHPOLY",
                "sector": "Chemicals",
                "issue_size": 45.00,
                "price_band": "85-90",
                "listing_price": 110.00,
                "listing_at": "BSE",
                "status": "LISTED",
                "open_date": "2022-06-29",
                "description": "Polymer compounds manufacturer."
            },
            {
                "company_name": "Agarwal Toughened Glass India",
                "symbol": "ATGL",
                "sector": "Building Materials",
                "issue_size": 25.00,
                "price_band": "120-125",
                "listing_price": 150.00,
                "listing_at": "BSE",
                "status": "LISTED",
                "open_date": "2022-07-13",
                "description": "Toughened glass manufacturer."
            },
            {
                "company_name": "Sula Vineyards",
                "symbol": "SULA",
                "sector": "Food & Beverage",
                "issue_size": 960.00,
                "price_band": "340-357",
                "listing_price": 420.00,
                "listing_at": "NSE",
                "status": "LISTED",
                "open_date": "2022-12-12",
                "description": "Wine producer and vineyard."
            },
        ]

        for data in real_ipos:
            # Handle dates
            if 'open_date' in data:
                open_date = timezone.datetime.strptime(data['open_date'], "%Y-%m-%d").date()
                close_date = open_date + timedelta(days=2)
                
                if data['status'] == 'LISTED':
                    listing_date = close_date + timedelta(days=3)
                else:
                    listing_date = None
            else:
                # Fallback
                open_date = timezone.now().date()
                close_date = open_date + timedelta(days=2)
                listing_date = None

            # Financial metrics generation (Randomized but within realistic sectors)
            # Tech/Growth -> High PE, High Growth
            # Finance -> Moderate PE, Moderate Growth
            # Manufacturing -> Lower PE, Stable Growth
            
            sector = data['sector']
            if sector == "Technology":
                pe = random.uniform(40, 100)
                revenue_growth = random.uniform(15, 50)
            elif sector == "Finance":
                pe = random.uniform(15, 30)
                revenue_growth = random.uniform(10, 25)
            elif sector == "Industrial":
                 pe = random.uniform(25, 60)
                 revenue_growth = random.uniform(10, 30)
            else:
                pe = random.uniform(20, 50)
                revenue_growth = random.uniform(8, 20)

            # Market Cap approx
            market_cap = data['issue_size'] * random.uniform(4, 8) 
            
            ipo = IPO(
                company_name=data['company_name'],
                symbol=data['symbol'],
                price_band=data['price_band'],
                open_date=open_date,
                close_date=close_date,
                listing_date=listing_date,
                status=data['status'],
                issue_size=data['issue_size'],
                market_cap=market_cap,
                listing_at=data['listing_at'],
                sector=data['sector'],
                lead_manager=random.choice(['Kotak Mahindra', 'Axis Capital', 'HDFC Bank', 'ICICI Securities', 'JP Morgan']),
                # description=data.get('description', ''), # Field does not exist in model
                
                # Financials
                revenue_growth=round(revenue_growth, 2),
                roe=round(random.uniform(12, 25), 2),
                roa=round(random.uniform(5, 15), 2),
                pe_ratio=round(pe, 2),
                volatility=round(random.uniform(10, 30), 2),
                
                # Qualitative Traits (Humanized)
                esg_score=self._generate_realistic_esg(data),
                management_quality=round(random.uniform(40, 95), 1),
                brand_moat=self._generate_realistic_moat(data)
            )
            
            # Set prices if available
            if data['price_band']:
                try:
                    parts = data['price_band'].split('-')
                    if len(parts) == 2:
                        upper_band = float(parts[1])
                    else:
                        upper_band = float(parts[0])

                    if data['status'] == 'LISTED' and data.get('listing_price'):
                        ipo.current_price = data['listing_price'] * random.uniform(0.95, 1.1) # Current price slightly varies from listing
                        ipo.listing_price = data['listing_price']
                    else:
                        ipo.current_price = upper_band
                except:
                    pass

            ipo.save()
            self.stdout.write(self.style.SUCCESS(f'Created IPO: {ipo.company_name}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully populated database with {len(real_ipos)} REAL IPO entries'))

    def _generate_realistic_esg(self, data):
        """Simulate realistic ESG scores based on sector."""
        sector = data['sector']
        # Energy/Industrial often start lower or are high-risk
        if sector in ['Energy', 'Industrial', 'Agriculture']:
            return round(random.uniform(30, 70), 1)
        # Tech/Healthcare/Finance often have higher ESG focus
        elif sector in ['Technology', 'Healthcare', 'Finance']:
            return round(random.uniform(60, 95), 1)
        return round(random.uniform(50, 85), 1)

    def _generate_realistic_moat(self, data):
        """Simulate brand moat based on company importance and sector."""
        high_moat_names = ['TATA', 'HYUNDAI', 'RELIANCE', 'NYKAA', 'PAYTM', 'OLA']
        name = data['company_name'].upper()
        
        if any(hm in name for hm in high_moat_names):
            return round(random.uniform(80, 98), 1)
            
        if data['sector'] == 'Technology':
            return round(random.uniform(60, 90), 1)
            
        return round(random.uniform(40, 75), 1)
