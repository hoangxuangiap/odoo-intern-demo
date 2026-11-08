# intern_perf_demo (Bài 5.4)
**Mục đích:** code chậm cho sẵn (search trong for, compute không store) + phiên bản tối ưu (`_read_group`, SQL có tham số, compute theo lô) + wizard đo thời gian và số query.
**Cách dùng:** Settings › Technical › Performance Lab (Developer mode): 1) Generate sample data 2) Run benchmark. Có thể bật Profiler (biểu tượng con bọ) để xem flamegraph.
**Hạn chế:** số query lấy từ `cursor.sql_log_count`; kết quả phụ thuộc máy.
