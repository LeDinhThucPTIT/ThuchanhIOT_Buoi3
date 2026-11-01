#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bài 3: Mô phỏng hệ thống giám sát và điều khiển đèn thông minh bằng CoAP Observe
Chương trình 2: Light Controller Client
Tài nguyên: coap://<host>:<port>/iot/lab/<device_id>/status
"""

import sys
import json
import asyncio
import argparse
import aiocoap

if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass


async def controller_loop(host: str, port: int, device_id: str):
    uri = f"coap://{host}:{port}/iot/lab/{device_id}/status"
    client_context = await aiocoap.Context.create_client_context()

    print("=" * 60)
    print("           CoAP Light Controller Client")
    print("=" * 60)
    print(f"Target Resource: {uri}")
    print("Cac lenh ho tro: ON, OFF, STATUS, EXIT")
    print("=" * 60)

    try:
        while True:
            # Nhập lệnh từ bàn phím (sử dụng to_thread để không chặn event loop)
            user_input = await asyncio.to_thread(input, "Nhap lenh (ON/OFF/STATUS/EXIT): ")
            cmd = user_input.strip().upper()

            if not cmd:
                continue

            if cmd == "EXIT":
                print("Dang thoat chuong trinh...")
                break

            elif cmd in ["ON", "OFF"]:
                print("Sending PUT request...")
                payload = json.dumps({
                    "device_id": device_id,
                    "command": cmd
                }).encode("utf-8")

                request = aiocoap.Message(
                    code=aiocoap.Code.PUT,
                    uri=uri,
                    payload=payload,
                    content_format=aiocoap.numbers.ContentFormat.JSON
                )

                try:
                    response = await asyncio.wait_for(client_context.request(request).response, timeout=5.0)
                    print(f"Response Code: {response.code}")
                    if response.code.is_successful():
                        if cmd == "ON":
                            print(f"Da bat den {device_id}")
                        else:
                            print(f"Da tat den {device_id}")
                    else:
                        print(f"Server tra ve loi: {response.payload.decode('utf-8', errors='replace')}")
                except asyncio.TimeoutError:
                    print("Loi: Yeu cau PUT bi Timeout!")
                except Exception as e:
                    print(f"Loi: {e}")

            elif cmd == "STATUS":
                print("Sending GET request...")
                request = aiocoap.Message(code=aiocoap.Code.GET, uri=uri)
                try:
                    response = await asyncio.wait_for(client_context.request(request).response, timeout=5.0)
                    print("Response:")
                    print(response.payload.decode("utf-8", errors="replace"))
                except asyncio.TimeoutError:
                    print("Loi: Yeu cau GET bi Timeout!")
                except Exception as e:
                    print(f"Loi: {e}")

            else:
                print(f"Lenh khong hop le: '{cmd}'. Vui long chon ON, OFF, STATUS hoac EXIT.")

    finally:
        await client_context.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Light Controller Client - Bai 3")
    parser.add_argument("--host", default="127.0.0.1", help="Dia chi CoAP Server (mac dinh: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cong CoAP Server (mac dinh: 5683)")
    parser.add_argument("--device", default="light01", help="Ma den (mac dinh: light01)")
    args = parser.parse_args()

    try:
        asyncio.run(controller_loop(args.host, args.port, args.device))
    except KeyboardInterrupt:
        print("\nDa thoat khoi chuong trinh.")


if __name__ == "__main__":
    main()
