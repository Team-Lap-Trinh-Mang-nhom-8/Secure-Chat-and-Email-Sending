import asyncio
import ssl
import json

HOST = '127.0.0.1'
PORT = 5555

async def send_json(writer, data):
    writer.write(json.dumps(data).encode() + b'\n')
    await writer.drain()

async def read_json(reader):
    line = await reader.readline()
    if not line:
        return None
    return json.loads(line.decode().strip())

async def tcp_client():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    reader, writer = await asyncio.open_connection(HOST, PORT, ssl=context)

    # Nhận yêu cầu username
    msg = await read_json(reader)
    print(msg["message"])
    username = input("> ")
    await send_json(writer, {"username": username})

    async def listen_server():
        while True:
            data = await read_json(reader)
            if not data:
                break
            print(f"\n[{data.get('type')}] {data.get('message')}\n> ", end='')

    async def send_messages():
        while True:
            text = input("> ")
            if text.startswith("/pm"):
                _, target, msg = text.split(" ", 2)
                await send_json(writer, {"type": "pm", "target": target, "message": msg})
            elif text.startswith("/mail"):
                _, to, msg = text.split(" ", 2)
                await send_json(writer, {"type": "mail", "to": to, "message": msg})
            else:
                await send_json(writer, {"type": "chat", "message": text})

    await asyncio.gather(listen_server(), send_messages())

asyncio.run(tcp_client())
