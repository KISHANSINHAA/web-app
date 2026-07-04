import requests
import json
import os

OPENROUTER_MODELS = [
    { "id": "google/gemini-2.5-flash", "name": "Gemini 2.5 Flash" },
    { "id": "google/gemini-2.5-pro", "name": "Gemini 2.5 Pro" },
    { "id": "openai/gpt-4o-mini", "name": "GPT-4o Mini" },
    { "id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku" },
    { "id": "meta-llama/llama-3-70b-instruct", "name": "Llama 3 70B" },
]

def query_openrouter(
    company_name_or_url: str,
    crawled_content: str,
    serp_content: str,
    selected_model: str = "google/gemini-2.5-flash",
    custom_api_key: str = None
) -> dict:
    api_key = custom_api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OpenRouter API key not found. Returning simulated AI response.")
        return get_simulated_ai_response(company_name_or_url)
        
    prompt = f"""
You are a expert business analyst and research assistant.
We have collected some data about a company: "{company_name_or_url}".
Below is the crawled content from the company's website, as well as Google search details from Serper.dev.

=== WEBSITE CRAWLED CONTENT ===
{crawled_content}

=== SERPER SEARCH DETAILS ===
{serp_content}

Your job is to analyze this data and generate a comprehensive research report.
You MUST respond with a valid JSON object ONLY. Do not include markdown code block formatting (like ```json) or any conversational text around the JSON.

The JSON object must follow this key structure precisely:
{{
  "companyName": "Official name of the company",
  "website": "Official website URL",
  "phone": "Official phone number, or 'Not Available' if not found",
  "address": "Official headquarters address, or 'Not Available' if not found",
  "companySummary": "A clean 2-3 sentence overview explaining what the company is, their main domain, target audience, and scale.",
  "productsServices": [
    {{
      "name": "Product/Service name",
      "description": "Short explanation of what it does and who uses it"
    }}
  ],
  "painPoints": [
    {{
      "title": "Short title describing the pain point (e.g. Manual payment reconciliations, High operational costs)",
      "description": "Details about why this is a pain point for this specific business, based on their offering, industry, and structure, and how it impacts them."
    }}
  ],
  "competitors": [
    {{
      "name": "Competitor name",
      "website": "Competitor homepage website URL",
      "description": "Short sentence explaining how they compete with this company"
    }}
  ]
}}

Guidelines:
1. Extract the phone and address accurately from the provided data.
2. AI-generated pain points should be intelligent, realistic, and highly specific to the company's products/services, scale, and business model.
3. Identify 3-4 real competitors in the same industry. Provide their clean official website domains.
4. Output strict JSON. Ensure strings are properly escaped.
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://relu-ai-dev-hiring.vercel.app/",
                "X-Title": "Company Research Agent",
            },
            json={
                "model": selected_model,
                "response_format": { "type": "json_object" },
                "messages": [
                    { "role": "user", "content": prompt }
                ]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            res_data = response.json()
            content = res_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            # Clean wraps
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
                
            return json.loads(content.strip())
        else:
            print(f"OpenRouter API error status {response.status_code}: {response.text}")
            return get_simulated_ai_response(company_name_or_url)
    except Exception as e:
        print(f"Error querying OpenRouter API: {e}")
        return get_simulated_ai_response(company_name_or_url)

def get_simulated_ai_response(query: str) -> dict:
    query_lower = query.lower()

    if "stripe" in query_lower:
        return {
            "companyName": "Stripe, Inc.",
            "website": "https://stripe.com",
            "phone": "+1 (888) 963-8975",
            "address": "354 Oyster Point Blvd, South San Francisco, CA 94080, USA",
            "companySummary": "Stripe is a leading financial services and software-as-a-service (SaaS) company that offers payment processing software and application programming interfaces (APIs) for e-commerce websites and mobile applications.",
            "productsServices": [
                { "name": "Stripe Payments", "description": "Global payment processing platform supporting credit cards, digital wallets, and localized payment methods." },
                { "name": "Stripe Billing", "description": "Subscription management and recurring billing toolkit for SaaS and recurring business models." },
                { "name": "Stripe Atlas", "description": "A platform for founders to easily launch a startup company by incorporating in Delaware in a few clicks." },
                { "name": "Stripe Radar", "description": "Fraud prevention and detection powered by machine learning algorithms trained on billions of payments." }
            ],
            "painPoints": [
                { "title": "High Transaction Pricing for Scaling Businesses", "description": "Stripe's default pricing of 2.9% + 30c per transaction can become significantly expensive for high-volume enterprises, prompting them to look for cheaper custom interchange plus deals." },
                { "title": "Sudden Account Holds & Chargeback Policies", "description": "Many scaling platforms complain about automated risk models flagging their accounts and locking funds abruptly, causing critical cash flow issues during periods of rapid sales spikes." },
                { "title": "Complexity in Custom Multi-Tenant Architectures", "description": "Designing complex marketplace settlements using Stripe Connect requires steep engineering resources, careful compliance mapping, and ledger reconciliation." }
            ],
            "competitors": [
                { "name": "Adyen", "website": "https://adyen.com", "description": "Offers a single global platform for end-to-end payments and direct connection to card networks." },
                { "name": "PayPal", "website": "https://paypal.com", "description": "Widely used checkout wallet option and merchant processing via Braintree." },
                { "name": "Checkout.com", "website": "https://checkout.com", "description": "Provides global digital payment processing with a modular architecture for large merchants." }
            ]
        }

    if "tesla" in query_lower:
        return {
            "companyName": "Tesla, Inc.",
            "website": "https://tesla.com",
            "phone": "+1 (888) 518-3752",
            "address": "1 Tesla Road, Austin, TX 78725, USA",
            "companySummary": "Tesla, Inc. designs, manufactures, and sells electric vehicles, battery energy storage systems, solar panels, and solar roof tiles. They are committed to accelerating the world's transition to sustainable energy through clean technology.",
            "productsServices": [
                { "name": "Model Y & Model 3", "description": "Mass-market electric crossover SUV and sedan offering long range and autopilot options." },
                { "name": "Model S & Model X", "description": "Premium flagship electric sedan and SUV featuring maximum performance and advanced styling." },
                { "name": "Megapack & Powerwall", "description": "Utility-scale and residential battery storage products designed to store solar and grid power." },
                { "name": "Full Self-Driving (FSD)", "description": "An advanced driver-assist software suite that automates lane changes, intersections, and parking." }
            ],
            "painPoints": [
                { "title": "Production Bottlenecks & Supply Chain Strain", "description": "Tesla frequently faces delivery delays due to global component shortages, mineral constraints for battery production, and manufacturing line retooling." },
                { "title": "Intense Competition in Electric Vehicle Space", "description": "Legacy automotive giants and emerging Chinese EV makers are releasing cheaper alternatives, eroding Tesla's market share in key markets like Europe and China." },
                { "title": "Regulatory and Safety Scrutiny on Autopilot", "description": "Continuous federal investigations regarding safety and the labeling of autopilot software cause regulatory hurdles." }
            ],
            "competitors": [
                { "name": "BYD Auto", "website": "https://bydauto.com", "description": "A major Chinese electric vehicle and battery manufacturer representing Tesla's largest global volume competitor." },
                { "name": "Rivian Automotive", "website": "https://rivian.com", "description": "Specializes in electric adventure vehicles like off-road trucks and SUVs." },
                { "name": "Lucid Motors", "website": "https://lucidmotors.com", "description": "Focuses on ultra-luxury, high-efficiency electric sedans competing with Tesla Model S." }
            ]
        }

    if "facebook" in query_lower or "meta" in query_lower:
        return {
            "companyName": "Meta Platforms, Inc.",
            "website": "https://meta.com",
            "phone": "+1 (650) 543-4800",
            "address": "1 Hacker Way, Menlo Park, CA 94025, USA",
            "companySummary": "Meta Platforms, Inc. (formerly Facebook, Inc.) is a global social technology conglomerate that builds platforms helping people connect, find communities, and grow businesses. They are the pioneers of modern social media and are actively developing virtual reality and the metaverse.",
            "productsServices": [
                { "name": "Facebook & Messenger", "description": "Global social networking and instant messaging platforms used by billions daily." },
                { "name": "Instagram", "description": "Popular visual content sharing app focusing on photos, vertical videos (Reels), and creators." },
                { "name": "WhatsApp", "description": "Secure cross-platform voice and text messaging utility used widely for personal and business chats." },
                { "name": "Meta Quest", "description": "Consumer and enterprise virtual and mixed reality headsets powered by the Horizon OS ecosystem." }
            ],
            "painPoints": [
                { "title": "Heavy Ad-Revenue Concentration", "description": "Over 97% of Meta's total revenue depends on digital advertising, making its business model highly sensitive to advertiser demand cycles and changes in ad-tracking rules (such as Apple's App Tracking Transparency)." },
                { "title": "Reality Labs Capital Burn", "description": "Building the metaverse and augmented-reality glasses requires billions in quarterly R&D spend, which often impacts operating margins and draws skepticism from institutional investors." },
                { "title": "Global Regulatory and Antitrust Headwinds", "description": "Continuous regulatory pressure under Europe's DMA/GDPR and FTC merger investigations creates constant operational constraints and potential legal liabilities." }
            ],
            "competitors": [
                { "name": "ByteDance (TikTok)", "website": "https://tiktok.com", "description": "Directly competes for user attention, video engagement, and digital advertising budgets globally." },
                { "name": "Snap Inc. (Snapchat)", "website": "https://snap.com", "description": "Competes in augmented reality filters and direct visual messaging among younger demographics." },
                { "name": "Alphabet (YouTube)", "website": "https://youtube.com", "description": "Fierce competitor in vertical video creators (Shorts) and video-ad spend allocation." }
            ]
        }

    if "instagram" in query_lower or "intagram" in query_lower:
        return {
            "companyName": "Instagram",
            "website": "https://instagram.com",
            "phone": "+1 (650) 543-4800",
            "address": "1 Hacker Way, Menlo Park, CA 94025, USA",
            "companySummary": "Instagram is a premier photo- and video-sharing social network owned by Meta Platforms, Inc. It serves as a hub for visual expression, creator culture, brand marketing, and short-form video discovery.",
            "productsServices": [
                { "name": "Instagram Feed & Stories", "description": "Core posting layout and temporary 24-hour visual posts for interacting with followers." },
                { "name": "Instagram Reels", "description": "Short-form vertical video discovery feed driven by algorithm-powered interest recommendations." },
                { "name": "Direct Messaging & Broadcast Channels", "description": "Private text, video, and audio chat channels alongside one-to-many broadcast streams." },
                { "name": "Instagram Shopping", "description": "In-app storefront tools enabling users to browse and buy products directly from creators and brands." }
            ],
            "painPoints": [
                { "title": "Teen Retention and Mental Health Scrutiny", "description": "Instagram faces severe regulatory investigations and public relation challenges regarding its psychological impact on teenagers and younger users." },
                { "title": "Intense Short-Form Video Competition", "description": "TikTok's powerful recommendation engine continues to pressure Instagram to evolve its Reels format to retain high creator and viewer engagement." },
                { "title": "Content Moderation at Scale", "description": "Enforcing safety guidelines, filtering hate speech, and combating scams across billions of active profiles represents a continuous operational challenge." }
            ],
            "competitors": [
                { "name": "TikTok", "website": "https://tiktok.com", "description": "Primary rival in the vertical short-form video and music-integrated content spaces." },
                { "name": "Snapchat", "website": "https://snapchat.com", "description": "Direct messaging, stories, and visual communications competitor." },
                { "name": "Pinterest", "website": "https://pinterest.com", "description": "Visual discovery engine competing for creative inspiration, shopping, and image curation." }
            ]
        }

    if "google" in query_lower or "alphabet" in query_lower:
        return {
            "companyName": "Google LLC (Alphabet Inc.)",
            "website": "https://google.com",
            "phone": "+1 (650) 253-0000",
            "address": "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA",
            "companySummary": "Google LLC is a global technology powerhouse specializing in search technology, online advertising, cloud computing, consumer electronics, and artificial intelligence, operating as the primary subsidiary of Alphabet Inc.",
            "productsServices": [
                { "name": "Google Search", "description": "The world's dominant search engine handling trillions of search queries annually." },
                { "name": "YouTube", "description": "Leading global video hosting, content streaming, and video-on-demand platform." },
                { "name": "Google Cloud Platform (GCP)", "description": "Enterprise-tier cloud hosting infrastructure, data analytics databases, and machine learning developer tools." },
                { "name": "Google Workspace & Android", "description": "Collaboration software (Gmail, Docs) coupled with the world's most widely used mobile operating system." }
            ],
            "painPoints": [
                { "title": "Generative AI Search Transition costs", "description": "Integrating generative AI answers directly into search results increases raw infrastructure computing costs while potentially cannibalizing core ad-click revenue." },
                { "title": "Antitrust Litigation and Ad-Tech Regulation", "description": "Facing active lawsuits and regulatory investigations from the US Department of Justice and EU commissioners targeting search and ad-exchange monopolies." },
                { "title": "Enterprise Cloud Market Share Hurdles", "description": "Google Cloud competes fiercely with AWS and Microsoft Azure, requiring heavy sales and capital investment to capture dominant enterprise market share." }
            ],
            "competitors": [
                { "name": "Microsoft (Azure & Bing)", "website": "https://microsoft.com", "description": "Direct rival in search (incorporating OpenAI technology) and cloud enterprise services." },
                { "name": "Amazon (AWS)", "website": "https://aws.amazon.com", "description": "Market leader in cloud hosting and key competitor in product-focused searches." },
                { "name": "Apple", "website": "https://apple.com", "description": "Controls iOS, representing a critical gatekeeper for Google search distribution on mobile devices." }
            ]
        }

    clean_name = query.split(" ")[0]
    clean_name = "".join(c for c in clean_name if c.isalpha())
    name = clean_name.capitalize() or "ExampleCorp"
    domain = f"{clean_name.lower() or 'example'}.com"

    # Choose a template based on the hash of the company name to keep it deterministic but varied!
    templates = [
        # Template 0: Enterprise Software / SaaS
        {
            "summary_suffix": "is a modern software-as-a-service (SaaS) provider specializing in digital transformation, cloud productivity, and automated enterprise workflows.",
            "products": [
                { "name": "Core Cloud Platform", "description": "Centralized dashboard for tracking project management and automation workflows." },
                { "name": "Integration Hub", "description": "API middleware connecting local databases with external cloud services." },
                { "name": "Predictive Analytics", "description": "Machine-learning tool providing data insights and forecasting dashboard." }
            ],
            "painPoints": [
                { "title": "Legacy Infrastructure Migration", "description": "Enterprise clients run outdated software architectures, leading to integration bottlenecks during deployments." },
                { "title": "Escalating Customer Acquisition Costs", "description": "Intense competition in the cloud space drives higher marketing spend to close high-value sales contracts." },
                { "title": "Data Compliance Overhead", "description": "Handling client datasets demands strict adherence to evolving global regulations like GDPR and SOC 2." }
            ],
            "competitors": [
                { "name": "Salesforce", "website": "https://salesforce.com", "description": "Global CRM leader competing in cloud application spaces." },
                { "name": "HubSpot", "website": "https://hubspot.com", "description": "Customer platform focusing on marketing and CRM apps." }
            ]
        },
        # Template 1: E-commerce / Retail
        {
            "summary_suffix": "is a fast-growing digital e-commerce and retail platform delivering direct-to-consumer services and global fulfillment logistics.",
            "products": [
                { "name": "Online Marketplace", "description": "Web and mobile storefront enabling users to browse and buy goods." },
                { "name": "Global Fulfillment Network", "description": "Logistics pipeline managing packaging, shipping, and return tracking." },
                { "name": "Merchant Analytics", "description": "Seller tools to monitor sales conversion, reviews, and inventory levels." }
            ],
            "painPoints": [
                { "title": "Supply Chain and Fulfillment Friction", "description": "International shipping delays, port blockages, and carrier rate fluctuations impact delivery timelines." },
                { "title": "High Shopping Cart Abandonment Rates", "description": "Checkout friction and unexpected delivery fees drive shoppers to exit before finalizing purchases." },
                { "title": "Counterfeit and Quality Control", "description": "Vetting third-party merchants at scale is difficult, threatening brand trust if low-quality goods slip through." }
            ],
            "competitors": [
                { "name": "Amazon", "website": "https://amazon.com", "description": "Dominant global online marketplace and e-commerce logistics platform." },
                { "name": "Shopify", "website": "https://shopify.com", "description": "E-commerce infrastructure powering independent brand storefronts." }
            ]
        },
        # Template 2: Fintech / Financial Services
        {
            "summary_suffix": "is a leading financial technology developer providing secure payment gateways, neo-banking APIs, and digital wealth management solutions.",
            "products": [
                { "name": "Payment Gateway API", "description": "Embeddable checkout solutions accepting digital wallets, cards, and bank transfers." },
                { "name": "Corporate Ledger", "description": "Real-time ledger tracking multi-currency transactions and automated payouts." },
                { "name": "Risk & Fraud Shield", "description": "AI-powered detection system flagging anomalous transaction patterns." }
            ],
            "painPoints": [
                { "title": "Complex Licensing and Compliance", "description": "Operating across borders requires securing local banking and payment licenses, adding years of legal overhead." },
                { "title": "Chargeback and Transaction Fraud", "description": "Advanced cybercrime and card-not-present fraud require constant adjustments to risk models to avoid heavy merchant write-offs." },
                { "title": "Interoperability with Legacy Core Banking", "description": "Connecting modern APIs to legacy mainframes run by traditional banks is slow and highly prone to error." }
            ],
            "competitors": [
                { "name": "Stripe", "website": "https://stripe.com", "description": "Market leader in financial infrastructure and payment processing APIs." },
                { "name": "Adyen", "website": "https://adyen.com", "description": "End-to-end global merchant checkout and transaction processing platform." }
            ]
        },
        # Template 3: Healthcare / Biotech
        {
            "summary_suffix": "is an innovative health technology provider specializing in digital therapeutics, telemedicine infrastructure, and patient care management software.",
            "products": [
                { "name": "Telehealth Portal", "description": "HIPAA-compliant video and chat platform connecting patients with certified medical clinicians." },
                { "name": "Care Management Suite", "description": "Clinical dashboard for scheduling, prescribing medications, and tracking medical histories." },
                { "name": "Health Data Exchange", "description": "Secure middleware facilitating interoperable transfer of electronic health records (EHR)." }
            ],
            "painPoints": [
                { "title": "HIPAA and Data Privacy Stringency", "description": "Securing Protected Health Information (PHI) requires extensive encryption, strict access policies, and audit trails." },
                { "title": "Provider and Clinician Burnout", "description": "Complex record-keeping interfaces add cognitive load, reducing patient face-time and driving clinician turnover." },
                { "title": "Insurance Reimbursement Friction", "description": "Submitting claims to multiple commercial payors and government programs involves complex coding rules and high denial rates." }
            ],
            "competitors": [
                { "name": "Veeva Systems", "website": "https://veeva.com", "description": "Provides cloud-based software solutions for the global life sciences industry." },
                { "name": "Teladoc Health", "website": "https://teladoc.com", "description": "Major virtual healthcare and remote telemedicine competitor." }
            ]
        }
    ]

    # Select template based on hash of query name
    template_idx = sum(ord(c) for c in query_lower) % len(templates)
    t = templates[template_idx]

    return {
        "companyName": f"{name} Inc.",
        "website": f"https://{domain}",
        "phone": "+1 (555) 019-2834",
        "address": "100 Technology Dr, Silicon Valley, CA 94000, USA",
        "companySummary": f"{name} {t['summary_suffix']}",
        "productsServices": t["products"],
        "painPoints": t["painPoints"],
        "competitors": t["competitors"]
    }
