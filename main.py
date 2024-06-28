import subprocess
from typing import Literal
from pydantic import BaseModel, Field


class Email(BaseModel):
    subject: str
    sender: str
    date: str
    content: str


def get_emails() -> list[Email]:
    applescript = """
    tell application "Mail"
        set allMessages to every message of inbox
        set emailData to {}
        repeat with theMessage in allMessages
            set end of emailData to {subject:subject of theMessage, sender:sender of theMessage, date:date received of theMessage, body:content of theMessage}
        end repeat
        return emailData
    end tell
    """

    try:
        emails = subprocess.run(
            ["osascript", "-e", applescript], capture_output=True, text=True, check=True
        )
        return [Email(**email) for email in eval(emails.stdout)]
    except subprocess.CalledProcessError as e:
        print(f"Error executing AppleScript: {e}")
        return []


class ClassifiedEmail(BaseModel):
    """Represents a one classified email."""

    title: str
    summary: str
    category: Literal[
        "important",
        "business",
        "marketing",
        "personal",
        "spam",
    ] = Field(..., description="category of the email")
