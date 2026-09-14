#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intro_emoji_decorator.py
Module dùng chung hỗ trợ nhận diện và tự động chèn icon Hoa & Lá ngẫu nhiên luân phiên
vào các dòng mục thông tin (Metadata, Tags, Bullets) của chương giới thiệu EPUB.
"""

from __future__ import annotations

import os
import sys
import zipfile
import argparse
from pathlib import Path
import re
import random
from typing import List, Tuple, Optional

# ================= BỘ EMOJI HOA & LÁ =================
SET_FLOWERS: List[str] = ['🌸', '🪷', '🌷', '🌼', '💐', '🌺', '🌻']
SET_LEAVES: List[str]  = ['🍃', '🌿', '🌱', '🎋', '🍀', '🌾']

EMOJI_PATTERN = re.compile(r'[\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]')

META_REGEX = re.compile(
    r'^(thể loại|tác giả|editor|chuyển ngữ|người dịch|convert|nguồn|tên hán việt|'
    r'tên truyện|tên gốc|số chương|độ dài|lịch ra|giới thiệu|văn án|tiểu kịch trường|'
    r'thiết lập nhân vật|hình mẫu|từ khóa|nhân vật chính|vai chính|nhân vật phụ|'
    r'góc nhìn|tag|tag nội dung|tóm tắt|một câu tóm tắt|giới thiệu tóm tắt|thông điệp|'
    r'chủ đề|cp|couple|lập ý|khác|ghi chú|lưu ý|lời nhắc|lời nhắc nhỏ|note|cảnh báo|'
    r'review|tình trạng|nam chính|nữ chính)\b',
    re.IGNORECASE
)


def clean_leading_emoji_and_markers(text: str) -> str:
    """
    Loại bỏ emoji cũ, ký tự bullet (*, •, -, –) ở đầu chuỗi 
    hoặc nằm ngay sau các thẻ HTML mở (như <b>, <strong>, <i>)
    """
    s = text.strip()
    while True:
        m = re.match(r'^((?:<[a-zA-Z0-9]+[^>]*>\s*)*)(?:' + EMOJI_PATTERN.pattern + r'|[\*•\-\–\—])\s*', s)
        if m:
            s = m.group(1) + s[m.end():]
        else:
            break
    return s


def is_target_line(inner_html: str, tag_name: str = 'p') -> Tuple[bool, str]:
    """
    Xác định xem một dòng trong chương giới thiệu có phải là dòng thông tin
    (Metadata / Tag / Header / Bullet) cần chèn emoji hay không.
    Trả về: (is_target, cleaned_html)
    """
    raw_has_emoji = bool(re.match(r'^((?:<[a-zA-Z0-9]+[^>]*>\s*)*)' + EMOJI_PATTERN.pattern, inner_html.strip()))
    clean = clean_leading_emoji_and_markers(inner_html)
    plain = re.sub(r'<[^>]+>', '', clean).strip()

    # Bỏ qua dòng rỗng, đường kẻ phân cách
    if not plain or plain in ['--', '—', '-', '–', '***']:
        return False, clean
    # Bỏ qua số thứ tự phân đoạn đơn lẻ: 1., 2., 1, 2...
    if re.match(r'^[0-9]+[\.,]\s*$', plain):
        return False, clean

    # 1. Dòng có dấu hai chấm : hoặc ： đi kèm từ khóa metadata
    if ':' in plain or '：' in plain:
        before_colon = plain.split(':', 1)[0].split('：', 1)[0].strip()
        before_colon = re.sub(r'^[\*•\-\–\—\s]+', '', before_colon)
        if META_REGEX.search(before_colon):
            return True, clean
    else:
        # Tiêu đề mục ngắn (dưới 35 ký tự) như "VĂN ÁN", "GIỚI THIỆU TRUYỆN"
        if META_REGEX.search(plain) and len(plain) < 35:
            return True, clean

    # 2. Dòng nguyên bản đã có sẵn emoji -> Rõ ràng là dòng bullet trang trí
    if raw_has_emoji:
        return True, clean

    # 3. Dòng in đậm có dấu hai chấm: <b>Tác giả:</b> hoặc <strong>Editor:</strong>
    if re.match(r'^(<b>|<strong>)[^<:]+:(<br\s*/?>)?\s*</(b|strong)>', clean, flags=re.I):
        return True, clean

    # 4. Khối lưu ý/cảnh báo in nghiêng + in đậm của editor
    if re.match(r'^(<i><strong>|<strong><i>)', clean, flags=re.I):
        return True, clean

    # 5. Khung tiêu đề: 【...】, [...], Hashtag #..., hoặc cặp nhân vật "A × B"
    if plain.startswith('【') or plain.startswith('[') or plain.startswith('#'):
        return True, clean
    if ' × ' in plain or ' x ' in plain:
        return True, clean

    # 6. Thẻ h4 được dùng làm sub-header trong nội dung
    if tag_name.lower() == 'h4':
        return True, clean

    return False, clean


def process_intro_html(raw_html: str, seed: Optional[int] = None) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Xử lý HTML của chương giới thiệu:
    - Bóc emoji cũ
    - Chèn emoji Hoa & Lá ngẫu nhiên luân phiên vào các dòng mục tiêu
    - Giữ nguyên các đoạn văn án tự sự trơn, thoáng
    """
    rng = random.Random(seed) if seed is not None else random.Random()

    tag_regex = re.compile(r'(<(p|h4)(?:\s+[^>]*)?>)(.*?)(</\2>)', flags=re.DOTALL | re.IGNORECASE)

    last_type: Optional[str] = None
    log_changes: List[Tuple[str, str]] = []

    def replacer(match: re.Match) -> str:
        nonlocal last_type
        open_tag = match.group(1)
        tag_name = match.group(2)
        inner = match.group(3)
        close_tag = match.group(4)

        clean_text = re.sub(r'<[^>]+>', '', inner).replace('&nbsp;', '').replace('\xa0', '').strip()
        if not clean_text:
            return match.group(0)

        target, cleaned_inner = is_target_line(inner, tag_name)
        if not target:
            return f'{open_tag}{cleaned_inner}{close_tag}'

        # Luân phiên bốc ngẫu nhiên Hoa và Lá
        if last_type == 'flower':
            chosen_emoji = rng.choice(SET_LEAVES)
            last_type = 'leaf'
        elif last_type == 'leaf':
            chosen_emoji = rng.choice(SET_FLOWERS)
            last_type = 'flower'
        else:
            chosen_emoji = rng.choice(SET_FLOWERS)
            last_type = 'flower'

        plain = re.sub(r'<[^>]+>', '', cleaned_inner).strip()
        log_changes.append((chosen_emoji, plain[:60]))

        return f'{open_tag}{chosen_emoji} {cleaned_inner}{close_tag}'

    new_html = tag_regex.sub(replacer, raw_html)
    return new_html, log_changes


def is_intro_file(filename: str) -> bool:
    name = os.path.basename(filename).lower()
    return any(k in name for k in ["intro", "gioithieu", "vanan", "chap_00000", "chap_0_"]) and name.endswith((".xhtml", ".html", ".htm"))


def process_single_epub(epub_path: Path, seed: Optional[int] = None) -> Tuple[bool, str, List[Tuple[str, str]]]:
    epub_path = Path(epub_path)
    if not epub_path.is_file():
        return False, f"File không tồn tại: {epub_path}", []

    temp_target = epub_path.with_name(epub_path.stem + ".tmp.epub")
    all_logs: List[Tuple[str, str]] = []

    file_seed = seed if seed is not None else (hash(epub_path.name) & 0xFFFFFFFF)

    try:
        with zipfile.ZipFile(epub_path, "r") as zin:
            infolist = zin.infolist()
            has_intro = any(is_intro_file(item.filename) for item in infolist)
            if not has_intro:
                return False, "Không tìm thấy chương giới thiệu / văn án trong file EPUB", []

            with zipfile.ZipFile(temp_target, "w") as zout:
                if "mimetype" in zin.namelist():
                    zout.writestr("mimetype", zin.read("mimetype"), compress_type=zipfile.ZIP_STORED)

                for item in infolist:
                    if item.filename == "mimetype":
                        continue
                    data = zin.read(item.filename)
                    if is_intro_file(item.filename):
                        text = data.decode("utf-8", errors="replace")
                        text, logs = process_intro_html(text, seed=file_seed)
                        all_logs.extend(logs)
                        data = text.encode("utf-8")
                    compress = zipfile.ZIP_DEFLATED if item.compress_type != zipfile.ZIP_STORED else zipfile.ZIP_STORED
                    zout.writestr(item.filename, data, compress_type=compress)

        with zipfile.ZipFile(temp_target, "r") as zcheck:
            first_name = zcheck.namelist()[0] if zcheck.namelist() else ""
            if first_name != "mimetype":
                if temp_target.exists():
                    temp_target.unlink()
                return False, "File tạm vi phạm chuẩn EPUB (thiếu mimetype ở vị trí đầu)", []

        os.replace(temp_target, epub_path)
        return True, "Thành công", all_logs

    except Exception as exc:
        if temp_target.exists():
            try:
                temp_target.unlink()
            except Exception:
                pass
        return False, str(exc), []


def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="Trang trí emoji Hoa & Lá ngẫu nhiên vào chương giới thiệu / văn án của file EPUB"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Đường dẫn một hoặc nhiều file .epub (hoặc thư mục chứa file EPUB)",
    )
    parser.add_argument(
        "--file", "-f",
        nargs="+",
        dest="flag_files",
        help="Đường dẫn file .epub cần xử lý",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed cố định để sinh emoji ngẫu nhiên (mặc định băm theo tên file)",
    )

    args = parser.parse_args()

    raw_inputs = []
    if args.flag_files:
        raw_inputs.extend(args.flag_files)
    if args.files:
        raw_inputs.extend(args.files)

    if not raw_inputs:
        parser.print_help()
        print("\nVí dụ sử dụng:")
        print('  python scripts/intro_emoji_decorator.py "duong_dan_truyen.epub"')
        return

    target_files: List[Path] = []
    combined = " ".join(raw_inputs).strip('"').strip("'")
    if Path(combined).is_file() and Path(combined).suffix.lower() == ".epub":
        target_files.append(Path(combined))
    else:
        for item in raw_inputs:
            p = Path(item.strip('"').strip("'"))
            if p.is_file() and p.suffix.lower() == ".epub":
                target_files.append(p)
            elif p.is_dir():
                for r, _, fnames in os.walk(p):
                    for fn in fnames:
                        if fn.lower().endswith(".epub") and not fn.endswith(".tmp.epub"):
                            target_files.append(Path(r) / fn)

    if not target_files:
        print("[ERROR] Không tìm thấy file .epub hợp lệ nào từ tham số đầu vào.")
        sys.exit(1)

    print(f"[*] Tìm thấy {len(target_files)} file EPUB cần xử lý:")
    for f in target_files:
        print(f"    - {f.name}")

    for epub_file in target_files:
        print(f"\n[*] Đang xử lý: {epub_file.name}...")
        ok, msg, logs = process_single_epub(epub_file, seed=args.seed)
        if ok:
            print(f"[SUCCESS] Đã chèn emoji hoa & lá thành công!")
            if logs:
                print(f"    Tổng số dòng được trang trí: {len(logs)}")
                for emoji_char, line_preview in logs[:10]:
                    print(f"      {emoji_char} {line_preview}")
                if len(logs) > 10:
                    print(f"      ... và {len(logs) - 10} dòng khác.")
            else:
                print("    (Không có dòng thông tin/metadata nào cần chèn thêm)")
        else:
            print(f"[FAIL] {epub_file.name}: {msg}")


if __name__ == "__main__":
    main()

