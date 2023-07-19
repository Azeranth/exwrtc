import io
import json
import threading
from typing import Any
import uuid
import websockets

from azerutils.multistream import MultiStream
from azerutils.jsonextract import SpliceJsonHeader
from azerutils.delegates import Delegate

class MessageHeader:
    def __init__(self, _headers=None):
        self.__dict__['headers'] = _headers if _headers else {}
    
    def __iter__(self):
        return self.headers.__iter__()

    def __len__(self):
        return len(self.headers)

    def __getattr__(self, _name):
        if _name in self.headers:
            return self.headers[_name]
        return None
        
    def __setattr__(self, _name, _value):
        if _name in self.__dict__:
            super().__setattr__(_name, _value)
        else:
            self.headers[_name] = _value

    def Serialize(self):
        return json.dumps(self.headers)

    @staticmethod
    def JsonUnpack(json_string):
        headers = json.loads(json_string)
        return MessageHeader(headers)

class MessageContent:
    def __init__(self, _content=io.BytesIO()):
        self.multiStream =MultiStream(_content)
        self.stream = self.multiStream.baseStream
class StructuredMessage:
    META = 0
    CONT = 1

    def __init__(self, _header=None, _content=None):
        self.header = _header if _header is not None else MessageHeader()
        self.content = _content if _content is not None else MessageContent()
        self.lastSequence = -1
        self.messageQueue = {}

    def UnpackRaw(_message):
        print(_message)
        dataStream = io.BytesIO(_message)
        return StructuredMessage(MessageHeader.JsonUnpack(SpliceJsonHeader(dataStream)), MessageContent(dataStream))

    def PackRaw(self):
        return bytes(self.header.Serialize(), 'utf-8') + bytes(self.content.stream.read())

    def IsNextMessage(self, _continue):
        return _continue.IsContinue and _continue.Id == self.header.Id and _continue.Sequence == (self.lastSequence + 1)

    def ContinueMessage(self, _message):
        if self.IsNextMessage(_message.header):
            self.content.stream.write(_message.stream.read())

    def AppendMessageToQueue(self, _message, _flush=False, _attemptClose=False):
        if _message.header.IsContinue and _message.header.Id == self.header.Id:
            if not _message.header.Sequence in self.messageQueue:
                self.messageQueue[_message.header.Sequence] = _message
        if _flush:
            self.Flush(_attemptClose)

    def Flush(self, _attemptClose=False):
        for i in range(self.lastSequence + 1, self.lastSequence + len(self.messageQueue)):
            if i in self.messageQueue:
                self.ContinueMessage(self.messageQueue[i])
                self.messageQueue.pop(i)
            else:
                break
        if _attemptClose:
            self.AttemptClose()

    def AttemptClose(self):
        self.Flush()
        if not any(self.messageQueue):
            self.content.content.close()
            return True
        return False

    def ForceClose(self):
        self.Flush()
        self.content.content.close()

class ManagedSession:
    def __init__(self, _websocket, _path):
        print("Creating session")
        self.websocket = _websocket
        self.path = _path

        self.openMessages = {}
        self.strandedMessages = {}
        self.onMessageReceive = Delegate(self.MessageReceive, 1)
        self.onMetaReceive = Delegate([],1)
        self.onContentReceive = Delegate([],1)
        print(self.onMessageReceive)
        print(self.onMetaReceive)
        print(self.onContentReceive)

    async def Send(self, _message):
        print("sending")
        await self.websocket.send(_message.PackRaw())
        print("sent")
    
    async def Receive(self):
        print(self.onMetaReceive)
        while True:
            print("Waiting for message")
            try:
                self.onMessageReceive(StructuredMessage.UnpackRaw(await self.websocket.recv()))
                print("message received")
            except websockets.exceptions.ConnectionClosed as e:
                print("Connection Closed")
                await self.websocket.close()
                return
            except websockets.exceptions.ConnectionClosedOK as e:
                print("Connection Closed")
                await self.websocket.close()
                return
            except websockets.exceptions.ConnectionClosedError as e:
                print("Connection Closed")
                await self.websocket.close()
                return

    def MessageReceive(self, _message):
        print(self.onMetaReceive)
        # Handle Root Messages
        if not _message.header.IsStandalone and not _message.header.IsContinue:
            self.openMessages[_message.header.Id] = _message
            # Check if Root Message arrived with Stranded Continuations
            if _message.header.Id in self.strandedMessages:
                for m in self.strandedMessages.values():
                    _message.AppendMessageToQueue(m)
                self.strandedMessages.pop(_message.header.Id)
                _message.Flush()
        
        # Handle Continuation Messages
        if _message.header.IsContinue:
            if _message.header.Id in self.openMessages:
                self.openMessages[_message.header.Id].AppendMessageToQueue(_message, _flush=True)
            # Handle Stranded Continuations
            elif _message.header.Id in self.strandedMessages:
                if not _message.header.Sequence in self.strandedMessages[_message.header.Id]:
                    self.strandedMessages[_message.header.Id][_message.header.Sequence] = _message
                else:
                    self.strandedMessages[_message.header.Id] = {_message.header.Sequence : _message}
        
        #Dispatch Events
        if(_message.header.MessageType == StructuredMessage.META):
            print("META")
            print(self.onMetaReceive)
            try:
                self.onMetaReceive(_message)
            except TypeError as e:
                print(e.__dict__)
                print(f"TypeError: {e}")
                print(f"arguments: {e.args}")
        if(_message.header.MessageType == StructuredMessage.CONT):
            print("CONT")
            self.onContentReceive(_message)