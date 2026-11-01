#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bài 2: Mô phỏng cảm biến nhiệt độ và độ ẩm bằng CoAP
Chương trình 1: Sensor CoAP Server
Tài nguyên: coap://<host>:<port>/iot/lab/<device_id>/data
"""

import sys
import json
import random
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


class SensorDataResource(resource.Resource):
    """
    Tài nguyên cung cấp dữ liệu cảm biến dạng JSON
    """

    def __init__(self, device_id: str = "sensor01"):
        super().__init__()
        self.device_id = device_id
        self.temperature = 28.0
        self.humidity = 60.0
        self.last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_new_data(self):
        """
        Sinh ngẫu nhiên giá trị nhiệt độ và độ ẩm trong khoảng thực tế:
        - Nhiệt độ: 22.0°C đến 39.0°C (thi thoảng > 35°C để thử nghiệm cảnh báo)
        - Độ ẩm: 32.0% đến 80.0% (thi thoảng < 40% để thử nghiệm cảnh báo)
        """
        self.temperature = round(random.uniform(22.0, 39.0), 1)
        self.humidity = round(random.uniform(32.0, 80.0), 1)
        self.last_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def render_get(self, request):
        """
        Xử lý yêu cầu GET: Trả về dữ liệu cảm biến mới nhất dạng JSON
        """
        now = datetime.datetime.now().strftime("%H:%M:%S")
        client_addr = request.remote if request.remote is not None else "Client"
        print(f"[{now}] GET request from {client_addr}")
        print(f"       Data: Temp={self.temperature}°C, Humidity={self.humidity}%")

        payload_dict = {
            "device_id": self.device_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "timestamp": self.last_update
        }

        payload_bytes = json.dumps(payload_dict, indent=2).encode("utf-8")

        return aiocoap.Message(
            code=aiocoap.Code.CONTENT,
            payload=payload_bytes,
            content_format=aiocoap.numbers.ContentFormat.JSON
        )


async def sensor_simulator_task(sensor_res: SensorDataResource, interval_sec: float = 3.0):
    """
    Tác vụ ngầm tự động cập nhật dữ liệu cảm biến sau mỗi interval_sec giây
    """
    while True:
        sensor_res.generate_new_data()
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Sensor updated -> Temp: {sensor_res.temperature}°C | Hum: {sensor_res.humidity}%")
        await asyncio.sleep(interval_sec)


def resolve_bind_ip(bind_ip: str) -> str:
    if bind_ip in ("", "0.0.0.0", "::"):
        return "127.0.0.1"
    return bind_ip


async def run_server(bind_ip: str, port: int, device_id: str, interval: float):
    bind_ip = resolve_bind_ip(bind_ip)
    root = resource.Site()
    sensor_res = SensorDataResource(device_id=device_id)

    # Thêm tài nguyên theo URI: /iot/lab/<device_id>/data
    resource_path = ["iot", "lab", device_id, "data"]
    root.add_resource(resource_path, sensor_res)

    server_context = await aiocoap.Context.create_server_context(
        root, bind=(bind_ip, port)
    )

    print("=" * 65)
    print("           CoAP Sensor Server (Temperature & Humidity)")
    print("=" * 65)
    print(f"Server started on port {port} (Bound to {bind_ip})")
    print(f"Device ID: {device_id}")
    print(f"Cap nhat du lieu moi: {interval} giay/lan")
    print("URI tai nguyen:")
    print(f"  coap://localhost:{port}/iot/lab/{device_id}/data")
    print("Nhan Ctrl+C de dung Server.")
    print("=" * 65)

    # Chạy tác vụ mô phỏng cảm biến trong nền
    sim_task = asyncio.create_task(sensor_simulator_task(sensor_res, interval))

    try:
        await asyncio.get_running_loop().create_future()
    except asyncio.CancelledError:
        pass
    finally:
        sim_task.cancel()
        print("\nDang tat Sensor Server...")
        await server_context.shutdown()
        print("Server da dung hoan toan.")


def main():
    parser = argparse.ArgumentParser(description="Sensor CoAP Server - Bai 2")
    parser.add_argument("--bind", default="127.0.0.1", help="Dia chi IP bind (mac dinh: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cong CoAP (mac dinh: 5683)")
    parser.add_argument("--device", default="sensor01", help="Ma cam bien (mac dinh: sensor01)")
    parser.add_argument("--interval", type=float, default=3.0, help="Chu ky sinh du lieu giay (mac dinh: 3.0)")
    args = parser.parse_args()

    try:
        asyncio.run(run_server(args.bind, args.port, args.device, args.interval))
    except KeyboardInterrupt:
        print("\nDa dung boi nguoi dung.")


if __name__ == "__main__":
    main()
