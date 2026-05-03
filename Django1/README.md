# Website Đọc Truyện Trực Tuyến

# Những cái quan trọng ở dưới cùng#

## 1. Giới thiệu

Dự án **Website Đọc Truyện Trực Tuyến** được xây dựng trong khuôn khổ học phần **Phát triển Ứng dụng Python** – Khoa Công nghệ Thông tin, Trường Đại học Công nghệ Thông tin & Truyền Thông.

Hệ thống cho phép người dùng đọc truyện online, tìm kiếm, theo dõi truyện yêu thích và tương tác thông qua bình luận, đánh giá. Quản trị viên có thể quản lý nội dung và theo dõi thống kê hoạt động của website.

---

## 2. Mục tiêu dự án

- Xây dựng một ứng dụng web hoàn chỉnh bằng Python.
- Áp dụng framework Django vào phát triển ứng dụng thực tế.
- Thiết kế và triển khai cơ sở dữ liệu có quan hệ.
- Thực hiện đầy đủ các chức năng CRUD, xác thực và phân quyền người dùng.
- Hoàn thiện tài liệu và mã nguồn theo chuẩn dự án phần mềm.

---

## 3. Công nghệ sử dụng

### Backend

- Python 3.14
- Django Framework
- Django ORM
- Django Authentication

### Frontend

- HTML5, CSS3
- Bootstrap 5
- Django Template Engine
- JavaScript
- Chart.js (Thư viện vẽ biểu đồ thống kê)

### Cơ sở dữ liệu

- SQLite (môi trường phát triển)
- PostgreSQL (định hướng triển khai thực tế)

---

## 4. Các chức năng chính

- Đăng ký, đăng nhập, đăng xuất người dùng
- Phân quyền Guest / User / Admin
- Quản lý truyện tập và chương (CRUD)
- Tìm kiếm và lọc truyện theo nhiều tiêu chí
- Đọc truyện, chuyển chương
- Bình luận và đánh giá truyện
- Bookmark truyện yêu thích
- Thống kê số lượng truyện và người dùng
  -Quản trị & Thống kê:

+Báo cáo cơ cấu truyện theo thể loại (biểu đồ Pie).

## +Thống kê top truyện tương tác cao (biểu đồ Bar).

## 5. Tiến độ thực hiện

### Đã hoàn thành

- Phân tích yêu cầu hệ thống
- Xác định nghiệp vụ và vai trò người dùng
- Thiết kế Use Case Diagram
- Thiết kế ERD (Entity–Relationship Diagram)
- Khởi tạo project Django
- Thiết kế cấu trúc CSDL
- Tạo seed data mẫu
- Xây dựng chức năng CRUD cho Truyện và Chapter
- Hoàn thiện chức năng Authentication
- Thiết kế giao diện đọc truyện
- Hoàn thiện giao diện người dùng
- Xây dựng chức năng thống kê – báo cáo
- Kiểm thử và tối ưu hệ thống
- Hoàn thiện báo cáo và slide thuyết trình

---

## 6. Hướng dẫn cài đặt và chạy thử

### 6.1. Yêu cầu hệ thống

- Python 3.14
- pip
- virtualenv (khuyến khích)

### 6.2. Các bước cài đặt

Bước 1: Clone source code
git clone https://github.com/SuigintouS5/web-doc-truyen
cd web-doc-truyen

Bước 2: Cài đặt thư viện
pip install -r requirements.txt

Bước 3: Migration database
python manage.py migrate

Bước 4: Chạy server
python manage.py runserver

### Tài khoản mẫu

gmail:thtruex1@gmail.com
mật khẩu:kankin2005

## video cách dùng

https://www.youtube.com/watch?v=FFrUrKtp70I

## Nhóm thực hiện

Nhóm 19

Chung Dương Thiên Phước

Trần Quang Công
