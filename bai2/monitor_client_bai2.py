#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bài 2: Mô phỏng cảm biến nhiệt độ và độ ẩm bằng CoAP
Chương trình 2: Monitoring CoAP Client
Tài nguyên: coap://<host>:<port>/iot/lab/<device_id>/data
"""

import sys
import csv
import json
import time
import asyncio
import datetime
import argparse
import aiocoap

if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass


async def monitor_loop(host: str, port: int, device_id: str, interval: float, csv_file: str):
    uri = f"coap://{host}:{port}/iot/lab/{device_id}/data"
    client_context = await aiocoap.Context.create_client_context()

    print("=" * 65, flush=True)
    print("           Monitoring CoAP Client (Sensor Polling)", flush=True)
    print("=" * 65, flush=True)
    print(f"Target URI: {uri}", flush=True)
    print(f"Polling Interval: {interval} seconds", flush=True)
    if csv_file:
        print(f"Luu ket qua vao file CSV: {csv_file}", flush=True)
    print("Nhan Ctrl+C de dung theo doi.", flush=True)
    print("=" * 65, flush=True)

    # Nếu có cấu hình lưu file CSV, ghi tiêu đề cột
    if csv_file:
        try:
            with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Chỉ ghi header nếu file rỗng
                if f.tell() == 0:
                    writer.writerow(["Timestamp", "Device", "Temperature_C", "Humidity_Pct", "Alerts", "Latency_ms"])
        except Exception as e:
            print(f"Luu y: Khong the tao file CSV ({e})")

    request_count = 0
    total_latency_ms = 0.0

    try:
        while True:
            request_count += 1
            request = aiocoap.Message(code=aiocoap.Code.GET, uri=uri)
            start_time = time.perf_counter()

            try:
                response = await asyncio.wait_for(client_context.request(request).response, timeout=4.0)
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                total_latency_ms += elapsed_ms

                now_str = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"[{now_str}] Received sensor data (Latency: {elapsed_ms:.1f}ms)", flush=True)

                data = json.loads(response.payload.decode("utf-8"))
                dev = data.get("device_id", device_id)
                temp = float(data.get("temperature", 0.0))
                hum = float(data.get("humidity", 0.0))

                print(f"Device: {dev}", flush=True)
                print(f"Temperature: {temp:.1f} C", flush=True)
                print(f"Humidity: {hum:.1f} %", flush=True)

                # Kiểm tra các điều kiện cảnh báo
                alerts = []
                if temp > 35.0:
                    print("CANH BAO: Nhiet do cao", flush=True)
                    alerts.append("HIGH_TEMP")
                if hum < 40.0:
                    print("CANH BAO: Do am thap", flush=True)
                    alerts.append("LOW_HUMIDITY")

                if not alerts:
                    print("Trang thai: Binh thuong", flush=True)

                print("-" * 35, flush=True)

                # Ghi vào file CSV nếu bật
                if csv_file:
                    try:
                        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow([
                                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                dev, temp, hum,
                                ";".join(alerts) if alerts else "NORMAL",
                                f"{elapsed_ms:.1f}"
                            ])
                    except Exception:
                        pass

            except asyncio.TimeoutError:
                now_str = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"[{now_str}] Canh bao: Yeu cau bi Timeout! Server khong phan hoi.")
                print("-" * 35)
            except Exception as ex:
                now_str = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"[{now_str}] Loi ket noi: {ex}")
                print("-" * 35)

            await asyncio.sleep(interval)

    finally:
        await client_context.shutdown()
        if request_count > 0:
            avg_latency = total_latency_ms / max(1, request_count)
            print("\n" + "=" * 45)
            print("THONG KE GIAM SAT:")
            print(f"- Tong so yeu cau gui: {request_count}")
            print(f"- Thoi gian phan hoi trung binh: {avg_latency:.2f} ms")
            print("=" * 45)


def main():
    parser = argparse.ArgumentParser(description="Monitoring CoAP Client - Bai 2")
    parser.add_argument("--host", default="127.0.0.1", help="Dia chi CoAP Server (mac dinh: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5683, help="Cong CoAP Server (mac dinh: 5683)")
    parser.add_argument("--device", default="sensor01", help="Ma thiet bi cam bien (mac dinh: sensor01)")
    parser.add_argument("--interval", type=float, default=3.0, help="Chu ky polling giay (mac dinh: 3.0)")
    parser.add_argument("--csv", default="", help="Duong dan file CSV ghi log (vi du: sensor_data.csv)")
    args = parser.parse_args()

    try:
        asyncio.run(monitor_loop(args.host, args.port, args.device, args.interval, args.csv))
    except KeyboardInterrupt:
        print("\nDa dung chuong trinh giam sat.")


if __name__ == "__main__":
    main()
