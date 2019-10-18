# pylint: disable=too-many-lines
import random
import unittest
from pathlib import Path
from typing import Mapping  # pylint: disable=unused-import
from typing import Sequence
from typing import Tuple

from putput import ComboOptions
from putput import Pipeline
from putput.presets import displaCy
from putput.presets import iob2
from putput.presets import luis
from putput.presets import stochastic
from tests.unit.helper_functions import compare_all_pairs


class TestPipeline(unittest.TestCase):
    # pylint: disable=too-many-public-methods
    def setUp(self) -> None:
        self._disable_progress_bar = True
        self.maxDiff = None
        self._base_dir = Path(__file__).parent / 'pattern_definitions' / 'valid'
        random.seed(0)

    def test_expansion_hooks_tokens(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('kanye west', 'the beatles')
        }

        expansion_hooks_map = {
            'START, PLAY, ARTIST': (_sample_artist, _sample_play)
        }

        p = Pipeline(pattern_def_path,
                     expansion_hooks_map=expansion_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to listen the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_expansion_hooks_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('kanye west', 'the beatles')
        }

        expansion_hooks_map = {
            'DEFAULT': (_sample_artist, _sample_play)
        }

        p = Pipeline(pattern_def_path,
                     expansion_hooks_map=expansion_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to listen the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_expansion_hooks_tokens_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('kanye west', 'the beatles')
        }

        expansion_hooks_map = {
            'START, PLAY, ARTIST': (_sample_play,),
            'DEFAULT': (_sample_artist,)
        }

        p = Pipeline(pattern_def_path,
                     expansion_hooks_map=expansion_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to listen kanye west', 'he will want to listen the beatles',
                               'she will want to listen kanye west', 'she will want to listen the beatles',
                               'the beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(kanye west)]'),
                                ('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(kanye west)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[ARTIST(the beatles)]',))
        expected_groups = (('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(kanye west)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(kanye west)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([ARTIST(the beatles)])}',))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_hooks_tokens(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }

        combo_hooks_map = {
            'START, PLAY, ARTIST' : (_add_random_words,)
        }

        p = Pipeline(pattern_def_path,
                     combo_hooks_map=combo_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the please beatles',
                               'um he will want to listen the beatles',
                               'she will want to play the beatles please',
                               'she will want to please listen the beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_maps_with_utterance_pattern_as_key_expands(self) -> None:
        pattern_def_path = self._base_dir / 'nested_group_tokens_and_ranges.yml'
        expansion_hooks_map = {
            'WAKE, PLAY_PHRASE': (_group_nonsense,)
        }
        combo_hooks_map = {
            'WAKE, PLAY_PHRASE': (_add_random_words,)
        }
        combo_options_map = {
            'WAKE, PLAY_PHRASE': ComboOptions(max_sample_size=2, with_replacement=False)
        }

        p = Pipeline(pattern_def_path,
                     expansion_hooks_map=expansion_hooks_map,
                     combo_hooks_map=combo_hooks_map,
                     combo_options_map=combo_options_map)

        keys = ('WAKE, START, PLAY',
                'WAKE, START, PLAY, PLAY',
                'WAKE, START, PLAY, PLAY, PLAY',
                'WAKE, START, PLAY, PLAY, PLAY, PLAY')

        pairs = [(keys, p.expansion_hooks_map.keys()), # type: ignore
                 (keys, p.combo_hooks_map.keys()), # type: ignore
                 (keys, p.combo_options_map.keys())] # type: ignore
        compare_all_pairs(self, pairs)

    def test_property_maps_with_utterance_pattern_as_key_expands(self) -> None:
        pattern_def_path = self._base_dir / 'nested_group_tokens_and_ranges.yml'
        expansion_hooks_map = {
            'WAKE, PLAY_PHRASE': (_group_nonsense,)
        }
        combo_hooks_map = {
            'WAKE, PLAY_PHRASE' : (_add_random_words,)
        }
        combo_options_map = {
            'WAKE, PLAY_PHRASE': ComboOptions(max_sample_size=2, with_replacement=False)
        }

        p = Pipeline(pattern_def_path)
        p.expansion_hooks_map = expansion_hooks_map
        p.combo_hooks_map = combo_hooks_map
        p.combo_options_map = combo_options_map

        keys = ('WAKE, START, PLAY',
                'WAKE, START, PLAY, PLAY',
                'WAKE, START, PLAY, PLAY, PLAY',
                'WAKE, START, PLAY, PLAY, PLAY, PLAY')

        pairs = [(keys, p.expansion_hooks_map.keys()), # type: ignore
                 (keys, p.combo_hooks_map.keys()), # type: ignore
                 (keys, p.combo_options_map.keys())] # type: ignore
        compare_all_pairs(self, pairs)

    def test_maps_with_utterance_pattern_as_key_applies(self) -> None:
        # pylint: disable=too-many-locals
        pattern_def_path = self._base_dir / 'nested_group_tokens_and_ranges.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }

        expansion_hooks_map = {
            'WAKE, PLAY_PHRASE': (_group_nonsense,)
        }

        combo_hooks_map = {
            'WAKE, PLAY_PHRASE': (_add_random_words, _add_commas_to_groups)
        }

        combo_options_map = {
            'WAKE, PLAY_PHRASE': ComboOptions(max_sample_size=1, with_replacement=False)
        }

        p = Pipeline(pattern_def_path,
                     combo_options_map=combo_options_map,
                     combo_hooks_map=combo_hooks_map,
                     expansion_hooks_map=expansion_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map,
                     seed=0)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi she wants hmmmm to listen',
                               'hi she wants to listen to play please',
                               'hi she wants to listen to play um to play',
                               'hi she wants to play to listen to uh listen to play')
        expected_tokens_list = (('[WAKE(hi)]', '[START(she wants)]', '[PLAY(to listen)]'),
                                ('[WAKE(hi)]', '[START(she wants)]', '[PLAY(to listen)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(she wants)]', '[PLAY(to listen)]', '[PLAY(to play)]',
                                 '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(she wants)]', '[PLAY(to play)]', '[PLAY(to listen)]',
                                 '[PLAY(to listen)]', '[PLAY(to play)]'))
        expected_groups = (('{nonsense([WAKE(hi)])},', '{PLAY_PHRASE([START(she wants)] [PLAY(to listen)])},'),
                           ('{nonsense([WAKE(hi)])},',
                            '{PLAY_PHRASE([START(she wants)] [PLAY(to listen)] [PLAY(to play)])},'),
                           ('{nonsense([WAKE(hi)])},',
                            '{PLAY_PHRASE([START(she wants)] [PLAY(to listen)] [PLAY(to play)] [PLAY(to play)])},'),
                           ('{nonsense([WAKE(hi)])},',
                            '{PLAY_PHRASE([START(she wants)] [PLAY(to play)] [PLAY(to listen)] [PLAY(to listen)] \
[PLAY(to play)])},'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_hooks_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }

        combo_hooks_map = {
            'DEFAULT' : (_add_random_words, _add_commas_to_groups)
        }

        p = Pipeline(pattern_def_path,
                     combo_hooks_map=combo_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the please beatles',
                               'um he will want to listen the beatles',
                               'she will want to play the beatles please',
                               'she will want to please listen the beatles')
        expected_tokens_list = (('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(he will want)])},', '{None([PLAY(to play)])},',
                            '{None([ARTIST(the beatles)])},'),
                           ('{None([START(he will want)])},', '{None([PLAY(to listen)])},',
                            '{None([ARTIST(the beatles)])},'),
                           ('{None([START(she will want)])},', '{None([PLAY(to play)])},',
                            '{None([ARTIST(the beatles)])},'),
                           ('{None([START(she will want)])},', '{None([PLAY(to listen)])},',
                            '{None([ARTIST(the beatles)])},'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_hooks_tokens_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }

        combo_hooks_map = {
            'START, PLAY, ARTIST' : (_add_random_words,),
            'DEFAULT' : (_lowercase_handled_tokens,)
        }

        p = Pipeline(pattern_def_path,
                     combo_hooks_map=combo_hooks_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('the beatles',
                               'he will want to play the please beatles',
                               'um he will want to listen the beatles',
                               'she will want to play the beatles please',
                               'she will want to please listen the beatles')
        expected_tokens_list = (('[artist(the beatles)]',),
                                ('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([ARTIST(the beatles)])}',),
                           ('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_token_handlers_token(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }
        token_handler_map = {
            'START': _just_tokens,
        }
        p = Pipeline(pattern_def_path,
                     token_handler_map=token_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START])}', '{None([PLAY(to play)])}', '{None([ARTIST(the beatles)])}'),
                           ('{None([START])}', '{None([PLAY(to listen)])}', '{None([ARTIST(the beatles)])}'),
                           ('{None([START])}', '{None([PLAY(to play)])}', '{None([ARTIST(the beatles)])}'),
                           ('{None([START])}', '{None([PLAY(to listen)])}', '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_token_handlers_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }
        token_handler_map = {
            'DEFAULT': _just_tokens,
        }
        p = Pipeline(pattern_def_path,
                     token_handler_map=token_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START]', '[PLAY]', '[ARTIST]'),
                                ('[START]', '[PLAY]', '[ARTIST]'),
                                ('[START]', '[PLAY]', '[ARTIST]'),
                                ('[START]', '[PLAY]', '[ARTIST]'))
        expected_groups = (('{None([START])}', '{None([PLAY])}', '{None([ARTIST])}'),
                           ('{None([START])}', '{None([PLAY])}', '{None([ARTIST])}'),
                           ('{None([START])}', '{None([PLAY])}', '{None([ARTIST])}'),
                           ('{None([START])}', '{None([PLAY])}', '{None([ARTIST])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_token_handlers_token_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }
        token_handler_map = {
            'START': _just_tokens,
            'DEFAULT': _remove_token,
        }
        p = Pipeline(pattern_def_path,
                     token_handler_map=token_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START]', '[(to play)]', '[(the beatles)]',),
                                ('[START]', '[(to play)]', '[(the beatles)]',),
                                ('[START]', '[(to listen)]', '[(the beatles)]',),
                                ('[START]', '[(to listen)]', '[(the beatles)]'))
        expected_groups = (('{None([START])}', '{None([(to play)])}', '{None([(the beatles)])}'),
                           ('{None([START])}', '{None([(to listen)])}', '{None([(the beatles)])}'),
                           ('{None([START])}', '{None([(to play)])}', '{None([(the beatles)])}'),
                           ('{None([START])}', '{None([(to listen)])}', '{None([(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_group_handlers_group(self) -> None:
        pattern_def_path = self._base_dir / 'static_and_base_tokens_and_group_tokens.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }
        group_handler_map = {
            'PLAY_PHRASE': _remove_group,
        }
        p = Pipeline(pattern_def_path,
                     group_handler_map=group_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen')
        expected_tokens_list = (('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to listen)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to listen)]'))
        expected_groups = (('{None([WAKE(hi)])}', '{([START(he will want)] [PLAY(to play)])}'),
                           ('{None([WAKE(hi)])}', '{([START(he will want)] [PLAY(to listen)])}'),
                           ('{None([WAKE(hi)])}', '{([START(she will want)] [PLAY(to play)])}'),
                           ('{None([WAKE(hi)])}', '{([START(she will want)] [PLAY(to listen)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_group_handlers_default(self) -> None:
        pattern_def_path = self._base_dir / 'static_and_base_tokens_and_group_tokens.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }
        group_handler_map = {
            'DEFAULT': _just_groups,
        }
        p = Pipeline(pattern_def_path,
                     group_handler_map=group_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen')
        expected_tokens_list = (('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to listen)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to listen)]'))
        expected_groups = (('[None]', '[PLAY_PHRASE]'),
                           ('[None]', '[PLAY_PHRASE]'),
                           ('[None]', '[PLAY_PHRASE]'),
                           ('[None]', '[PLAY_PHRASE]'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_group_handlers_group_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'static_and_base_tokens_and_group_tokens.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }
        group_handler_map = {
            'None': _remove_group,
            'DEFAULT': _just_groups,
        }
        p = Pipeline(pattern_def_path,
                     group_handler_map=group_handler_map,
                     dynamic_token_patterns_map=dynamic_token_patterns_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play', 'hi he will want to listen',
                               'hi she will want to play', 'hi she will want to listen')
        expected_tokens_list = (('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(he will want)]', '[PLAY(to listen)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to play)]'),
                                ('[WAKE(hi)]', '[START(she will want)]', '[PLAY(to listen)]'))
        expected_groups = (('{([WAKE(hi)])}', '[PLAY_PHRASE]'),
                           ('{([WAKE(hi)])}', '[PLAY_PHRASE]'),
                           ('{([WAKE(hi)])}', '[PLAY_PHRASE]'),
                           ('{([WAKE(hi)])}', '[PLAY_PHRASE]'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_options_without_replacement(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }
        combo_options_map = {
            'START, PLAY, ARTIST': ComboOptions(max_sample_size=5, with_replacement=False)
        }

        p = Pipeline(pattern_def_path,
                     dynamic_token_patterns_map=dynamic_token_patterns_map,
                     combo_options_map=combo_options_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('he will want to play the beatles', 'he will want to listen the beatles',
                               'she will want to play the beatles', 'she will want to listen the beatles')
        expected_tokens_list = (('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_options_with_replacement(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }
        max_sample_size = 5
        combo_options_map = {
            'START, PLAY, ARTIST': ComboOptions(max_sample_size=max_sample_size,
                                                with_replacement=True)
        }

        p = Pipeline(pattern_def_path,
                     dynamic_token_patterns_map=dynamic_token_patterns_map,
                     combo_options_map=combo_options_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('she will want to listen the beatles', 'she will want to listen the beatles',
                               'he will want to play the beatles', 'she will want to play the beatles',
                               'she will want to listen the beatles')
        expected_tokens_list = (('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_options_default(self) -> None:
        pattern_def_path = self._base_dir / 'dynamic_and_static_token_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles',)
        }
        max_sample_size = 5
        combo_options_map = {
            'DEFAULT': ComboOptions(max_sample_size=max_sample_size, with_replacement=True)
        }

        p = Pipeline(pattern_def_path,
                     dynamic_token_patterns_map=dynamic_token_patterns_map,
                     combo_options_map=combo_options_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('she will want to listen the beatles',
                               'she will want to listen the beatles',
                               'he will want to play the beatles',
                               'she will want to play the beatles',
                               'she will want to listen the beatles')
        expected_tokens_list = (('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_combo_options_tokens_and_default(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_utterance_patterns.yml'
        dynamic_token_patterns_map = {
            'ARTIST': ('the beatles', 'kanye')
        }
        combo_options_map = {
            'ARTIST': ComboOptions(max_sample_size=1, with_replacement=True),
            'DEFAULT': ComboOptions(max_sample_size=3, with_replacement=True)
        }

        p = Pipeline(pattern_def_path,
                     dynamic_token_patterns_map=dynamic_token_patterns_map,
                     combo_options_map=combo_options_map)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('kanye',
                               'she will want to listen the beatles',
                               'he will want to play the beatles',
                               'she will want to play the beatles')
        expected_tokens_list = (('[ARTIST(kanye)]',),
                                ('[START(she will want)]', '[PLAY(to listen)]', '[ARTIST(the beatles)]'),
                                ('[START(he will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'),
                                ('[START(she will want)]', '[PLAY(to play)]', '[ARTIST(the beatles)]'))
        expected_groups = (('{None([ARTIST(kanye)])}',),
                           ('{None([START(she will want)])}', '{None([PLAY(to listen)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(he will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'),
                           ('{None([START(she will want)])}', '{None([PLAY(to play)])}',
                            '{None([ARTIST(the beatles)])}'))

        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_tokens_to_include(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset(iob2.preset(tokens_to_include=('WAKE',)), pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = (('B-WAKE', 'O O O', 'O O'),
                                ('B-WAKE', 'O O O', 'O O'),
                                ('B-WAKE', 'O O O', 'O O'),
                                ('B-WAKE', 'O O O', 'O O'),
                                ('B-WAKE',))
        expected_groups = (('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None',))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_tokens_to_exclude(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset(iob2.preset(tokens_to_exclude=('WAKE',)), pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = (('O', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('O', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('O', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('O', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('O',))
        expected_groups = (('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None',))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_tokens_to_include_and_tokens_to_exclude(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        with self.assertRaises(ValueError):
            Pipeline.from_preset(iob2.preset(tokens_to_include=('WAKE',),
                                             tokens_to_exclude=('PLAY',)),
                                 pattern_def_path)

    def test_iob2_preset_groups_to_include_and_groups_to_exclude(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        with self.assertRaises(ValueError):
            Pipeline.from_preset(iob2.preset(groups_to_include=('PLAY_SONG',),
                                             groups_to_exclude=('PLAY_ARTIST',)),
                                 pattern_def_path)

    def test_preset_str_invalid(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        with self.assertRaises(ValueError):
            Pipeline.from_preset('INVALID', pattern_def_path)

    def test_iob2_preset_groups_to_include(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset(iob2.preset(groups_to_include=('PLAY_PHRASE',)), pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = (('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE',))
        expected_groups = (('O', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('O', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('O', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('O', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('O',))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_preset_groups_to_exclude(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset(iob2.preset(groups_to_exclude=('PLAY_PHRASE',)), pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = (('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE',))
        expected_groups = (('B-None', 'O O O O O'),
                           ('B-None', 'O O O O O'),
                           ('B-None', 'O O O O O'),
                           ('B-None', 'O O O O O'),
                           ('B-None',))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_iob2_str_preset(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset('IOB2', pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = ('hi he will want to play',
                               'hi he will want to listen',
                               'hi she will want to play',
                               'hi she will want to listen',
                               'hi')
        expected_tokens_list = (('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE', 'B-START I-START I-START', 'B-PLAY I-PLAY'),
                                ('B-WAKE',))
        expected_groups = (('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None', 'B-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE I-PLAY_PHRASE'),
                           ('B-None',))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_displaCy_func_preset(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset(displaCy.preset(), pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_tokens_visualizer, actual_groups_visualizer = zip(*generator)
        exp_tokens_visualizer = ({'text': 'hi he will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 15, 'label': 'START'},
                                           {'start': 16, 'end': 23, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi he will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 15, 'label': 'START'},
                                           {'start': 16, 'end': 25, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi she will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 16, 'label': 'START'},
                                           {'start': 17, 'end': 24, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi she will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 16, 'label': 'START'},
                                           {'start': 17, 'end': 26, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'}],
                                  'title': 'Tokens'})
        exp_groups_visualizer = ({'text': 'hi he will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 23, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi he will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 25, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi she will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 24, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi she will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 26, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'}],
                                  'title': 'Groups'})
        pairs = [(actual_tokens_visualizer, exp_tokens_visualizer),
                 (actual_groups_visualizer, exp_groups_visualizer)]
        compare_all_pairs(self, pairs)

    def test_displaCy_str_preset(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset('DISPLACY', pattern_def_path)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_tokens_visualizer, actual_groups_visualizer = zip(*generator)
        exp_tokens_visualizer = ({'text': 'hi he will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 15, 'label': 'START'},
                                           {'start': 16, 'end': 23, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi he will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 15, 'label': 'START'},
                                           {'start': 16, 'end': 25, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi she will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 16, 'label': 'START'},
                                           {'start': 17, 'end': 24, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi she will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'},
                                           {'start': 3, 'end': 16, 'label': 'START'},
                                           {'start': 17, 'end': 26, 'label': 'PLAY'}],
                                  'title': 'Tokens'},
                                 {'text': 'hi',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'WAKE'}],
                                  'title': 'Tokens'})
        exp_groups_visualizer = ({'text': 'hi he will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 23, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi he will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 25, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi she will want to play',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 24, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi she will want to listen',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'},
                                           {'start': 3, 'end': 26, 'label': 'PLAY_PHRASE'}],
                                  'title': 'Groups'},
                                 {'text': 'hi',
                                  'ents': [{'start': 0, 'end': 2, 'label': 'None'}],
                                  'title': 'Groups'})
        pairs = [(actual_tokens_visualizer, exp_tokens_visualizer),
                 (actual_groups_visualizer, exp_groups_visualizer)]
        compare_all_pairs(self, pairs)

    def test_luis_preset_no_entities_one_intent(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        intent_map = {
            'WAKE, PLAY_PHRASE': 'PLAY_INTENT'
        }
        p = Pipeline.from_preset(luis.preset(intent_map=intent_map,
                                             entities=[]),
                                 pattern_def_path,
                                 seed=0)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        luis_tests = list(generator)
        expected_luis_tests = [
            {'text': 'hi he will want to play', 'intent': 'PLAY_INTENT', 'entities': []},
            {'text': 'hi he will want to listen', 'intent': 'PLAY_INTENT', 'entities': []},
            {'text': 'hi she will want to play', 'intent': 'PLAY_INTENT', 'entities': []},
            {'text': 'hi she will want to listen', 'intent': 'PLAY_INTENT', 'entities': []}
        ]
        pairs = [(luis_tests, expected_luis_tests)]
        compare_all_pairs(self, pairs)

    def test_luis_preset_no_entities_multiple_intent(self) -> None:
        pattern_def_path = self._base_dir / 'no_entities_multiple_intent.yml'
        p = Pipeline.from_preset('LUIS',
                                 pattern_def_path,
                                 seed=0)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        luis_tests = list(generator)
        expected_luis_tests = [
            {'text': 'hi', 'intent': 'WAKE_INTENT', 'entities': []},
            {'text': 'hi he will want to play', 'intent': 'PLAY_INTENT', 'entities': []},
            {'text': 'hi he will want to listen', 'intent': 'PLAY_INTENT', 'entities': []},
            {'text': 'hi she will want to play', 'intent': 'PLAY_INTENT', 'entities': []},
            {'text': 'hi she will want to listen', 'intent': 'PLAY_INTENT', 'entities': []}
        ]
        pairs = [(luis_tests, expected_luis_tests)]
        compare_all_pairs(self, pairs)

    def test_luis_preset_only_entities(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        entities = ['PLAY']
        p = Pipeline.from_preset(luis.preset(entities=entities), pattern_def_path, seed=0)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        luis_tests = list(generator)
        expected_luis_tests = [
            {'text': 'hi', 'intent': 'None', 'entities': []},
            {'text': 'hi he will want to play',
             'intent': 'None',
             'entities': [{'entity': 'PLAY', 'startPos': 16, 'endPos': 22}]},
            {'text': 'hi he will want to listen',
             'intent': 'None',
             'entities': [{'entity': 'PLAY', 'startPos': 16, 'endPos': 24}]},
            {'text': 'hi she will want to play',
             'intent': 'None',
             'entities': [{'entity': 'PLAY', 'startPos': 17, 'endPos': 23}]},
            {'text': 'hi she will want to listen',
             'intent': 'None',
             'entities': [{'entity': 'PLAY', 'startPos': 17, 'endPos': 25}]}]
        pairs = [(luis_tests, expected_luis_tests)]
        compare_all_pairs(self, pairs)

    def test_luis_preset_intent_and_entities(self) -> None:
        pattern_def_path = self._base_dir / 'simple_intent_and_entity.yml'
        p = Pipeline.from_preset('LUIS',
                                 pattern_def_path,
                                 seed=0)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        luis_tests = list(generator)
        expected_luis_tests = [
            {
                'text': 'hi he will want to play',
                'intent': 'PLAY_INTENT',
                'entities': [{'entity': 'PLAY', 'startPos': 16, 'endPos': 22}]
            },
            {
                'text': 'hi he will want to listen',
                'intent': 'PLAY_INTENT',
                'entities': [{'entity': 'PLAY', 'startPos': 16, 'endPos': 24}]
            },
            {
                'text': 'hi she will want to play',
                'intent': 'PLAY_INTENT',
                'entities': [{'entity': 'PLAY', 'startPos': 17, 'endPos': 23}]
            },
            {
                'text': 'hi she will want to listen',
                'intent': 'PLAY_INTENT',
                'entities': [{'entity': 'PLAY', 'startPos': 17, 'endPos': 25}]
            }
        ]
        pairs = [(luis_tests, expected_luis_tests)]
        compare_all_pairs(self, pairs)

    def test_luis_preset_str(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset('LUIS', pattern_def_path=pattern_def_path, seed=0)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        luis_tests = list(generator)
        expected_luis_tests = [] # type: Sequence[Mapping]
        pairs = [(luis_tests, expected_luis_tests)]
        compare_all_pairs(self, pairs)

    def test_luis_all_entities(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        entities = ['__ALL']
        p = Pipeline.from_preset(luis.preset(entities=entities), pattern_def_path, seed=0)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        luis_tests = list(generator)
        expected_luis_tests = [
            {'text': 'hi',
             'intent': 'None',
             'entities': [{'entity': 'WAKE', 'startPos': 0, 'endPos': 1}]},
            {'text': 'hi he will want to play',
             'intent': 'None',
             'entities': [{'entity': 'WAKE', 'startPos': 0, 'endPos': 1},
                          {'entity': 'START', 'startPos': 3, 'endPos': 14},
                          {'entity': 'PLAY', 'startPos': 16, 'endPos': 22}]},
            {'text': 'hi he will want to listen',
             'intent': 'None',
             'entities': [{'entity': 'WAKE', 'startPos': 0, 'endPos': 1},
                          {'entity': 'START', 'startPos': 3, 'endPos': 14},
                          {'entity': 'PLAY', 'startPos': 16, 'endPos': 24}]},
            {'text': 'hi she will want to play',
             'intent': 'None',
             'entities': [{'entity': 'WAKE', 'startPos': 0, 'endPos': 1},
                          {'entity': 'START', 'startPos': 3, 'endPos': 15},
                          {'entity': 'PLAY', 'startPos': 17, 'endPos': 23}]},
            {'text': 'hi she will want to listen',
             'intent': 'None',
             'entities': [{'entity': 'WAKE', 'startPos': 0, 'endPos':1},
                          {'entity': 'START', 'startPos': 3, 'endPos': 15},
                          {'entity': 'PLAY', 'startPos': 17, 'endPos': 25}]}]
        pairs = [(luis_tests, expected_luis_tests)]
        compare_all_pairs(self, pairs)

    def test_luis_preset_reserved_word(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        intent_map = {
            'WAKE, PLAY_PHRASE': '__DISCARD'
        }
        with self.assertRaises(ValueError):
            Pipeline.from_preset(luis.preset(intent_map=intent_map),
                                 pattern_def_path,
                                 seed=0)

    def test_properties_getter_setters_access_level(self) -> None:
        props = {} # type: dict
        props['pattern_def_path'] = self._base_dir / 'nested_group_tokens_and_ranges.yml'
        props['dynamic_token_patterns_map'] = {
            'ARTIST': ((('kanye west', 'the beatles'),),)
        }
        props['token_handler_map'] = {
            'START': _just_tokens,
        }
        props['group_handler_map'] = {
            'PLAY_PHRASE': _remove_group,
        }
        props['expansion_hooks_map'] = {
            'WAKE': (_group_nonsense,)
        }
        props['combo_hooks_map'] = {
            'WAKE' : (_add_random_words,)
        }
        props['combo_options_map'] = {
            'WAKE': ComboOptions(max_sample_size=2, with_replacement=False)
        }
        props['seed'] = 0

        p = Pipeline(**props)
        for name, value in props.items():
            prop = getattr(p, name)
            self.assertEqual(prop, value)
        with self.assertRaises(AttributeError):
            p.pattern_def_path = "some value" # type: ignore

    def test_stochastic_preset_obj(self) -> None:
        pattern_def_path = self._base_dir / 'all_pos.yml'
        p = Pipeline.from_preset(stochastic.preset(chance=80),
                                 pattern_def_path,
                                 seed=0)
        generator = p.flow(disable_progress_bar=self._disable_progress_bar)
        actual_utterances, actual_tokens_list, actual_groups = zip(*generator)
        expected_utterances = (('hi',
                                'howdy he will real much desire to play the happy song',
                                'hi he will rattling much want to listen the happy song',
                                'howdy she will rattling much want to play the happy song',
                                'hello she will very much desire to listen the happy vocal'))
        expected_tokens_list = (('[WAKE(hi)]',),
                                ('[WAKE(howdy)]', '[START(he will real much desire)]', '[PLAY(to play)]',
                                 '[MOD(the happy)]', '[SONG(song)]'),
                                ('[WAKE(hi)]', '[START(he will rattling much want)]', '[PLAY(to listen)]',
                                 '[MOD(the happy)]', '[SONG(song)]'),
                                ('[WAKE(howdy)]', '[START(she will rattling much want)]', '[PLAY(to play)]',
                                 '[MOD(the happy)]', '[SONG(song)]'),
                                ('[WAKE(hello)]', '[START(she will very much desire)]', '[PLAY(to listen)]',
                                 '[MOD(the happy)]', '[SONG(vocal)]'))
        expected_groups = (('{[WAKE(hi)]}',),
                           ('{[WAKE(howdy)]}',
                            '{[START(he will real much desire)] [PLAY(to play)] [MOD(the happy)] [SONG(song)]}'),
                           ('{[WAKE(hi)]}',
                            '{[START(he will rattling much want)] [PLAY(to listen)] [MOD(the happy)] [SONG(song)]}'),
                           ('{[WAKE(howdy)]}',
                            '{[START(she will rattling much want)] [PLAY(to play)] [MOD(the happy)] [SONG(song)]}'),
                           ('{[WAKE(hello)]}',
                            '{[START(she will very much desire)] [PLAY(to listen)] [MOD(the happy)] [SONG(vocal)]}'))
        pairs = [(actual_utterances, expected_utterances),
                 (actual_tokens_list, expected_tokens_list),
                 (actual_groups, expected_groups)]
        compare_all_pairs(self, pairs)

    def test_chaining_preset_obj(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        presets = (iob2.preset(tokens_to_include=('WAKE',)),
                   luis.preset())
        p = Pipeline.from_preset(presets,
                                 pattern_def_path,
                                 seed=0)
        self.assertTrue(hasattr(p, 'combo_hooks_map'))
        self.assertEqual(len(p.combo_hooks_map['DEFAULT']), 2) # type: ignore
        self.assertTrue(hasattr(p, 'token_handler_map'))
        self.assertTrue(hasattr(p, 'group_handler_map'))

    def test_chaining_preset_str(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        presets = ('DISPLACY', 'LUIS')
        p = Pipeline.from_preset(presets,
                                 pattern_def_path,
                                 seed=0)
        self.assertTrue(hasattr(p, 'combo_hooks_map'))
        self.assertEqual(len(p.combo_hooks_map['DEFAULT']), 4) # type: ignore

    def test_chaining_preset_str_obj(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        presets = ('DISPLACY', luis.preset())
        p = Pipeline.from_preset(presets,
                                 pattern_def_path,
                                 seed=0)
        self.assertTrue(hasattr(p, 'combo_hooks_map'))
        self.assertEqual(len(p.combo_hooks_map['DEFAULT']), 4) # type: ignore

    def test_chaining_order(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        presets = ('DISPLACY', 'LUIS')
        p = Pipeline.from_preset(presets,
                                 pattern_def_path,
                                 seed=0)
        self.assertTrue(hasattr(p, 'combo_hooks_map'))
        self.assertEqual(p.combo_hooks_map['DEFAULT'][-1].func.__name__, '_handle_intents_and_entities') # type: ignore

    def test_preset_with_kwargs(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        p = Pipeline.from_preset('DISPLACY',
                                 pattern_def_path,
                                 combo_hooks_map={"UNIQUE": (_add_random_words,)})
        self.assertTrue(len(set(p.combo_hooks_map)), 2) # type: ignore

    def test_chaining_invalid_overlap(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        presets = (iob2.preset(tokens_to_include=('WAKE',)),
                   iob2.preset(tokens_to_include=('START',)))
        with self.assertRaises(ValueError):
            Pipeline.from_preset(presets, pattern_def_path)

    def test_stochastic_preset_invalid_chance(self) -> None:
        pattern_def_path = self._base_dir / 'multiple_group_patterns.yml'
        invalid_chances = [-1, 101]
        for chance in invalid_chances:
            with self.assertRaises(ValueError):
                Pipeline.from_preset(stochastic.preset(chance=chance),
                                     pattern_def_path,
                                     seed=0)

def _just_groups(group_name: str, _: Sequence[str]) -> str:
    return '[{group_name}]'.format(group_name=group_name)

def _remove_group(_: str, handled_tokens: Sequence[str]) -> str:
    return '{{({handled_tokens})}}'.format(handled_tokens=' '.join(handled_tokens))

def _just_tokens(token: str, _: str) -> str:
    return '[{token}]'.format(token=token)

def _remove_token(_: str, phrase: str) -> str:
    return '[({phrase})]'.format(phrase=phrase)

def _sample_utterance_combo(utterance_combo: Sequence[Sequence[str]],
                            tokens: Sequence[str],
                            groups: Sequence[Tuple[str, int]],
                            token_to_sample: str,
                            sample_size: int,
                            ) -> Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]:
    TOKEN_INDEX = tokens.index(token_to_sample)
    utterance_combo_list = list(utterance_combo)
    sampled_combos = tuple(random.sample(utterance_combo_list.pop(TOKEN_INDEX), sample_size))
    utterance_combo_list.insert(TOKEN_INDEX, sampled_combos)
    utterance_combo = tuple(utterance_combo_list)
    return utterance_combo, tokens, groups

def _sample_play(utterance_combo: Sequence[Sequence[str]],
                 tokens: Sequence[str],
                 groups: Sequence[Tuple[str, int]]
                 ) -> Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]:
    return _sample_utterance_combo(utterance_combo, tokens, groups, 'PLAY', 1)

def _sample_artist(utterance_combo: Sequence[Sequence[str]],
                   tokens: Sequence[str],
                   groups: Sequence[Tuple[str, int]]
                   ) -> Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]:
    return _sample_utterance_combo(utterance_combo, tokens, groups, 'ARTIST', 1)

def _group_nonsense(utterance_combo: Sequence[Sequence[str]],
                    tokens: Sequence[str],
                    groups: Sequence[Tuple[str, int]]
                    ) -> Tuple[Sequence[Sequence[str]], Sequence[str], Sequence[Tuple[str, int]]]:
    nonsense_groups = list(groups)
    nonsense_groups[0] = ('nonsense', groups[0][1])
    return utterance_combo, tokens, nonsense_groups

def _add_random_words(utterance: str,
                      handled_tokens: Sequence[str],
                      handled_groups: Sequence[str],
                      ) -> Tuple[str, Sequence[str], Sequence[str]]:
    utterances = utterance.split()
    random_words = ['hmmmm', 'uh', 'um', 'please']
    insert_index = random.randint(0, len(utterances))
    random_word = random.choice(random_words)
    utterances.insert(insert_index, random_word)
    utterance = ' '.join(utterances)
    return utterance, handled_tokens, handled_groups

def _lowercase_handled_tokens(utterance: str,
                              handled_tokens: Sequence[str],
                              handled_groups: Sequence[str]
                              ) -> Tuple[str, Sequence[str], Sequence[str]]:
    return utterance, tuple([handled_token.lower() for handled_token in handled_tokens]), handled_groups

def _lowercase_handled_groups(utterance: str,
                              handled_tokens: Sequence[str],
                              handled_groups: Sequence[str]
                              ) -> Tuple[str, Sequence[str], Sequence[str]]:
    return utterance, handled_tokens, tuple([handled_group.lower() for handled_group in handled_groups])

def _add_commas_to_groups(utterance: str,
                          handled_tokens: Sequence[str],
                          handled_groups: Sequence[str]
                          ) -> Tuple[str, Sequence[str], Sequence[str]]:
    return utterance, handled_tokens, tuple([handled_group + ',' for handled_group in handled_groups])

if __name__ == '__main__':
    unittest.main()
