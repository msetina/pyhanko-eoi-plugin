python-eoi-plugin
=================


Introduction
^^^^^^^^^^^^

This package provides a plugin for `pyHanko <https://github.com/MatthiasValvekens/pyHanko>`_'s
PDF signing CLI. The implementation is a very thin convenience wrapper around the PKCS#11
functionality included within the "core" pyHanko library.


Installation
^^^^^^^^^^^^

Assuming you are installing with ``pip``, running
``pip install pyhanko-eoi-plugin`` will install both pyHanko and the plugin.
If you already have a working pyHanko install, take care to ensure that
the plugin is installed in the same Python environment.

PyHanko makes use of Python's package entry point mechanism to discover
plugins, so installing both side-by-side should suffice. To test whether
everything works, run ``pyhanko sign addsig`` and verify that ``eoi``
appears in the list of subcommands.


Installation troubleshooting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're having issues getting the plugin autodection to work, you can
also add the following snippet to your PyHanko configuration file:

.. code-block:: yaml

   plugins:
     - pyhanko_eoi.cli:EOIPlugin


This will work as long as you ensure that ``pyhanko_eoi`` is importable.



Signing a PDF file using a Slovenian eOI card
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To sign a PDF file using your eOI card and pyHanko's CLI (with this plugin),
use the ``eoi`` subcommand to ``addsig``, with the ``--lib`` parameter to
tell pyHanko where to look for the eOI PKCS#11 library.

.. note::
    Of course, you can also use the ``pkcs11`` subcommand, but ``eoi`` provides an extra layer
    of convenience.

On Linux, it is named ``opensc-pkcs11.so`` and can usually be found under
``/usr/lib`` or ``/usr/local/lib``.
On macOS, it is named ``opensc-pkcs11.dylib``, and can similarly be found under
``/usr/local/lib``.
The Windows version is typically installed to ``C:\Windows\System32`` and is
called ``opensc-pkcs11.dll``.


On Linux, this boils down to the following:

.. code-block:: bash

    pyhanko sign addsig --field Sig1 eoi --user-pin 12345 \
        --lib /path/to/opensc-pkcs11.so input.pdf output.pdf


.. warning::
    This command will produce a non-repudiable signature using the 'Signature'
    certificate on your eOI card. These signatures are legally equivalent to
    a normal "wet" signature wherever they are allowed, so use them with care.

    In particular, you should only allow software you trust\ [#disclaimer]_
    to use the 'Signature' certificate!

.. [#disclaimer]
    This obviously also applies to pyHanko itself.

