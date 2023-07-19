import asyncio
import sys
import websockets
import io

from exwrtcutil import ManagedSession, StructuredMessage, MessageHeader, MessageContent
from azerutils.delegates import Delegate

class MaximumConnectionAttemptsExceeded(Exception):
    def __init__(self, _client):
        self.message = f"Failed to connect to server at {_client.uri}\twithin {_client.connectAttempts}/{_client.connectAttmptLimit}\tattempts"

class ManagedWebSocketClient:
    def __init__(self, _uri ,_connectAttemptLimit=3, _connectBackoffRate = 1.5):
        self.uri = _uri
        self.connectAttmptLimit = _connectAttemptLimit
        self.connectBackoffRate = _connectBackoffRate

        self.connectAttempts = 0
        self.session = None
        self.onProcessContent = Delegate(self.ProcessContent, 1)
        self.onProcessMeta = Delegate(self.ProcessMeta, 1)

    async def Connect(self):
        print("Connecting")
        if self.connectAttempts >= self.connectAttmptLimit:
            raise MaximumConnectionAttemptsExceeded(self)
        ws = await websockets.connect(self.uri)
        print("connected")
        self.session = ManagedSession(ws, "")
        print("session")
        asyncio.create_task(self.session.Receive())
    
    async def onConnectionEstablished(self):
        return None
    
    async def onConnectionClose(self):
        return None
            
    def ProcessMeta(_message):
        print("A meta message has bee received")
        pass

    def ProcessContent(_message):
        print("A content message has been received")
        pass
    

    
async def main():
    client = ManagedWebSocketClient("ws://localhost:80")
    while True:
        try:
            await client.Connect()
            # Client Code Entry Point
            # Begin Example
            header = MessageHeader()
            header.MessageType = StructuredMessage.META
            content = MessageContent()
            message = StructuredMessage(header, content)
            await client.session.Send(message)
            # End Example
        except ConnectionRefusedError as e:
            print(e, file=sys.stderr)
            client.connectAttempts += 1
            pass
        except asyncio.exceptions.TimeoutError as e:
            print(f"Server at {client.uri}\t did not complete handshake in configured time", file=sys.stderr)
            client.connectAttempts += 1
            pass
        except MaximumConnectionAttemptsExceeded as e:
            print(e.message, file=sys.stderr)
            break
        break

if __name__ == "__main__":
    asyncio.run(main())