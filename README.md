# BÁO CÁO THỰC HÀNH: LẬP TRÌNH PYTHON VỚI GIAO THỨC CoAP (Constrained Application Protocol)

> **Môn học:** IOT | 
> **Hình thức nộp bài:** GitHub Repository

---

## 1. Thông tin sinh viên / Nhóm thực hiện
| Họ và tên | Mã sinh viên |
| :--- | :--- |
| Lê Đình Thức | B23DCCN803 |
| Đỗ Minh Hoàng | B23DCCN328 |
| Nguyễn Hoàng Quốc Việt | B22DCCN897 |

---

## 2. Giới thiệu tổng quan & Môi trường thực hiện

### 2.1. Giới thiệu giao thức CoAP
- **CoAP (Constrained Application Protocol - RFC 7252)** là giao thức truyền thông chuyên dụng dành cho các thiết bị IoT bị giới hạn tài nguyên (CPU, RAM, băng thông).
- Hoạt động trên tầng giao vận **UDP**, sử dụng cổng mặc định **5683**.
- Kế thừa mô hình RESTful tương tự HTTP (GET, POST, PUT, DELETE) với kích thước header rất nhẹ (tối thiểu 4 bytes).
- Hỗ trợ cơ chế **CoAP Observe (RFC 7641)** theo mô hình Publish/Subscribe trực tiếp trên giao thức CoAP mà không cần Broker trung gian.

### 2.2. Môi trường phát triển & Thư viện
- **Hệ điều hành:** Windows 10/11, Linux, macOS
- **Phiên bản Python:** Python 3.8+ (Khuyến nghị Python 3.10, 3.11 hoặc 3.12)
- **Thư viện chính:**
  - `aiocoap>=0.4.17`: Thư viện bất đồng bộ (asyncio) hỗ trợ đầy đủ CoAP Client, CoAP Server và Observe (RFC 7641).

---

## 3. Cấu trúc thư mục dự án

```text
CoAP_Lab/
│
├── bai1/
│   ├── coap_server_bai1.py       # CoAP Server bài 1 (Tài nguyên /iot/lab/message)
│   └── coap_client_bai1.py       # CoAP Client bài 1 (Gửi GET và POST)
│
├── bai2/
│   ├── sensor_server_bai2.py     # Sensor Server bài 2 (Mô phỏng nhiệt độ, độ ẩm)
│   └── monitor_client_bai2.py    # Monitoring Client bài 2 (Polling GET chu kỳ 3s)
│
├── bai3/
│   ├── light_server_bai3.py      # Smart Light Server bài 3 (Tài nguyên /status + Observe)
│   ├── light_controller_bai3.py  # Controller Client bài 3 (Điều khiển PUT ON/OFF)
│   └── light_monitor_bai3.py     # Observe Client bài 3 (Tự động nhận Notification)
│
├── requirements.txt              # Danh sách thư viện phụ thuộc
├── .gitignore                    # Bỏ qua các file rác, môi trường ảo (.venv)
└── README.md                     # Báo cáo thực hành chi tiết
```

---

## 4. Hướng dẫn cài đặt môi trường

### Bước 1: Clone kho mã nguồn từ GitHub
```bash
git clone (https://github.com/LeDinhThucPTIT/ThuchanhIOT_Buoi3)
cd CoAP_Lab
```

### Bước 2: Tạo và kích hoạt môi trường ảo (Khuyến nghị)
- **Trên Windows (PowerShell/CMD):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\activate
  ```
- **Trên Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Bước 3: Cài đặt thư viện aiocoap
```bash
pip install -r requirements.txt
```
*(Hoặc cài đặt trực tiếp qua `pip install aiocoap`)*

---

## 5. Danh mục Tài nguyên CoAP (URI, Cổng, Phương thức)

| Bài | Tên thành phần | Cổng UDP | Đường dẫn URI | Phương thức hỗ trợ | Định dạng Payload |
|:---:|:---|:---:|:---|:---:|:---:|
| **Bài 1** | Message Resource | 5683 | `coap://<server_ip>:5683/iot/lab/message` | `GET`, `POST` | `text/plain` |
| **Bài 2** | Sensor Data | 5683 | `coap://<server_ip>:5683/iot/lab/sensor01/data` | `GET` | `application/json` |
| **Bài 3** | Smart Light State | 5683 | `coap://<server_ip>:5683/iot/lab/light01/status` | `GET`, `PUT`, `OBSERVE` | `application/json` |

---

## 6. Hướng dẫn chạy và Kết quả thực nghiệm từng bài

### BÀI 1: Ứng dụng gửi và nhận thông điệp CoAP cơ bản

#### 1. Mô tả
- **Server:** Lắng nghe trên cổng 5683, cung cấp tài nguyên `/iot/lab/message`.
  - Phương thức `GET`: Trả về thông điệp chào mừng và thông điệp sinh viên gần nhất.
  - Phương thức `POST`: Nhận thông điệp chứa Họ tên và Mã sinh viên, in ra màn hình thời điểm nhận và phản hồi `2.04 Changed`.
- **Client:** Gửi `GET` ban đầu, sau đó gửi `POST` thông điệp sinh viên, và gửi lại `GET` kiểm tra server lưu trữ. Có hỗ trợ cờ tương tác `--interactive`.

#### 2. Lệnh thực thi (Chạy 2 Terminal riêng biệt)
- **Terminal 1 (Server):**
  ```bash
  python bai1/coap_server_bai1.py --bind 127.0.0.1 --port 5683
  ```
- **Terminal 2 (Client):**
  ```bash
  python bai1/coap_client_bai1.py --host 127.0.0.1 --port 5683 --id B23DCCN001 --name "Nguyen Van A"
  ```

#### 3. Log thực tế minh chứng
- **Log phía Client:**
  ```text
  CoAP Client
  Sending GET request...
  URI: coap://127.0.0.1:5683/iot/lab/message
  Response:
  Code: 2.05 Content
  Payload: Xin chao tu CoAP Server

  Sending POST request...
  Payload: Xin chao tu CoAP Client - B23DCCN001 - Nguyen Van A
  Response:
  Code: 2.04 Changed
  Payload: Server da nhan thong diep

  --- Kiem tra thong diep luu tren Server bang GET lan 2 ---
  CoAP Client
  Sending GET request...
  URI: coap://127.0.0.1:5683/iot/lab/message
  Response:
  Code: 2.05 Content
  Payload: Xin chao tu CoAP Server (Thong diep gan nhat: "Xin chao tu CoAP Client - B23DCCN001 - Nguyen Van A")
  ```

- **Log phía Server:**
  ```text
  CoAP Server started on port 5683
  Listening on: 127.0.0.1:5683
  Resource available at:
    coap://localhost:5683/iot/lab/message
  Nhan Ctrl+C de dung Server.
  ============================================================
  [10:15:18] GET request received: /iot/lab/message

  POST request received:
  Payload: Xin chao tu CoAP Client - B23DCCN001 - Nguyen Van A
  Time: 10:15:20
  [10:15:21] GET request received: /iot/lab/message
  ```

---

### BÀI 2: Mô phỏng cảm biến nhiệt độ và độ ẩm bằng CoAP

#### 1. Mô tả
- **Sensor Server:** Mô phỏng thiết bị `sensor01`, tự động cập nhật ngẫu nhiên giá trị nhiệt độ và độ ẩm sau mỗi 3 giây; trả về JSON với `ContentFormat.JSON` khi có yêu cầu `GET`.
- **Monitoring Client:** Polling định kỳ mỗi 3 giây gửi yêu cầu `GET`, phân tích dữ liệu và kích hoạt cảnh báo:
  - Nếu `temperature > 35.0°C` $\rightarrow$ Hiển thị `"CANH BAO: Nhiet do cao"`.
  - Nếu `humidity < 40.0%` $\rightarrow$ Hiển thị `"CANH BAO: Do am thap"`.
  - Nếu trong ngưỡng bình thường $\rightarrow$ Hiển thị `"Trang thai: Binh thuong"`.
  - Tính thời gian phản hồi (latency), hỗ trợ lưu bản ghi ra file CSV (`--csv sensor_data.csv`).

#### 2. Lệnh thực thi
- **Terminal 1 (Sensor Server):**
  ```bash
  python bai2/sensor_server_bai2.py --bind 127.0.0.1 --port 5683 --device sensor01 --interval 3.0
  ```
- **Terminal 2 (Monitoring Client):**
  ```bash
  python bai2/monitor_client_bai2.py --host 127.0.0.1 --port 5683 --device sensor01 --interval 3.0 --csv sensor_log.csv
  ```

#### 3. Log thực tế minh chứng
- **Log phía Monitoring Client:**
  ```text
  =================================================================
             Monitoring CoAP Client (Sensor Polling)
  =================================================================
  Target URI: coap://127.0.0.1:5683/iot/lab/sensor01/data
  Polling Interval: 3.0 seconds
  Luu ket qua vao file CSV: sensor_log.csv
  Nhan Ctrl+C de dung theo doi.
  =================================================================
  [10:20:03] Received sensor data (Latency: 2.5ms)
  Device: sensor01
  Temperature: 36.1 C
  Humidity: 38.7 %
  CANH BAO: Nhiet do cao
  CANH BAO: Do am thap
  -----------------------------------
  [10:20:06] Received sensor data (Latency: 2.1ms)
  Device: sensor01
  Temperature: 29.4 C
  Humidity: 62.5 %
  Trang thai: Binh thuong
  -----------------------------------
  [10:20:09] Received sensor data (Latency: 2.3ms)
  Device: sensor01
  Temperature: 37.2 C
  Humidity: 55.0 %
  CANH BAO: Nhiet do cao
  -----------------------------------
  ```

---

### BÀI 3: Mô phỏng hệ thống giám sát và điều khiển đèn thông minh bằng CoAP Observe

#### 1. Mô tả
- **Mô hình hai chiều (Full-Duplex Monitoring & Actuation):**
  - **Server (`light_server_bai3.py`):** Tài nguyên `/iot/lab/light01/status` kế thừa `ObservableResource`. Trạng thái ban đầu là `OFF`.
    - Hỗ trợ `GET`: Trả về trạng thái hiện tại.
    - Hỗ trợ `PUT`: Nhận lệnh `{"device_id": "light01", "command": "ON"}` hoặc `OFF`. Khi trạng thái thay đổi, Server gọi hàm `self.updated_state()`.
    - Hỗ trợ `OBSERVE`: Tự động gửi gói tin Notification (RFC 7641) tới tất cả các Monitor Client đang đăng ký mà không cần Client phải liên tục gửi GET (polling).
  - **Controller Client (`light_controller_bai3.py`):** Giao diện tương tác bàn phím (`ON`, `OFF`, `STATUS`, `EXIT`) gửi PUT/GET tới Server.
  - **Monitoring Client (`light_monitor_bai3.py`):** Đăng ký CoAP Observe (`observe=0`) và lắng nghe luồng sự kiện bất đồng bộ qua `async for notification in pr.observation`.

#### 2. Lệnh thực thi (Chạy trên 3 Terminal đồng thời)
- **Terminal 1 (Smart Light Server):**
  ```bash
  python bai3/light_server_bai3.py --bind 127.0.0.1 --port 5683 --device light01
  ```
- **Terminal 2 (Controller Client):**
  ```bash
  python bai3/light_controller_bai3.py --host 127.0.0.1 --port 5683 --device light01
  ```
- **Terminal 3 (Monitoring Client - CoAP Observe):**
  ```bash
  python bai3/light_monitor_bai3.py --host 127.0.0.1 --port 5683 --device light01
  ```

#### 3. Log thực tế minh chứng

- **Terminal 1 – Smart Light Server:**
  ```text
  =================================================================
  CoAP Smart Light Server started...
  Resource: /iot/lab/light01/status
  URI: coap://localhost:5683/iot/lab/light01/status
  Initial State: OFF
  Supports: GET, PUT, and CoAP Observe
  Nhan Ctrl+C de dung Server.
  =================================================================
  [10:30:00] New Observe registration received from 127.0.0.1:52134

  PUT request received:
  Device: light01
  Command: ON
  Light state changed: OFF -> ON
  Notify observers: ON

  PUT request received:
  Device: light01
  Command: OFF
  Light state changed: ON -> OFF
  Notify observers: OFF
  ```

- **Terminal 2 – Controller Client:**
  ```text
  Nhap lenh (ON/OFF/STATUS/EXIT): ON
  Sending PUT request...
  Response Code: 2.04 Changed
  Da bat den light01
  Nhap lenh (ON/OFF/STATUS/EXIT): STATUS
  Sending GET request...
  Response:
  {"device_id": "light01", "status": "ON", "timestamp": "2026-11-01 10:30:15"}
  Nhap lenh (ON/OFF/STATUS/EXIT): OFF
  Sending PUT request...
  Response Code: 2.04 Changed
  Da tat den light01
  ```

- **Terminal 3 – Monitoring Client (Observe Notification tức thời):**
  ```text
  ============================================================
          Light Monitoring Client (CoAP Observe - RFC 7641)
  ============================================================
  Monitoring Resource: coap://127.0.0.1:5683/iot/lab/light01/status
  Dang ky nhan thong bao tu dong khi trang thai thay doi...
  Nhan Ctrl+C de huy dang ky va thoat.
  ============================================================
  Registering CoAP Observe...
  Observe registration successful
  [10:30:00] Initial State
  Device: light01
  Status: OFF
  -----------------------------------
  [10:30:15] State Updated
  Device: light01
  Status: ON
  -----------------------------------
  [10:30:25] State Updated
  Device: light01
  Status: OFF
  -----------------------------------
  ```

---

## 7. Triển khai giữa 2 máy tính khác nhau qua mạng LAN
Khi triển khai Server và Client trên hai máy tính độc lập trong mạng nội bộ:
1. **Trên máy chạy Server:**
   - Xác định địa chỉ IP máy server (ví dụ `192.168.1.15` qua lệnh `ipconfig` trên Windows hoặc `ip a` trên Linux).
   - Mở port UDP 5683 trên Windows Defender Firewall:
     ```powershell
     netsh advfirewall firewall add rule name="CoAP_5683_UDP" dir=in action=allow protocol=UDP localport=5683
     ```
   - Khởi động server với IP máy:
     ```bash
     python bai1/coap_server_bai1.py --bind 192.168.1.15 --port 5683
     ```
2. **Trên máy chạy Client:**
   - Chỉ định tham số `--host 192.168.1.15`:
     ```bash
     python bai1/coap_client_bai1.py --host 192.168.1.15 --port 5683
     ```

---

## 8. Kết luận & Đánh giá đạt được
- Đã nắm vững nguyên lý hoạt động của giao thức **CoAP**, sự khác biệt và tối ưu so với HTTP trong môi trường mạng IoT.
- Xây dựng thành công toàn bộ mã nguồn theo chuẩn kiến trúc bất đồng bộ `asyncio` và thư viện `aiocoap`.
- Đáp ứng chính xác và đầy đủ tất cả các yêu cầu về:
  - Phương thức `GET`, `POST`, `PUT` và chuẩn mã trạng thái CoAP (`2.05 Content`, `2.04 Changed`, `4.00 Bad Request`).
  - Định dạng chuẩn JSON (`application/json`).
  - Cơ chế **CoAP Observe (RFC 7641)** tự động thông báo mà không cần Polling.
- Mã nguồn được tổ chức module hóa, xử lý ngoại lệ chặt chẽ (Timeout, đứt kết nối, dừng chương trình với `Ctrl+C`).
"# ThuchanhIOT_Buoi3" 
