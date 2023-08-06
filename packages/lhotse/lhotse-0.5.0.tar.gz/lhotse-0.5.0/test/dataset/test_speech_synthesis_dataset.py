import pytest

from lhotse.cut import CutSet
from lhotse.dataset.speech_synthesis import SpeechSynthesisDataset


@pytest.fixture
def cut_set():
    return CutSet.from_json('test/fixtures/ljspeech/cuts.json')


def test_speech_synthesis_dataset(cut_set):
    ids = cut_set.ids
    dataset = SpeechSynthesisDataset(cut_set)
    example = dataset[ids]
    assert example['audio'].shape[1] > 0
    assert example['features'].shape[1] > 0
    assert len(example['tokens'][0]) > 0
