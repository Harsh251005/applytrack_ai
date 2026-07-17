from agents import function_tool

from src.services.gmail_service import get_gmail_service


def search_emails_impl(
    query: str,
    max_results: int = 10,
) -> dict:
    """
    Searches Gmail using Gmail search syntax.

    Args:
        query: Gmail search query.
        max_results: Maximum number of emails to return.
            Examples:
            - newer_than:30d
            - subject:interview
            - from:linkedin.com
        max_results: Maximum number of emails to return.
    """

    service = get_gmail_service()

    print(f"Searching Gmail for {query}")

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            q=query,
            maxResults=max_results,
        )
        .execute()
    )

    messages = response.get("messages", [])

    results = []

    for message in messages:
        metadata = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message["id"],
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            )
            .execute()
        )

        headers = {
            h["name"]: h["value"]
            for h in metadata.get("payload", {}).get("headers", [])
        }

        results.append(
            {
                "id": metadata["id"],
                "thread_id": metadata["threadId"],
                "subject": headers.get("Subject", ""),
                "from": headers.get("From", ""),
                "date": headers.get("Date", ""),
                "snippet": metadata.get("snippet", ""),
            }
        )

    return {
        "count": len(results),
        "emails": results,
    }


@function_tool
def search_emails(
    query: str,
    max_results: int = 10,
) -> dict:
    return search_emails_impl(query, max_results)