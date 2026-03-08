#!/usr/bin/env python3
"""PDF 파일들을 marker-pdf를 이용하여 마크다운으로 변환하는 프로그램."""

import argparse
import os
import sys
import time
from pathlib import Path


def convert_pdfs(input_dir: str, output_dir: str | None = None):
    """지정된 폴더의 모든 PDF 파일을 마크다운으로 변환합니다.

    Args:
        input_dir: PDF 파일이 있는 폴더 경로
        output_dir: 마크다운 파일을 저장할 폴더 경로 (미지정 시 input_dir 사용)
    """
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered

    input_path = Path(input_dir)
    if not input_path.is_dir():
        print(f"오류: '{input_dir}' 폴더가 존재하지 않습니다.")
        sys.exit(1)

    output_path = Path(output_dir) if output_dir else input_path
    output_path.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(input_path.glob("*.pdf"))
    if not pdf_files:
        print(f"'{input_dir}' 폴더에 PDF 파일이 없습니다.")
        sys.exit(0)

    print(f"총 {len(pdf_files)}개의 PDF 파일을 발견했습니다.")
    print(f"출력 폴더: {output_path}\n")

    # 모델을 한 번만 로드
    print("모델 로딩 중...")
    converter = PdfConverter(artifact_dict=create_model_dict())
    print("모델 로딩 완료.\n")

    success_count = 0
    fail_count = 0

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] 변환 중: {pdf_file.name}")
        start_time = time.time()

        try:
            rendered = converter(str(pdf_file))
            markdown_text, _, images = text_from_rendered(rendered)

            md_filename = pdf_file.stem + ".md"
            md_filepath = output_path / md_filename

            # 이미지 저장
            if images:
                img_dir = output_path / pdf_file.stem
                img_dir.mkdir(parents=True, exist_ok=True)
                for img_name, img_data in images.items():
                    img_path = img_dir / img_name
                    img_data.save(str(img_path))
                print(f"  이미지 {len(images)}개 저장 -> {img_dir}/")

            md_filepath.write_text(markdown_text, encoding="utf-8")

            elapsed = time.time() - start_time
            print(f"  완료: {md_filepath} ({elapsed:.1f}초)")
            success_count += 1

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"  실패: {e} ({elapsed:.1f}초)")
            fail_count += 1

    print(f"\n변환 완료: 성공 {success_count}개, 실패 {fail_count}개")


def main():
    parser = argparse.ArgumentParser(
        description="PDF 파일들을 marker-pdf를 이용하여 마크다운으로 변환합니다."
    )
    parser.add_argument("input_dir", help="PDF 파일이 있는 폴더 경로")
    parser.add_argument(
        "-o", "--output-dir",
        help="마크다운 파일을 저장할 폴더 경로 (기본값: 입력 폴더와 동일)",
    )
    args = parser.parse_args()

    convert_pdfs(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
