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
    assert redact("Blinkit/YESB/pa ytm-blin/Blink 0097694162092 AT 31821") \
        == "Blinkit/YESB/pa ytm-blin/Blink AT", redact("Blinkit 0097694162092 AT 31821")
    assert redact("CRED Club cred.club@axisbank") == "CRED Club", redact("CRED Club cred.club@axisbank")
    assert redact("Snapmint T219097") == "Snapmint T"
    assert redact("CHAYAN") == "CHAYAN"  # plain name untouched
    print("redact OK")
