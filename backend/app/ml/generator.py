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
        # use_fast=False is a safe default across model families (required for
        # rinna's SentencePiece-based T5Tokenizer, and also works for others)
        _tokenizer = AutoTokenizer.from_pretrained(
            settings.generation_model, use_fast=False
        )
        # float16 roughly halves memory usage vs. the fp32 default, which
        # matters when running on a memory-constrained Docker environment.
        # device_map="auto" (via accelerate) places the model on the GPU when
        # one is visible to the container (see docker-compose.yml's GPU
        # reservation), and transparently falls back to CPU otherwise.
        _model = AutoModelForCausalLM.from_pretrained(
            settings.generation_model,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            device_map="auto",
        )
        _model.eval()
        if _tokenizer.pad_token_id is None:
            _tokenizer.pad_token = _tokenizer.eos_token
    return _tokenizer, _model


def _build_inputs(tokenizer, messages: list[dict]) -> dict:
    """Build model inputs from chat messages.

    Instruction-tuned models ship a chat template (system/user/assistant
    turns with the model's own special tokens); base models like gpt2 don't,
    so we fall back to concatenating the message contents as plain text.
    """
    if getattr(tokenizer, "chat_template", None):
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        )
        # causal LMs don't accept token_type_ids, but some tokenizers add it
        inputs.pop("token_type_ids", None)
        return inputs
    text = "\n\n".join(m["content"] for m in messages) + "\n\n回答:"
    return tokenizer(text, return_tensors="pt")


def stream_generate(
    messages: list[dict], max_new_tokens: Optional[int] = None
) -> Iterator[str]:
    """Generator that yields tokens from a PyTorch model incrementally.

    model.generate is a blocking call, so it runs in a separate thread
    and tokens are streamed via TextIteratorStreamer.
    """
    tokenizer, model = _load()
    inputs = _build_inputs(tokenizer, messages).to(model.device)
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
