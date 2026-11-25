# opencti_connector

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the application databag from the leader unit.
- MUST relate to at most one OpenCTI application.
- If it sets `connector_id`, MUST generate it once and keep it for the life of the relation.
- MUST read the API token from the `token` key of the secret in `opencti_token`, and SHOULD use the latest revision of that secret when it changes.
- SHOULD wait until both `opencti_url` and `opencti_token` are set before connecting to OpenCTI.

### Requirer

- MUST write the application databag from the leader unit.
- SHOULD NOT write anything until the provider has set both `connector_charm_name` and `connector_type`.
- MUST create an OpenCTI user for each connector, with privileges that suit its `connector_type`, and put that user's API token in a Juju secret under the `token` key.
- MUST grant that secret to the relation.
- MUST update the secret's content when the user's API token changes, and MUST update `opencti_url` when the URL that OpenCTI is reachable at changes.
- SHOULD deactivate the OpenCTI user of a connector when its relation is removed.
- MAY relate to any number of connectors.

## Implementation notes

The `opencti_connector` library provides a base class, `OpenctiConnectorCharm`, that implements the provider side for connector charms. A connector charm that inherits from it:

- MUST implement the `connector_type` property.
- MUST implement the `charm_dir` property, returning the charm's root directory (the one with `charmcraft.yaml` in it), so the class can read the charm's configuration options and pass them to the connector as environment variables.

The class also sets `connector_charm_name` to the charm's name (not the application's), sets `connector_id` to a random UUID if it isn't set yet, and blocks if the application has more than one unit.
