import sys
import time
import timeit

SHIM = sys.argv[1] if len(sys.argv) > 1 else ""

if SHIM:
    sys.path.insert(0, "/home/jp/repos/transformers-salix/src")
    from transformers._salix_shim import install

    install()

t0 = time.perf_counter()
import transformers  # noqa: E402

t_import = time.perf_counter() - t0
from transformers import BertConfig, GPT2Config, T5Config  # noqa: E402

print(f"import transformers: {t_import:.2f} s")
print(f"BertConfig() x500:  {timeit.timeit(BertConfig, number=500):.2f} s")
print(f"GPT2Config() x500:  {timeit.timeit(GPT2Config, number=500):.2f} s")
print(f"T5Config() x500:    {timeit.timeit(T5Config, number=500):.2f} s")
