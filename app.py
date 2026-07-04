import streamlit as st
import os
import json
from utils.serper import resolve_official_website, get_company_details, find_competitors_serp
from utils.crawler import crawl_website
from utils.openrouter import query_openrouter, OPENROUTER_MODELS
from utils.pdf_generator import generate_company_report_pdf
from utils.discord_client import send_report_to_discord

# 1. Page Configuration & Layout
st.set_page_config(
    page_title="Enterprise Company Research Analyst Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (injecting custom CSS rules)
st.markdown("""
<style>
    /* Styling variables and general colors */
    .stApp {
        background-color: #0b0f19;
        background-image: 
            radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.1) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.08) 0px, transparent 50%);
    }
    
    /* Font custom settings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* Glassmorphic boxes */
    .report-box {
        background-color: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }
    
    .metric-card {
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 10px;
        padding: 12px 16px;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f3f4f6;
    }
    
    .bullet-item {
        background-color: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
    
    .bullet-title {
        font-weight: 600;
        font-size: 0.9rem;
        color: #fff;
        margin-bottom: 4px;
    }
    
    .bullet-desc {
        font-size: 0.85rem;
        color: #9ca3af;
        line-height: 1.4;
    }
    
    .pain-point-item {
        border-left: 3px solid #ef4444;
        background-color: rgba(239, 68, 68, 0.02);
    }
    
    .competitor-card {
        background-color: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 12px;
        transition: transform 0.2s ease;
    }
    
    .competitor-card:hover {
        transform: translateY(-2px);
        border-color: rgba(79, 70, 229, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# 2. State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Sidebar Panel Configuration
st.sidebar.markdown("<div style='display:flex; align-items:center; gap:10px; margin-bottom:20px;'><div style='background:linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold; box-shadow:0 4px 14px rgba(79, 70, 229, 0.4)'>C</div><h2 style='margin:0; font-size:1.2rem; background:linear-gradient(120deg, #fff 40%, #c7d2fe 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>Company Intelligence</h2></div>", unsafe_allow_html=True)

st.sidebar.subheader("AI Processing Model")
selected_model = st.sidebar.selectbox(
    "Select Model",
    options=[m["id"] for m in OPENROUTER_MODELS],
    format_func=lambda x: next(m["name"] for m in OPENROUTER_MODELS if m["id"] == x),
    key="selected_model"
)

st.sidebar.subheader("API Keys (Optional)")
serper_key = st.sidebar.text_input("Serper.dev API Key", type="password", key="serper_key")
openrouter_key = st.sidebar.text_input("OpenRouter API Key", type="password", key="openrouter_key")
st.sidebar.caption("Leave blank to fallback to system environment variables or demo profiles.")

st.sidebar.subheader("Discord Delivery Config")
discord_token = st.sidebar.text_input("Discord Bot Token", type="password", key="discord_token")
discord_channel = st.sidebar.text_input("Discord Channel ID", key="discord_channel")
applicant_name = st.sidebar.text_input("Applicant Name", key="applicant_name")
applicant_email = st.sidebar.text_input("Applicant Email", key="applicant_email")

# Save configurations to local memory session state on button click
if st.sidebar.button("Save Configuration Parameters", use_container_width=True):
    st.sidebar.success("Configuration updated successfully!")

# 4. Main Chat Area Header
st.title("Interactive Research Chat Agent")
st.caption("AI-powered company profiler. Submit a company name or website domain to get started.")

# Render Welcome Info Screen if empty chat
if not st.session_state.messages:
    st.markdown("""
    <div class="report-box" style="text-align: center; max-width: 700px; margin: 40px auto 0 auto;">
        <h2 style="margin-bottom:12px; background: linear-gradient(135deg, #fff 30%, #a5b4fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Enterprise Company Profiler</h2>
        <p style="color: #9ca3af; font-size: 0.95rem; line-height: 1.6; margin-bottom: 20px;">
            Input a company name (e.g. <b>Tesla</b>) or a website URL (e.g. <b>https://stripe.com</b>) in the message box below. 
            The agent will perform site crawling, search public contact files, generate a professional report PDF, and deliver details directly to your Discord integrations.
        </p>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; text-align: left;">
            <div style="background-color:rgba(255,255,255,0.02); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.03)">
                <div style="font-weight:600; color:#fff; font-size:0.85rem; margin-bottom:4px;">🕷️ Crawler</div>
                <div style="font-size:0.75rem; color:#6b7280;">Resolves internal page nodes and scrapes relevant text segments.</div>
            </div>
            <div style="background-color:rgba(255,255,255,0.02); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.03)">
                <div style="font-weight:600; color:#fff; font-size:0.85rem; margin-bottom:4px;">🤖 AI Analysis</div>
                <div style="font-size:0.75rem; color:#6b7280;">Identifies corporate summary summaries, list services, and pain points.</div>
            </div>
            <div style="background-color:rgba(255,255,255,0.02); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.03)">
                <div style="font-weight:600; color:#fff; font-size:0.85rem; margin-bottom:4px;">📄 PDF Creator</div>
                <div style="font-size:0.75rem; color:#6b7280;">Produces formatted high-contrast page reports for offline reading.</div>
            </div>
            <div style="background-color:rgba(255,255,255,0.02); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.03)">
                <div style="font-weight:600; color:#fff; font-size:0.85rem; margin-bottom:4px;">📬 Discord Publish</div>
                <div style="font-size:0.75rem; color:#6b7280;">Automatically streams report buffers directly to Discord channels.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["sender"]):
        if "text" in msg:
            st.write(msg["text"])
        if "report_data" in msg:
            data = msg["report_data"]
            pdf_bytes = msg.get("pdf_bytes")
            discord_status = msg.get("discord_status", False)
            
            # Draw beautiful company report card
            st.markdown(f"""
            <div class="report-box">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;">
                    <div>
                        <h3 style="margin:0; color:#fff; font-size:1.5rem;">{data['companyName']}</h3>
                        <a href="{data['website']}" target="_blank" style="color:#06b6d4; font-size:0.85rem; text-decoration:none;">{data['website']} ↗</a>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Metadata Columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📞 Phone</div>
                    <div class="metric-value">{data['phone']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📍 HQ Address</div>
                    <div class="metric-value">{data['address']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                status_color = "#10b981" if discord_status else "#6b7280"
                status_text = "Delivered to Discord" if discord_status else "Discord Not Configured"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">📬 Delivery Status</div>
                    <div class="metric-value" style="color: {status_color}; font-weight: bold;">{status_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Download PDF button in streamlit
            if pdf_bytes:
                safe_name = "".join(c for c in data['companyName'] if c.isalnum() or c in (" ", "_")).replace(" ", "_")
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"{safe_name}_Research_Report.pdf",
                    mime="application/pdf",
                    key=f"dl_{msg['id']}"
                )
                
            # Summary
            st.markdown("#### 🏢 Executive Summary")
            st.write(data["companySummary"])
            
            # Products & Services
            st.markdown("#### 📋 Key Products & Services")
            for prod in data.get("productsServices", []):
                st.markdown(f"""
                <div class="bullet-item">
                    <div class="bullet-title">{prod.get('name')}</div>
                    <div class="bullet-desc">{prod.get('description')}</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Pain Points
            st.markdown("#### ⚠️ AI-Generated Pain Points")
            for point in data.get("painPoints", []):
                st.markdown(f"""
                <div class="bullet-item pain-point-item">
                    <div class="bullet-title" style="color:#fca5a5;">{point.get('title')}</div>
                    <div class="bullet-desc">{point.get('description')}</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Competitors
            st.markdown("#### ⚔️ Suggested Competitors")
            comp_cols = st.columns(len(data.get("competitors", [])) or 1)
            for idx, comp in enumerate(data.get("competitors", [])):
                with comp_cols[idx % len(comp_cols)]:
                    st.markdown(f"""
                    <div class="competitor-card">
                        <div style="font-weight:600; font-size:0.9rem; color:#fff;">{comp.get('name')}</div>
                        <a href="{comp.get('website')}" target="_blank" style="color:#06b6d4; font-size:0.78rem; text-decoration:none;">{comp.get('website')} ↗</a>
                        <div style="font-size:0.75rem; color:#9ca3af; margin-top:6px; font-style:italic;">{comp.get('description', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)

# 5. Handle Chat Submissions
if user_query := st.chat_input("Enter company name or website domain..."):
    # Add user message
    st.session_state.messages.append({"id": f"usr_{len(st.session_state.messages)}", "sender": "user", "text": user_query})
    st.rerun()

# Execute pipeline logic if the last message is from user
if st.session_state.messages and st.session_state.messages[-1]["sender"] == "user":
    current_query = st.session_state.messages[-1]["text"]
    
    with st.chat_message("assistant"):
        # Streamlit collapsible status tracking component (UI/UX Wow factor!)
        with st.status("Analyzing company details...", expanded=True) as status:
            # Step 1: URL Resolution
            st.write("Resolving official company URL...")
            resolved_url = current_query.strip()
            is_url = bool(re.match(r'^(https?://)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$', resolved_url, re.IGNORECASE) and " " not in resolved_url)
            company_name_val = current_query.strip()
            
            if not is_url:
                try:
                    resolved_url = resolve_official_website(company_name_val, serper_key)
                except Exception:
                    clean = "".join(c for c in company_name_val if c.isalnum()).lower()
                    resolved_url = f"https://www.{clean or 'example'}.com"
            else:
                if not resolved_url.startswith("http://") and not resolved_url.startswith("https://"):
                    resolved_url = f"https://{resolved_url}"
                try:
                    url_obj = urlparse(resolved_url)
                    company_name_val = url_obj.hostname.replace("www.", "").split(".")[0].capitalize()
                except Exception:
                    pass
            st.write(f"Resolved website to: {resolved_url}")
            
            # Step 2: Website Crawling
            st.write("Crawling website pages (About, Products, Solutions, Contact)...")
            crawled_pages = []
            try:
                crawled_pages = crawl_website(resolved_url)
            except Exception as e:
                print(f"Crawl error: {e}")
                
            crawled_text = "\n---\n".join(
                f"[URL: {p['url']}]\nTitle: {p['title']}\nHeadings: {', '.join(p['headings'])}\nExcerpt: {p['contentExcerpt']}\n"
                for p in crawled_pages
            )
            st.write(f"Scraped {len(crawled_pages)} pages successfully.")
            
            # Step 3: Scrape public details from Serper
            st.write("Searching Google for company details, addresses, and phone numbers...")
            phone = "Not Available"
            address = "Not Available"
            serp_description = ""
            try:
                url_host = urlparse(resolved_url).hostname.replace("www.", "")
                details = get_company_details(url_host, serper_key)
                phone = details.get("phone", "Not Available")
                address = details.get("address", "Not Available")
                serp_description = details.get("infoSnippet", "")
            except Exception as e:
                print(f"Serp details error: {e}")
                
            serp_text = f"Company Name: {company_name_val}\nWebsite: {resolved_url}\nPhone: {phone}\nAddress: {address}\nDescription Summary: {serp_description}"
            st.write("Retrieved company contact details.")
            
            # Step 4: AI Analysis on OpenRouter
            st.write(f"Querying OpenRouter ({selected_model}) for business summaries and pain points...")
            try:
                report_data = query_openrouter(
                    company_name_val,
                    crawled_text or "No content found from website crawl.",
                    serp_text,
                    selected_model,
                    openrouter_key
                )
            except Exception as e:
                st.error("AI Analysis failed!")
                report_data = None
                
            if report_data:
                # Merge crawled metadata overrides
                if phone != "Not Available" and report_data.get("phone", "Not Available") == "Not Available":
                    report_data["phone"] = phone
                if address != "Not Available" and report_data.get("address", "Not Available") == "Not Available":
                    report_data["address"] = address
                if "website" not in report_data or report_data.get("website", "Not Available") == "Not Available":
                    report_data["website"] = resolved_url
                    
                st.write("Synthesized corporate research insights.")
                
                # Step 5: PDF Generation
                st.write("Compiling PDF report document...")
                pdf_bytes = generate_company_report_pdf(
                    report_data,
                    applicant_name,
                    applicant_email
                )
                st.write("Generated PDF document.")
                
                # Step 6: Discord webhook dispatch
                discord_status = False
                if discord_token and discord_channel:
                    st.write("Sending report to Discord channel...")
                    discord_status = send_report_to_discord(
                        pdf_bytes,
                        report_data["companyName"],
                        report_data["website"],
                        {
                            "botToken": discord_token,
                            "channelId": discord_channel,
                            "applicantName": applicant_name,
                            "applicantEmail": applicant_email
                        }
                    )
                    st.write("Dispatched message and attachment file to Discord Bot API.")
                    
                status.update(label="Research Complete!", state="complete")
                
                # Append assistant message to chat history
                st.session_state.messages.append({
                    "id": f"ast_{len(st.session_state.messages)}",
                    "sender": "assistant",
                    "report_data": report_data,
                    "pdf_bytes": pdf_bytes,
                    "discord_status": discord_status
                })
            else:
                status.update(label="Failed to complete research", state="error")
                st.session_state.messages.append({
                    "id": f"ast_{len(st.session_state.messages)}",
                    "sender": "assistant",
                    "text": "Failed to retrieve company data. Please double-check your API configurations and try again."
                })
                
        # Trigger refresh to display the newly added report card
        st.rerun()
