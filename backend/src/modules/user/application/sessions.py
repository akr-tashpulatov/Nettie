from typing import Protocol


class ISessionRevoker(Protocol):
    """Port for dropping a user's sessions after a credential change.

    Implemented by the auth module's token service; bound in
    `api/dependencies.py` so this layer stays free of that dependency.
    """

    async def revoke_all(self, user_id: int) -> None: ...
