import contextlib
from typing import ContextManager, List, Optional

import click
from pyhanko.cli._ctx import CLIContext
from pyhanko.cli.commands.signing.pkcs11_cli import (
    UNAVAIL_MSG,
    pkcs11_available,
)
from pyhanko.cli.config import CLIConfig
from pyhanko.cli.plugin_api import SigningCommandPlugin
from pyhanko.cli.utils import logger, readable_file
from pyhanko.sign import Signer


class EOIPlugin(SigningCommandPlugin):
    subcommand_name = "eoi"
    help_summary = "use Slovenian eOI to sign"
    unavailable_message = UNAVAIL_MSG

    def is_available(self) -> bool:
        return pkcs11_available

    def click_options(self) -> List[click.Option]:
        return [
            click.Option(
                ("--lib",),
                help="path to opensc-pkcs11 library file",
                type=readable_file,
                required=False,
            ),
            click.Option(
                ("--token_label",),
                help="specify PKCS#11 token",
                required=False,
                type=str,
                default="Podpis in prijava (Sig PIN)",
            ),
            click.Option(
                ("--user_pin",),
                help="specify user pin for accessing the token",
                required=False,
                type=str,
                default=None,
            ),
        ]

    def create_signer(
        self, context: CLIContext, **kwargs
    ) -> ContextManager[Signer]:
        return _eoi_signer_context(context, **kwargs)


def _eoi_signer_context(ctx: CLIContext, lib, token_label, user_pin):
    from pkcs11 import PKCS11Error

    from pyhanko_eoi import eoi

    module_path: str
    if not lib:
        cli_config: Optional[CLIConfig] = ctx.config
        eoi_module_path = None
        if cli_config is not None:
            eoi_module_path = cli_config.raw_config.get("eoi-module-path", None)
        if eoi_module_path is None:
            raise click.ClickException(
                "The --lib option is mandatory unless eoi-module-path is "
                "provided in the configuration file."
            )
        module_path = eoi_module_path
    else:
        module_path = lib

    @contextlib.contextmanager
    def manager():
        try:
            session = eoi.open_eoi_session(
                module_path, token_label=token_label, user_pin=user_pin
            )
        except PKCS11Error as e:
            logger.error("PKCS#11 error", exc_info=e)
            raise click.ClickException(
                f"PKCS#11 error: [{type(e).__name__}] {e}"
            )

        with session:
            yield eoi.EOISigner(session)

    return manager()
