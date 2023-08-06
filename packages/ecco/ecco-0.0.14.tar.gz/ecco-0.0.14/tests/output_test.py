from ecco import output
import pytest
import torch
import numpy as np
from ecco.output import NMF
import ecco

class TestOutput:
    def test_position_raises_value_error_more(self):
        output_seq = output.OutputSeq(tokens=[0, 0], n_input_tokens=1)

        with pytest.raises(ValueError):
            output_seq.position(position=4)

    def test_position_raises_value_error_less(self):
        output_seq = output.OutputSeq(tokens=[0, 0], n_input_tokens=1)

        with pytest.raises(ValueError):
            output_seq.position(position=0)

    def test_saliency(self, output_seq_1):
        actual = output_seq_1.saliency(printJson=True)
        expected = {'tokens': [{'token': ' 1', 'token_id': 352, 'type': 'input', 'value': '0.31678662', 'position': 0},
                               {'token': ',', 'token_id': 11, 'type': 'input', 'value': '0.18056837', 'position': 1},
                               {'token': ' 1', 'token_id': 352, 'type': 'input', 'value': '0.37555906', 'position': 2},
                               {'token': ',', 'token_id': 11, 'type': 'input', 'value': '0.12708597', 'position': 3},
                               {'token': ' 2', 'token_id': 362, 'type':
                                   'output', 'value': '0', 'position': 4}], 'attributions': [
            [0.31678661704063416, 0.1805683672428131, 0.3755590617656708, 0.12708596885204315]]}

        assert actual == expected


    def test_layer_position_zero_raises_valueerror(self, output_seq_1):
        with pytest.raises(ValueError, match=r".* set to 0*") as ex:
            actual = output_seq_1.layer_predictions(position=0)

    def test_layer_predictions_all_layers(self, output_seq_1):
        actual = output_seq_1.layer_predictions(printJson=True)
        assert len(actual) == 6  # an array for each layer

        assert actual[0][0]['ranking'] == 1
        assert actual[0][0]['layer'] == 0

    def test_layer_predictions_one_layer(self, output_seq_1):
        actual = output_seq_1.layer_predictions(layer=2, printJson=True)
        assert len(actual) == 1  # an array for each layer
        assert actual[0][0]['ranking'] == 1
        assert actual[0][0]['layer'] == 2

    def test_layer_predictions_topk(self, output_seq_1):
        actual = output_seq_1.layer_predictions(layer=2, printJson=True, topk=15)
        assert len(actual) == 1  # an array for each layer
        assert len(actual[0]) == 15

    def test_rankings(self, output_seq_1):
        actual = output_seq_1.rankings(printJson=True)
        assert len(actual['output_tokens']) == 1
        assert actual['rankings'].shape == (6, 1)
        assert isinstance(int(actual['rankings'][0][0]), int)

    def test_rankings_watch(self, output_seq_1):
        actual = output_seq_1.rankings_watch(printJson=True, watch=[0, 0])
        assert len(actual['output_tokens']) == 2
        assert actual['rankings'].shape == (6, 2)
        assert isinstance(int(actual['rankings'][0][0]), int)

    def test_nmf_raises_activations_dimension_value_error(self):
        with pytest.raises(ValueError, match=r".* four dimensions.*") as ex:
            NMF(np.zeros(0),
                n_components=2)

    def test_nmf_raises_value_error_same_layer(self):
        with pytest.raises(ValueError, match=r".* same value.*") as ex:
            NMF(np.zeros((1, 1, 1, 1)),
                n_components=2,
                from_layer=0,
                to_layer=0)

    def test_nmf_raises_value_error_layer_bounds(self):
        with pytest.raises(ValueError, match=r".* larger.*"):
            NMF(np.zeros((1, 1, 1, 1)),
                n_components=2,
                from_layer=1,
                to_layer=0)

    # NMF properly deals with collect_activations_layer_nums
    def test_nmf_reshape_activations_1(self):
        batch, layers, neurons, position = 1, 6, 128, 10
        activations = np.ones((batch, layers, neurons, position))
        merged_activations = NMF.reshape_activations(activations,
                                                     None, None, None)
        assert merged_activations.shape == (layers*neurons, batch*position)

    # NMF properly deals with collect_activations_layer_nums
    def test_nmf_reshape_activations_2(self):
        batch, layers, neurons, position = 2, 6, 128, 10
        activations = np.ones((batch, layers, neurons, position))
        merged_activations = NMF.reshape_activations(activations,
                                                     None, None, None)
        assert merged_activations.shape == (layers*neurons, batch*position)


    def test_nmf_explore_on_dummy_gpt(self):
        lm = ecco.from_pretrained('sshleifer/tiny-gpt2',
                                  activations=True,
                                  verbose=False)
        output = lm.generate('test', generate=1)
        nmf = output.run_nmf()
        exp = nmf.explore(printJson=True)

        assert len(exp['tokens']) == 2 # input & output tokens
        # 1 redundant dimension, 1 generation /factor, 2 tokens.
        assert np.array(exp['factors']).shape == (1, 1, 2)

    def test_nmf_explore_on_dummy_bert(self):
        lm = ecco.from_pretrained('julien-c/bert-xsmall-dummy',
                                  activations=True,
                                  verbose=False)
        inputs = lm.to(lm.tokenizer(['test', 'hi'],
                                    padding=True,
                                    truncation=True,
                                    return_tensors="pt",
                                    max_length=512))
        output = lm(inputs)
        nmf = output.run_nmf()
        exp = nmf.explore(printJson=True)

        assert len(exp['tokens']) == 3  # CLS UNK SEP
        # 1 redundant dimension,6 factors, 6 tokens (a batch of two examples, 3 tokens each)
        assert np.array(exp['factors']).shape == (1, 6, 6)

    def test_nmf_output_dims(self):
        pass
    # 4d activations to 2d activations: one batch
    # multiple batches
    # one batch collect_activations_layer_nums


@pytest.fixture
def output_seq_1():
    class MockTokenizer:
        def decode(self, i=None):
            return ''

    output_1 = output.OutputSeq(**{'tokenizer': MockTokenizer(),
                                   'token_ids': [[352, 11, 352, 11, 362]],
                                   'n_input_tokens': 4,
                                   'output_text': ' 1, 1, 2',
                                   'tokens': [[' 1', ',', ' 1', ',', ' 2']],
                                   'hidden_states': [torch.rand(4, 768) for i in range(7)],
                                   'attention': None,
                                   'model_outputs': None,
                                   'attribution': {'gradient': [
                                       np.array([0.41861308, 0.13054065, 0.23851791, 0.21232839], dtype=np.float32)],
                                       'grad_x_input': [
                                           np.array([0.31678662, 0.18056837, 0.37555906, 0.12708597],
                                                    dtype=np.float32)]},
                                   'activations': [],
                                   'lm_head': torch.nn.Linear(768, 50257, bias=False),
                                   'device': 'cpu'})

    yield output_1
