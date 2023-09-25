from django.core.signing import Signer


class DebugSigner(Signer):
    def signature(self, value: bytes | str, key: "str| None" = None) -> str:
        return str(value)

    def sign(self, value: str) -> str:
        return str(value)

    def unsign(self, signed_value: str) -> str:
        return signed_value
