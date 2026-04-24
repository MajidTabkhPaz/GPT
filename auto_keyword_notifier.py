#!/usr/bin/env python3
"""Poll a webpage for a keyword and send an email notification when found."""

from __future__ import annotations

import argparse
import os
import smtplib
import ssl
import sys
import time
from dataclasses import dataclass
from email.message import EmailMessage
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class MonitorConfig:
    url: str
    keyword: str
    interval: int
    timeout: int
    from_email: str
    to_email: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    subject: str
    notify_every_hit: bool


def parse_args() -> MonitorConfig:
    parser = argparse.ArgumentParser(
        description="Automatically refresh a website and send an email when a keyword is found."
    )
    parser.add_argument("--url", required=True, help="Website URL to monitor")
    parser.add_argument("--keyword", required=True, help="Keyword to watch for")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Seconds between refreshes (default: 60)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="HTTP timeout in seconds (default: 20)",
    )

    parser.add_argument("--from-email", default=os.getenv("FROM_EMAIL", ""))
    parser.add_argument("--to-email", default=os.getenv("TO_EMAIL", ""))
    parser.add_argument("--smtp-host", default=os.getenv("SMTP_HOST", "smtp.gmail.com"))
    parser.add_argument("--smtp-port", type=int, default=int(os.getenv("SMTP_PORT", "465")))
    parser.add_argument("--smtp-username", default=os.getenv("SMTP_USERNAME", ""))
    parser.add_argument("--smtp-password", default=os.getenv("SMTP_PASSWORD", ""))
    parser.add_argument(
        "--subject",
        default="Keyword detected on monitored page",
        help="Email subject line",
    )
    parser.add_argument(
        "--notify-every-hit",
        action="store_true",
        help="Send an email on every match instead of only the first one",
    )

    args = parser.parse_args()

    missing = []
    for field_name in [
        "from_email",
        "to_email",
        "smtp_username",
        "smtp_password",
    ]:
        if not getattr(args, field_name):
            missing.append(field_name)

    if missing:
        parser.error(
            "Missing required email settings: "
            + ", ".join(missing)
            + ". Provide args or env vars: FROM_EMAIL, TO_EMAIL, SMTP_USERNAME, SMTP_PASSWORD"
        )

    return MonitorConfig(
        url=args.url,
        keyword=args.keyword,
        interval=args.interval,
        timeout=args.timeout,
        from_email=args.from_email,
        to_email=args.to_email,
        smtp_host=args.smtp_host,
        smtp_port=args.smtp_port,
        smtp_username=args.smtp_username,
        smtp_password=args.smtp_password,
        subject=args.subject,
        notify_every_hit=args.notify_every_hit,
    )


def fetch_page(url: str, timeout: int) -> str:
    req = Request(url, headers={"User-Agent": "AutoKeywordNotifier/1.0"})
    with urlopen(req, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def send_email(config: MonitorConfig, body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = config.subject
    msg["From"] = config.from_email
    msg["To"] = config.to_email
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port, context=context) as server:
        server.login(config.smtp_username, config.smtp_password)
        server.send_message(msg)


def monitor(config: MonitorConfig) -> None:
    print(f"Monitoring {config.url} every {config.interval}s for keyword: {config.keyword!r}")
    has_alerted = False

    while True:
        try:
            html = fetch_page(config.url, config.timeout)
            if config.keyword in html:
                if config.notify_every_hit or not has_alerted:
                    body = (
                        f"Keyword '{config.keyword}' detected at {config.url}.\n"
                        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}"
                    )
                    send_email(config, body)
                    has_alerted = True
                    print("Keyword found and notification sent.")
                else:
                    print("Keyword still present; notification already sent.")
            else:
                print("Keyword not found.")
                if config.notify_every_hit:
                    has_alerted = False
        except (HTTPError, URLError) as exc:
            print(f"Request failed: {exc}", file=sys.stderr)
        except smtplib.SMTPException as exc:
            print(f"Email failed: {exc}", file=sys.stderr)

        time.sleep(config.interval)


def main() -> None:
    config = parse_args()
    monitor(config)


if __name__ == "__main__":
    main()
