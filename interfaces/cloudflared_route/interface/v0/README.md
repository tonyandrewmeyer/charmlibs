# cloudflared-route

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the tunnel configuration to the application databag from the leader unit.
- MUST put the cloudflared tunnel token in a Juju secret, under the `tunnel-token` key, and grant the secret to the relation.
- When the tunnel token changes, MUST either update the content of the existing secret or create a new secret and replace `tunnel_token_secret_id`.
- SHOULD remove the secret's revisions when the relation is removed.
- If it sets `nameserver`, the nameserver MUST listen on port 53.
- If it sets `nameserver`, the nameserver MUST be able to resolve public domains, and any domain configured as a backend service for the cloudflared tunnel.

### Requirer

- MUST NOT write to either databag.
- SHOULD treat the relation as not ready until `tunnel_token_secret_id` is set.
- MUST run a cloudflared tunnel with the tunnel token from the secret.
- MUST restart the tunnel with the new token when the token changes, and SHOULD use the latest revision of the secret.
- SHOULD treat the relation as invalid if the secret doesn't have a `tunnel-token` key.
- If `nameserver` is set, MUST run the tunnel with that nameserver; otherwise, MUST run the tunnel with the system's default nameserver.
- MAY be integrated with several providers, and if it is, MUST run a separate tunnel for each relation.
