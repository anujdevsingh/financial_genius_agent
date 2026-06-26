"""Redaction for anything sent to an external LLM (OpenAI).

Bank statements carry account numbers, customer/reference IDs and UPI VPAs.
We strip those before they leave the machine. Merchant/payee names are kept
(the advisor needs them); only 4+ digit identifiers and email/VPA handles go.
Amounts are passed to the model as numbers, never through this text path, so
stripping digit-runs here never touches money values.
"""

import re

_LONG_DIGITS = re.compile(r"\d{4,}")
_VPA = re.compile(r"\b[\w.\-]+@[\w.\-]+\b")
_MULTISPACE = re.compile(r"\s{2,}")


def redact(text) -> str:
    """Remove account/reference numbers and UPI VPAs from `text`."""
    t = _VPA.sub("", str(text))
    t = _LONG_DIGITS.sub("", t)
    return _MULTISPACE.sub(" ", t).strip()


if __name__ == "__main__":  # ponytail: smallest check that redaction holds
    # Synthetic examples only — no real statement data.
    assert redact("Merchant/BANK/handle/Pay 1234567890123 AT 00000") \
        == "Merchant/BANK/handle/Pay AT", redact("Merchant 1234567890123 AT 00000")
    assert redact("Example Co example@bank") == "Example Co", redact("Example Co example@bank")
    assert redact("Sample T999999") == "Sample T"
    assert redact("FIRSTNAME") == "FIRSTNAME"  # plain name untouched
    print("redact OK")
