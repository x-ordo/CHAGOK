"""
AWS Lambda Handler for LEH AI Worker.
Triggered by S3 ObjectCreated events.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Import AI Pipeline modules
from src.parsers import (
    ImageOCRParser,
    ImageVisionParser,
    PDFParser,
    AudioParser,
    VideoParser
)
from src.parsers.text import TextParser
from src.storage.metadata_store import MetadataStore
from src.storage.vector_store import VectorStore
from src.analysis.summarizer import EvidenceSummarizer
from src.analysis.article_840_tagger import Article840Tagger

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def route_parser(file_extension: str) -> Optional[Any]:
    """
    파일 확장자에 따라 적절한 파서를 반환

    Args:
        file_extension: 파일 확장자 (예: '.pdf', '.jpg', '.mp4')

    Returns:
        적절한 파서 인스턴스 또는 None
    """
    ext = file_extension.lower()

    # 이미지 파일
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        # Vision API 우선 사용 (감정/맥락 분석)
        return ImageVisionParser()

    # PDF 파일
    elif ext == '.pdf':
        return PDFParser()

    # 오디오 파일
    elif ext in ['.mp3', '.wav', '.m4a', '.aac']:
        return AudioParser()

    # 비디오 파일
    elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
        return VideoParser()

    # 텍스트 파일 (카톡 포함)
    elif ext in ['.txt', '.csv', '.json']:
        return TextParser()

    else:
        logger.warning(f"Unsupported file type: {ext}")
        return None


def route_and_process(bucket_name: str, object_key: str) -> Dict[str, Any]:
    """
    S3 파일을 파싱하고 분석하는 메인 처리 함수

    Args:
        bucket_name: S3 버킷 이름
        object_key: S3 객체 키 (파일 경로)

    Returns:
        처리 결과 딕셔너리
    """
    try:
        # 파일 확장자 추출
        file_path = Path(object_key)
        file_extension = file_path.suffix

        logger.info(f"Processing file: {object_key} (extension: {file_extension})")

        # 적절한 파서 선택
        parser = route_parser(file_extension)
        if not parser:
            return {
                "status": "skipped",
                "reason": f"Unsupported file type: {file_extension}",
                "file": object_key
            }

        # TODO: S3에서 파일 다운로드
        # import boto3
        # s3_client = boto3.client('s3')
        # local_path = f"/tmp/{file_path.name}"
        # s3_client.download_file(bucket_name, object_key, local_path)

        # TODO: 파서 실행
        # parsed_result = parser.parse(local_path)

        # TODO: 메타데이터 저장
        # metadata_store = MetadataStore()
        # metadata_store.save(parsed_result)

        # TODO: 벡터 임베딩 및 저장
        # vector_store = VectorStore()
        # vector_store.index(parsed_result)

        # TODO: 분석 엔진 실행
        # summarizer = EvidenceSummarizer()
        # summary = summarizer.summarize(parsed_result)

        # tagger = Article840Tagger()
        # tags = tagger.tag(parsed_result)

        return {
            "status": "processed",
            "file": object_key,
            "parser_type": parser.__class__.__name__,
            "bucket": bucket_name
            # "summary": summary,
            # "tags": tags
        }

    except Exception as e:
        logger.error(f"Error processing {object_key}: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "file": object_key,
            "error": str(e)
        }


def handle(event, context):
    """
    AWS Lambda Entrypoint.
    S3 이벤트를 수신하여 파일 정보를 파싱하고 AI 파이프라인을 시작합니다.
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # S3 이벤트가 아닌 경우(테스트 등) 방어 로직
    if "Records" not in event:
        return {"status": "ignored", "reason": "No S3 Records found"}

    results = []

    for record in event["Records"]:
        try:
            # 1. S3 이벤트에서 버킷과 키(파일 경로) 추출
            s3 = record.get("s3", {})
            bucket_name = s3.get("bucket", {}).get("name")
            object_key = s3.get("object", {}).get("key")

            # URL Decoding (공백 등이 + 또는 %20으로 들어올 수 있음)
            # object_key = urllib.parse.unquote_plus(object_key)

            logger.info(f"Processing file: s3://{bucket_name}/{object_key}")

            # 2. 파일 처리 로직 실행 (Strategy Pattern 적용)
            result = route_and_process(bucket_name, object_key)
            results.append(result)

        except Exception as e:
            logger.error(f"Error processing record: {e}", exc_info=True)
            # 실제 운영 시에는 여기서 DLQ로 보내거나 에러를 다시 raise 해야 함
            results.append({"error": str(e), "status": "failed"})

    return {
        "statusCode": 200,
        "body": json.dumps({"results": results})
    }
