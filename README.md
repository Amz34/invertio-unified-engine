# Invertio Unified AGY Gemini Enterprise Engine 🚀
> Centralized High-Throughput Token Compression, O(N²) Context Quota Defense, and Resilient Multi-Account Orchestration for Google Antigravity (AGY), Telegram Infra, and Multi-Agent Environments.

## 📌 Vision & Architecture
This repository provides the persistent enterprise orchestration and optimization layer unifying **Google Antigravity (AGY) Gemini**, **Invertio-Hub**, and **Telegram Infrastructure**. 

Engineered with zero-drift principles, this strategy automatically activates across all local agent harnesses, remote execution workers, and multi-account workspaces (`aamir1nesma@gmail.com` and `amer231105@gmail.com`) without requiring prompt-level trigger keywords.

---

## ⚡ Core Architecture Pillars

### 1. Autonomous Transcript Compaction & O(N²) Quota Defense Engine
* **The Mathematical Root Cause**: In conversational AI architectures, every turn re-transmits cumulative session history to the LLM context. Left unchecked, a session running for $N$ turns accumulates context quadratically:
  $$\text{Cumulative Volume} \approx \frac{1}{2} N^2 S$$
* **Ground-Truth Breakthrough**: Telemetry revealed single monolithic sessions running 1,000 to 4,294 turns consumed upwards of **559 Million tokens** in a single thread, exhausting weekly limits within 48 hours.
* **Autonomous Compactor (`agy_transcript_compactor.py`)**:
  * Automatically detects sessions exceeding 40 turns.
  * **Semantic Memory Graph Manifest**: Analyzes the pruned turns before archival, extracting locked architectural decisions, active modified files, and user objectives into a compact structured `semantic_state_manifest.json` injected directly into Turn 1.
  * Preserves Step 0 (initial user goal and metadata) and the last 15 turns (tail context) for seamless resumption with 0 context amnesia.
  * Losslessly compresses full original trajectories into gzip archives (`/home/ubuntu/ops/antigravity/archive_transcripts/<cid>/transcript.jsonl.gz`).
  * **Verified Live Impact**: Compacted 334 bloated sessions, successfully preventing **4,600,642,799 tokens (4.6 Billion tokens)** of dragging context reload and dropping live context footprint by **94.3%** (from 5,063M to 287M tokens).

### 2. Multi-Account Hot-Swap Mesh (`agy_account_mesh.py`)
When scaling across 4 or more lifetime accounts, running 4 separate long-running daemon processes creates resource overhead (~2.5GB RAM). The enterprise architecture decouples account identities from daemon processes:
* **Operational Topology**:
  * **Primary Instance (`antigravity-cli-daemon.service`)**: Dedicated to `aamir1nesma@gmail.com` under `/home/ubuntu`.
  * **Secondary Instance (`agy-argon.service`)**: Dedicated to `amer231105@gmail.com` under `/home/ubuntu/agy-argon-home`.
  * **Extensible Slots (Slot 3 & 4)**: Standby token seeds dynamically mounted upon quota exhaustion.
* **Proactive Rate-Limit & Quota Detection**:
  * Monitored via `agy_account_mesh.py check`.
  * If HTTP 429 or `ResourceExhausted` signals are detected in journal logs, the mesh proactively hot-swaps active tokens and cycles the daemon in <3 seconds without session loss.

### 3. agy-shield Standalone CLI Suite (`packages/agy-shield`)
The context compaction and quota defense engine is packaged as a standalone zero-dependency CLI utility:
* `agy-shield compact`: Compresses transcripts with semantic state manifest extraction.
* `agy-shield watch`: Continuous background sentinel monitoring agent workspaces.
* `agy-shield stats`: Real-time fleet compaction metrics and archive storage footprint.
* `agy-shield benchmark`: Mathematical $O(N^2)$ simulation comparing unbounded trajectories vs 30-turn caps.
* `agy-shield mesh`: Hot-swap manager and health inspector for multi-account pools.

### 3. Programmatic Code Mode & 0-Token Local Execution Mesh
* **Caveman Proxy & RTK Rust Optimizer**: Terminal commands and file lookups pass through RTK, achieving an **82.2% reduction in shell verbosity** (29.1M+ tokens saved globally).
* **Local 0-Token Engines**: Heavy analytical queries, web scraping, and vector searches are offloaded to host processes without passing raw data through model context:
  * **DuckDB**: Sub-second analytical SQL on local databases.
  * **Lightpanda (Zig Runtime)**: Fast DOM extraction and HTML parsing (<100ms startup).
  * **Local ONNX MiniLM / Qdrant**: Local embedding generation and semantic indexing.

### 4. 12-Hour Automated Instance Recycler & Quota Renewal
* **Scheduled Recycler (`agy_quota_recycler.py`)**: Runs twice daily (00:05 UTC & 12:05 UTC):
  1. Executes autonomous transcript compaction across all completed sessions.
  2. Synchronizes backup OAuth tokens for both active lanes.
  3. Gracefully cycles systemd user daemons with Vertex AI detached ($0 cloud billing).
  4. Flushes stale in-memory singleflight locks and triggers fresh quota reloads.
  5. Dispatches execution telemetry to Telegram (`@AzGem_Bot`).

---

## 🛠️ Operational CLI Commands

```bash
# 1. Run live autonomous transcript compaction with Semantic Memory Graph
python3 scripts/agy_transcript_compactor.py --live

# 2. agy-shield Standalone CLI commands
agy-shield benchmark                 # Run O(N²) trajectory simulation
agy-shield stats                     # Inspect fleet token savings & storage
agy-shield watch --interval 300      # Launch continuous context sentinel
agy-shield compact --live            # One-shot compaction across all workspaces

# 3. Multi-Account Hot-Swap Mesh
python3 scripts/agy_account_mesh.py status   # Inspect account pool & daemon health
python3 scripts/agy_account_mesh.py check    # Proactive rate-limit check & auto-swap
python3 scripts/agy_account_mesh.py swap     # Manual zero-latency hot swap

# 4. Execute on-demand quota recycling and compaction
bash scripts/agy_daily_quota_recycle.sh

# 5. Run self-healing infrastructure health sentinel
./sentinel.sh

# 6. Inspect RTK token compression telemetry
rtk gain
```

---

## 📂 Repository Structure

```
.
├── README.md                      # Architecture blueprint & operational manual
├── sentinel.sh                    # Host self-healing & daemon audit script
├── packages/
│   └── agy-shield/                # Standalone zero-dependency Python CLI package
│       ├── pyproject.toml
│       ├── setup.py
│       └── agy_shield/
│           ├── __init__.py
│           └── cli.py             # CLI entrypoint (compact, watch, stats, benchmark)
└── scripts/
    ├── agy_transcript_compactor.py # O(N²) semantic compactor & archiver
    ├── agy_account_mesh.py         # Multi-account dynamic hot-swap mesh
    ├── agy_quota_recycler.py       # 12-hour automated instance recycler
    └── agy_daily_quota_recycle.sh  # Instant on-demand recycling script
```

---

## 📜 Repository Management
Maintained by the **Invertio Engineering Team** under unified infrastructure automation.

---

Part of [my always-on agent stack](https://github.com/Amz34) · [Awesome Agent Infrastructure](https://github.com/Amz34/awesome-agent-infrastructure) (135 live-checked building blocks).
