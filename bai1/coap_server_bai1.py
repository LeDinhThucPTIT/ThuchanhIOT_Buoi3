#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bài 1: Ứng dụng gửi và nhận thông điệp CoAP cơ bản
Chương trình 1: CoAP Server
Tài nguyên: coap://localhost:5683/iot/lab/message
"""

import sys
import asyncio
import datetime
import argparse
import aiocoap
import aiocoap.resource as resource

# Thiết lập WindowsSelectorEventLoopPolicy trên Windows nếu cần
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass


class MessageResource(resource.Resource):
    """
    Tài nguyên CoAP quản lý thông điệp tại /iot/lab/message
    Hỗ trợ GET (lấy lời chào / thông điệp) và POST (gửi thông điệp sinh viên)
    """

    def __init__(self):
        super().__init__()
        self.last_message = None
        self.last_time = None
        self.post_count = 0

    async def render_get(self, request):
        """
        Xử lý yêu cầu GET: Trả về thông điệp chào mừng từ Server
        """
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] GET request received: /iot/lab/message")

        if self.last_message:
            payload_text = f"Xin chao tu CoAP Server (Thong diep gan nhat: \"{self.last_message}\")"
        else:
            payload_text = "Xin chao tu CoAP Server"

        return aiocoap.Message(
            code=aiocoap.Code.CONTENT,
            payload=payload_text.encode("utf-8"),
            content_format=aiocoap.numbers.ContentFormat.TEXT
        )

    async def render_post(self, request):
        """
        Xử lý yêu cầu POST: Nhận thông điệp từ Client, hiển thị và lưu lại
        """
        received_time = datetime.datetime.now().strftime("%H:%M:%S")
        payload_str = request.payload.decode("utf-8", errors="replace")

        self.last_message = payload_str
        self.last_time = received_time
        self.post_count += 1

        print(f"\nPOST request received:")
        print(f"Payload: {payload_str}")
        print(f"Time: {received_time}")

        response_text = "Server da nhan thong diep"
        return aiocoap.Message(
            code=aiocoap.Code.CHANGED,
            payload=response_text.encode("utf-8"),
            content_format=aiocoap.numbers.ContentFormat.TEXT
        )


def resolve_bind_ip(bind_ip: str) -> str:
    """
    Kiem tra va chuyen doi dia chi bind phu hop.
    Tren Windows, transport simplesocketserver khong cho phep bind '0.0.0.0'
    nen can su dung dia chi cu the ('127.0.0.1' hoac IP mang LAN).
    """
    if bind_ip in ("", "0.0.0.0", "::"):
        return "127.0.0.1"
    return bind_ip


async def run_server(bind_ip: str = "127.0.0.1", port: int = 5683):
    """
    Khởi tạo và chạy CoAP Server
    """
    bind_ip = resolve_bind_ip(bind_ip)
    root = resource.Site()
    msg_resource = MessageResource()
    root.add_resource(["iot", "lab", "message"], msg_resource)

    # Lắng nghe trên địa chỉ IP và cổng cấu hình
    server_context = await aiocoap.Context.create_server_context(
        root, bind=(bind_ip, port)
    )

    print("=" * 60)
    print(f"CoAP Server started on port {port}")
    print(f"Listening on: {bind_ip}:{port}")
    print("Resource available at:")
    print(f"  coap://localhost:{port}/iot/lab/message")
    print("Nhan Ctrl+C de dung Server.")
    print("=" * 60)

    try:
        # Giữ server chạy vô hạn cho đến khi người dùng bấm Ctrl+C
        await asyncio.get_running_loop().create_future()
    except asyncio.CancelledError:
        pass
    finally:
        print("\nDang tat CoAP Server...")
        await server_context.shutdown()
        print("Server da dung hoan toan.")


def main():
    parser = argparse.ArgumentParser(description="CoAP Server - Bai 1")
    parser.add_argument("--bind", default="127.0.0.1", help="Dia chi IP bind (mac dinh: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cong UDP CoAP (mac dinh: 5683)")
    args = parser.parse_args()

    try:
        asyncio.run(run_server(args.bind, args.port))
    except KeyboardInterrupt:
        print("\nDa nhan tin hieu KeyboardInterrupt. Tam biet!")


if __name__ == "__main__":
    main()
