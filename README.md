# exwrtc
A server and client implementation for handling structured messages for C2 and file transfer over wRTC

## exwrtcclient.ManagedWebSocketClient
Basic client connection for handling outgoing requests, designed to run from the remote node.

Connections are made by the `ManagedWebSocketClient.Connect(string _uri)`.
The managed client is only designed to handle connection to a single server and resource location at a time, and does not currently support state preservation between connections. (Future feature intended)
Messages are handled by the `ManagedSession ManagedWebSocketClient.session` in the `StructuredMessage` format.
Messages are received and handled asynchronously, and dispatched from the `ManagedWebSocketClient.onMessageReceive`, `ManagedWebSocketClient.onMetaReceive` and `ManagedWebSocketClient.onContentReceive` which by default includes the static `ManagedWebSocketClient.ProcessMeta` and `ManagedWebSocketClient.ProcessContent` functions
Messages are sent by `ManagedWebSocketClient.session.send(StructuredMessage _message)`

## exwrtcserver.ManagedWebSocketServer
Basic server for handling incoming requests, designed to run from the C2 node.

Service provided after `ManagedWebSocketServer.Serve()` on host and port configured in `ManagedWebSocketServer.host` and `ManagedWebSocketServer.port`
The managed server is only designed to handle connections volatilely, and does not currently support state preservation between connections.
Messages are handled by the `ManagedSession ManagedWebSocketClient.session` in the `StructuredMessage` format.
Messages are received and handled asynchronously, and dispatched from the `ManagedWebSocketClient.onMetaReceive`, `ManagedWebSocketClient.onMetaReceive` and `ManagedWebSocketClient.onContentReceive` which by default includes the static `ManagedWebSocketClient.ProcessMeta` and `ManagedWebSocketClient.ProcessContent` functions
Messages are sent by `ManagedWebSocketClient.session.send(StructuredMessage _message)`

## exwrtcutils.ManagedSession, ##exwrtcutils.StructuredMessage
Consistent logic for receiving and processing incoming messages, and dispatcing related events using a standard StructuredMessage format.

`ManagedSession` provides message queing, allowing messages to be received out of order and recomposed. Out of sequence messages are not dropped or rejected to preserve memory or performance (Potential vulnerability).
`ManagedSession` does not preserve header of continue messages, and only stores the root messages headers when composing messages from continue messages. Root headers are optionally mutable.

`StructuredMessage` defines packing and unpacking functions for bytes-like objects, as well as header and content members- represented by a MultiStream
`MessageHeader` Manages a collection of headers which can be accessed arbitarily by dot notation for convenience. Headers not present will be returned as `None` type object and set by adding a header by that name to the underlying collection.
`MessageContent` Manages a MultiStream, and provides a `stream` member to directly reference the base stream of the MultiStream.
Tasks which consume the message content should use `MessageContent.multistream.getNewAccessor()` to ensure their stream access is unique and thread safe.

Future features intended
- `exwrtcclient.ManagedWebSocketClient` Server authentication
- `exwrtcclient.ManagedWebSocketClient` session state preservation
- `exwrtcserver.ManagedWebServerServer` Client authentication
- `exwrtcserver.ManagedWebServerServer` Client session keys and preservation across multiple connections
- `exwrtcserver.ManagedWebServerServer` automated event attachment based on target path (like CGI)
- `exwrtcutils.ManagedSession` automated disposal of message blobs after final continue is received.
- `exwrtcutils.ManagedSession` automated rerequest of missing message fragments
- `exwrtcutils.MessageHeader` configurable read-only enforcement on headers
- `exwrtcutils.MessageHeader` intuitive handling of removing headers after assignment