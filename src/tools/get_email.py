import base64

from agents import function_tool

from src.services.gmail_service import get_gmail_service


def get_email_impl(email_id: str) -> dict:
    """
    Retrieves the full content of an email.

    Args:
        email_id: Gmail message ID.
    """

    service = get_gmail_service()

    print(f"[TOOL] Getting email: {email_id}")

    message = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=email_id,
            format="full",
        )
        .execute()
    )

    headers = {
        h["name"]: h["value"]
        for h in message["payload"].get("headers", [])
    }

    body = ""

    def extract_text(part):
        nonlocal body

        if part.get("mimeType") == "text/plain":
            data = part["body"].get("data")
            if data:
                body += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        for child in part.get("parts", []):
            extract_text(child)

    extract_text(message["payload"])

    return {
        "id": message["id"],
        "thread_id": message["threadId"],
        "subject": headers.get("Subject", ""),
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "date": headers.get("Date", ""),
        "body": body,
        "snippet": message.get("snippet", ""),
    }


@function_tool
def get_email(email_id: str) -> dict:
    return get_email_impl(email_id)