"""
Sign PDF files using a Slovenian eID card.

This module defines a very thin convenience wrapper around
:mod:`.pyhanko.sign.pkcs11` to set up a PKCS#11 session with an eID card and
read the appropriate certificates on the device.

EOI driver is available in OpenSC from version 0.24.0 . For best experience use version 0.25.0 .
Official driver based on IDProtect is not supported (yet).
"""

from pkcs11 import KeyType, ObjectClass, Session
from pyhanko.sign import pkcs11 as sign_pkcs11

tokens = {
    "opensc": {
        "Prijava brez PIN-a (Norm PIN)": {"needs_pin": False},
        "Podpis in prijava (Norm PIN)": {"needs_pin": True},
        "Podpis in prijava (Sig PIN)": {"needs_pin": True},
    },
    "nxp": {
        "Prijava brez PIN-a": {"needs_pin": False},
        "Podpis in prijava": {"needs_pin": True},
    },
}

__all__ = ["open_eoi_session", "EOISigner"]


def open_eoi_session(
    lib_location,
    token_label: str = "Podpis in prijava (Sig PIN)",
    user_pin: str | None = None,
) -> Session:
    """
    Open a PKCS#11 session

    :param lib_location:
        Path to the shared library file containing the eID PKCS#11 module.
    :param token_label:
        Token label to use. If not specified token
        labelled ``Podpis in prijava (Sig PIN)`` will be used.
        This is the only token containg key with non-repudiation.
    :param user_pin:
        Pin to authenticate to tokens ``Podpis in prijava (Sig PIN)``
        and ``Podpis in prijava (Norm PIN)``.
        Default is None, which means no authentication.
        If user_pin is None only ``Prijava brez PIN-a (Norm PIN)``
        is available, but that is not realy acceptable for signing.
    :return:
        An open PKCS#11 session object.
    """
    pksc11_lib_type = "opensc"

    if token_label in tokens[pksc11_lib_type]:
        if user_pin:
            return sign_pkcs11.open_pkcs11_session(
                lib_location, user_pin=user_pin, token_label=token_label
            )
        else:
            if not tokens[pksc11_lib_type][token_label]["needs_pin"]:
                return sign_pkcs11.open_pkcs11_session(
                    lib_location, token_label=token_label
                )
            else:
                raise sign_pkcs11.PKCS11Error(
                    "For provided token_label, you need to provide user_pin"
                )
    else:
        raise sign_pkcs11.PKCS11Error(
            "Provided token is not available on the card"
        )


class EOISigner(sign_pkcs11.PKCS11Signer):
    """
    Slovenian eID-specific signer implementation that automatically populates
    the (trustless) certificate list with the relevant certificates stored
    on the card.
    This includes the government's (self-signed) root certificate and the
    certificate of the appropriate intermediate CA.
    To be able to elevate trust of your signature use ValidationContext with
    trust_roots set to a list top issuer certs in PdfSignatureMetadata,
    because top issuer cert is self signed.
    """

    def __init__(
        self,
        pkcs11_session: Session,
        bulk_fetch: bool = False,
        embed_roots=True,
    ):
        priv = pkcs11_session.get_key(ObjectClass.PRIVATE_KEY, KeyType.EC)
        if priv is None:
            lbl = None
        else:
            lbl = priv.label
        super().__init__(
            pkcs11_session=pkcs11_session,
            cert_label=lbl,
            bulk_fetch=bulk_fetch,
            embed_roots=embed_roots,
        )
