import re
from functools import partial
from typing import Any
from typing import Callable
from typing import Mapping
from typing import Optional
from typing import Sequence


def preset(*,
           intent_map: Mapping[str, str] = None,
           entities: Optional[Sequence[str]] = None
           ) -> Callable:
    """Configures the Pipeline for LUIS test format.

    Adheres to: https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-tutorial-batch-testing.

    This function should be used as the 'preset' argument of putput.Pipeline instead of
    the 'LUIS' str to specify intents and entities.

    Examples:
        >>> import json
        >>> from pathlib import Path
        >>> from putput.pipeline import Pipeline
        >>> from pprint import pprint
        >>> import random
        >>> random.seed(0)
        >>> pattern_folder = Path(__file__).parent.parent.parent / 'tests' / 'doc'
        >>> pattern_def_path = pattern_folder / 'example_pattern_definition_with_intents.yml'
        >>> dynamic_token_patterns_map = {'ITEM': ('fries',)}
        >>> p = Pipeline.from_preset('LUIS',
        ...                          pattern_def_path,
        ...                          dynamic_token_patterns_map=dynamic_token_patterns_map)
        >>> for luis_result in p.flow(disable_progress_bar=True):
        ...     print(json.dumps(luis_result, sort_keys=True))
        ...     break
        {"entities": [{"endPos": 16, "entity": "ITEM", "startPos": 12},
                      {"endPos": 34, "entity": "ITEM", "startPos": 30},
                      {"endPos": 44, "entity": "ITEM", "startPos": 40}],
         "intent": "ADD_INTENT",
         "text": "can she get fries can she get fries and fries"}

    Args:
        intent_map: A mapping from an utterance pattern string to a single intent.
            The value '__DISCARD' is reserved.

        entities: A sequence of tokens that are considered entities. To make all tokens
            entities, give a list with only the value '__ALL'. E.g. entities=['_ALL']

    Returns:
        A Callable that when called returns parameters for instantiating a Pipeline.
        This Callable can be passed into putput.Pipeline as the 'preset' argument.
    """
    if intent_map:
        if '__DISCARD' in set(intent_map.values()):
            raise ValueError('__DISCARD is a reserved value.')
    return partial(_preset,
                   intent_map=intent_map,
                   entities=entities)

def _preset(intent_map: Optional[Mapping[str, str]], # pylint: disable=W0613
            entities: Optional[Sequence[str]],
            __intent_map_from_pipeline: Mapping[str, str],
            __entities_from_pipeline: Sequence[str],
            **kwargs: Any
            ) -> Mapping:
    # only override if caller does not specify intent_map/entities
    if not intent_map and __intent_map_from_pipeline is not None:
        intent_map = __intent_map_from_pipeline
    if not entities and __entities_from_pipeline is not None:
        entities = __entities_from_pipeline

    combo_hooks_map = {}
    # Combo hook per intent
    for pattern, intent in intent_map.items():
        combo_hooks_map[pattern] = (partial(_handle_intents_and_entities, intent=intent, entities=entities),)

    # Handle entities and no intent
    if entities and not intent_map:
        combo_hooks_map['DEFAULT'] = (partial(_handle_intents_and_entities, intent=None, entities=entities),)
    else:
        # Default case
        combo_hooks_map['DEFAULT'] = (partial(_handle_intents_and_entities, intent='__DISCARD', entities=entities),)
    return {
        'combo_hooks_map': combo_hooks_map
    }

def _convert_to_luis_entities(utterance: str,
                              entities: Sequence[str],
                              handled_items: Sequence[str]
                              ) -> Sequence[Mapping]:
    ents = []
    offset = 0
    for handled_item in handled_items:
        label = _token_extractor(handled_item)
        phrase = ' '.join(re.findall(r'\(([^()]+)\)', handled_item))
        start = offset + utterance[offset:].index(phrase)
        end = start + len(phrase) - 1
        if label in entities:
            ent = {
                'entity': label,
                'startPos': start,
                'endPos': end
            }
            ents.append(ent)
        offset = end
    return ents

def _token_extractor(handled_item: str) -> str:
    return handled_item[handled_item.index('[') + 1: handled_item.index('(')]

def _handle_intents_and_entities(utterance: str,
                                 handled_tokens: Sequence[str],
                                 _: Sequence[str],
                                 *,
                                 intent: Optional[str] = None,
                                 entities: Sequence[str]
                                 ) -> Optional[Mapping]:
    if intent == '__DISCARD':
        return None
    if intent is None:
        intent = 'None'
    if len(entities) == 1 and entities[0] == '__ALL':
        entities = list(map(_token_extractor, handled_tokens))
    luis_entities = _convert_to_luis_entities(utterance, entities, handled_tokens)
    return {
        'text': utterance,
        'intent': intent,
        'entities': luis_entities
    }
