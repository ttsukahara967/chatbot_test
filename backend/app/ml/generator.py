from threading import Thread
from typing import Iterator, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

from app.config import settings

_tokenizer = None
_model = None


def _load():
    global _tokenizer, _model
    if _model is None:
        # rinna-style Japanese models use a SentencePiece-based T5Tokenizer
        # that doesn't support fast-tokenizer conversion, so use_fast=False is required
        _tokenizer = AutoTokenizer.from_pretrained(
            settings.generation_model, use_fast=False
        )
        _model = AutoModelForCausalLM.from_pretrained(settings.generation_model)
        _model.eval()
        if _tokenizer.pad_token_id is None:
            _tokenizer.pad_token = _tokenizer.eos_token
    return _tokenizer, _model


def stream_generate(prompt: str, max_new_tokens: Optional[int] = None) -> Iterator[str]:
    """Generator that yields tokens from a PyTorch model incrementally.

    model.generate is a blocking call, so it runs in a separate thread
    and tokens are streamed via TextIteratorStreamer.
    """
    tokenizer, model = _load()
    inputs = tokenizer(prompt, return_tensors="pt")
    streamer = TextIteratorStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True
    )

    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens or settings.max_new_tokens,
        do_sample=True,
        top_p=0.9,
        temperature=0.8,
        repetition_penalty=1.3,
        no_repeat_ngram_size=3,
        pad_token_id=tokenizer.pad_token_id,
    )

    # HF's generate() is already wrapped with @torch.no_grad() internally
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    for token_text in streamer:
        yield token_text

    thread.join()
