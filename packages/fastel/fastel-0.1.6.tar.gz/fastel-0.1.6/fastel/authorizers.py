from typing import Any, Optional, TypeVar

import revjwt  # ignore: type
from mongoengine import DoesNotExist
from mongoengine.document import BaseDocument  # ignore: type

from . import exceptions

AuthType = TypeVar("AuthType", bound="BaseAuth")


class Credential:
    def __init__(
        self, client: BaseDocument, user: Any = None, server_call: bool = False
    ) -> None:
        self.client = client
        self.user = user
        self.server_call = server_call


class BaseAuth:
    client_model_class: BaseDocument = None

    def __init__(self, force: bool = False):
        self.force = force

    def __or__(self, other: AuthType) -> "BaseAuth":
        return OR(self, other)

    def __call__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:
        return self.verify(
            client_id=client_id, token=token, client_secret=client_secret
        )

    def verify(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:
        raise NotImplementedError("verify() should be implemented")  # pragma: no cover


class ClientIdAuth(BaseAuth):
    def __init__(self, force: bool = False):
        super().__init__(force)
        if self.client_model_class is None:
            raise ValueError(
                "client_model_class should not be None"
            )  # pragma: no cover

    def verify(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:
        if not client_id and self.force:
            raise exceptions.APIException(
                status_code=403,
                error="access_denied",
                detail="client_id is required",
            )
        if not client_id:
            return None
        try:
            client = self.client_model_class.objects.get(client_id=client_id)
        except self.client_model_class.DoesNotExist as exc:
            raise exceptions.APIException(
                status_code=403,
                error="access_denied",
                detail=f"{client_id} not found",
            ) from exc
        return Credential(client=client)


class JWBaseAuth(BaseAuth):
    expected_aud: Optional[str] = None

    def verify(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:
        if not token and self.force:
            raise exceptions.APIException(
                status_code=403,
                error="permission_denied",
                detail="token is required",
            )
        if not token:
            return None

        try:
            decoded = revjwt.decode(token)
        except Exception as exc:
            raise exceptions.APIException(
                status_code=403, error="permission_denied", detail=str(exc)
            )

        if self.expected_aud and decoded["aud"] != self.expected_aud:
            raise exceptions.APIException(
                status_code=403,
                error="permission_denied",
                detail=f"required aud: {self.expected_aud}",
            )

        if self.client_model_class:
            try:
                client = self.client_model_class.objects.get(client_id=decoded["aud"])
            except self.client_model_class.DoesNotExist as exc:
                raise exceptions.APIException(
                    status_code=403,
                    error="permission_denied",
                    detail=f"{client_id} not found",
                ) from exc
        else:
            client = None
        return Credential(client=client, user=decoded)


class ClientSecretAuth(BaseAuth):
    root_client_class: BaseDocument

    def __init__(self, force: bool = False):
        super().__init__(force)
        if self.client_model_class is None:
            raise ValueError(
                "client_model_class should not be None"
            )  # pragma: no cover

    def verify(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Credential]:

        if self.force and (client_secret is None or client_id is None):
            raise exceptions.APIException(
                status_code=403,
                error="permission_denied",
                detail="client_secret is required",
            )

        if client_secret is None or client_id is None:
            return None

        try:
            client = self.client_model_class.objects.get(client_id=client_id)
            root = self.root_client_class.objects.get(client_id=client_id)
        except DoesNotExist as exc:
            raise exceptions.APIException(
                status_code=403,
                error="permission_denied",
                detail=f"{client_id} not found",
            ) from exc

        if root.client_secret != client_secret:
            raise exceptions.APIException(
                status_code=403,
                error="permission_denied",
                detail="client_sercet not match",
            )

        return Credential(client=client, server_call=True)


class OR(BaseAuth):
    def __init__(self, left: BaseAuth, right: BaseAuth):
        super().__init__()
        self.left = left
        self.right = right

    def verify(self, *args: Any, **kwargs: Any) -> Optional[Credential]:
        result = self.left(*args, **kwargs)
        if not result:
            result = self.right(*args, **kwargs)
        return result
