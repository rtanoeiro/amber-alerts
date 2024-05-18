"""Class that hold all email functions the team uses to send reports by email."""

import logging
import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

import pandas as pd

SMTP_SERVER: str = os.environ["SMTP_SERVER"]
if SMTP_SERVER is None:
    raise ValueError("SMTP_SERVER not found in environment variables")

SMTP_USERNAME: str = os.environ["SMTP_USERNAME"]
if SMTP_USERNAME is None:
    raise ValueError("SMTP_USERNAME not found in environment variables")

SMTP_PASSWORD: str = os.environ["SMTP_PASSWORD"]
if SMTP_PASSWORD is None:
    raise ValueError("SMTP_PASSWORD not found in environment variables")
EMAIL = os.environ["EMAIL"]


class Email:
    """
    Class to hold all email functions the team uses to send reports by email.
    """

    def __init__(
        self,
        to_address: List[str],
        subject: str,
        cc_addresses: Optional[List[str]] = None,
    ) -> None:
        """
        Each Email object will represent a MIMEMultipart object. Therefore a different
        email.

        As each different email, it will need to receive the following parameters:

        INPUTS
        ------
            to_address (List[str]): Addresses that will receive the email
            subject (str): Subject of email
            cc_addresses (Optional[List[str]]): List of addresses to be cced.
                Defaults to None.
        """

        self.message = MIMEMultipart()
        self.smtp_server = SMTP_SERVER
        self.smtp_username = SMTP_USERNAME
        self.smtp_password = SMTP_PASSWORD
        self.default_sender = EMAIL
        self.to_address = to_address

        self.message["From"] = self.default_sender
        self.message["To"] = ", ".join(to_address)
        self.message["Subject"] = subject
        if cc_addresses:
            self.message["Cc"] = ", ".join(cc_addresses)

    def add_dataframe_attachment(
        self,
        attachment_name: str,
        attachment_dataframe: pd.DataFrame,
    ):
        """
        This function will be used to add Dataframes as csv files to an email.
        For a better understanding of attachment types, please visit the following link:
        https://docs.python.org/3/library/email.mime.html

        We'll deal with dataframe objects only to avoid writing reports into files.

        Args:
            attachment_name (str): Name of the attachment on the email
            attachment_dataframe (pd.DataFrame): DataFrame object to be attached.
            attachment_object (bool): Python object to be attached. Defaults to False
        """

        if not isinstance(attachment_dataframe, pd.DataFrame):
            raise ValueError("Object passed is not a DataFrame")

        string_report = attachment_dataframe.to_csv(index=False)
        attachment = MIMEText(string_report, "csv")
        attachment.add_header(
            "Content-Disposition", "attachment", filename=attachment_name
        )
        self.message.attach(attachment)

    def add_image_attachment(self, image_path: str, image_name: str) -> None:
        """
        Function to add an image to the email.
        In case a report needs an image to stakeholders

        Args:
            image_path (str): Path to image file
            image_name (str): Name of the image file
        """
        with open(image_path, "rb") as image_file:
            binary_image = image_file.read()
            image = MIMEImage(binary_image, "png")
            image.add_header("Content-Disposition", "attachment", filename=image_name)
            self.message.attach(image)

    def add_email_text(self, email_text: str) -> None:
        """
        Function to add text to the body of the email.

        Args:
            email_text (str): Text to be added to the body of the email.
        """
        self.message.attach(MIMEText(email_text, "html"))

    def send_email(self) -> None:
        """
        Separate function to send constructed email object.
        """
        with smtplib.SMTP(self.smtp_server, 587) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            failed_emails = server.sendmail(
                self.default_sender, self.to_address, self.message.as_string()
            )

        if len(failed_emails) == 0:
            logging.info("Email sent successfully to all recipients")
        else:
            logging.error("Email failed to send to %s", failed_emails)
