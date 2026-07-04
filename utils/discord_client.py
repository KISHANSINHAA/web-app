import requests
import json

def send_report_to_discord(
    pdf_bytes: bytes,
    company_name: str,
    company_website: str,
    config: dict
) -> bool:
    bot_token = config.get("botToken", "").strip()
    channel_id = config.get("channelId", "").strip()
    applicant_name = config.get("applicantName", "").strip()
    applicant_email = config.get("applicantEmail", "").strip()

    if not bot_token or not channel_id:
        print("Discord configuration details are incomplete. Skipping Discord dispatch.")
        return False

    # Format bot token (ensure it starts with 'Bot ')
    formatted_token = bot_token if bot_token.startswith("Bot ") else f"Bot {bot_token}"

    try:
        # Prepare message content
        message_payload = {
            "content": (
                f"🔍 **New Company Research Report Generated**\n\n"
                f"👤 **Applicant Details:**\n"
                f"• **Name:** {applicant_name or 'Not Provided'}\n"
                f"• **Email:** {applicant_email or 'Not Provided'}\n\n"
                f"🏢 **Research Details:**\n"
                f"• **Company:** {company_name}\n"
                f"• **Website:** {company_website or 'Not Available'}\n\n"
                f"📄 The generated PDF report is attached below."
            )
        }

        # Prepare file attachment
        safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")
        filename = f"{safe_company_name}_Research_Report.pdf"

        # Construct multipart payload
        files = {
            "files[0]": (filename, pdf_bytes, "application/pdf")
        }
        data = {
            "payload_json": json.dumps(message_payload)
        }

        print(f"Uploading report to Discord channel: {channel_id}")
        
        response = requests.post(
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers={
                "Authorization": formatted_token,
            },
            data=data,
            files=files,
            timeout=15
        )

        if response.status_code in (200, 201):
            print("Successfully posted research report and applicant metadata to Discord channel!")
            return True
        else:
            print(f"Discord API error ({response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"Error pushing report to Discord: {e}")
        return False
