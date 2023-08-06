# encoding: utf-8

# author: BrikerMan
# contact: eliyar917@gmail.com
# blog: https://eliyar.biz

# file: base_indexer.py
# time: 2019-05-21 11:27

from typing import Dict, Any, Tuple




class BaseIndexer():
    def to_dict(self) -> Dict[str, Any]:
        return {
            'config': {
                'token_pad': self.token_pad,
                'token_unk': self.token_unk,
                'token_bos': self.token_bos,
                'token_eos': self.token_eos,
                'vocab2idx': self.vocab2idx
            },
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
        }

    def __init__(self, **kwargs: Any) -> None:
        self.vocab2idx = kwargs.get('vocab2idx', {})
        self.idx2vocab = dict([(v, k) for k, v in self.vocab2idx.items()])

        self.token_pad: str = kwargs.get('token_pad', '[PAD]')  # type: ignore
        self.token_unk: str = kwargs.get('token_unk', '[UNK]')  # type: ignore
        self.token_bos: str = kwargs.get('token_bos', '[CLS]')  # type: ignore
        self.token_eos: str = kwargs.get('token_eos', '[SEP]')  # type: ignore

    @property
    def vocab_size(self) -> int:
        return len(self.vocab2idx)

    @property
    def is_vocab_build(self) -> bool:
        return self.vocab_size != 0

    def build_vocab(self, x_data, y_data):
        from kolibri.data.text.corpus.generators import DataGenerator
        corpus_gen = DataGenerator(x_data, y_data)
        self.build_vocab_generator([corpus_gen])

    def build_vocab_generator(self, generators):
        raise NotImplementedError

    def get_tensor_shape(self, batch_size: int, seq_length: int) -> Tuple:
        return batch_size, seq_length

    def transform(self, samples):
        raise NotImplementedError

    def inverse_transform(self, labels, lengths=None, threshold: float = 0.5, **kwargs):
        raise NotImplementedError

if __name__ == "__main__":
    print("Hello world")
