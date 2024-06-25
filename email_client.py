# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
# from dotenv import load_dotenv
# import os
#
# load_dotenv()  # Load environment variables from .env file
#
#
# def str_to_bool(value: str) -> bool:
#     return value.lower() in ['true', '1', 't']
#
#
# conf = ConnectionConfig(
#     MAIL_USERNAME=os.getenv("MAIL_USERNAME", "default_username"),
#     MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "default_password"),
#     MAIL_FROM=os.getenv("MAIL_FROM", "default_email@example.com"),
#     MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
#     MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
#     MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Default Name"),
#     USE_CREDENTIALS=str_to_bool(os.getenv("USE_CREDENTIALS", "True")),
#     VALIDATE_CERTS=str_to_bool(os.getenv("VALIDATE_CERTS", "True"))
# )
#
#
# async def send_email(subject: str, email_to: str, body: str):
#     message = MessageSchema(
#         subject=subject,
#         recipients=[email_to],
#         body=body,
#         subtype="html"
#     )
#
#     fm = FastMail(conf)
#     await fm.send_message(message)



from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os
import logging
from pydantic import EmailStr, ValidationError
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def str_to_bool(value: str) -> bool:
    return value.lower() in ['true', '1', 't']

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "default_username"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "default_password"),
    MAIL_FROM=os.getenv("MAIL_FROM", "default_email@example.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Default Name"),
    USE_CREDENTIALS=str_to_bool(os.getenv("USE_CREDENTIALS", "True")),
    VALIDATE_CERTS=str_to_bool(os.getenv("VALIDATE_CERTS", "True")),
    MAIL_TLS=True,  # Ensure TLS is used
    MAIL_SSL=False  # Ensure SSL is not used
)

async def send_email(subject: str, email_to: str, body: str):
    try:
        # Validate email address
        valid_email_to = EmailStr.validate(email_to)

        message = MessageSchema(
            subject=subject,
            recipients=[valid_email_to],
            body=body,
            subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Email sent to {email_to}")

    except ValidationError as e:
        logger.error(f"Invalid email address: {email_to}. Error: {e}")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}. Error: {e}")
