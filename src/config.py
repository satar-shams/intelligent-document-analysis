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

VECTOR_DB_PATH = _get_config_value(
    "vectorstore",
    "db_path",
)

COLLECTION_NAME = _get_config_value(
    "vectorstore",
    "collection_name",
)