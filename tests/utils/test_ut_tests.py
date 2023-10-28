from hope_country_report.utils.signer import DebugSigner


def test_signer():
    signer = DebugSigner()
    value = "abc"
    assert signer.unsign(signer.sign(value)) == value
