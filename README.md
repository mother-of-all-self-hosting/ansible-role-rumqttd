<!--
SPDX-FileCopyrightText: 2023 Slavi Pantaleev
SPDX-FileCopyrightText: 2025, 2026 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# rumqttd Ansible role

This is an [Ansible](https://www.ansible.com/) role which installs [rumqttd](https://github.com/bytebeamio/rumqtt) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

This role *implicitly* depends on:

- [`com.devture.ansible.role.playbook_help`](https://github.com/devture/com.devture.ansible.role.playbook_help)
- [`com.devture.ansible.role.systemd_docker_base`](https://github.com/devture/com.devture.ansible.role.systemd_docker_base)

Check [`defaults/main.yml`](defaults/main.yml) for the full list of supported options. Refer to [this page](docs/configuring-rumqttd.md) for details about setting up the service with this role.

💡 For an Ansible playbook which integrates this role and makes it easier to use, see the [Mother-of-All-Self-Hosting Ansible playbook](https://github.com/mother-of-all-self-hosting/mash-playbook).

## Development

### pre-commit

You can optionally install a Git pre-commit hook (via [mise](https://mise.jdx.dev/) + [prek](https://prek.j178.dev/)) that runs formatting and linting checks before each commit. See [`.pre-commit-config.yaml`](./.pre-commit-config.yaml) for which hooks are to be executed.

To install the hook, run the [`just`](https://github.com/casey/just) command below:

```sh
just prek-install-git-pre-commit-hook
```

### Molecule

This role supports [Molecule](https://docs.ansible.com/projects/molecule/), an Ansible testing framework designed for developing and testing Ansible collections, playbooks, and roles.

Refer to [this page](./molecule/README.md) for details about how to utilize it.

### Releases

Release tags are computed from the state of the repository rather than written by hand. [`bin/compute-next-tag.sh`](./bin/compute-next-tag.sh) reads the rumqttd version out of [`defaults/main.yml`](defaults/main.yml) and the tags that already exist, and prints the tag the current commit should carry — a fresh `-0` for a version that has never been released, the next counter for anything else that changes the role, and nothing at all for a commit that only touches documentation or CI. The [autotag workflow](.github/workflows/autotag.yml) pushes whatever it prints.

Because the answer depends only on what is in the tree, merges release themselves and the result does not depend on the order pull requests land in. [`bin/test-compute-next-tag.sh`](./bin/test-compute-next-tag.sh) exercises that against throwaway repositories, and runs as a pre-commit hook whenever the computation or the defaults change.
