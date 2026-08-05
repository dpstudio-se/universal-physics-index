"""UPI Image Index — machine-readable image feature extraction and classification."""

__version__ = "0.1.0"

from .classifier import (
    ScientificStatus,
    build_extraction_layer,
    build_image_node,
    classify_layer,
    content_hash,
)
from .extractor import (
    extract_all_layers,
    extract_symbolic_elements,
    hash_file,
)
from .shadow import analyze_shadow_layer

__all__ = [
    "__version__",
    "ScientificStatus",
    "build_extraction_layer",
    "build_image_node",
    "classify_layer",
    "content_hash",
    "extract_all_layers",
    "extract_symbolic_elements",
    "hash_file",
    "analyze_shadow_layer",
]
