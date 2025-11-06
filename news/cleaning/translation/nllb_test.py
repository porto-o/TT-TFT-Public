import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_ID = "facebook/nllb-200-distilled-600M"

# Detectar GPUs
n_gpus = torch.cuda.device_count()
print("GPUs disponibles:", n_gpus)

# Configurar device_map y max_memory para sharding
device_map = "auto" if n_gpus > 1 else None
max_memory = None
if n_gpus > 1:
    total_gb = int(torch.cuda.get_device_properties(0).total_memory / 1024**3)
    headroom = 2
    per_gpu = max(1, total_gb - headroom)
    max_memory = {i: f"{per_gpu}GiB" for i in range(n_gpus)}
    print("Usando sharding con device_map=auto y max_memory:", max_memory)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_ID,
    torch_dtype="auto",
    attn_implementation="sdpa",
    device_map=device_map,
    max_memory=max_memory
)

primary_device = "cuda:0" if n_gpus > 0 else "cpu"
if device_map is None:
    model = model.to(primary_device)

model.eval()

sentences = [
    "UN Chief says there is no military solution in Syria",
] * 100000

target_lang = "fra_Latn"
forced_id = tokenizer.convert_tokens_to_ids(target_lang)

batch_size = 220
translated = []

with torch.inference_mode():
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]
        inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True).to(primary_device)
        out_tokens = model.generate(
            **inputs,
            forced_bos_token_id=forced_id,
            max_length=40,
            do_sample=False,   
            num_beams=1
        )
        translated.extend(tokenizer.batch_decode(out_tokens, skip_special_tokens=True))

for i, t in enumerate(translated[:5]):
    print(f"{i+1}: {t}")
print(f"Total traducidas: {len(translated)}")

