import asyncio
import ssl
import json
import logging
from datetime import datetime

# ================== CẤU HÌNH ==================
HOST = "0.0.0.0"
PORT = 5555
CERT_FILE = "server.crt"
KEY_FILE = "server.key"

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

# ================== QUẢN LÝ CLIENT ==================
class ClientManager:
    def __init__(self):
        self.clients = {}  # username -> writer

    def add_client(self, username, writer):
        self.clients[username] = writer
        logging.info(f"✅ {username} đã kết nối. Tổng client: {len(self.clients)}")

    def remove_client(self, username):
        self.clients.pop(username, None)
        logging.info(f"❌ {username} ngắt kết nối. Còn lại: {len(self.clients)}")

    def get_writer(self, username):
        return self.clients.get(username)

    def all_clients(self):
        return self.clients.items()

clients = ClientManager()

# ================== HÀM HỖ TRỢ ==================
async def send_json(writer, data):
    try:
        message = json.dumps(data).encode()
        writer.write(message + b"\n")
        await writer.drain()
    except Exception as e:
        logging.error(f"Lỗi gửi dữ liệu: {e}")

async def read_json(reader):
    try:
        line = await reader.readline()
        if not line:
            return None
        return json.loads(line.decode().strip())
    except Exception as e:
        logging.error(f"Lỗi đọc dữ liệu: {e}")
        return None

async def broadcast(data, exclude_username=None):
    """Gửi cho tất cả client trừ người gửi"""
    for username, writer in clients.all_clients():
        if username != exclude_username:
            await send_json(writer, data)

async def send_private(sender, target, message):
    """Nhắn riêng giữa hai người"""
    target_writer = clients.get_writer(target)
    if target_writer:
        await send_json(target_writer, {
            "type": "pm",
            "sender": sender,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    else:
        sender_writer = clients.get_writer(sender)
        await send_json(sender_writer, {
            "type": "error",
            "message": f"Không tìm thấy người dùng {target}"
        })

# ================== XỬ LÝ LỆNH ==================
async def handle_command(username, data):
    cmd = data.get("type")

    if cmd == "chat":
        msg = {
            "type": "chat",
            "sender": username,
            "message": data.get("message", ""),
            "timestamp": datetime.now().isoformat()
        }
        await broadcast(msg, exclude_username=username)

    elif cmd == "pm":
        await send_private(username, data.get("target"), data.get("message"))

    elif cmd == "mail":
        # Giả lập xử lý gửi mail (sẽ để nhóm khác làm thật)
        await send_json(clients.get_writer(username), {
            "type": "system",
            "message": f"Mail đã được gửi đến {data.get('to')} (giả lập)"
        })

    else:
        logging.warning(f"Lệnh không hợp lệ từ {username}: {cmd}")
        await send_json(clients.get_writer(username), {
            "type": "error",
            "message": f"Lệnh không hợp lệ: {cmd}"
        })

# ================== XỬ LÝ CLIENT ==================
async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    try:
        # Gửi yêu cầu username
        await send_json(writer, {"type": "system", "message": "USERNAME?"})
        username_data = await read_json(reader)
        if not username_data:
            writer.close()
            return

        username = username_data.get("username")
        clients.add_client(username, writer)

        # Thông báo người khác biết
        await broadcast({
            "type": "system",
            "message": f"{username} đã tham gia vào phòng chat."
        }, exclude_username=username)

        # Vòng lặp nhận tin
        while True:
            data = await read_json(reader)
            if not data:
                break
            await handle_command(username, data)

    except Exception as e:
        logging.error(f"Lỗi xử lý client {addr}: {e}")

    finally:
        clients.remove_client(username)
        writer.close()
        await writer.wait_closed()
        await broadcast({
            "type": "system",
            "message": f"{username} đã rời phòng."
        })

# ================== KHỞI TẠO SERVER ==================
async def main():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    server = await asyncio.start_server(handle_client, HOST, PORT, ssl=context)
    addr = server.sockets[0].getsockname()
    logging.info(f"🚀 Server lắng nghe tại {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    logging.info("Chat Server đang khởi động...")
    asyncio.run(main())
