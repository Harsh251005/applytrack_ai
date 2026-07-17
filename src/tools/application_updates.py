from agents import function_tool

from src.tools.search_emails import search_emails_impl
from src.tools.get_email import get_email_impl



@function_tool
def check_for_application_updates(
        days: int = 30,
        max_results: int = 20
) -> dict:
    """
    Finds recent emails that may contain job application updates.
    """

    results = search_emails_impl(
        query=(
            f"newer_than:{days}d "
            "-category:promotions "
            "-category:social"
        ),
        max_results=max_results,
    )

    emails = []

    for email in results["emails"]:
        emails.append(get_email_impl(email["id"]))

    return {
        "count": len(emails),
        "emails": emails,
    }
