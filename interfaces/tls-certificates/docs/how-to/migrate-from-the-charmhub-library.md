---
myst:
  html_meta:
    description: Move a charm from the Charmhub-hosted charms.tls_certificates_interface.v4 library to charmlibs.interfaces.tls_certificates.
---

# Migrate from the Charmhub library

This guide is for a charm that vendors `charms.tls_certificates_interface.v4` under `lib/` and wants to use `charmlibs.interfaces.tls_certificates` instead. The steps are the same for a requirer and a provider charm.

Read more: {ref}`charmhub-libraries-deprecation`

## Existing keys and certificates survive the upgrade

The move is an in-place upgrade. This library keeps the `LIBID` of the Charmhub library it was ported from, and it builds every Juju secret label from that `LIBID`, so after the upgrade it finds the private key and the certificates that the previous revision of the charm stored. It also carries shims for the labels that older versions wrote, including the ones from `charms.tls_certificates_interface.v4` before `LIBPATCH` 30.

So there's nothing to migrate and nothing to rotate: the certificates your units are serving stay valid, and the provider doesn't have to issue new ones.

```{note}
The reverse isn't true. If your charm manages its own private key and is handing that job to the library for the first time, the library generates a new key, and that does cause one certificate rotation. See [the library design](../explanation/design.md).
```

## Add the dependency

Add `charmlibs-interfaces-tls-certificates` to your charm's Python dependencies, in `requirements.txt` or in `pyproject.toml`. The package declares its own dependencies, so you can drop the entries you added by hand to satisfy the Charmhub library's `PYDEPS`, unless your charm uses them directly.

## Stop fetching the Charmhub library

Remove the library from the `charm-libs` section of `charmcraft.yaml`:

```diff
 charm-libs:
-  - lib: tls_certificates_interface.tls_certificates
-    version: "4"
```

Remove the entry as well as deleting `lib/charms/tls_certificates_interface/`. `charmcraft pack` downloads any library listed in `charm-libs` that's missing from `lib/`, so otherwise your charm ends up shipping both.

## Change the imports

The class and function names are unchanged, so the import is the only edit in the charm code:

```diff
-from charms.tls_certificates_interface.v4.tls_certificates import (
+from charmlibs.interfaces.tls_certificates import (
     Certificate,
     CertificateRequestAttributes,
     Mode,
     PrivateKey,
     TLSCertificatesRequiresV4,
 )
```

Check the charm's tests as well. A `unittest.mock.patch` of a class or method, such as `TLSCertificatesRequiresV4.get_assigned_certificate`, only needs the new path, `charmlibs.interfaces.tls_certificates`. A patch of a module-level function that the library calls itself, `calculate_relative_datetime` or `chain_has_valid_order`, won't be seen through that path, because the package re-exports those names from a private module.
