<!--
SPDX-FileCopyrightText: 2020 - 2024 MDAD project contributors
SPDX-FileCopyrightText: 2020 - 2024, 2026 Slavi Pantaleev
SPDX-FileCopyrightText: 2020 Aaron Raimist
SPDX-FileCopyrightText: 2020 Chris van Dijk
SPDX-FileCopyrightText: 2020 Dominik Zajac
SPDX-FileCopyrightText: 2020 Mickaël Cornière
SPDX-FileCopyrightText: 2022 François Darveau
SPDX-FileCopyrightText: 2022 Julian Foad
SPDX-FileCopyrightText: 2022 Warren Bailey
SPDX-FileCopyrightText: 2023 Antonis Christofides
SPDX-FileCopyrightText: 2023 Felix Stupp
SPDX-FileCopyrightText: 2023 Julian-Samuel Gebühr
SPDX-FileCopyrightText: 2023 Pierre 'McFly' Marty
SPDX-FileCopyrightText: 2024 - 2025 Suguru Hirahara

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Setting up rumqttd

This is an [Ansible](https://www.ansible.com/) role which installs [rumqttd](https://github.com/bytebeamio/rumqtt) to run as a [Docker](https://www.docker.com/) container wrapped in a systemd service.

rumqttd is a high performance, embeddable [MQTT](https://en.wikipedia.org/wiki/MQTT) broker.

See the project's [documentation](https://github.com/bytebeamio/rumqtt/blob/main/README.md) to learn what rumqtt does and why it might be useful to you.

## Adjusting the playbook configuration

To enable rumqttd with this role, add the following configuration to your `vars.yml` file.

```yaml
########################################################################
#                                                                      #
# rumqttd                                                              #
#                                                                      #
########################################################################

rumqttd_enabled: true

########################################################################
#                                                                      #
# /rumqttd                                                             #
#                                                                      #
########################################################################
```

### Change the MQTT port (optional)

If you need to change the port that MQTT clients connect to, add the following configuration to your `vars.yml` file (adapt to your needs).

```yaml
rumqttd_container_tcp_host_bind_port: "2883"
```

That changes the port on the host. To change the port that the broker itself listens on inside its container, set `rumqttd_container_tcp_port` instead — `rumqttd_container_tcp_host_bind_port` follows it unless you also set it explicitly.

Setting `rumqttd_container_tcp_host_bind_port` to an empty string keeps the broker unpublished on the host, which is what you want if the clients are other containers on `rumqttd_container_additional_networks_custom`.

### Require credentials (optional)

By default rumqttd accepts any client that connects, which is only appropriate on a network you trust. To require credentials, add the following configuration to your `vars.yml` file (adapt to your needs).

```yaml
rumqttd_auth_users_custom:
  - username: someone
    password: some-password
```

Credentials apply to every listener. rumqttd has no notion of hashed credentials, so they are stored in plain text in the configuration file that this role writes to the server.

### Other listeners (optional)

Besides the MQTT v3.1.1 listener that `rumqttd_container_tcp_port` configures, the role sets up:

| Listener | Enabled by default | Port setting | Published on the host by default |
| --- | --- | --- | --- |
| MQTT v5 | yes | `rumqttd_container_v5_port` (1884) | no |
| MQTT over WebSocket | yes | `rumqttd_container_websocket_port` (8083) | no |
| HTTP console | yes | `rumqttd_container_console_port` (3030) | no |
| Prometheus metrics | no | `rumqttd_container_metrics_prometheus_port` (9042) | no |

Clients speaking MQTT v5 cannot use the v3.1.1 listener (and vice versa), which is why both exist.

Each of them can be turned off (`rumqttd_v5_enabled`, `rumqttd_websocket_enabled`, `rumqttd_console_enabled`, `rumqttd_metrics_prometheus_enabled`) and each has a matching `*_host_bind_port` setting for publishing it on the host. Think twice before publishing the console: it is unauthenticated, reports the broker's configuration and the state of connected devices, and can change the broker's log level.

### Extend the configuration (optional)

Anything the settings above do not cover can be appended to the configuration file verbatim:

```yaml
rumqttd_configuration_extension_toml: |
  [metrics]
    [metrics.meters]
    push_interval = 5
```

Because TOML keys belong to whichever table was declared last, what you put here must open with its own `[section]` header.

## Installing

After configuring the playbook, run the installation command of your playbook as below:

```sh
ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start
```

If you use the MASH playbook, the shortcut commands with the [`just` program](https://github.com/mother-of-all-self-hosting/mash-playbook/blob/main/docs/just.md) are also available: `just install-all` or `just setup-all`

## Usage

After running the command for installation, you can start to send and subscribe to MQTT topics. Use port `1883` (or whatever you set `rumqttd_container_tcp_host_bind_port` to) and the server's IP or any domain you configured to point at this server.

## Troubleshooting

### Check the service's logs

You can find the logs in [systemd-journald](https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html) by logging in to the server with SSH and running `journalctl -fu rumqttd` (or how you/your playbook named the service, e.g. `mash-rumqttd`).

## Alternatives

[Mosquitto](https://mosquitto.org/) is another, more feature-complete MQTT broker. The role for it is available at [this repository](https://github.com/mother-of-all-self-hosting/ansible-role-mosquitto) maintained by the [Mother-of-All-Self-Hosting (MASH)](https://github.com/mother-of-all-self-hosting) team.
