import sendgrid
import sys
from sendgrid import Email, Mail, Content, ReplyTo
import pprint
import argparse
from pathlib import Path


def main(args):
    content = ""
    buf = sys.stdin.read(1024)
    while len(buf) > 0:
        content += str(buf)
        buf = sys.stdin.read(1024)

    sg = sendgrid.SendGridAPIClient(api_key=args.keypath.read_text().strip())
    from_email = Email("admin@ecko.ga", "SVS Administrátor")
    recipients = [e.strip() for e in args.emailpath.read_text().splitlines()]
    mail = Mail(
        from_email,
        "notifications@ecko.ga",
        args.subject,
        Content("text/plain", content),
    )
    mail.reply_to = ReplyTo("adam.suchy@student.gyarab.cz")
    mail.bcc = recipients

    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except Exception as e:
        pprint.pprint(e.body)
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("subject", help="subject of the email")
    parser.add_argument(
        "-k",
        "--keypath",
        help="path to a sendgrid API key",
        type=Path,
        default=Path("/opt/notifier/sendgridkey"),
    )
    parser.add_argument(
        "-e",
        "--emailpath",
        help="path to new-line delimited email recipients",
        type=Path,
        default=Path("/opt/notifier/emails"),
    )
    args = parser.parse_args()
    main(args)
