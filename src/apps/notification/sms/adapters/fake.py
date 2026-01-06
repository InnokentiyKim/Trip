from typing import Annotated

from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumberValidator

from src.apps.notification.sms.application.interfaces.gateway import SMSGatewayProto
from src.apps.notification.sms.domain.model import SMSType
from src.common.interfaces import CustomLoggerProto

PhoneNumberType = Annotated[str, PhoneNumberValidator()]


class OTPSMSSchema(BaseModel):
    template: str
    phone: PhoneNumberType
    otp_code: str
    lifetime_minutes: int


class FakeSMSAdapter(SMSGatewayProto):
    def __init__(
        self,
        logger: CustomLoggerProto,
    ) -> None:
        self._logger = logger

    async def send_sms(self, sms_details: SMSType) -> None:
        """
        Send an SMS message to a phone number.

        Args:
            sms_details (SMSType): The SMS details including recipients and template information.
        """
        self._logger.info(
            "SMS API: Sending SMS with OTP code",
            otp_code=sms_details.otp_code,
            recipients=sms_details.recipients,
        )

        # SMS schema validation
        OTPSMSSchema(
            template=sms_details.template,
            phone=sms_details.recipients[0],
            otp_code=sms_details.otp_code,
            lifetime_minutes=sms_details.lifetime_minutes,
        )

        self._logger.info(
            "SMS API: SMS with OTP code sent successfully",
            otp_code=sms_details.otp_code,
            recipients=sms_details.recipients,
        )
