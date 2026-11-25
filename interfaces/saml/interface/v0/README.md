# saml

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the Identity Provider (IdP) details to the application databag from the leader unit.
- SHOULD share every `SingleSignOnService` and `SingleLogoutService` endpoint that the IdP's metadata lists for the entity, using the key names described below.
- SHOULD set `metadata_url` when the IdP's metadata is available at a URL.
- MUST update the databag when the IdP's details change, and SHOULD re-read the IdP's metadata periodically so that changes such as certificate rotation are picked up.

### Requirer

- MUST NOT write to either databag.
- SHOULD treat the relation as not ready until the provider's application databag is populated.
- SHOULD reconfigure itself when the provider's application databag changes.

## Endpoint keys

Each IdP endpoint is written as up to three keys, `<endpoint>_<method>_url`, `<endpoint>_<method>_binding`, and `<endpoint>_<method>_response_url`. `<endpoint>` is the snake-case name of the metadata element (`single_sign_on_service` or `single_logout_service`), and `<method>` is the last part of the binding, in lower case (`redirect` for `urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect`, `post` for `urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST`). The schema lists the HTTP-Redirect and HTTP-POST endpoints, but an IdP can also have endpoints with other bindings, such as `single_sign_on_service_soap_url` or `single_logout_service_artifact_url`, and requirers SHOULD ignore the ones they don't use.

## Identity providers

This interface was defined to support charms that require Launchpad group information. Other IdPs can be used interchangeably, as long as the requirer doesn't need custom attributes.
