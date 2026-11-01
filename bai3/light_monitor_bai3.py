#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bài 3: Mô phỏng hệ thống giám sát và điều khiển đèn thông minh bằng CoAP Observe
Chương trình 3: Light Monitoring Client (Observe Client)
Tài nguyên: coap://<host>:<port>/iot/lab/<device_id>/status
"""

import sys
import json
import asyncio
import datetime
import argparse
import aiocoap

if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass


async def observe_light(host: str, port: int, device_id: str):
    uri = f"coap://{host}:{port}/iot/lab/{device_id}/status"
    client_context = await aiocoap.Context.create_client_context()

    print("=" * 60, flush=True)
    print("        Light Monitoring Client (CoAP Observe - RFC 7641)", flush=True)
    print("=" * 60, flush=True)
    print(f"Monitoring Resource: {uri}", flush=True)
    print("Dang ky nhan thong bao tu dong khi trang thai thay doi...", flush=True)
    print("Nhan Ctrl+C de huy dang ky va thoat.", flush=True)
    print("=" * 60, flush=True)

    print("Registering CoAP Observe...", flush=True)

    # Gửi yêu cầu GET kèm tùy chọn observe=0 để bắt đầu đăng ký Observe
    request = aiocoap.Message(code=aiocoap.Code.GET, uri=uri, observe=0)
    pr = client_context.request(request)

    try:
        # 1. Nhận phản hồi trạng thái ban đầu
        initial_response = await asyncio.wait_for(pr.response, timeout=5.0)
        print("Observe registration successful", flush=True)

        init_data = json.loads(initial_response.payload.decode("utf-8"))
        now_str = datetime.datetime.now().strftime("%H:%M:%S")

        print(f"[{now_str}] Initial State", flush=True)
        print(f"Device: {init_data.get('device_id', device_id)}", flush=True)
        print(f"Status: {init_data.get('status', 'UNKNOWN')}", flush=True)
        print("-" * 35, flush=True)

        # 2. Lắng nghe các Notification đẩy về từ Server khi tài nguyên thay đổi
        # CoAP Observe stream tự động nhận gói tin mỗi khi Server gọi updated_state()
        async for notification in pr.observation:
            try:
                notif_data = json.loads(notification.payload.decode("utf-8"))
                now_str = datetime.datetime.now().strftime("%H:%M:%S")

                print(f"[{now_str}] State Updated", flush=True)
                print(f"Device: {notif_data.get('device_id', device_id)}", flush=True)
                print(f"Status: {notif_data.get('status', 'UNKNOWN')}", flush=True)
                print("-" * 35, flush=True)
            except Exception as parse_err:
                print(f"Loi phan tich payload: {parse_err}", flush=True)

    except asyncio.TimeoutError:
        print("Loi: Khong the ket noi toi Server (Timeout). Vui long kiem tra Server da bat chua.")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Loi Observe: {e}")
    finally:
        print("\nHuy dang ky CoAP Observe...")
        if pr.observation:
            pr.observation.cancel()
        await client_context.shutdown()
        print("Da dong ket noi.")


def main():
    parser = argparse.ArgumentParser(description="Light Monitoring Client - Bai 3")
    parser.add_argument("--host", default="127.0.0.1", help="Dia chi CoAP Server (mac dinh: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cong CoAP Server (mac dinh: 5683)")
    parser.add_argument("--device", default="light01", help="Ma den (mac dinh: light01)")
    args = parser.parse_args()

    try:
        asyncio.run(observe_light(args.host, args.port, args.device))
    except KeyboardInterrupt:
        print("\nDa ngat theo doi.")


if __name__ == "__main__":
    main()
