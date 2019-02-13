"""This module provides functionality to generate utterances and tokens after processing the pattern definition."""
import itertools
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict  # pylint: disable=unused-import
from typing import Iterable
from typing import List  # pylint: disable=unused-import
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

import yaml

from putput.joiner import ComboOptions
from putput.joiner import join_combo
from putput.types import COMBO
from putput.types import GROUP
from putput.types import TOKEN_HANDLER
from putput.types import TOKEN_HANDLER_MAP
from putput.types import TOKEN_PATTERN
from putput.types import TOKEN_PATTERNS_MAP
from putput.validator import RANGE_REGEX
from putput.validator import parse_range_token
from putput.validator import validate_pattern_def

_TOKEN_PATTERNS_WITH_BASE_TOKENS = Sequence[Sequence[Union[str, Sequence[str]]]]
_BASE_ITEM_MAP = Mapping[str, Sequence[str]]
_EXPANDED_BASE_ITEM_MAP = Mapping[str, Sequence[Sequence[str]]]
_HASHABLE_TOKEN_PATTERN = Tuple[Tuple[str, ...], ...]
_EXPANDED_UTTERANCE_PATTERN = Sequence[Sequence[TOKEN_PATTERN]]
_UTTERANCE_PATTERN = Sequence[str]

def generate_utterance_combo_tokens_and_groups(pattern_def_path: Path,
                                               *,
                                               dynamic_token_patterns_map: Optional[TOKEN_PATTERNS_MAP] = None
                                               ) -> Iterable[Tuple[COMBO, Sequence[str], Sequence[GROUP]]]:
    pattern_def = _load_pattern_def(pattern_def_path)
    validate_pattern_def(pattern_def)
    token_patterns_map = _get_token_patterns_map(pattern_def, dynamic_token_patterns_map=dynamic_token_patterns_map)

    utterance_patterns = _handle_ranges(pattern_def['utterance_patterns'])
    expanded_utterance_patterns, utterance_patterns_groups = _expand_groups(pattern_def, utterance_patterns)

    for utterance_pattern, utterance_pattern_group in zip(expanded_utterance_patterns, utterance_patterns_groups):
        expanded_utterance_pattern = tuple(token_patterns_map[token] for token in utterance_pattern)
        utterance_combo = _compute_utterance_combo(expanded_utterance_pattern)
        yield utterance_combo, tuple(utterance_pattern), tuple(utterance_pattern_group)

def generate_utterances_and_handled_tokens(utterance_combo: COMBO,
                                           tokens: Sequence[str],
                                           *,
                                           token_handler_map: Optional[TOKEN_HANDLER_MAP] = None,
                                           combo_options: Optional[ComboOptions] = None
                                           ) -> Iterable[Tuple[str, Sequence[str]]]:
    # pylint: disable=too-many-arguments, too-many-locals
    handled_token_combo = _compute_handled_token_combo(utterance_combo, tokens, token_handler_map=token_handler_map)
    combo_indices = tuple(tuple(i for i in range(len(component))) for component in utterance_combo)
    for indices in join_combo(combo_indices, combo_options=combo_options):
        utterance = []
        handled_tokens = []
        for utterance_component, token_component, index in zip(utterance_combo,
                                                               handled_token_combo,
                                                               indices):
            utterance.append(utterance_component[index])
            handled_tokens.append(token_component[index])
        yield ' '.join(utterance), tuple(handled_tokens)

def _load_pattern_def(pattern_def_path: Path) -> Mapping:
    with pattern_def_path.open(encoding='utf-8') as pattern_def_file:
        pattern_def = yaml.load(pattern_def_file, Loader=yaml.BaseLoader)
    return pattern_def

def _get_token_patterns_map(pattern_def: Mapping,
                            *,
                            dynamic_token_patterns_map: Optional[TOKEN_PATTERNS_MAP] = None
                            ) -> TOKEN_PATTERNS_MAP:
    token_patterns_map = {} # type: Dict[str, Sequence[TOKEN_PATTERN]]
    static_token_patterns_map = _get_static_token_patterns_map(pattern_def)
    token_patterns_map.update(static_token_patterns_map)
    token_patterns_map.update(dynamic_token_patterns_map or {})
    return token_patterns_map

def _get_base_item_map(pattern_def: Mapping, base_key: str) -> _BASE_ITEM_MAP:
    base_item_map = {next(iter(base_item_map.keys())): tuple(next(iter(base_item_map.values())))
                     for base_item_map in pattern_def[base_key]}
    return base_item_map

def _get_static_token_patterns_map(pattern_def: Mapping) -> TOKEN_PATTERNS_MAP:
    return {
        token: _process_static_token_patterns(pattern_def, token_patterns)
        for token_type_map in pattern_def['token_patterns']
        for token_type in token_type_map
        if token_type == 'static'
        for static_token_patterns_map in token_type_map['static']
        for token, token_patterns in static_token_patterns_map.items()
    }

def _process_static_token_patterns(pattern_def: Mapping,
                                   token_patterns: _TOKEN_PATTERNS_WITH_BASE_TOKENS
                                   ) -> Sequence[TOKEN_PATTERN]:
    if 'base_tokens' in pattern_def:
        token_patterns = _expand_base_tokens(pattern_def, token_patterns)
    return _convert_token_patterns_to_tuples(token_patterns)

def _convert_token_patterns_to_tuples(token_patterns: Sequence[TOKEN_PATTERN]) -> Tuple[_HASHABLE_TOKEN_PATTERN, ...]:
    return tuple(tuple(tuple(phrases) for phrases in token_pattern) for token_pattern in token_patterns)

def _expand_base_tokens(pattern_def: Mapping,
                        token_patterns: _TOKEN_PATTERNS_WITH_BASE_TOKENS
                        ) -> Sequence[TOKEN_PATTERN]:
    base_token_map = _get_base_item_map(pattern_def, 'base_tokens')
    return tuple(tuple(base_token_map[component] if isinstance(component, str) else component
                       for component in token_pattern) for token_pattern in token_patterns)

def _expand_groups(pattern_def: Mapping,
                   utterance_patterns: Sequence[_UTTERANCE_PATTERN]
                   ) -> Tuple[Sequence[_UTTERANCE_PATTERN], Sequence[Sequence[GROUP]]]:
    default_groups = [[('None', 1) for token in utterance_pattern] for utterance_pattern in utterance_patterns]
    if 'groups' in pattern_def:
        group_map = _get_base_item_map(pattern_def, 'groups')
        expanded_group_map = {name: _handle_ranges([pattern]) for name, pattern in group_map.items()}
        return _expand_groups_recursive(utterance_patterns, default_groups, expanded_group_map)
    return utterance_patterns, default_groups

def _expand_groups_recursive(utterance_patterns: Sequence[_UTTERANCE_PATTERN],
                             utterance_patterns_groups: Sequence[Sequence[GROUP]],
                             expanded_group_map: _EXPANDED_BASE_ITEM_MAP
                             ) -> Tuple[Sequence[_UTTERANCE_PATTERN], Sequence[Sequence[GROUP]]]:
    # Base case
    if not _any_pattern_token_in_group_map(utterance_patterns, expanded_group_map):
        return tuple(utterance_patterns), tuple(utterance_patterns_groups)

    # Recursive
    expanded_utterance_patterns = []  # type: List[_UTTERANCE_PATTERN]
    expanded_utterance_patterns_groups = []  # type: List[Sequence[GROUP]]
    for utterance_pattern, groups in zip(utterance_patterns, utterance_patterns_groups):
        index = _get_map_match_index(utterance_pattern, expanded_group_map)
        if index is not None:
            token = utterance_pattern[index]
            group_index = _get_current_group_index(index, groups)
            for group_pattern in expanded_group_map[token]:
                new_utterance_pattern = [_ for _ in utterance_pattern]
                new_utterance_pattern[index: index + 1] = group_pattern
                expanded_utterance_patterns.append(tuple(new_utterance_pattern))

                new_groups = [_ for _ in groups]
                new_groups[group_index: group_index + 1] = [(token, len(group_pattern))]
                expanded_utterance_patterns_groups.append(tuple(new_groups))
        else:
            expanded_utterance_patterns.append(tuple(utterance_pattern))
            expanded_utterance_patterns_groups.append(tuple(groups))
    return _expand_groups_recursive(tuple(expanded_utterance_patterns),
                                    tuple(expanded_utterance_patterns_groups),
                                    expanded_group_map)

def _handle_ranges(utterance_patterns: Sequence[_UTTERANCE_PATTERN]) -> Sequence[_UTTERANCE_PATTERN]:
    # Base case
    if not _any_patterns_match_regex(utterance_patterns, RANGE_REGEX):
        return tuple(utterance_patterns)

    # Recursive
    handled_utterance_patterns = [] # type: List[_UTTERANCE_PATTERN]
    for utterance_pattern in utterance_patterns:
        match_index = _get_regex_match_index(utterance_pattern, RANGE_REGEX)
        if match_index and match_index > 0:
            token = utterance_pattern[match_index]
            previous_token = utterance_pattern[match_index - 1]
            min_range, max_range = parse_range_token(token)
            if min_range is not None:
                for range_value in range(min_range, max_range):
                    new_utterance_pattern = [_ for _ in utterance_pattern]
                    new_utterance_pattern[match_index - 1: match_index + 1] = [previous_token] * range_value
                    handled_utterance_patterns.append(tuple(new_utterance_pattern))
            else:
                new_utterance_pattern = [_ for _ in utterance_pattern]
                new_utterance_pattern[match_index - 1: match_index + 1] = [previous_token] * max_range
                handled_utterance_patterns.append(tuple(new_utterance_pattern))
        else:
            handled_utterance_patterns.append(tuple(utterance_pattern))
    return _handle_ranges(tuple(handled_utterance_patterns))

def _get_current_group_index(token_index: int, groups: Sequence[GROUP]) -> int:
    cur_index = 0
    cur_sum = 0
    while cur_sum < token_index:
        cur_sum += groups[cur_index][1]
        cur_index += 1
    return cur_index

def _get_regex_match_index(utterance_pattern: _UTTERANCE_PATTERN, regex: str) -> Optional[int]:
    for index, token in enumerate(utterance_pattern):
        if re.match(regex, token):
            return index
    return None

def _any_patterns_match_regex(utterance_patterns: Sequence[_UTTERANCE_PATTERN], regex: str) -> bool:
    matches = [_get_regex_match_index(utterance_pattern, regex) is not None for utterance_pattern in utterance_patterns]
    return any(matches)

def _get_map_match_index(utterance_pattern: _UTTERANCE_PATTERN,
                         expanded_group_map: _EXPANDED_BASE_ITEM_MAP) -> Optional[int]:
    for index, token in enumerate(utterance_pattern):
        if token in expanded_group_map:
            return index
    return None

def _any_pattern_token_in_group_map(utterance_patterns: Sequence[_UTTERANCE_PATTERN],
                                    expanded_group_map: _EXPANDED_BASE_ITEM_MAP) -> bool:
    matches = [_get_map_match_index(utterance_pattern, expanded_group_map) is not None
               for utterance_pattern in utterance_patterns]
    return any(matches)

def _compute_utterance_combo(expanded_utterance_pattern: _EXPANDED_UTTERANCE_PATTERN) -> COMBO:
    utterance_combo = []
    for token_patterns in expanded_utterance_pattern:
        hashable_token_patterns = _convert_token_patterns_to_tuples(token_patterns)
        expanded_token_patterns = tuple(_expand_token_pattern(token_pattern)
                                        for token_pattern in hashable_token_patterns)
        utterance_components = tuple(itertools.chain.from_iterable(expanded_token_patterns))
        utterance_combo.append(utterance_components)
    return tuple(utterance_combo)

def _compute_handled_token_combo(utterance_combo: COMBO,
                                 tokens: Sequence[str],
                                 *,
                                 token_handler_map: Optional[TOKEN_HANDLER_MAP] = None
                                 ) -> COMBO:
    handled_token_combo = []
    for utterance_component, token in zip(utterance_combo, tokens):
        token_components = tuple(_get_token_handler(token, token_handler_map=token_handler_map)(token, phrase)
                                 for phrase in utterance_component)
        handled_token_combo.append(token_components)
    return tuple(handled_token_combo)

def _get_token_handler(token: str,
                       *,
                       token_handler_map: Optional[TOKEN_HANDLER_MAP] = None
                       ) -> TOKEN_HANDLER:
    default_token_handler = lambda token, phrase: '[{}({})]'.format(token, phrase)
    if token_handler_map:
        return token_handler_map.get(token) or token_handler_map.get('DEFAULT') or default_token_handler
    return default_token_handler

@lru_cache(maxsize=None)
def _expand_token_pattern(token_pattern: _HASHABLE_TOKEN_PATTERN) -> Sequence[str]:
    return tuple(' '.join(phrase) for phrase in join_combo(token_pattern))
