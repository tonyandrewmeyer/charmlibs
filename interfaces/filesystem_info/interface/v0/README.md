# filesystem_info

## Behavior

Keywords are as in RFC 2119.

### Provider

- MUST write the `endpoint` to the application databag from the leader unit.
- MUST write an `endpoint` that follows the grammar and the requirements in "Endpoint format".
- MUST export mount information for a valid and accessible shared filesystem.
- MUST provide sensitive data as a Juju secret where possible. Only charms that cannot create secrets MAY provide their sensitive data as plain text.
- If the `endpoint` has the ID of a Juju secret, MUST grant that secret to the relation.
- MUST update the `endpoint` when the mount information changes.

### Requirer

- MUST NOT write to either databag.
- MUST be able to parse the `endpoint` according to the grammar in "Endpoint format".
- MUST either support mounting the provider's exported filesystem, or gracefully handle when it cannot mount it.
- SHOULD treat the relation as not ready until the provider has written the `endpoint`.
- If the `endpoint` has the ID of a Juju secret, SHOULD use the latest revision of that secret.
- SHOULD unmount the filesystem when the relation is removed.

## Endpoint format

The `endpoint` MUST be in a sublanguage of the URI grammar, which is specified by [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986#appendix-A). The specific sublanguage is defined by the following grammar in Augmented Backus–Naur form:

```
key = 1*( unreserved )
value = 1*( unreserved / ":" / "/" / "?" / "#" / "[" / "]" / "@" / "!" / "$"
      / "'" / "(" / ")" / "*" / "+" / "," / ";" )
options = key "=" value ["&" options]

host-port = host [":" port]
hosts = host-port ["," hosts]
authority = [userinfo "@"] "(" hosts ")"

endpoint = scheme "://" authority path-absolute ["?" options]
```

Any unspecified grammar rule is specified by RFC 3986.

Additionally, the `endpoint` MUST meet these requirements:

- The `scheme` component MUST identify the type of filesystem that needs to be mounted by the client, for example `nfs`, `cephfs`, or `lustre`.
- The `userinfo` component MAY contain a user for authentication purposes, but it MUST NOT contain any password required to authenticate against the filesystem. In other words, the `user:password` syntax is not allowed.
- The `hosts` component MUST contain the host or list of hosts encompassing the server. The characters `(` and `)` MUST encompass the list, and the character `,` MUST delimit each host IP address or domain name. If only a single host is required, the host MUST still be encompassed by `(` and `)`.
- The `path-absolute` component MAY be the exported path of the filesystem.
- The `options` component MAY contain any other data required for the specific filesystem type, including but not limited to:
  - A password to authenticate a user (as a Juju secret).
  - A cluster identifier.
  - A filesystem identifier.
- Since each filesystem type will require different data for its `options` component, and it is unknown if more data will be required in the future, the `scheme` component MAY be used to version different data formats for the same filesystem type, which will not introduce any breaking changes.
- Any reserved character in the URI according to RFC 3986 MUST be percent-encoded, for example `!` becomes `%21` and `#` becomes `%23`. Inside `hosts`, this includes the `:` before a port, which is written as `%3A`. The `filesystem-client` charm's library also writes the `,` between hosts as `%2C`, and reads it either way.

## Filesystem types

The `filesystem-client` charm's library writes and reads these filesystem types:

- `nfs`: one host, with an optional port, and the exported path. The optional `version` option is the NFS version to mount with, which the `filesystem-client` charm passes as the `vers` mount option.
- `cephfs`: the Ceph user in `userinfo`, the monitor hosts, and the path within the filesystem. The `fsid` option is the cluster identifier, `name` is the filesystem name, and `auth` is either `secret:<ID>`, the ID of a Juju secret that has the Cephx key in its `key` field, or `plain:<key>` for providers that cannot create secrets. The `auth-rev` option is the revision of the secret, so that the `endpoint` changes when the key changes.
- `lustre`: the MGS NIDs as the hosts, and the `fs-name` option for the filesystem name. There's no path.
