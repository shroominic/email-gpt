import asyncio
import subprocess
import base64
import json
from pydantic import BaseModel, Field
from typing import Literal
from rich import print
from funcchain import achain


class Email(BaseModel):
    subject: str
    content: str


def get_email(nth: int) -> Email:
    apple_script = f"""
    tell application "Mail"
        set unreadMessages to (messages of inbox whose read status is false)
        if (count of unreadMessages) > {nth} then
            set theMessage to item ({nth} + 1) of unreadMessages
            set theSubject to subject of theMessage
            set theContent to content of theMessage
            set escapedSubject to do shell script "echo " & quoted form of theSubject & " | iconv -t utf-8 | base64"
            set escapedContent to do shell script "echo " & quoted form of theContent & " | iconv -t utf-8 | base64"
            set emailJson to "{{\\"subject\\": \\"" & escapedSubject & "\\", \\"content\\": \\"" & escapedContent & "\\"}}"
            return emailJson
        else
            return "{{\\"subject\\": \\"No unread email\\", \\"content\\": \\"There are no more unread emails.\\"}}"
        end if
    end tell
    """

    # Run the AppleScript and get the result
    process = subprocess.Popen(
        ["osascript", "-e", apple_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    result, error = process.communicate()

    if error:
        error_str = error.decode("utf-8").strip()
        return Email(subject="Error", content=f"Failed to retrieve email: {error_str}")

    result_str = result.decode("utf-8").strip()

    # Parse the JSON
    email_data = json.loads(result_str)

    # Decode the base64 encoded subject and content
    subject = base64.b64decode(email_data["subject"]).decode("utf-8")
    content = base64.b64decode(email_data["content"]).decode("utf-8")

    return Email(subject=subject, content=content)


def get_emails(n: int = 10) -> list[Email]:
    return [get_email(i) for i in range(n)]


class ClassifiedEmail(BaseModel):
    """Represents a one classified email."""

    title: str
    summary: str
    category: Literal["important", "business", "marketing", "personal", "spam"] = Field(
        ..., description="category of the email"
    )
    needed_action: str | None = Field(
        None,
        description=(
            "action that recipient needs to do "
            "given from the sender (eg respond back, do certain task, etc)"
        ),
    )


async def classify_email(email: Email) -> ClassifiedEmail:
    """
    Classify the given email.
    """
    return await achain()


async def main() -> None:
    emails = get_emails()

    classified_emails = await asyncio.gather(
        *[classify_email(email) for email in emails]
    )

    for email in classified_emails:
        # do something
        print(email)


if __name__ == "__main__":
    asyncio.run(main())
