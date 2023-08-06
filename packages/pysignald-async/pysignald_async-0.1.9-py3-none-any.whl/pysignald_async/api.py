import asyncio
import typing

from pysignald_async.error import SignaldException
from pysignald_async.generated import *
import pysignald_async.util as util


class SignaldAPI(SignaldGeneratedAPI):
    async def get_response_and_wait_for(
        self, request: dict, validator: typing.Callable
    ):
        future = self.get_future_for(validator)
        try:
            await self.get_response(request)
        except SignaldException:
            self.specific_handlers.remove(future.handler)
            future.cancel()
            raise
        else:
            await future

    async def subscribe(self, username: str):
        """
        Starts receiving messages for the account identified by the argument
        username (a phone number).
        """
        await self.get_response_and_wait_for(
            request={"type": "subscribe", "username": username},
            validator=lambda response: response.get("type") == "listen_started"
            and response.get("data") == username,
        )

    async def unsubscribe(self, username: str):
        """
        Stops receiving message for an phone 'username'.
        """
        await self.get_response({"type": "unsubscribe", "username": username})

    async def verify(self, username: str, code: str):
        await self.get_response({"type": "verify", "username": username, "code": code})

    async def register(self, username: str, captcha: str = None):
        """
        Register signald as the primary signal device for a phone number.
        To complete to process, the SignaldAPI.verify coroutine must then be
        awaited with the code received by SMS.
        """
        payload = {"type": "register", "username": username}
        if captcha is not None:
            payload["captcha"] = captcha
        await self.get_response(payload)

    async def list_accounts(self) -> JsonAccountListv0:
        data = await self.get_response({"type": "list_accounts"})
        return JsonAccountListv0(**data)

    def handle_message(self, payload):
        envelope = JsonMessageEnvelopev1(**payload.get("data", dict()))
        self.handle_envelope(envelope)

    def handle_envelope(self, envelope):
        print(envelope)
