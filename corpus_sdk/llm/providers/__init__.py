# corpus_sdk/llm/providers/__init__.py
# SPDX-License-Identifier: Apache-2.0
"""
Concrete provider adapters for the LLM Protocol V1.

Each module here implements ``BaseLLMAdapter`` against a specific vendor's
HTTP API while remaining wire-compatible with the vendor-neutral contract
defined in :mod:`corpus_sdk.llm.llm_base`.
"""

from corpus_sdk.llm.providers.minimax import MINIMAX_MODELS, MINIMAX_REGIONS, MiniMaxAdapter

__all__ = ["MiniMaxAdapter", "MINIMAX_MODELS", "MINIMAX_REGIONS"]
