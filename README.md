# Secure Chat (Asyncio + TLS)

Hướng dẫn chạy nhanh cho project chat mã hoá bằng TLS.

Yêu cầu

- Python 3.7+

Chạy server

1. Mở PowerShell và chuyển đến thư mục `server`:

```powershell
cd d:\PythonCode\Bai-cuoi-ky\server
python .\server.py
```

Server sẽ lắng nghe trên `0.0.0.0:5555` và dùng `server.crt` + `server.key` có sẵn.

Chạy client

1. Mở PowerShell mới và chuyển đến thư mục `client`:

```powershell
cd d:\PythonCode\Bai-cuoi-ky\client
python .\client.py
```

2. Khi client hiện `USERNAME?`, gõ tên của bạn và Enter.
3. Bắt đầu nhắn tin tại prompt `>`.

Lưu ý bảo mật

- Client hiện đang bỏ qua xác thực chứng chỉ (`CERT_NONE`). Trong môi trường production, hãy bật `CERT_REQUIRED` và load `server.crt` làm CA tin cậy.

Liên hệ

- Nếu cần thêm hướng dẫn (tạo CA, ký cert, xác thực client), cho tôi biết để tôi bổ sung.
