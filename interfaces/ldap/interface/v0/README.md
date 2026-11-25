# ldap

## Glossary of LDAP terms

| Abbreviation |            Term            |
|:------------:|:--------------------------:|
|      DN      |     Distinguished Name     |
|     DIT      | Directory Information Tree |

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write to the application databag from the leader unit.
- MUST create a bind account in the DIT for the requirer, using the requirer's `user` and `group`, and MUST write its DN as `bind_dn`. If the requirer doesn't set `user` and `group`, SHOULD use the requirer's application name and model name.
- MUST put the bind account's password in a Juju secret, under the `password` key, MUST grant the secret to the relation, and MUST write its ID as `bind_password_secret`, rather than putting the password in the databag.
- SHOULD delete the secret when the relation is removed.
- MAY write the URLs, base DN, and StartTLS setting before it has created the bind account.
- MUST update the application databag when any of the data changes.

### Requirer

- MAY write `user` and `group` to the application databag from the leader unit, for the provider to create the bind DN.
- SHOULD avoid the [special characters in RFC 2253](https://datatracker.ietf.org/doc/html/rfc2253#section-2.4) in `user` and `group`.
- SHOULD treat the relation as not ready until the provider's application databag has `urls` and `bind_dn`.
- MUST use the LDAP configuration from the provider to configure its application, and MUST read the bind password from the secret.
