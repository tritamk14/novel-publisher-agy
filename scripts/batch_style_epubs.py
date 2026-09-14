# -*- coding: utf-8 -*-
"""
batch_style_epubs.py

Script xử lý hàng loạt đổi màu chữ cho toàn bộ file EPUB theo chuẩn:
- Mục lục (nav.xhtml): #C49C13 (Vàng Rapeseed / Hoàng yến)
- Chương Giới thiệu / Văn án: #C49C13 (Vàng Rapeseed / Hoàng yến)
- Tiêu đề các chương (1 -> hết): #EF729E (Hồng pastel)
- Nội dung đọc truyện: Giữ nguyên màu mặc định

Cơ chế an toàn:
- Ghi qua file tạm .tmp.epub và kiểm tra tính toàn vẹn trước khi hoán đổi (atomic replace).
- Đảm bảo chuẩn EPUB: file `mimetype` luôn ở vị trí đầu tiên và không nén (ZIP_STORED).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

from tqdm import tqdm

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dataclasses import dataclass

DEFAULT_INTRO_COLOR = "#C49C13"
DEFAULT_CHAP_COLOR = "#EF729E"
DEFAULT_BORDER_INTRO = "#eadcac"
DEFAULT_BG_INTRO = "#fcfaf3"
DEFAULT_BORDER_CHAP = "#ffd1df"


def lighten_hex(hex_color: str, factor: float = 0.8) -> str:
    """Hòa trộn màu hex với màu trắng (#ffffff).
    factor=0.8 nghĩa là 80% trắng, 20% màu gốc.
    """
    hex_color = hex_color.strip()
    if not hex_color.startswith("#"):
        hex_color = f"#{hex_color}"
    clean = hex_color.lstrip("#")
    if len(clean) == 6:
        try:
            r, g, b = int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)
            nr = int(r + (255 - r) * factor)
            ng = int(g + (255 - g) * factor)
            nb = int(b + (255 - b) * factor)
            return f"#{nr:02x}{ng:02x}{nb:02x}"
        except Exception:
            pass
    return hex_color


def normalize_hex(color_str: str, default: str) -> str:
    if not color_str:
        return default
    c = color_str.strip()
    if not c.startswith("#") and len(c) in (3, 6, 8):
        c = f"#{c}"
    return c


@dataclass
class StyleConfig:
    intro_color: str = DEFAULT_INTRO_COLOR
    chap_color: str = DEFAULT_CHAP_COLOR
    border_intro: Optional[str] = None
    bg_intro: Optional[str] = None
    border_chap: Optional[str] = None

    def __post_init__(self):
        self.intro_color = normalize_hex(self.intro_color, DEFAULT_INTRO_COLOR)
        self.chap_color = normalize_hex(self.chap_color, DEFAULT_CHAP_COLOR)

        if not self.border_intro:
            if self.intro_color.lower() == DEFAULT_INTRO_COLOR.lower():
                self.border_intro = DEFAULT_BORDER_INTRO
            else:
                self.border_intro = lighten_hex(self.intro_color, 0.65)
        else:
            self.border_intro = normalize_hex(self.border_intro, DEFAULT_BORDER_INTRO)

        if not self.bg_intro:
            if self.intro_color.lower() == DEFAULT_INTRO_COLOR.lower():
                self.bg_intro = DEFAULT_BG_INTRO
            else:
                self.bg_intro = lighten_hex(self.intro_color, 0.95)
        else:
            self.bg_intro = normalize_hex(self.bg_intro, DEFAULT_BG_INTRO)

        if not self.border_chap:
            if self.chap_color.lower() == DEFAULT_CHAP_COLOR.lower():
                self.border_chap = DEFAULT_BORDER_CHAP
            else:
                self.border_chap = lighten_hex(self.chap_color, 0.70)
        else:
            self.border_chap = normalize_hex(self.border_chap, DEFAULT_BORDER_CHAP)

    def get_intro_css_block(self) -> str:
        return f"""
<style type="text/css">/* Batch Restyle */
body, body * {{ color: {self.intro_color} !important; }}
h1, h2, h3, .intro-title, .intro-main-title {{
    color: {self.intro_color} !important;
    text-align: center;
    font-weight: bold;
}}
h1, h2 {{
    border-bottom: 1px solid {self.border_intro} !important;
    padding-bottom: 0.3em;
}}
.meta-box {{
    background-color: {self.bg_intro} !important;
    border-left: 4px solid {self.intro_color} !important;
    padding: 15px 20px;
    margin: 20px 0 30px 0;
    border-radius: 4px;
}}
a, a:link, a:visited {{
    color: {self.intro_color} !important;
    text-decoration: underline;
}}
p {{
    color: {self.intro_color} !important;
    text-indent: 1.5em;
    margin: 0.6em 0;
    text-align: justify;
}}
</style>
"""

    def get_nav_css_block(self) -> str:
        return f"""
<style type="text/css">/* Batch Restyle */
nav, nav h1, nav h2, nav h3, nav ol, nav ul, nav li, nav a {{
    color: {self.intro_color} !important;
}}
nav a:link, nav a:visited, nav a:hover, nav a:active {{
    color: {self.intro_color} !important;
    text-decoration: none;
}}
</style>
"""

    def get_chap_css_block(self) -> str:
        return f"""
<style type="text/css">/* Batch Restyle */
h1, h2, h3, .chapter-title, .chapter-title-heading, .entry-title {{
    color: {self.chap_color} !important;
    text-align: center;
    font-weight: bold;
    border-bottom: 1px solid {self.border_chap};
    padding-bottom: 0.3em;
    margin-top: 1em;
    margin-bottom: 0.8em;
}}
body.chapter-page p, p {{
    text-indent: 1.5em;
    margin: 0.6em 0;
    text-align: justify;
}}
</style>
"""

    def get_append_css_rules(self) -> str:
        return f"""
/* === Batch Restyle Colors === */
nav, nav h1, nav h2, nav h3, nav ol, nav ul, nav li, nav a {{
    color: {self.intro_color} !important;
}}
nav a:link, nav a:visited, nav a:hover, nav a:active {{
    color: {self.intro_color} !important;
    text-decoration: none;
}}
body.intro-page, body.intro-page * {{
    color: {self.intro_color} !important;
}}
body.intro-page h1, body.intro-page h2, body.intro-page h3 {{
    color: {self.intro_color} !important;
    text-align: center;
}}
body.intro-page .meta-box {{
    background-color: {self.bg_intro} !important;
    border-left: 4px solid {self.intro_color} !important;
}}
body.chapter-page h1, body.chapter-page h2, .chapter-title, .chapter-title-heading, .entry-title {{
    color: {self.chap_color} !important;
    text-align: center;
    border-bottom: 1px solid {self.border_chap};
    padding-bottom: 0.3em;
}}
"""


INTRO_COLOR = DEFAULT_INTRO_COLOR
CHAP_COLOR = DEFAULT_CHAP_COLOR
BORDER_INTRO = DEFAULT_BORDER_INTRO
BG_INTRO = DEFAULT_BG_INTRO
BORDER_CHAP = DEFAULT_BORDER_CHAP
DEFAULT_STYLE_CONFIG = StyleConfig()


def is_intro_file(filename: str) -> bool:
    name = os.path.basename(filename).lower()
    return any(k in name for k in ["intro", "gioithieu", "vanan", "chap_00000", "chap_0_"])


def is_nav_file(filename: str) -> bool:
    name = os.path.basename(filename).lower()
    return "nav" in name and name.endswith((".xhtml", ".html"))


def is_cover_file(filename: str) -> bool:
    name = os.path.basename(filename).lower()
    return "cover" in name and name.endswith((".xhtml", ".html"))


def is_chapter_file(filename: str) -> bool:
    name = os.path.basename(filename).lower()
    if not name.endswith((".xhtml", ".html", ".htm")):
        return False
    if is_intro_file(filename) or is_nav_file(filename) or is_cover_file(filename):
        return False
    return True


def strip_style_from_html(html_str: str) -> str:
    # Xóa bất kỳ khối style nào trước đó đã từng inject bởi script
    html_str = re.sub(r'<style type="text/css">\s*/\* Batch Restyle.*?</style>\s*', "", html_str, flags=re.DOTALL)
    html_str = re.sub(r'<style type="text/css">\s*body,\s*body\s*\*.*?</style>\s*', "", html_str, flags=re.DOTALL)
    html_str = re.sub(r'<style type="text/css">\s*nav,\s*nav\s*h1.*?</style>\s*', "", html_str, flags=re.DOTALL)
    html_str = re.sub(r'<style type="text/css">\s*h1,\s*h2,\s*h3,\s*\.chapter-title.*?</style>\s*', "", html_str, flags=re.DOTALL)
    return html_str


def inject_style_into_head(html_str: str, css_block: str) -> str:
    html_str = strip_style_from_html(html_str)

    if "</head>" in html_str:
        return html_str.replace("</head>", f"{css_block}</head>", 1)
    elif "<head>" in html_str:
        return html_str.replace("<head>", f"<head>{css_block}", 1)
    elif "<body>" in html_str:
        return html_str.replace("<body>", f"<head>{css_block}</head><body>", 1)
    return f"<head>{css_block}</head>{html_str}"


def process_single_epub(
    epub_path: Path,
    output_path: Optional[Path] = None,
    style_config: Optional[StyleConfig] = None,
    rollback: bool = False,
) -> Tuple[bool, str]:
    cfg = style_config or DEFAULT_STYLE_CONFIG
    target_path = output_path or epub_path
    temp_target = target_path.with_suffix(".tmp.epub")

    try:
        with zipfile.ZipFile(epub_path, "r") as zin:
            infolist = zin.infolist()
            if not infolist:
                return False, "File EPUB rỗng"

            # Tìm file mimetype nếu có
            mimetype_item = None
            other_items = []
            for item in infolist:
                if item.filename == "mimetype":
                    mimetype_item = item
                else:
                    other_items.append(item)

            temp_target.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(temp_target, "w") as zout:
                # 1. Ghi mimetype không nén ở vị trí đầu tiên
                if mimetype_item:
                    mimetype_bytes = zin.read(mimetype_item.filename)
                    zout.writestr("mimetype", mimetype_bytes, compress_type=zipfile.ZIP_STORED)
                else:
                    zout.writestr("mimetype", b"application/epub+zip", compress_type=zipfile.ZIP_STORED)

                # 2. Xử lý các file còn lại
                for item in other_items:
                    data = zin.read(item.filename)
                    compress = item.compress_type if item.compress_type is not None else zipfile.ZIP_DEFLATED

                    if rollback:
                        if item.filename.lower().endswith((".xhtml", ".html", ".htm")):
                            text = data.decode("utf-8", errors="replace")
                            text = strip_style_from_html(text)
                            data = text.encode("utf-8")
                        elif item.filename.endswith(".css"):
                            text = data.decode("utf-8", errors="replace")
                            text = re.sub(
                                r'/\* === Batch Restyle Colors === \*/.*',
                                '',
                                text,
                                flags=re.DOTALL,
                            ).rstrip()
                            if text:
                                text += "\n"
                            data = text.encode("utf-8")
                    else:
                        if is_nav_file(item.filename):
                            text = data.decode("utf-8", errors="replace")
                            text = inject_style_into_head(text, cfg.get_nav_css_block())
                            data = text.encode("utf-8")

                        elif is_intro_file(item.filename):
                            text = data.decode("utf-8", errors="replace")
                            # Thay thế màu cũ nếu có
                            text = re.sub(r'#A06F7B|#a06f7b|#6A74A8|#6a74a8|#C49C13|#c49c13', cfg.intro_color, text)
                            text = re.sub(r'#dfcbd0|#DFCBD0|#c4c9e2|#C4C9E2|#eadcac|#EADCAC', cfg.border_intro, text)
                            text = re.sub(r'#faf5f6|#FAF5F6|#f7f8fc|#F7F8FC|#fcfaf3|#FCFAF3', cfg.bg_intro, text)
                            text = inject_style_into_head(text, cfg.get_intro_css_block())
                            data = text.encode("utf-8")

                        elif is_chapter_file(item.filename):
                            text = data.decode("utf-8", errors="replace")
                            text = re.sub(r'#EF729E|#ef729e', cfg.chap_color, text)
                            text = re.sub(r'#ffd1df|#FFD1DF', cfg.border_chap, text)
                            text = inject_style_into_head(text, cfg.get_chap_css_block())
                            data = text.encode("utf-8")

                        elif item.filename.endswith(".css"):
                            text = data.decode("utf-8", errors="replace")
                            if "/* === Batch Restyle Colors === */" not in text:
                                text += "\n" + cfg.get_append_css_rules()
                            else:
                                # Cập nhật khối restyle hiện tại
                                text = re.sub(
                                    r'/\* === Batch Restyle Colors === \*/.*?(?=\n/\*|\Z)',
                                    cfg.get_append_css_rules().strip(),
                                    text,
                                    flags=re.DOTALL,
                                )
                            # Thay thế mã màu cũ nếu có
                            text = re.sub(r'#A06F7B|#a06f7b|#6A74A8|#6a74a8|#C49C13|#c49c13', cfg.intro_color, text)
                            text = re.sub(r'#dfcbd0|#DFCBD0|#c4c9e2|#C4C9E2|#eadcac|#EADCAC', cfg.border_intro, text)
                            text = re.sub(r'#faf5f6|#FAF5F6|#f7f8fc|#F7F8FC|#fcfaf3|#FCFAF3', cfg.bg_intro, text)
                            text = re.sub(r'#EF729E|#ef729e', cfg.chap_color, text)
                            text = re.sub(r'#ffd1df|#FFD1DF', cfg.border_chap, text)
                            data = text.encode("utf-8")

                    zout.writestr(item.filename, data, compress_type=compress)

        # Kiểm tra tính hợp lệ của file tạm vừa tạo
        if not temp_target.exists() or temp_target.stat().st_size <= 0:
            if temp_target.exists():
                temp_target.unlink()
            return False, "Tạo file tạm thất bại"

        # Kiểm tra file tạm có mở được không
        with zipfile.ZipFile(temp_target, "r") as test_z:
            test_names = test_z.namelist()
            if not test_names or test_names[0] != "mimetype":
                temp_target.unlink()
                return False, "File tạm vi phạm chuẩn EPUB (thiếu mimetype)"

        # Hoán đổi sang file đích an toàn (atomic replace)
        os.replace(temp_target, target_path)
        return True, "Thành công"

    except Exception as exc:
        if temp_target.exists():
            try:
                temp_target.unlink()
            except Exception:
                pass
        return False, str(exc)


def main():
    parser = argparse.ArgumentParser(
        description="Đổi màu cho file EPUB theo chuẩn màu tùy biến (hỗ trợ cả 1 file hoặc cả thư mục)"
    )
    parser.add_argument("--file", "-f", nargs="+", help="Đường dẫn một hoặc nhiều file .epub cụ thể cần đồng bộ màu")
    parser.add_argument("--dir", "-d", help="Thư mục chứa các file EPUB (hoặc đường dẫn tới 1 file .epub)")
    parser.add_argument(
        "--output-dir", "--out-dir", "-o", help="Thư mục xuất file mới (nếu không truyền sẽ ghi đè an toàn tại chỗ)"
    )
    parser.add_argument(
        "--workers", type=int, default=6, help="Số luồng xử lý đồng thời khi chạy nhiều file (mặc định: 6)"
    )
    parser.add_argument("--sample", type=int, help="Chỉ chạy thử trên N file mẫu để kiểm tra")

    # 2 option chính cho 2 phần riêng biệt
    parser.add_argument(
        "--intro-color",
        "--intro",
        dest="intro_color",
        default=DEFAULT_INTRO_COLOR,
        help=f"Mã màu hex cho phần Giới thiệu / Văn án & Mục lục (mặc định: {DEFAULT_INTRO_COLOR})",
    )
    parser.add_argument(
        "--chap-color",
        "--chapter-color",
        "--chap",
        "--title-color",
        dest="chap_color",
        default=DEFAULT_CHAP_COLOR,
        help=f"Mã màu hex cho Tiêu đề các chương truyện (mặc định: {DEFAULT_CHAP_COLOR})",
    )

    # Tùy chọn nâng cao bổ trợ (border / bg)
    parser.add_argument(
        "--border-intro",
        dest="border_intro",
        default=None,
        help="Tùy chọn: Mã màu viền gạch dưới của Intro (mặc định tự động tính theo intro-color)",
    )
    parser.add_argument(
        "--bg-intro",
        dest="bg_intro",
        default=None,
        help="Tùy chọn: Mã màu nền khung meta-box của Intro (mặc định tự động tính theo intro-color)",
    )
    parser.add_argument(
        "--border-chap",
        dest="border_chap",
        default=None,
        help="Tùy chọn: Mã màu viền gạch dưới tiêu đề chương (mặc định tự động tính theo chap-color)",
    )
    parser.add_argument(
        "--rollback",
        "--revert",
        action="store_true",
        help="Gỡ bỏ toàn bộ CSS/style đã thêm bởi script, khôi phục lại EPUB nguyên bản ban đầu",
    )

    args = parser.parse_args()

    style_config = StyleConfig(
        intro_color=args.intro_color,
        chap_color=args.chap_color,
        border_intro=args.border_intro,
        bg_intro=args.bg_intro,
        border_chap=args.border_chap,
    )

    epub_files: List[Path] = []
    root_dir: Optional[Path] = None

    if args.file:
        processed_files: List[Path] = []
        # Kiểm tra xem toàn bộ các token có tạo thành 1 file duy nhất (do lỗi quote trong PowerShell)
        combined_all = " ".join(args.file).strip('"').strip("'")
        if Path(combined_all).is_file() and Path(combined_all).suffix.lower() == ".epub":
            processed_files.append(Path(combined_all))
        else:
            # Gom nhóm các token liên tiếp nếu ghép lại thành đường dẫn file hợp lệ
            i = 0
            while i < len(args.file):
                matched = False
                for j in range(len(args.file), i, -1):
                    candidate = " ".join(args.file[i:j]).strip('"').strip("'")
                    p = Path(candidate)
                    if p.is_file() and p.suffix.lower() == ".epub":
                        processed_files.append(p)
                        i = j
                        matched = True
                        break
                if not matched:
                    f_str = args.file[i].strip('"').strip("'")
                    p = Path(f_str)
                    if p.is_file() and p.suffix.lower() == ".epub":
                        processed_files.append(p)
                    else:
                        print(f"[WARN] Bỏ qua file không hợp lệ hoặc không tồn tại: {f_str}")
                    i += 1
        epub_files.extend(processed_files)
        if epub_files:
            root_dir = epub_files[0].parent
    else:
        target_dir = args.dir or r"G:\My Drive\Ebook\Ebook_crawler\individual_sharing\nganngoctu"
        p_target = Path(target_dir)
        if not p_target.exists():
            print(f"[ERROR] Đường dẫn không tồn tại: {target_dir}")
            sys.exit(1)

        if p_target.is_file():
            if p_target.suffix.lower() == ".epub":
                epub_files.append(p_target)
                root_dir = p_target.parent
            else:
                print(f"[ERROR] File không phải định dạng .epub: {p_target}")
                sys.exit(1)
        else:
            root_dir = p_target
            print(f"[*] Đang tìm kiếm các file .epub trong {root_dir}...")
            for r, d, files in os.walk(root_dir):
                for f in files:
                    if f.lower().endswith(".epub") and not f.endswith(".tmp.epub"):
                        epub_files.append(Path(r) / f)

    total_found = len(epub_files)
    if total_found == 0:
        print("[WARN] Không tìm thấy file .epub nào để xử lý.")
        sys.exit(0)

    if args.rollback:
        print(f"[*] CHẾ ĐỘ: ROLLBACK (Gỡ bỏ toàn bộ style đã inject, khôi phục nguyên bản)")
    else:
        print(f"[*] CẤU HÌNH GIAO DIỆN (Color Theme):")
        print(f"    - Intro & Mục lục (intro-color) : {style_config.intro_color} (Viền: {style_config.border_intro}, Nền: {style_config.bg_intro})")
        print(f"    - Tiêu đề chương (chap-color)   : {style_config.chap_color} (Viền: {style_config.border_chap})")
    print(f"[*] Tìm thấy tổng cộng: {total_found:,} file EPUB.")

    if args.sample and args.sample > 0 and len(epub_files) > args.sample:
        epub_files = epub_files[:args.sample]
        print(f"[!] Chế độ chạy thử nghiệm trên {len(epub_files)} file mẫu.")

    output_root = Path(args.output_dir) if args.output_dir else None
    if output_root:
        output_root.mkdir(parents=True, exist_ok=True)
        print(f"[*] Chế độ: Xuất ra thư mục mới -> {output_root}")
    else:
        print(f"[*] Chế độ: Ghi đè an toàn tại chỗ (In-place Atomic Update).")

    success_count = 0
    fail_count = 0
    failed_files = []

    def task_worker(p: Path) -> Tuple[Path, bool, str]:
        if output_root and root_dir:
            try:
                rel = p.relative_to(root_dir)
                out_p = output_root / rel
            except Exception:
                out_p = output_root / p.name
        else:
            out_p = None
        ok, msg = process_single_epub(p, out_p, style_config=style_config, rollback=args.rollback)
        return p, ok, msg

    action_name = "Rollback EPUB" if args.rollback else "Đổi màu EPUB"
    print(f"[*] Bắt đầu xử lý với {args.workers} workers...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(task_worker, p): p for p in epub_files}
        with tqdm(total=len(epub_files), desc=action_name, unit="file") as pbar:
            for future in concurrent.futures.as_completed(futures):
                p, ok, msg = future.result()
                if ok:
                    success_count += 1
                else:
                    fail_count += 1
                    failed_files.append((str(p), msg))
                    tqdm.write(f"[FAIL] {p.name}: {msg}")
                pbar.update(1)

    print(f"\n{'='*60}")
    print(f"[*] KẾT QUẢ XỬ LÝ:")
    print(f"    - Thành công: {success_count:,} / {len(epub_files):,} file")
    print(f"    - Thất bại  : {fail_count:,} file")
    if failed_files:
        print(f"\n[!] Danh sách file lỗi ({len(failed_files)}):")
        for fp, err in failed_files[:10]:
            print(f"    - {fp}: {err}")
        if len(failed_files) > 10:
            print(f"    ... và {len(failed_files) - 10} file khác.")


if __name__ == "__main__":
    main()
