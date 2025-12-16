from src.apps.notification.sms.application.interfaces.gateway import SMSGatewayProto
from src.apps.notification.sms.domain.commands import SendOTPPasswordResetSMS
from src.common.application.service import ServiceBase
from src.apps.notification.sms.domain import model as sms_model
from src.config import Configs


class SMSService(ServiceBase):
    """Service for handling SMS notifications."""
    def __init__(self, sms: SMSGatewayProto, config: Configs):
        super().__init__()
        self._sms = sms
        self._config = config

    async def send_otp_code(self, cmd: SendOTPPasswordResetSMS):
        """Send an OTP code via SMS for password reset.

        Args:
            cmd (SendPasswordResetSMS): Command containing phone number and OTP code.
        """
        sms = sms_model.OTPPasswordResetSMS(
            recipients=[cmd.phone],
            otp_code=cmd.otp_code,
            lifetime_minutes=cmd.lifetime_minutes,
        )
        await self._sms.send_sms(sms)
