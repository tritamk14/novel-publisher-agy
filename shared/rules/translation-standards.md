# 📏 Tiêu Chuẩn Chất Lượng Dịch Thuật

Định nghĩa các tiêu chuẩn chất lượng cho bản dịch. Bản dịch phải đạt
TẤT CẢ các tiêu chuẩn dưới đây mới được coi là chất lượng xuất bản.

---

## 1. Tiêu Chuẩn Bắt Buộc (Must-Pass)

Nếu vi phạm bất kỳ điều nào dưới đây, bản dịch cần sửa lại.

### 1.1 Nhất quán nhân vật
- ✅ Mỗi nhân vật có TÊN DỊCH DUY NHẤT xuyên suốt truyện
- ✅ Biệt danh dùng đúng ngữ cảnh
- ✅ Không nhầm nhân vật A thành B
- ✅ Nhân vật đã chết/đi không tự nhiên xuất hiện lại (trừ flashback)

### 1.2 Nhất quán xưng hô
- ✅ Xưng hô trong đối thoại đúng theo relationships.yaml
- ✅ Xưng hô thay đổi đúng phase (đúng chương)
- ✅ Xưng hô trong tường thuật phù hợp POV và sắc thái
- ✅ Không có hiện tượng "xuyên không xưng hô" (phase sai)

### 1.3 Đầy đủ nội dung
- ✅ Không thiếu bất kỳ đoạn nào so với bản gốc
- ✅ Không thêm nội dung không có trong bản gốc
- ✅ Số lượng đoạn hội thoại tương đương bản gốc
- ✅ Mô tả cảnh, hành động, nội tâm đầy đủ

### 1.4 Nhất quán thuật ngữ
- ✅ Thuật ngữ đúng theo glossary/terms.yaml
- ✅ Địa danh, chức danh, tên tổ chức nhất quán
- ✅ Không dịch cùng một thuật ngữ bằng nhiều cách khác nhau

---

## 2. Tiêu Chuẩn Chất Lượng (Quality Standards)

### 2.1 Tự nhiên (Naturalness)

**Tiêu chí:** Đọc như văn Việt gốc, không thấy dấu hiệu dịch.

| Mức | Mô tả |
|-----|-------|
| A | Đọc hoàn toàn tự nhiên, không nhận ra là bản dịch |
| B | Hầu hết tự nhiên, đôi chỗ hơi "dịch" nhưng chấp nhận được |
| C | Nhiều chỗ đọc lộ dịch, câu cứng |
| D | Đọc như Google Translate có chỉnh sửa |

→ Yêu cầu tối thiểu: **Mức B**

### 2.2 Cảm xúc (Emotional Fidelity)

**Tiêu chí:** Bản dịch giữ đúng tông cảm xúc của bản gốc.

| Mức | Mô tả |
|-----|-------|
| A | Cảm xúc mãnh liệt, đọc rung động |
| B | Cảm xúc đúng tông, có thể chưa sâu bằng gốc |
| C | Cảm xúc phẳng, đọc không rung động |
| D | Cảm xúc sai tông (buồn thành vui, vui thành flat) |

→ Yêu cầu tối thiểu: **Mức B**

### 2.3 Nhịp văn (Pacing)

**Tiêu chí:** Nhịp văn phù hợp với nội dung.

- Cảnh lãng mạn: nhịp chậm, mượt mà
- Cảnh hành động: nhịp nhanh, gọn
- Cảnh ngược: nhịp thay đổi, cao trào
- Cảnh hài: timing đúng, punchline đúng chỗ

→ Yêu cầu: Nhịp văn phù hợp với nội dung cảnh

### 2.4 Đối thoại (Dialogue Quality)

**Tiêu chí:** Đối thoại nghe như người thật nói.

- ✅ Mỗi nhân vật có "giọng" riêng (personality through voice)
- ✅ Câu ngắn, tự nhiên, có ngữ khí từ khi cần
- ✅ Không nói kiểu "sách giáo khoa"
- ✅ Phân biệt được ai đang nói qua cách nói (không cần đọc "anh nói")

---

## 3. Quy Trình Đảm Bảo Chất Lượng

### 3.1 Trong quá trình dịch (Inline QA)
- Dịch giả tự kiểm tra xưng hô sau mỗi đoạn đối thoại
- Đọc lại toàn chương sau khi dịch xong
- Kiểm tra liên tục với chương trước

### 3.2 Review sau dịch (Post-Translation Review)
- Chạy prompt 03-review-chapter.md
- Sửa tất cả lỗi CRITICAL
- Sửa lỗi MAJOR nếu có thể
- Ghi nhận lỗi MINOR cho batch sửa sau

### 3.3 Khi phát hiện lỗi hệ thống
Nếu phát hiện lỗi lặp lại ở nhiều chương:
1. Xác định nguyên nhân gốc (registry sai? relationship sai? glossary thiếu?)
2. Sửa file gốc
3. Dịch lại các chương bị ảnh hưởng

---

## 4. Anti-Patterns — Các Lỗi Phải Tránh

### Lỗi "Google Translate có chỉnh"
```
❌ "Anh ấy đặt tay của mình lên vai của cô ấy"
✅ "Anh đặt tay lên vai cô"
```

### Lỗi "Dịch thừa đại từ"
Tiếng Trung hay dùng 他/她, tiếng Việt không cần lặp lại nhiều.
```
❌ "Cô ấy nhìn anh ấy. Cô ấy cảm thấy anh ấy rất đẹp trai. Cô ấy nghĩ..."
✅ "Cô nhìn anh, lòng thầm nghĩ sao mà người này đẹp trai đến vậy..."
```

### Lỗi "Dịch thành ngữ word-by-word"
```
❌ "Tim cô như bị một con hươu đâm" (心如鹿撞)
✅ "Tim cô đập thình thịch"
```

### Lỗi "Văn phong sách giáo khoa"
```
❌ "Tôi rất vui vì được gặp lại anh. Tôi đã rất nhớ anh trong thời gian qua."
✅ "Lâu rồi mới gặp lại... Em nhớ anh lắm."
```

### Lỗi "Quá trung thành với cấu trúc Trung"
```
❌ "Sau khi ăn xong cơm, sau đó anh ấy mới đi ra ngoài"
✅ "Ăn xong, anh mới ra ngoài"
```

---

## 5. Checklist Cuối Cùng

Trước khi coi một chương là "hoàn thành":

- [ ] Đọc lại toàn chương — đọc to thành tiếng nếu cần
- [ ] Kiểm tra xưng hô mọi đoạn đối thoại
- [ ] Đối chiếu nhanh với bản gốc — có thiếu đoạn không?
- [ ] Đọc liền với chương trước — có gãy mạch không?
- [ ] Tự hỏi: "Nếu đây là sách mua ở nhà sách, mình có hài lòng không?"
