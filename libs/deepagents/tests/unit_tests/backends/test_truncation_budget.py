"""List truncation preserves complete results that fit the rendered budget."""

import pytest

from deepagents.backends.utils import TOOL_RESULT_TOKEN_LIMIT, TRUNCATION_GUIDANCE, truncate_if_too_long


@pytest.mark.parametrize("spare", [0, 1, 10, 50])
def test_list_at_or_below_budget_is_preserved(spare: int) -> None:
    limit = TOOL_RESULT_TOKEN_LIMIT * 4
    paths = [f"/{index:03d}" + "x" * 72 for index in range(999)]
    paths.append("x" * (limit - len(str(paths)) - 4 - spare))
    assert len(str(paths)) == limit - spare
    assert truncate_if_too_long(paths) == paths


@pytest.mark.parametrize(
    "paths",
    [[], ["/short"], ["'", '"', "\\", "\n"]],
)
def test_small_lists_are_unchanged(paths: list[str]) -> None:
    assert truncate_if_too_long(paths) == paths


@pytest.mark.parametrize("item", ["/" + "x" * 75, "'\"\\\n" * 20])
def test_oversized_list_keeps_a_prefix_with_guidance(item: str) -> None:
    limit = TOOL_RESULT_TOKEN_LIMIT * 4
    paths = [item] * 2000
    result = truncate_if_too_long(paths)
    assert result[-1] == TRUNCATION_GUIDANCE
    assert result[:-1] == paths[: len(result) - 1]
    assert len(str(result)) <= limit
    assert len(str([*result[:-1], item, TRUNCATION_GUIDANCE])) > limit


def test_oversized_first_item_returns_only_guidance() -> None:
    assert truncate_if_too_long(["x" * (TOOL_RESULT_TOKEN_LIMIT * 4)]) == [TRUNCATION_GUIDANCE]


def test_string_truncation_is_unchanged() -> None:
    limit = TOOL_RESULT_TOKEN_LIMIT * 4
    assert truncate_if_too_long("x" * limit) == "x" * limit
    result = truncate_if_too_long("x" * (limit + 1))
    assert len(result) == limit
    assert result.endswith("\n" + TRUNCATION_GUIDANCE)
