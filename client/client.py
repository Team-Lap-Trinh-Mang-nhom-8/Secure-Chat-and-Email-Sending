import asyncio
import ssl

HOST = '127.0.0.1'
PORT = 5555

async def tcp_client():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    reader, writer = await asyncio.open_connection(HOST, PORT, ssl=context)

    # Nhập username
    data = await reader.read(1024)
    print(data.decode(), end='')
    username = input()
    writer.write(username.encode())
    await writer.drain()

    async def listen_server():
        while True:
            data = await reader.read(1024)
            if not data:
                break
            print(f"\n{data.decode()}\n> ", end='')

    async def send_messages():
        while True:
            message = input("> ")
            writer.write(message.encode())
            await writer.drain()

    await asyncio.gather(listen_server(), send_messages())

asyncio.run(tcp_client())
