from exwrtcclient import main as clientEntry
from exwrtcserver import main as serverEntry
import multiprocessing

def main():
    clientEvent = multiprocessing.Event()
    serverEvent = multiprocessing.Event()
    client = multiprocessing.Process(target=clientEntry, args=(clientEvent,), group=None)
    server = multiprocessing.Process(target=serverEntry, args=(serverEvent,), group=None)

    print("Starting server")
    server.start()
    serverEvent.wait()
    print("Server started")
    # Server Setup Entry Point

    print("Starting client")
    client.start()
    clientEvent.wait()
    print("Client started")
    # Client Setup Entry Point

if __name__ == "__main__":
    main()