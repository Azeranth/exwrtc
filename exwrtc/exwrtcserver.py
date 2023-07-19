import asyncio
import sys
import websockets

from azerutils.delegates import Delegate
from exwrtcutil import ManagedSession

class ManagedWebSocketServer:
    def __init__(self, host="localhost", port="80"):
        self.host = host
        self.port = port
        self.server = None

        self.onProcessContent = Delegate(ManagedWebSocketServer.ProcessContent, 1)
        self.onProcessMeta = Delegate(ManagedWebSocketServer.ProcessMeta, 1)

    async def Serve(self):
        async with websockets.serve(self.onIncomingConnection, self.host, self.port) as server:
            self.server = server
            await asyncio.Event().wait()  # Keep the server running indefinitely

    async def onIncomingConnection(self, ws, path):
        print("connection!")
        session = ManagedSession(ws, path)
        session.onContentReceive += ManagedWebSocketServer.ProcessContent
        session.onMetaReceive += ManagedWebSocketServer.ProcessMeta
        asyncio.create_task(session.Receive())
        
    @staticmethod       
    def ProcessMeta(_message):
        # Meta Command Server Logic Entry Point
        # Begin Example
        print("A meta message has been received")
        # End Example
        pass

    @staticmethod
    def ProcessContent(_message):
        # Content Server Logic Entry Point
        # Begin Example
        print("A content message has been received")
        # End Example
        pass

def main():
    print("Server inner code")
    server = ManagedWebSocketServer()
    asyncio.run(server.Serve())
    print("Server started success")

if __name__ == "__main__":
    main()