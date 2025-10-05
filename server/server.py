import asyncio
import ssl

# ======== CẤU HÌNH SERVER ========
HOST = '0.0.0.0'
PORT = 5555
CERT_FILE = 'server.crt'
KEY_FILE = 'server.key'

# Danh sách client kết nối: {writer, username}
clients = []

# ======== XỬ LÝ CLIENT ========
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    try:
        # Yêu cầu username
        writer.write("USERNAME?".encode())
        await writer.drain()
        username = (await reader.read(1024)).decode().strip()
        clients.append({"writer": writer, "username": username})
        print(f"[NEW CONNECTION] {username} ({addr}) connected. Active clients: {len(clients)}")

        # Thông báo client join
        await broadcast(f"[{username}] joined the chat!", writer)

        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode().strip()
            print(f"[{username}] {message}")
            await broadcast(f"[{username}] {message}", writer)

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")

    finally:
        # Remove client khi ngắt kết nối
        clients[:] = [c for c in clients if c["writer"] != writer]
        writer.close()
        await writer.wait_closed()
        print(f"[DISCONNECT] {username} ({addr}) disconnected. Active clients: {len(clients)}")
        await broadcast(f"[{username}] left the chat.", None)

# ======== BROADCAST TIN NHẮN ========
async def broadcast(message, sender_writer):
    for c in clients:
        if c["writer"] != sender_writer:
            try:
                c["writer"].write(message.encode())
                await c["writer"].drain()
            except:
                pass

# ======== KHỞI TẠO SERVER ========
async def main():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    server = await asyncio.start_server(handle_client, HOST, PORT, ssl=context)
    addr = server.sockets[0].getsockname()
    print(f"[LISTENING] Server on {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    print("[STARTING] Asyncio SSL Chat Server is starting...")
    asyncio.run(main())
