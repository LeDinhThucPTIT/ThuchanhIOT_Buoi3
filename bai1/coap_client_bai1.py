#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bài 1: Ứng dụng gửi và nhận thông điệp CoAP cơ bản
Chương trình 2: CoAP Client
Tài nguyên: coap://<host>:<port>/iot/lab/message
"""

import sys
import asyncio
import argparse
import aiocoap

if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass


async def send_get_request(client_context, uri: str):
    """
    Gửi yêu cầu GET đến Server và hiển thị phản hồi
    """
    print("CoAP Client")
    print("Sending GET request...")
    print(f"URI: {uri}")

    request = aiocoap.Message(code=aiocoap.Code.GET, uri=uri)
    try:
        response = await asyncio.wait_for(client_context.request(request).response, timeout=5.0)
        print("Response:")
        print(f"Code: {response.code}")
        print(f"Payload: {response.payload.decode('utf-8', errors='replace')}")
        return response
    except asyncio.TimeoutError:
        print("Loi: Yeu cau GET bi Timeout (Server khong phan hoi trong 5 giay)!")
        return None
    except Exception as e:
        print(f"Loi khi gui GET: {e}")
        return None


async def send_post_request(client_context, uri: str, payload_str: str):
    """
    Gửi yêu cầu POST đến Server với nội dung thông điệp
    """
    print("\nSending POST request...")
    print(f"Payload: {payload_str}")

    request = aiocoap.Message(
        code=aiocoap.Code.POST,
        uri=uri,
        payload=payload_str.encode("utf-8"),
        content_format=aiocoap.numbers.ContentFormat.TEXT
    )
    try:
        response = await asyncio.wait_for(client_context.request(request).response, timeout=5.0)
        print("Response:")
        print(f"Code: {response.code}")
        print(f"Payload: {response.payload.decode('utf-8', errors='replace')}")
        return response
    except asyncio.TimeoutError:
        print("Loi: Yeu cau POST bi Timeout (Server khong phan hoi trong 5 giay)!")
        return None
    except Exception as e:
        print(f"Loi khi gui POST: {e}")
        return None


async def main_async(host: str, port: int, student_id: str, student_name: str, interactive: bool):
    uri = f"coap://{host}:{port}/iot/lab/message"
    client_context = await aiocoap.Context.create_client_context()

    try:
        # 1. Gửi yêu cầu GET ban đầu
        await send_get_request(client_context, uri)

        # 2. Gửi yêu cầu POST chứa thông tin sinh viên
        post_message = f"Xin chao tu CoAP Client - {student_id} - {student_name}"
        await send_post_request(client_context, uri, post_message)

        # 3. Gửi lại GET để kiểm tra server cập nhật thông điệp gần nhất
        print("\n--- Kiem tra thong diep luu tren Server bang GET lan 2 ---")
        await send_get_request(client_context, uri)

        # 4. Che do tuong tac (Goi y mo rong)
        if interactive:
            print("\n=== Che do tuong tac (Gui thong diep tuy y) ===")
            print("Nhap tin nhan can gui (hoac go 'exit' de thoat):")
            while True:
                msg = await asyncio.to_thread(input, "Nhap tin nhan: ")
                if not msg or msg.strip().lower() == "exit":
                    break
                await send_post_request(client_context, uri, msg.strip())
                await send_get_request(client_context, uri)

    finally:
        await client_context.shutdown()


def main():
    parser = argparse.ArgumentParser(description="CoAP Client - Bai 1")
    parser.add_argument("--host", default="127.0.0.1", help="Dia chi CoAP Server (mac dinh: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cong CoAP Server (mac dinh: 5683)")
    parser.add_argument("--id", default="B23DCCN001", help="Ma sinh vien (mac dinh: B23DCCN001)")
    parser.add_argument("--name", default="Nguyen Van A", help="Ho ten sinh vien (mac dinh: Nguyen Van A)")
    parser.add_argument("--interactive", action="store_true", help="Bat che do nhap tin nhan tu ban phim")
    args = parser.parse_args()

    try:
        asyncio.run(main_async(args.host, args.port, args.id, args.name, args.interactive))
    except KeyboardInterrupt:
        print("\nKet thuc chuong trinh.")


if __name__ == "__main__":
    main()
