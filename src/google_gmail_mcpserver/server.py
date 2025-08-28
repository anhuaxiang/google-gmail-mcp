import os
import base64
from mcp.server.fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import List, Optional, Annotated, Literal
from pydantic import Field
from email.mime.text import MIMEText

mcp = FastMCP("netmind-mcpserver-mcp")

creds = Credentials(
    token=os.environ["GOOGLE_ACCESS_TOKEN"],
    refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["GOOGLE_CLIENT_ID"],
    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    scopes=[
        "https://www.googleapis.com/auth/gmail.labels",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.addons.current.message.action",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://mail.google.com/",
        "https://www.googleapis.com/auth/gmail.addons.current.action.compose",
    ]
)
service = build("gmail", "v1", credentials=creds)


@mcp.tool(description="Get Gmail profile of the authenticated user")
async def get_me_profile() -> dict:
    profile = service.users().getProfile(userId="me").execute()
    return profile


@mcp.tool(description="Send an email via Gmail API")
async def send_email(
        to: Annotated[
            str,
            Field(description="Recipient email address (comma-separated if multiple).")
        ],
        subject: Annotated[
            str,
            Field(description="Subject line of the email.")
        ],
        body: Annotated[
            str,
            Field(description="Plain text body content of the email.")
        ],
        cc: Annotated[
            Optional[str],
            Field(description="CC recipient email address (optional, comma-separated if multiple).")
        ] = None,
        bcc: Annotated[
            Optional[str],
            Field(description="BCC recipient email address (optional, comma-separated if multiple).")
        ] = None,
) -> dict:
    """
    Send an email using the authenticated Gmail account.
    """
    # 构建 MIME 邮件
    message = MIMEText(body, "plain", "utf-8")
    message["to"] = to
    message["subject"] = subject
    if cc:
        message["cc"] = cc
    if bcc:
        message["bcc"] = bcc

    # Gmail API 要求 base64url 编码
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    # 发送
    sent_message = (
        service.users()
        .messages()
        .send(userId="me", body={"raw": raw_message})
        .execute()
    )

    return sent_message


@mcp.tool(description="List messages from Gmail with optional filters and pagination")
async def list_messages(
        include_spam_trash: Annotated[
            Optional[bool],
            Field(
                description="Whether to include messages from SPAM and TRASH folders in the results. Default is False.")
        ] = False,
        label_ids: Annotated[
            Optional[List[str]],
            Field(description="Only return messages with all of the specified label IDs.")
        ] = None,
        max_results: Annotated[
            Optional[int],
            Field(description="Maximum number of messages to return. Default is 50. Max allowed is 500.")
        ] = 50,
        page_token: Annotated[
            Optional[str],
            Field(description="Page token to retrieve a specific page of results (for pagination).")
        ] = None,
        q: Annotated[
            Optional[str],
            Field(description=(
                    "Gmail search query string. Supports the same format as Gmail search box, "
                    'e.g., "from:someone@example.com is:unread".'
            ))
        ] = None,
) -> dict:
    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            includeSpamTrash=include_spam_trash,
            labelIds=label_ids,
            maxResults=max_results,
            pageToken=page_token,
            q=q,
        )
        .execute()
    )
    return results


@mcp.tool(description="Get a Gmail message by ID")
async def get_message(
        id: Annotated[
            str,
            Field(description="The Gmail message ID to retrieve. Usually obtained via list_messages.")
        ],
        format: Annotated[
            Optional[Literal["minimal", "full", "raw", "metadata"]],
            Field(
                description=(
                        "The format of the returned message. Allowed values:\n"
                        "- minimal: Only message ID and labels.\n"
                        "- full: Full message data with parsed payload.\n"
                        "- raw: Full message data with base64url encoded raw content.\n"
                        "- metadata: Only ID, labels, and headers."
                )
            )
        ] = "full",
        metadata_headers: Annotated[
            Optional[List[str]],
            Field(description="When format=metadata, only include these headers (e.g. ['From', 'To', 'Subject']).")
        ] = None,
) -> dict:
    """
    Retrieve a specific Gmail message.
    """
    message = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=id,
            format=format,
            metadataHeaders=metadata_headers,
        )
        .execute()
    )

    return message


@mcp.tool(description="Permanently delete a Gmail message by ID")
async def delete_message(
        id: Annotated[
            str,
            Field(description="The Gmail message ID to delete. Usually obtained via list_messages.")
        ]
):
    """
    Permanently deletes the specified Gmail message. This action cannot be undone.
    """
    service.users().messages().delete(
        userId="me",
        id=id
    ).execute()

    return {"status": "success", "message": f"Message {id} deleted."}


@mcp.tool(description="Move a Gmail message to the trash")
async def trash_message(
        id: Annotated[
            str,
            Field(description="The Gmail message ID to move to Trash. Usually obtained via list_messages.")
        ]
) -> dict:
    """
    Move the specified Gmail message to the Trash.
    """
    res = service.users().messages().trash(
        userId="me",
        id=id
    ).execute()

    return res


@mcp.tool(description="Restore a Gmail message from the trash")
async def untrash_message(
        id: Annotated[
            str,
            Field(description="The Gmail message ID to restore from Trash. Usually obtained via list_messages.")
        ]
):
    """
    Remove the specified Gmail message from the Trash.
    """
    res = service.users().messages().untrash(
        userId="me",
        id=id
    ).execute()

    return res


def main():
    mcp.run()


if __name__ == '__main__':
    main()
