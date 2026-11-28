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
  * Preserves Step 0 (initial user goal and metadata) and the last 15 turns (tail context) for seamless resumption.
  * Losslessly compresses full original trajectories into gzip archives (`/home/ubuntu/ops/antigravity/archive_transcripts/<cid>/transcript.jsonl.gz`).
  * **Verified Live Impact**: Compacted 333 bloated sessions, successfully preventing **4,600,642,799 tokens (4.6 Billion tokens)** of dragging context reload and dropping live context footprint by **94.3%** (from 5,063M to 287M tokens).

### 2. Multi-Account Governance: 2 Lean Daemons vs. 4 Physical Instances
When scaling across 4 or more lifetime accounts, running 4 separate long-running daemon processes creates resource overhead (~2.5GB RAM). The enterprise architecture decouples account identities from daemon processes:
* **Current Operational Topology**:
  * **Primary Instance (`antigravity-cli-daemon.service`)**: Dedicated to `aamir1nesma@gmail.com` under `/home/ubuntu`.
  * **Secondary Instance (`agy-argon.service`)**: Dedicated to `amer231105@gmail.com` under `/home/ubuntu/agy-argon-home`.
* **Dynamic Pool Failover Architecture**:
  * Instead of running 4 memory-heavy daemons, the system utilizes a **2-Daemon Dynamic Token Pool**.
  * When an account nears rolling quota saturation, the automated recycler hot-swaps the OAuth seed token to an alternate pool account in <2 seconds with 0 extra memory allocation.
  * This provides 4-account (or N-account) continuous throughput while strictly keeping subprocess memory under 150MB per task.

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
# 1. Run live autonomous transcript compaction
python3 scripts/agy_transcript_compactor.py --live

# 2. Execute on-demand quota recycling and compaction
bash scripts/agy_daily_quota_recycle.sh

# 3. Run self-healing infrastructure health sentinel
./sentinel.sh

# 4. Inspect RTK token compression telemetry
rtk gain
```

---

## 📂 Repository Structure

```
.
├── README.md                      # Architecture blueprint & operational manual
├── sentinel.sh                    # Host self-healing & daemon audit script
└── scripts/
    ├── agy_transcript_compactor.py # O(N²) transcript compactor & archiver
    ├── agy_quota_recycler.py       # 12-hour automated instance recycler
    └── agy_daily_quota_recycle.sh  # Instant on-demand recycling script
```

---

## 📜 Repository Management
Maintained by the **Invertio Engineering Team** under unified infrastructure automation.

---

Part of [my always-on agent stack](https://github.com/Amz34) · [Awesome Agent Infrastructure](https://github.com/Amz34/awesome-agent-infrastructure) (135 live-checked building blocks).
