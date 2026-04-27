# Frameworks & Libraries Reference

Deep-dive reference for the AI Principal Engineer skill.
Read this file when detailed API guidance, version-specific behavior, or integration patterns are needed.

---

## 1. Orchestration & Agentic Frameworks

### FastLangGraph (Rust-accelerated)

**When to use**: LangGraph dispatch overhead is the measured bottleneck (profiled, not guessed).

**Architecture**: Rust graph scheduler (via PyO3) calling Python node functions. The scheduling,
state merging, and conditional-edge evaluation happen in Rust; only the node bodies run in Python.

**Integration pattern (maturin-based)**:

```toml
# Cargo.toml
[package]
name = "fast-langgraph"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.21", features = ["extension-module"] }
petgraph = "0.6"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

```rust
use pyo3::prelude::*;
use petgraph::graph::DiGraph;

#[pyclass]
struct FastGraph {
    graph: DiGraph<String, String>,
}

#[pymethods]
impl FastGraph {
    #[new]
    fn new() -> Self {
        FastGraph { graph: DiGraph::new() }
    }

    fn add_node(&mut self, name: String) -> usize {
        self.graph.add_node(name).index()
    }

    fn add_edge(&mut self, from: usize, to: usize, condition: String) {
        self.graph.add_edge(from.into(), to.into(), condition);
    }

    fn execute(&self, py: Python, state: PyObject, nodes: &PyDict) -> PyResult<PyObject> {
        // Rust-native topological traversal, calling Python node fns
        // via nodes.get_item(name)?.call1((state,))?
        todo!("implement graph execution")
    }
}
```

**Build and distribute**:

```bash
pip install maturin
maturin develop --release    # dev install
maturin build --release      # produces wheel in target/wheels/
```

**Decision criteria**: Only move to FastLangGraph when profiling shows >15% of wall-clock time in
graph dispatch (not node execution). If nodes are 95%+ of runtime (typical for LLM calls), Rust
dispatch saves nothing — that is anti-ROI engineering.

---

### LangGraph (≥ 0.2)

**When to use**: Stateful, multi-step AI pipelines with conditional routing, human-in-the-loop, or checkpointing.

**Core concepts**:
- `StateGraph` — define nodes (functions) and edges (routing logic) over a shared `TypedDict` state.
- `Checkpointer` — persist state between invocations (Postgres, SQLite, Redis).
- `Subgraph` — compose reusable pipeline fragments.
- `Command` — programmatic state updates + routing from within nodes.

**Patterns**:

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

builder = StateGraph(MyState)
builder.add_node("classify", classify_node)
builder.add_node("analyze", analyze_node)
builder.add_node("respond", respond_node)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", routing_fn, {
    "defect": "analyze",
    "feature": "respond",
})
builder.add_edge("analyze", "respond")
builder.add_edge("respond", END)

checkpointer = PostgresSaver.from_conn_string(DB_URL)
graph = builder.compile(checkpointer=checkpointer)

result = graph.invoke({"query": "GPU hang on MI300X"}, config={"configurable": {"thread_id": "t1"}})
```

**State reducers** for accumulating fields:

```python
from typing import Annotated
from operator import add

class State(TypedDict):
    messages: Annotated[list[str], add]  # appends rather than replaces
    final: str | None
```

**Human-in-the-loop**:

```python
builder.add_node("human_review", human_review_node)
graph = builder.compile(checkpointer=checkpointer, interrupt_before=["human_review"])
```

---

### SGLang (≥ 0.3)

**When to use**: High-throughput LLM inference/serving with prefix caching, constrained decoding, or batch-parallel generation.

**Architecture**: RadixAttention server + Python frontend DSL.

**Server launch**:

```bash
python -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-70B-Instruct \
    --tp 8 --dtype bfloat16 --port 30000
```

**Frontend patterns**:

```python
import sglang as sgl

@sgl.function
def triage_pipeline(s, ticket: str):
    s += sgl.system("You are a defect triage engine.")
    s += sgl.user(f"Triage: {ticket}")
    s += sgl.assistant(sgl.gen("classification", max_tokens=128, temperature=0.1))

    # Constrained decoding (regex)
    s += sgl.assistant(sgl.gen("severity", regex=r"(critical|high|medium|low)"))

    # Parallel fork
    forks = s.fork(3)
    for i, f in enumerate(forks):
        f += sgl.user(f"Perspective {i}: elaborate.")
        f += sgl.assistant(sgl.gen(f"detail_{i}", max_tokens=256))
    s += sgl.assistant(sgl.gen("summary", max_tokens=512))
```

**Key advantages over vLLM**: RadixAttention prefix sharing, native constrained decoding, fork-join parallelism, compiled frontend.

---

### LangChain (≥ 0.3) / LangChain-Core

**When to use**: RAG pipelines, tool-calling agents, model-agnostic LLM wrappers.

**LCEL (LangChain Expression Language)**:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the defect: {format_instructions}"),
    ("human", "{query}"),
])

parser = PydanticOutputParser(pydantic_object=TriageResult)
chain = prompt | ChatOpenAI(model="gpt-4o", temperature=0.1) | parser
result = chain.invoke({"query": ticket_text, "format_instructions": parser.get_format_instructions()})
```

**Prefer LangChain-Core** for primitives (prompts, parsers, runnables). Use full LangChain only when you need integrations (vector stores, document loaders).

---

## 2. ML Frameworks

### PyTorch (≥ 2.0)

**Key patterns**:

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

# Explicit device, dtype, reproducibility
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.manual_seed(42)

model = MyModel().to(device, dtype=torch.bfloat16)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

# torch.compile for 2x speedup (PyTorch 2.0+)
model = torch.compile(model, mode="reduce-overhead")

# Training loop
model.train()
for batch in dataloader:
    batch = {k: v.to(device) for k, v in batch.items()}
    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        loss = model(**batch).loss
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()
    scheduler.step()
    optimizer.zero_grad(set_to_none=True)  # more memory-efficient

# Inference
model.eval()
with torch.no_grad():
    outputs = model(**inputs)
```

**Distributed (DDP)**:

```python
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

dist.init_process_group("nccl")  # or "rccl" on AMD
local_rank = int(os.environ["LOCAL_RANK"])
model = DDP(model.to(local_rank), device_ids=[local_rank])
```

**FSDP (Fully Sharded Data Parallel)**:

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP, MixedPrecision

mp_policy = MixedPrecision(param_dtype=torch.bfloat16, reduce_dtype=torch.float32)
model = FSDP(model, mixed_precision=mp_policy, auto_wrap_policy=size_based_auto_wrap_policy)
```

---

### NumPy / pandas / scikit-learn

| Library | Primary Use | Key Patterns |
|---------|-------------|--------------|
| **NumPy** | Array ops, linear algebra | `np.einsum`, `np.linalg.svd`, broadcasting, structured arrays |
| **pandas** | Tabular data, EDA | `.groupby().agg()`, `.pipe()` chains, categorical dtypes for memory |
| **scikit-learn** | Classical ML, preprocessing | `Pipeline` + `ColumnTransformer`, `TfidfVectorizer`, `KMeans` |

---

## 3. Vector Databases

| DB | Best For | Integration |
|----|----------|-------------|
| **FAISS** | Local/embedded, exact & approximate NN | `langchain_community.vectorstores.FAISS` |
| **Chroma** | Local dev, simple API | `langchain_chroma.Chroma` |
| **Milvus** | Production, billion-scale | `langchain_milvus.Milvus` |
| **Pinecone** | Managed cloud, serverless | `langchain_pinecone.PineconeVectorStore` |
| **Weaviate** | Hybrid search (vector + BM25) | `langchain_weaviate.WeaviateVectorStore` |

**Embedding selection**:

| Model | Dims | Speed | Quality | Notes |
|-------|------|-------|---------|-------|
| `text-embedding-3-large` | 3072 | Medium | High | OpenAI, supports dimensionality reduction |
| `text-embedding-3-small` | 1536 | Fast | Good | Cost-effective for most retrieval |
| `all-MiniLM-L6-v2` | 384 | Very fast | Good | Local, sentence-transformers |
| `nomic-embed-text-v1.5` | 768 | Fast | High | Local, Matryoshka dims |

---

## 4. Parallel Programming

### CUDA / HIP Comparison

| CUDA | HIP (ROCm) | Notes |
|------|-----------|-------|
| `cudaMalloc` | `hipMalloc` | 1:1 API mapping |
| `cudaMemcpy` | `hipMemcpy` | Same semantics |
| `__syncthreads()` | `__syncthreads()` | Identical |
| `cudaStream_t` | `hipStream_t` | Same stream model |
| `nvcc` | `hipcc` | Compiler driver |
| `cuBLAS` | `rocBLAS` | GEMM primitives |
| `cuDNN` | `MIOpen` | Conv/RNN/attention |
| `NCCL` | `RCCL` | Collective comms |
| Warp (32 threads) | Wavefront (64 threads) | Critical for occupancy calcs |
| `__shfl_sync` | `__shfl` | Warp shuffle |

**HIP portability**: Use `hipify-perl` to convert CUDA → HIP. Most kernels port with zero logic changes.

### MPI Patterns

```python
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Scatter data
if rank == 0:
    data = np.array_split(full_data, size)
else:
    data = None
local_data = comm.scatter(data, root=0)

# Process locally
result = process(local_data)

# Gather results
all_results = comm.gather(result, root=0)

# Allreduce for gradient sync (common in distributed training)
local_grad = compute_gradient()
global_grad = np.zeros_like(local_grad)
comm.Allreduce(local_grad, global_grad, op=MPI.SUM)
```

### OpenMP (via Cython/C extensions)

```c
#pragma omp parallel for reduction(+:total) schedule(dynamic)
for (int i = 0; i < N; i++) {
    total += compute(data[i]);
}
```

In Python, prefer `multiprocessing` or `concurrent.futures.ProcessPoolExecutor` for CPU parallelism. OpenMP is relevant when writing C/C++ extensions or HIP host code.

### asyncio Patterns

```python
import asyncio
import aiohttp

async def fetch_issues(session: aiohttp.ClientSession, urls: list[str]) -> list[dict]:
    async def _fetch(url: str) -> dict:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()

    return await asyncio.gather(*[_fetch(u) for u in urls])

async def main():
    async with aiohttp.ClientSession(headers={"Authorization": f"Bearer {TOKEN}"}) as session:
        results = await fetch_issues(session, issue_urls)
```

**Rules**:
- `asyncio` for I/O-bound concurrency (HTTP, DB, file I/O).
- Never mix blocking calls in async context — use `asyncio.to_thread()` for blocking libs.
- Use `asyncio.Semaphore` for rate limiting API calls.

---

## 5. Profiling & Checkpointing

### PyTorch Profiler

```python
from torch.profiler import profile, ProfilerActivity, tensorboard_trace_handler

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
    on_trace_ready=tensorboard_trace_handler("./log"),
    record_shapes=True,
    profile_memory=True,
    with_stack=True,
) as prof:
    for step, batch in enumerate(dataloader):
        train_step(model, batch)
        prof.step()
```

### Model Checkpointing

```python
# Save
checkpoint = {
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "scheduler_state_dict": scheduler.state_dict(),
    "best_metric": best_metric,
    "config": config.dict(),
}
torch.save(checkpoint, f"checkpoints/epoch_{epoch}.pt")

# Load
checkpoint = torch.load("checkpoints/best.pt", map_location=device, weights_only=True)
model.load_state_dict(checkpoint["model_state_dict"])
```

**DeepSpeed checkpointing**:

```python
model_engine.save_checkpoint("checkpoints/", tag=f"step_{global_step}")
model_engine.load_checkpoint("checkpoints/", tag="latest")
```

### ONNX Export

```python
dummy_input = torch.randn(1, 3, 224, 224, device=device)
torch.onnx.export(
    model, dummy_input, "model.onnx",
    input_names=["input"], output_names=["output"],
    dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
    opset_version=17,
)
```

---

## 6. Python Packaging & Distribution

### pyproject.toml (PEP 621 — the only acceptable format)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "prysm"
version = "0.1.0"
description = "Prysm -- Intelligent navigator Platform"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [{ name = "Your Name", email = "you@amd.com" }]
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Framework :: AsyncIO",
    "Typing :: Typed",
]
dependencies = [
    "langgraph>=0.2",
    "langchain-core>=0.3",
    "pydantic>=2.0",
    "aiohttp>=3.9",
    "structlog>=24.0",
]

[project.scripts]
prysm = "prysm.cli:main"

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-asyncio>=0.23",
    "ruff>=0.4",
    "mypy>=1.10",
    "build>=1.0",
]
gpu = [
    "torch>=2.2",
    "accelerate>=0.28",
]

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "W", "F", "I", "N", "D", "UP", "ANN", "S", "B"]

[tool.ruff.pydocstyle]
convention = "google"

[tool.mypy]
strict = true
python_version = "3.11"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### Build commands

```bash
# Build wheel + sdist
python -m build

# Verify wheel contents
unzip -l dist/prysm-0.1.0-py3-none-any.whl

# Install in clean venv and verify
python -m venv /tmp/test-venv
source /tmp/test-venv/bin/activate
pip install dist/prysm-0.1.0-py3-none-any.whl
prysm --help
python -c "import prysm; print(prysm.__version__)"
```

### Rust extension wheels (maturin)

For Rust-accelerated components (e.g., FastLangGraph):

```bash
pip install maturin
maturin build --release --strip     # platform-specific wheel
maturin develop --release           # editable install for dev
```

Produces platform-tagged wheels: `prysm_core-0.1.0-cp311-cp311-manylinux_2_34_x86_64.whl`.

### Package structure for typed library

```
src/
├── prysm/
│   ├── __init__.py          # __version__, public API
│   ├── __main__.py          # python -m prysm
│   ├── py.typed             # PEP 561 marker (empty file)
│   ├── cli.py               # entry point for `prysm` console script
│   ├── config.py            # pydantic BaseSettings
│   └── ...
```

**Non-negotiables:**
- `py.typed` present for all typed packages.
- `src/` layout (not flat) to prevent import-before-install bugs.
- `__version__` in `__init__.py` matching `pyproject.toml` (use `importlib.metadata`).
- All deps pinned to minimum version (`>=`), never exact (`==`) unless justified.
