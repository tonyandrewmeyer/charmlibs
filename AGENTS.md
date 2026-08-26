# Agent instructions for charmlibs

`charmlibs` is a monorepo of Python libraries for Juju charms. General libraries live at the repo root (e.g. `pathops/`). Interface libraries live under `interfaces/` (for example, `interfaces/tls-certificates/`). See `README.md` for the two library categories and how to choose between them, and `CONTRIBUTING.md` for the full developer quick-reference — this file covers only what an agent would otherwise get wrong or have to dig for.

## Development workflow

### Inner loop

The command you'll run most often is:

```bash
just check <package>
```

This runs `just lint <package>`, `just unit <package>`, and `just docs html <package>`. **Run this before every commit on the affected package.**

The `<package>` argument is the path from the repo root, e.g. `pathops` or `interfaces/tls-certificates`.

### Command reference

| Command | Description |
|---------|-------------|
| `just check <package>` | Lint + unit tests + docs (the standard pre-commit check) |
| `just lint <package>` | ruff + pyright |
| `just fast-lint [path]` | ruff only, across the whole repo or a specific path |
| `just format [package]` | Auto-fix ruff and formatting errors |
| `just static <package>` | pyright only |
| `just unit <package>` | Run unit tests |
| `just functional <package>` | Run functional tests (may need external software available, or to be run with sudo -- and note that this probably indicates a test that's destructive to the local environment (e.g. adding or removing packages)). **Do not run functional tests directly on the host.** Use Workshop instead (see below). |
| `just pack-k8s <package>` | Pack K8s test charm(s) for integration tests, running the libraries `tests/integration/pack.sh` script with environment variables set |
| `just pack-machine <package>` | Pack machine test charm(s) for integration tests, as above |
| `just integration-k8s <package>` | Run Juju integration tests, excluding `pytest.mark.machine_only` tests |
| `just integration-machine <package>` | Run Juju integration tests against machine, excluding `pytest.mark.k8s_only` tests |
| `just docs html [packages]` | Build docs (including reference docs for all packages by default, or named ones -- run `just docs html -` to exclude all package reference docs (faster when working on docs only) |
| `just docs` | Alias for `just docs html` |
| `just add <package> <dep>` | Add a dependency to a library |
| `just init` | Scaffold a new general library |
| `just init --interface` | Scaffold a new interface library |

Extra arguments to `just unit`, `just functional`, and `just integration-*` are passed through to pytest:

```bash
just unit pathops -x -k test_write_text_newline   # stop on first failure, filter by name
```

### Adding dependencies

**Always use `just add <package> <dep>` instead of calling `uv add` directly.** This applies repo-level version constraints from `test-requirements.txt`, which is necessary to keep the lockfile consistent:

```bash
just add pathops 'pydantic>=2'
just add interfaces/tls-certificates --requirements my-requirements.txt
```

## Test types

A test type is only executed if the corresponding `tests/` subdirectory exists. Remove a directory to skip that test type entirely.

### Running functional tests with Workshop

Functional tests often require `sudo` and may be destructive to the local environment (e.g. installing or removing system packages). **Never run functional tests directly on the host machine.** Always use [Workshop](https://snapcraft.io/workshop) to run them in an isolated container:

```bash
workshop exec resolute -- sudo just functional <package>    # Ubuntu 26.04
workshop exec noble -- sudo just functional <package>       # Ubuntu 24.04
workshop exec jammy -- sudo just functional <package>       # Ubuntu 22.04
```

Workshop configs are defined in `.workshop/`. Extra pytest flags are passed through to `just functional` (and on to pytest):

```bash
workshop exec noble -- sudo just functional snap -x -k test_install
```

## Commit and PR conventions

**PRs are squash-merged.** The PR title becomes the single commit message on `main`. Branch commit messages are for local reference, and should follow conventional commits for clarity.

PR titles must follow [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/). When a PR affects a single library, use the distribution package name without the leading `charmlibs-` as the scope:

```
feat(pathops): add copytree and rmtree
fix(apt): handle multiarch package names correctly
chore(interfaces-tls-certificates): update to Pydantic v2
docs: improve tutorial for adding integration tests
```

**One PR should normally touch only one library.** The CI uses changed files to determine which packages to test and, on merge, which packages to publish.

### Versioning

- Libraries use semantic versioning (`MAJOR.MINOR.PATCH`).
- Dev versions (`X.Y.Z.devN`) are excluded from release CI — safe for in-progress work.
- When bumping to a non-dev version, you **must** also update `CHANGELOG.md`. CI will block the merge otherwise.
- The CI automatically publishes to PyPI on merge when a non-dev version bump is detected.

## Interface libraries

Interface libraries manage the structured data that charms exchange over a Juju relation databag. Key differences from general libraries:

- Live under `interfaces/<interface-name>/`, named exactly as the interface name appears in `charmcraft.yaml`.
- Source under `src/charmlibs/interfaces/<interface_name>/`.
- Typically have unit and integration tests but no functional tests (all meaningful interaction is through Juju).
- Use `just init --interface` to scaffold.

## Documentation

When writing or editing docstrings in `__init__.py` or other public modules, remember they appear verbatim in the published reference at [canonical.com/juju/docs/charmlibs](https://canonical.com/juju/docs/charmlibs). Keep them informative for library users, not implementation notes.

Don't use block quotes (`>`) for "Read more", "See also", or similar cross-reference sections. Instead, use bare text like `Read more: {ref}\`some-page\`` or, for two links, a comma-separated list or, for three or more links a bulleted list. For example:

```
Read more: {ref}`how-to-customize-integration-tests`

Read more: {ref}`charm-libs-charmhub-hosted`, {ref}`Charmcraft | Manage libraries <charmcraft:manage-libraries>`
```

## Common pitfalls

- **Don't add unnecessary features or refactor code beyond what's asked** — this is a multi-team monorepo with careful versioning; unintended public API changes require major version bumps.

## External resources

Integration tests use [Jubilant](https://canonical.com/juju/docs/jubilant/) as the Juju test client, and CI provisions the Juju environment with [Concierge](https://raw.githubusercontent.com/canonical/concierge/refs/heads/main/README.md).
