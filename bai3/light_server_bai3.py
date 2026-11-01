#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bài 3: Mô phỏng hệ thống giám sát và điều khiển đèn thông minh bằng CoAP Observe
Chương trình 1: Smart Light CoAP Server
Tài nguyên: coap://<host>:<port>/iot/lab/<device_id>/status
"""

import sys
import json
import asyncio
import datetime
import argparse
import aiocoap
import aiocoap.resource as resource

if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass


class SmartLightResource(resource.ObservableResource):
    """
    Tài nguyên Đèn thông minh hỗ trợ GET, PUT và cơ chế CoAP Observe (RFC 7641).
    Khi trạng thái đèn thay đổi, tự động gửi Notification đến tất cả Client đang Observe.
    """

    def __init__(self, device_id: str = "light01"):
        super().__init__()
        self.device_id = device_id
        self.status = "OFF"  # Trạng thái ban đầu: OFF
        self.last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def render_get(self, request):
        """
        Xử lý yêu cầu GET và đăng ký Observe ban đầu
        """
        now = datetime.datetime.now().strftime("%H:%M:%S")
        client_addr = request.remote if request.remote is not None else "Client"
        if request.opt.observe is not None:
            print(f"[{now}] New Observe registration received from {client_addr}")
        else:
            print(f"[{now}] GET request received for /{self.device_id}/status from {client_addr}")

        payload_dict = {
            "device_id": self.device_id,
            "status": self.status,
            "timestamp": self.last_update
        }
        payload_bytes = json.dumps(payload_dict).encode("utf-8")

        return aiocoap.Message(
            code=aiocoap.Code.CONTENT,
            payload=payload_bytes,
            content_format=aiocoap.numbers.ContentFormat.JSON
        )

    async def render_put(self, request):
        """
        Xử lý yêu cầu PUT để điều khiển bật/tắt đèn (ON / OFF)
        """
        now = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            payload_str = request.payload.decode("utf-8")
            data = json.loads(payload_str)
        except Exception:
            print(f"[{now}] PUT error: Invalid JSON payload")
            return aiocoap.Message(
                code=aiocoap.Code.BAD_REQUEST,
                payload=b"Error: Payload must be valid JSON",
                content_format=aiocoap.numbers.ContentFormat.TEXT
            )

        target_dev = data.get("device_id", self.device_id)
        command = data.get("command", "").strip().upper()

        print(f"\nPUT request received:")
        print(f"Device: {target_dev}")
        print(f"Command: {command}")

        # Kiểm tra tính hợp lệ của lệnh điều khiển
        if command not in ["ON", "OFF"]:
            print(f"Loi: Lenh khong hop le ('{command}'). Chi chap nhan 'ON' hoac 'OFF'.")
            error_msg = f"Invalid command '{command}'. Use 'ON' or 'OFF'."
            return aiocoap.Message(
                code=aiocoap.Code.BAD_REQUEST,
                payload=error_msg.encode("utf-8"),
                content_format=aiocoap.numbers.ContentFormat.TEXT
            )

        old_status = self.status
        self.status = command
        self.last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Nếu trạng thái thực sự thay đổi -> Thông báo cho tất cả Observers
        if old_status != self.status:
            print(f"Light state changed: {old_status} -> {self.status}")
            print(f"Notify observers: {self.status}")
            # Gọi updated_state() để aiocoap tự động gửi Observe Notification
            self.updated_state()
        else:
            print(f"Light state unchanged: {self.status}")

        response_payload = json.dumps({
            "device_id": self.device_id,
            "status": self.status,
            "message": f"Da cap nhat trang thai thanh {self.status}"
        }).encode("utf-8")

        return aiocoap.Message(
            code=aiocoap.Code.CHANGED,
            payload=response_payload,
            content_format=aiocoap.numbers.ContentFormat.JSON
        )


def resolve_bind_ip(bind_ip: str) -> str:
    if bind_ip in ("", "0.0.0.0", "::"):
        return "127.0.0.1"
    return bind_ip


async def run_server(bind_ip: str, port: int, device_id: str):
    bind_ip = resolve_bind_ip(bind_ip)
    root = resource.Site()
    light_res = SmartLightResource(device_id=device_id)

    # Đăng ký tài nguyên: /iot/lab/<device_id>/status
    resource_path = ["iot", "lab", device_id, "status"]
    root.add_resource(resource_path, light_res)

    server_context = await aiocoap.Context.create_server_context(
        root, bind=(bind_ip, port)
    )

    print("=" * 65)
    print("CoAP Smart Light Server started...")
    print(f"Resource: /iot/lab/{device_id}/status")
    print(f"URI: coap://localhost:{port}/iot/lab/{device_id}/status")
    print(f"Initial State: {light_res.status}")
    print("Supports: GET, PUT, and CoAP Observe")
    print("Nhan Ctrl+C de dung Server.")
    print("=" * 65)

    try:
        await asyncio.get_running_loop().create_future()
    except asyncio.CancelledError:
        pass
    finally:
        print("\nDang tat Smart Light Server...")
        await server_context.shutdown()
        print("Server da dung hoan toan.")


def main():
    parser = argparse.ArgumentParser(description="Smart Light CoAP Server - Bai 3")
    parser.add_argument("--bind", default="127.0.0.1", help="Dia chi IP bind (mac dinh: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cong CoAP (mac dinh: 5683)")
    parser.add_argument("--device", default="light01", help="Ma thiet bi den (mac dinh: light01)")
    args = parser.parse_args()

    try:
        asyncio.run(run_server(args.bind, args.port, args.device))
    except KeyboardInterrupt:
        print("\nDa dung Server.")


if __name__ == "__main__":
    main()
