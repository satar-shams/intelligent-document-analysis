from pathlib import Path

import yaml


CONFIG_FILE = (
    Path(__file__).resolve().parent.parent
    / "configs"
    / "config.yaml"
)


if not CONFIG_FILE.exists():
    raise FileNotFoundError(
        f"Configuration file not found: {CONFIG_FILE}"
    )


with CONFIG_FILE.open(
    mode="r",
    encoding="utf-8",
) as file:
    CONFIG = yaml.safe_load(file)


def _get_config_value(
    section: str,
    key: str,
):
    try:
        return CONFIG[section][key]

    except KeyError as exc:
        raise KeyError(
            f"Missing configuration: {section}.{key}"
        ) from exc


def _get_nested_config_value(
    section: str,
    subsection: str,
    key: str,
):
    try:
        return CONFIG[section][subsection][key]

    except KeyError as exc:
        raise KeyError(
            f"Missing configuration: "
            f"{section}.{subsection}.{key}"
        ) from exc


PROJECT_NAME = _get_config_value(
    "project",
    "name",
)

PROJECT_VERSION = _get_config_value(
    "project",
    "version",
)

RAW_DATA_PATH = _get_config_value(
    "paths",
    "raw_data",
)

PROCESSED_DATA_PATH = _get_config_value(
    "paths",
    "processed_data",
)

SAMPLES_PATH = _get_config_value(
    "paths",
    "samples",
)

INGESTION_INPUT_DIRECTORY = _get_config_value(
    "ingestion",
    "input_directory",
)

PDF_TEST_FILE = _get_nested_config_value(
    "ingestion",
    "test_files",
    "pdf",
)

DOCX_TEST_FILE = _get_nested_config_value(
    "ingestion",
    "test_files",
    "docx",
)

OCR_TEST_FILE = _get_nested_config_value(
    "ingestion",
    "test_files",
    "ocr",
)

OCR_START_PAGE = _get_nested_config_value(
    "ingestion",
    "ocr",
    "start_page",
)

OCR_END_PAGE = _get_nested_config_value(
    "ingestion",
    "ocr",
    "end_page",
)

EMBEDDING_MODEL_NAME = _get_config_value(
    "embedding",
    "model_name",
)

CHUNK_SIZE = _get_config_value(
    "chunking",
    "chunk_size",
)

CHUNK_OVERLAP = _get_config_value(
    "chunking",
    "chunk_overlap",
)

MAX_TEXT_PREVIEW_LENGTH = _get_config_value(
    "output",
    "max_text_preview_length",
)

VECTOR_DB_PATH = _get_config_value(
    "vectorstore",
    "db_path",
)

COLLECTION_NAME = _get_config_value(
    "vectorstore",
    "collection_name",
)