import requests
import os
from urllib.parse import urlparse

def search_serper(query: str, custom_api_key: str = None) -> dict:
    api_key = custom_api_key or os.environ.get("SERPER_API_KEY")
    if not api_key:
        print("Serper API key not found. Using simulated search results.")
        return get_simulated_serper_response(query)
    
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json",
            },
            json={"q": query},
            timeout=8
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Serper API error status {response.status_code}: {response.text}")
            return get_simulated_serper_response(query)
    except Exception as e:
        print(f"Error calling Serper API: {e}")
        return get_simulated_serper_response(query)

def resolve_official_website(company_name: str, custom_api_key: str = None) -> str:
    data = search_serper(company_name, custom_api_key)
    
    # Try knowledge graph
    kg = data.get("knowledgeGraph", {})
    if kg.get("website"):
        return kg.get("website")
    
    # Otherwise check organic links
    organic = data.get("organic", [])
    skip_domains = ["wikipedia.org", "linkedin.com", "facebook.com", "twitter.com", "instagram.com", "youtube.com", "crunchbase.com", "glassdoor.com", "yelp.com"]
    
    for result in organic:
        url = result.get("link")
        if url and not any(domain in url.lower() for domain in skip_domains):
            return url
            
    return organic[0].get("link") if organic else f"https://www.{company_name.lower().replace(' ', '')}.com"

def get_company_details(domain_or_name: str, custom_api_key: str = None) -> dict:
    data = search_serper(f"{domain_or_name} address phone contact", custom_api_key)
    
    kg = data.get("knowledgeGraph", {})
    phone = kg.get("phone")
    address = kg.get("address")
    info_snippet = kg.get("description")
    
    if not phone or not address:
        organic = data.get("organic", [])
        import re
        phone_regex = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        
        for result in organic:
            text = f"{result.get('title', '')} {result.get('snippet', '')}"
            if not phone:
                match = re.search(phone_regex, text)
                if match:
                    phone = match.group(0)
            if not address and any(keyword in text.lower() for keyword in ["address:", "hq:", "located at"]):
                # Simple extraction heuristic
                parts = re.split(r"address:|hq:|located at", text, flags=re.IGNORECASE)
                if len(parts) > 1:
                    address = parts[1].split(".")[0].strip()
                    
    return {
        "phone": phone or "Not Available",
        "address": address or "Not Available",
        "infoSnippet": info_snippet or ""
    }

def find_competitors_serp(company_name: str, industry: str, custom_api_key: str = None) -> list:
    data = search_serper(f"top competitors of {company_name} in {industry or 'same industry'}", custom_api_key)
    competitors = []
    
    organic = data.get("organic", [])
    for result in organic:
        text = f"{result.get('title', '')} {result.get('snippet', '')}"
        import re
        url_matches = re.findall(r"https?://[^\s$.?#].[^\s]*", text, re.IGNORECASE)
        for url in url_matches:
            try:
                domain = urlparse(url).hostname
                if domain:
                    domain = domain.replace("www.", "")
                    if company_name.lower() not in domain and not any(c["website"] == f"https://{domain}" for c in competitors):
                        name = domain.split(".")[0].capitalize()
                        competitors.append({
                            "name": name,
                            "website": f"https://{domain}"
                        })
            except Exception:
                pass
                
    return competitors[:5]

def get_simulated_serper_response(query: str) -> dict:
    query_lower = query.lower()
    
    if "stripe" in query_lower:
        return {
            "knowledgeGraph": {
                "title": "Stripe",
                "website": "https://stripe.com",
                "phone": "+1 (888) 963-8975",
                "address": "354 Oyster Point Blvd, South San Francisco, CA 94080, USA",
                "description": "Stripe is a suite of APIs powering online payment processing and commerce solutions for internet businesses of all sizes."
            },
            "organic": [
                { "title": "Stripe | Payment Processing Platform", "link": "https://stripe.com", "snippet": "Stripe is a suite of APIs powering online payment processing and commerce solutions for internet businesses of all sizes." },
                { "title": "Stripe Competitors & Alternatives", "link": "https://www.g2.com/products/stripe/competitors/alternatives", "snippet": "Top competitors include PayPal, Adyen, Braintree, and Square." }
            ]
        }
        
    if "tesla" in query_lower:
        return {
            "knowledgeGraph": {
                "title": "Tesla, Inc.",
                "website": "https://tesla.com",
                "phone": "+1 (888) 518-3752",
                "address": "1 Tesla Road, Austin, TX 78725, USA",
                "description": "Tesla, Inc. is an American multinational automotive and clean energy company headquartered in Austin, Texas."
            },
            "organic": [
                { "title": "Tesla: Electric Cars, Solar & Clean Energy", "link": "https://tesla.com", "snippet": "Tesla is accelerating the world's transition to sustainable energy with electric cars, solar and integrated renewable energy solutions." }
            ]
        }
        
    if "microsoft" in query_lower:
        return {
            "knowledgeGraph": {
                "title": "Microsoft",
                "website": "https://microsoft.com",
                "phone": "+1 (800) 642-7676",
                "address": "One Microsoft Way, Redmond, WA 98052, USA",
                "description": "Microsoft Corporation is an American multinational technology corporation headquartered in Redmond, Washington."
            },
            "organic": [
                { "title": "Microsoft - Cloud, Computers, Apps & Gaming", "link": "https://microsoft.com", "snippet": "Explore Microsoft products and services for your home or business. Shop Surface, Microsoft 365, Xbox, Windows, Azure, and more." }
            ]
        }

    if "facebook" in query_lower or "meta" in query_lower:
        return {
            "knowledgeGraph": {
                "title": "Meta Platforms, Inc.",
                "website": "https://meta.com",
                "phone": "+1 (650) 543-4800",
                "address": "1 Hacker Way, Menlo Park, CA 94025, USA",
                "description": "Meta Platforms, Inc., doing business as Meta and formerly named Facebook, Inc., and TheFacebook, Inc., is an American multinational technology conglomerate based in Menlo Park, California."
            },
            "organic": [
                { "title": "Meta: Introducing Meta Quest 3, Instagram, Facebook...", "link": "https://meta.com", "snippet": "Meta builds technologies that help people connect, find communities, and grow businesses. When Facebook launched in 2004, it changed the way people connect." },
                { "title": "Facebook - Log In or Sign Up", "link": "https://facebook.com", "snippet": "Create an account or log into Facebook. Connect with friends, family and other people you know. Share photos and videos, send messages and get updates." }
            ]
        }

    if "instagram" in query_lower or "intagram" in query_lower:
        return {
            "knowledgeGraph": {
                "title": "Instagram",
                "website": "https://instagram.com",
                "phone": "+1 (650) 543-4800",
                "address": "1 Hacker Way, Menlo Park, CA 94025, USA",
                "description": "Instagram is a photo and video sharing social networking service owned by American company Meta Platforms."
            },
            "organic": [
                { "title": "Instagram", "link": "https://instagram.com", "snippet": "Create an account or log in to Instagram - A simple, fun & creative way to capture, edit & share photos, videos & messages with friends & family." }
            ]
        }

    if "google" in query_lower or "alphabet" in query_lower:
        return {
            "knowledgeGraph": {
                "title": "Google LLC",
                "website": "https://google.com",
                "phone": "+1 (650) 253-0000",
                "address": "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA",
                "description": "Google LLC is an American multinational technology company focusing on artificial intelligence, search engine technology, online advertising, cloud computing, computer software, quantum computing, e-commerce, and consumer electronics."
            },
            "organic": [
                { "title": "Google", "link": "https://google.com", "snippet": "Search the world's information, including webpages, images, videos and more. Google has many special features to help you find exactly what you're looking for." }
            ]
        }
        
    clean_name = query.split(" ")[0]
    # filter non-alpha
    clean_name = "".join(c for c in clean_name if c.isalpha())
    domain = f"{clean_name.lower() or 'example'}.com"
    return {
        "knowledgeGraph": {
            "title": query,
            "website": f"https://{domain}",
            "phone": "+1 (555) 019-2834",
            "address": "100 Technology Dr, Silicon Valley, CA 94000, USA",
            "description": f"{query} is a leading enterprise in the technology and service industry."
        },
        "organic": [
            { "title": f"{query} Official Site", "link": f"https://{domain}", "snippet": f"{query} provides high-quality solutions, services, and products to accelerate business operations globally." }
        ]
    }
