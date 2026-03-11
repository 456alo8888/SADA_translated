# Implementation Report

## Những gì đã thay đổi

1. **Thêm module preprocess mới**
   - Tạo file `preprocess.py` với hàm `min_max_normalize(data)`.
   - Hàm này chuẩn hóa các cột số về khoảng `[0, 1]` theo công thức Min-Max.
   - Với cột hằng số (`max == min`), giá trị được đưa về `0.0` để tránh chia cho 0.
   - Cột không phải số được giữ nguyên.

2. **Tích hợp preprocessing vào luồng chạy chính**
   - Trong `main.py`, import hàm `min_max_normalize` từ module preprocess mới.
   - Áp dụng chuẩn hóa Min-Max cho dữ liệu ngay sau khi đọc `data.csv`.

3. **Đổi Conditional Independence Test sang KCIT**
   - Trong `SADA.py`, đổi thiết lập cho dữ liệu continuous từ `fisherz` sang `kci`:
     - `ci_test = 'kci'`
     - `CIT(..., method='kci')`

## Tình trạng hiện tại của project

- Project đã có preprocessing chuẩn hóa Min-Max ở đầu pipeline chạy chính.
- Nhánh SADA cho dữ liệu continuous hiện dùng KCIT thay cho Fisher Z.
- Các phần chưa hoàn thiện từ trước vẫn giữ nguyên (ví dụ `CAPA.py` và một số placeholder `...`).
- Đã kiểm tra nhanh cú pháp bằng `python -m compileall` cho các file chính.
