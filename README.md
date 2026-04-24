# Auto Keyword Notifier

A small Python app that automatically refreshes a website and emails you when a specific keyword appears.

## Features

- Polls a webpage at a configurable interval.
- Checks for a specific keyword in the HTML.
- Sends an email notification via SMTP over SSL when the keyword is found.
- Can notify once per run (default) or on every hit.

## Setup

1. Install dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. Set email environment variables (recommended):

   ```bash
   export FROM_EMAIL="your@email.com"
   export TO_EMAIL="your@email.com"
   export SMTP_HOST="smtp.gmail.com"
   export SMTP_PORT="465"
   export SMTP_USERNAME="your@email.com"
   export SMTP_PASSWORD="your-app-password"
   ```

## Usage

```bash
python3 auto_keyword_notifier.py \
  --url "https://example.com" \
  --keyword "in stock" \
  --interval 30
```

Optional flags:

- `--notify-every-hit`: send an email every time the keyword is seen.
- `--subject "Custom subject"`: customize the email subject line.
- `--timeout 20`: request timeout in seconds.

## Notes

- For Gmail, use an **App Password** instead of your regular account password.
- Keep this process running (e.g., in a `tmux` session or as a systemd service) for continuous monitoring.
