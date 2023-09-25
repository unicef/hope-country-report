from django.core.signing import base64_hmac, Signer


class DebugSigner(Signer):
    def signature(self, value, key=None):
        return value

    def sign(self, value):
        return str(value)

    def unsign(self, signed_value):
        return signed_value
