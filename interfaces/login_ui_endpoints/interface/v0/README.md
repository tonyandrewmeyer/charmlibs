# login_ui_endpoints

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST serve the Login UI pages at the URLs that it writes.
- MUST write the URLs to the application databag from the leader unit.
- SHOULD base the URLs on its externally accessible URL, and MUST update the databag when that URL changes.

### Requirer

- MUST NOT write to either databag.
- SHOULD treat the relation as not ready until the URLs that it needs are set.
- MUST send users to the provider's pages, using the URLs, to set up its integration with the Login UI.
