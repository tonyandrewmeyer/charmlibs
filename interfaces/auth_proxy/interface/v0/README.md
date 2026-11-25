# auth_proxy

## Direction

The provider is part of an Identity and Access Proxy, and doesn't write to the relation. It turns the requirer's configuration into access rules, and passes the names of the applications to protect to the ingress over the `forward_auth` interface. The ingress then asks the provider whether each request to those applications is allowed.

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST NOT write to either databag.
- MUST require authentication for requests to the requirer's protected URLs, except for its allowed endpoints.
- MUST set the requested headers on requests after a successful authentication, if it supports them.
- If `authenticated_emails` or `authenticated_email_domains` is set and not empty, SHOULD only allow access to users with those email addresses or in those domains.
- SHOULD ignore data that isn't valid, and SHOULD log an error when it does.
- MUST stop protecting the requirer when the relation is removed.

### Requirer

- MUST write to the application databag from the leader unit.
- MUST have ingress, and MUST set `protected_urls` to its ingress URLs once it has them.
- MUST only request headers that the provider supports.
- SHOULD update the databag when its ingress URLs or configuration change.
- SHOULD clear the application databag when the relation is removed.
