# Rumqttd Ansible Role

![Rumqtt Logo](assets/rumqtt.png)

A high performance, embeddable [MQTT](https://en.wikipedia.org/wiki/MQTT) broker. This role helps you to set up Rumqttd:

- with everything run in [Docker](https://www.docker.com/) containers
- powered by [the official Rumqttd container image](https://hub.docker.com/r/bytebeamio/rumqttd/)


## Installing

To configure and install Rumqttd on your own server(s), you should use a playbook like [Mother of all self-hosting](https://github.com/mother-of-all-self-hosting/mash-playbook) or write your own.

# Configuring this role for your playbook

```yaml
rumqttd_enabled: true
```

## Support

- Github issues: [mother-of-all-self-hosting/ansible-role-rumqttd/issues](https://github.com/mother-of-all-self-hosting/ansible-role-rumqttd/issues)
