from yaps.api import protocol
from yaps.client.base_connection import BaseConnection
from yaps.utils import Log


SLEEP_DELAY = 1      # In seconds.


class Subscribe(BaseConnection):
    """
        Helper class to perform a subscription to a YAPS server.
        This class can be used directly, but its more preferred to use
        a wrapper class like Client.
    """

    def __init__(self, ip: str, port: int, data_received: callable,
                 pong_callback: callable = None, flags=None):
        super().__init__(ip, port)
        self._alive = False
        self._data_received = data_received
        self._pong_callback = pong_callback

    def start(self, topic: str) -> bool:
        """ Starts the subscription.
            param data_received is a callback that will be called
            when new data arrvies at the subscribed topic.
        """
        # Start connection and initialize a new Subscription.
        self.open()
        self.send(protocol.Commands.SUBSCRIBE)

        # Wait for ACK, before sending the topic.
        packet = self.read()
        if not protocol.cmd_ok(packet, protocol.Commands.SUBSCRIBE_ACK,
                               self._writer):
            return

        # Send the topic we want to subscribe to.
        self.send(protocol.Commands.SUBSCRIBE,
                  data=topic.encode('utf-8'))

        # Wait for OK/NOT OK.
        sub_ack = self.read()
        if not protocol.cmd_ok(sub_ack, protocol.Commands.SUBSCRIBE_OK):
            Log.err(f'Failed to subscribe to {topic}. Got no ACK.')
            return False

        # Enter ping-pong state where we just wait for data published to
        # the chosen topic and give the data to the callback function provided.
        self._enter_ping_pong()

    def _enter_ping_pong(self) -> None:
        self._alive = True

        while self._alive:
            packet = self.read()

            if packet.cmd == protocol.Commands.NEW_DATA:
                # New data published!
                self._ack_new_data()

                # Unpack the data and send it to callback.
                data = packet.data.decode('utf-8')
                if self._data_received is not None:
                    self._data_received(data)
                else:
                    Log.err(f'No callback for new data provided!\n{data}')
            else:
                # Expecting a ping
                if not protocol.cmd_ok(packet, protocol.Commands.PING):
                    Log.err('Failed to get ping command. Exiting.')
                    return

                # Send a PONG back.
                self._pong()
                Log.debug('[Client] Pong')

                # If provided, call pong callback.
                if self._pong_callback is not None:
                    self._pong_callback()

    def _ack_new_data(self):
        self.send(protocol.Commands.NEW_DATA_ACK)

    def _pong(self) -> None:
        self.send(protocol.Commands.PONG)

    def die(self):
        self._alive = False
        self._writer.close()
