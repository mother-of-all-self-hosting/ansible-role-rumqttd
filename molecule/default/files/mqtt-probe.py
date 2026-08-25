#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Speaks MQTT 3.1.1 to a broker, so that the Molecule scenario can check what
rumqttd does rather than what its systemd unit says about itself.

The wire protocol is spoken directly rather than through a client library,
because the outcomes have to stay distinguishable. rumqttd does not answer a
rejected connection with a CONNACK carrying a reason code - it simply closes the
socket - so a client program's exit status cannot tell "nothing is listening"
apart from "the broker refused these credentials", and a check that cannot tell
those apart is satisfied by the very thing it is supposed to rule out.

Every subcommand prints one line whose first word is the outcome:

    connect     refused | rejected | accepted
    roundtrip   refused | rejected | received <payload>
"""

import socket
import struct
import sys

CONNECT = 0x10
CONNACK = 0x20
PUBLISH = 0x30
PUBACK = 0x40
SUBSCRIBE = 0x82
SUBACK = 0x90
DISCONNECT = 0xE0

TIMEOUT_SECONDS = 10


class Refused(Exception):
    """Nothing accepted the TCP connection."""


class Rejected(Exception):
    """The TCP connection was accepted and the broker then declined to serve it."""


def encode_string(value):
    encoded = value.encode("utf-8")
    return struct.pack("!H", len(encoded)) + encoded


def encode_remaining_length(length):
    encoded = b""
    while True:
        digit = length % 128
        length //= 128
        if length:
            digit |= 0x80
        encoded += bytes([digit])
        if not length:
            return encoded


class Connection:
    def __init__(self, host, port, client_id, username=None, password=None):
        self.socket = socket.socket()
        self.socket.settimeout(TIMEOUT_SECONDS)

        try:
            self.socket.connect((host, int(port)))
        except OSError as error:
            raise Refused(str(error)) from error

        flags = 0x02  # clean session
        payload = encode_string(client_id)
        if username is not None:
            flags |= 0x80
            payload += encode_string(username)
        if password is not None:
            flags |= 0x40
            payload += encode_string(password)

        variable_header = encode_string("MQTT") + bytes([4, flags]) + struct.pack("!H", 60)
        self._send(CONNECT, variable_header + payload)

        header, body = self._receive()
        if header & 0xF0 != CONNACK:
            raise Rejected("expected CONNACK, got packet type 0x%02x" % header)
        if body[1] != 0:
            raise Rejected("CONNACK return code %d" % body[1])

    def _send(self, header, body):
        try:
            self.socket.sendall(bytes([header]) + encode_remaining_length(len(body)) + body)
        except OSError as error:
            raise Rejected(str(error)) from error

    def _receive_exactly(self, count):
        buffer = b""
        while len(buffer) < count:
            try:
                chunk = self.socket.recv(count - len(buffer))
            except OSError as error:
                raise Rejected(str(error)) from error
            if not chunk:
                raise Rejected("the broker closed the connection")
            buffer += chunk
        return buffer

    def _receive(self):
        header = self._receive_exactly(1)[0]
        multiplier = 1
        length = 0
        while True:
            digit = self._receive_exactly(1)[0]
            length += (digit & 127) * multiplier
            if not digit & 128:
                break
            multiplier *= 128
        return header, self._receive_exactly(length)

    def subscribe(self, topic, packet_id=1):
        self._send(SUBSCRIBE, struct.pack("!H", packet_id) + encode_string(topic) + bytes([1]))
        header, body = self._receive()
        if header & 0xF0 != SUBACK:
            raise Rejected("expected SUBACK, got packet type 0x%02x" % header)
        if body[2] > 2:
            raise Rejected("subscription refused, return code %d" % body[2])

    def publish(self, topic, payload, packet_id=2):
        body = encode_string(topic) + struct.pack("!H", packet_id) + payload.encode("utf-8")
        self._send(PUBLISH | 0x02, body)  # QoS 1
        header, _ = self._receive()
        if header & 0xF0 != PUBACK:
            raise Rejected("expected PUBACK, got packet type 0x%02x" % header)

    def next_publish(self):
        while True:
            header, body = self._receive()
            if header & 0xF0 != PUBLISH:
                continue
            offset = 2 + struct.unpack("!H", body[:2])[0]
            if (header >> 1) & 0x03:
                offset += 2  # a packet identifier is only present above QoS 0
            return body[offset:].decode("utf-8")

    def close(self):
        try:
            self._send(DISCONNECT, b"")
        except (OSError, Rejected):
            pass
        self.socket.close()


def command_connect(host, port, username, password):
    Connection(host, port, "molecule-probe-connect", username, password).close()
    return "accepted"


def command_roundtrip(host, port, username, password, topic, payload):
    # The subscriber is fully established - its SUBACK is in hand - before the
    # publisher is opened, so the message cannot be missed by arriving early.
    # Two connections rather than one, so that the broker has to route the
    # message between clients rather than hand it straight back to its sender.
    subscriber = Connection(host, port, "molecule-probe-subscriber", username, password)
    try:
        subscriber.subscribe(topic)
        publisher = Connection(host, port, "molecule-probe-publisher", username, password)
        try:
            publisher.publish(topic, payload)
        finally:
            publisher.close()
        return "received %s" % subscriber.next_publish()
    finally:
        subscriber.close()


def main(argv):
    command, host, port = argv[0], argv[1], argv[2]
    username = argv[3] or None
    password = argv[4] or None

    try:
        if command == "connect":
            print(command_connect(host, port, username, password))
        elif command == "roundtrip":
            print(command_roundtrip(host, port, username, password, argv[5], argv[6]))
        else:
            raise SystemExit("unknown command: %s" % command)
    except Refused as error:
        print("refused %s" % error)
    except Rejected as error:
        print("rejected %s" % error)


if __name__ == "__main__":
    main(sys.argv[1:])
