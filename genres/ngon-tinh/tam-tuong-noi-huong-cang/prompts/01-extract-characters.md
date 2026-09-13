# 🔍 Prompt: Trích Xuất & Xây Dựng Hồ Sơ Nhân Vật
# Chạy prompt này TRƯỚC KHI dịch. Agent sẽ quét raw chapters và tạo character registry.

## Nhiệm vụ

Bạn là chuyên gia phân tích tiểu thuyết Trung Quốc. Nhiệm vụ của bạn là quét toàn bộ các chương trong thư mục `raw/` và xây dựng hồ sơ nhân vật hoàn chỉnh.

## Quy trình thực hiện

### Bước 1: Đọc cấu hình

Đọc file `config.yaml` để hiểu bối cảnh truyện (thể loại, bối cảnh, tông giọng).

### Bước 2: Quét nhân vật

Đọc **tất cả** các file trong `raw/` theo thứ tự (chapter-001, chapter-002, ...).

Với mỗi chương, trích xuất:
- Tên nhân vật xuất hiện (tất cả các dạng: tên đầy đủ, biệt danh, chức danh)
- Giới tính (suy luận từ ngữ cảnh nếu không rõ ràng)
- Vai trò trong truyện
- Mối quan hệ với các nhân vật khác
- Cách xưng hô giữa các nhân vật (CHÚ Ý đặc biệt phần này)
- Tính cách (suy luận từ hành động và lời nói)

### Bước 3: Phân loại vai trò

Xếp loại mỗi nhân vật:
- `male_lead` / `female_lead` — Nhân vật chính (thường chỉ có 1 nam 1 nữ trong ngôn tình)
- `male_second` / `female_second` — Nhân vật phụ quan trọng (tình địch, bạn thân...)
- `supporting` — Nhân vật phụ (gia đình, đồng nghiệp, bạn bè...)
- `antagonist` — Phản diện
- `minor` — Thoáng qua (xuất hiện 1-2 lần, không cần theo dõi kỹ)

### Bước 4: Xác định tên dịch

Chuyển tên Trung sang Hán Việt. Quy tắc:
- **Họ + Tên**: Đọc Hán Việt chuẩn (VD: 顾未易 → Cố Vị Dịch)
- **Biệt danh**: Dịch nghĩa hoặc Hán Việt tùy ngữ cảnh
  - 小顾 → Tiểu Cố (Hán Việt vì quen thuộc)
  - 暖暖 → Noãn Noãn (lặp tên thân mật)
- **Chức danh**: Dịch nghĩa + tên (VD: 顾总 → Tổng Cố)
- **Xưng hô gia đình**: Theo chuẩn Việt
  - 爸/爸爸 → ba/bố
  - 妈/妈妈 → mẹ/má
  - 哥/哥哥 → anh
  - 姐/姐姐 → chị
  - 爷爷 → ông (nội)
  - 奶奶 → bà (nội)

### Bước 5: Xây dựng ma trận xưng hô

Đây là bước QUAN TRỌNG NHẤT. Phân tích cách từng nhân vật xưng hô với nhau.

**Lưu ý đặc biệt cho ngôn tình:**

Quan hệ nam nữ chính thường tiến triển qua các phase:
1. **Xa lạ** — tôi/cô, tôi/anh, gọi họ tên đầy đủ
2. **Quen biết** — tôi/cô (anh), gọi tên
3. **Có tình cảm** — bắt đầu chuyển anh/em
4. **Yêu nhau** — anh/em, gọi tên thân mật
5. **Giận/hiểu lầm** — có thể quay lại xa cách

→ Xác định chính xác chương nào chuyển phase (dựa vào sự thay đổi trong nguyên tác).

Quan hệ gia đình thường cố định:
- Con → Bố mẹ: con/bố, con/mẹ
- Bố mẹ → Con: ba(bố)/con gái, mẹ/con

Quan hệ công việc:
- Cấp dưới → Cấp trên: tôi/giám đốc, tôi/sếp
- Cấp trên → Cấp dưới: tôi/tên nhân viên

### Bước 6: Xác định tự xưng tường thuật

Khi tường thuật (narration), nhân vật được gọi bằng gì?
- Nam chính: thường là "anh" hoặc tên
- Nữ chính: thường là "cô" hoặc tên
- Phụ: thường dùng tên hoặc "hắn/cô ta/y"

Quy tắc:
- Nếu đoạn tường thuật theo POV (point of view) của nhân vật nào, dùng đại từ thân mật cho nhân vật đó
- Nhân vật phản diện trong tường thuật: dùng "hắn/thị" hoặc tên

### Bước 7: Trích xuất thuật ngữ

Song song với nhân vật, trích xuất:
- Tên địa danh
- Tên công ty/tổ chức
- Chức danh
- Thuật ngữ chuyên ngành (VD: esport, y học, kinh doanh...)
- Thành ngữ Trung Quốc xuất hiện nhiều lần

### Bước 8: Ghi kết quả

Ghi kết quả vào các file sau (GHI ĐÈ nội dung mẫu):

1. **`characters/registry.yaml`** — Hồ sơ nhân vật đầy đủ
   - Theo đúng format trong file mẫu
   - Mỗi nhân vật phải có đủ: id, name_original, name_translated, gender, role, self_reference
   - Nhân vật minor có thể bỏ qua các trường không quan trọng

2. **`characters/relationships.yaml`** — Ma trận xưng hô
   - Theo đúng format trong file mẫu
   - BẮT BUỘC có: nam chính ↔ nữ chính (tất cả các phase)
   - BẮT BUỘC có: các cặp quan hệ gia đình
   - Nên có: quan hệ bạn bè, đồng nghiệp quan trọng

3. **`glossary/terms.yaml`** — Bảng thuật ngữ
   - Theo đúng format trong file mẫu

## Output

Sau khi hoàn thành, báo cáo tóm tắt:
- Tổng số nhân vật tìm thấy (phân theo role)
- Số cặp quan hệ đã xác định
- Số phase xưng hô đã phát hiện
- Các điểm KHÔNG CHẮC CHẮN cần user review
- Đề xuất điều chỉnh (nếu có)

## Lưu ý quan trọng

- Nếu KHÔNG CHẮC CHẮN về giới tính hoặc quan hệ → ghi chú và hỏi user
- Nếu phát hiện nhân vật CÓ THỂ là cùng một người (nhiều tên gọi) → liệt kê tất cả aliases
- Đặc biệt chú ý phát hiện **bước ngoặt xưng hô** — đó là dấu hiệu thay đổi quan hệ
- Với truyện cổ đại, chú ý xưng hô cổ phong: chàng/nàng, thiếp/phu quân, ta/ngươi
