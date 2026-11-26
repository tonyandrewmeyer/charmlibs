# grafana_auth

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the authentication configuration to `auth` in the application databag from the leader unit.
- MUST put the configuration under a top-level key for the authentication mode. The only mode so far is `proxy`.
- MUST use the names of Grafana's settings for that mode as the keys of the configuration. The modes and their settings are in Grafana's [authentication documentation](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/).

### Requirer

- MUST write the URLs at which Grafana can be reached to `urls` in the application databag from the leader unit.
- MUST configure Grafana's authentication as the provider describes.
- SHOULD ignore an authentication mode that it doesn't support.
