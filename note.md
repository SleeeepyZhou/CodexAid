```bash
.\llama\llama-cli.exe -m .\models\Qwen3-30B-A3B-Q4_K_M.gguf -ngl 999 --flash-attn --split-mode layer --tensor-split 0,1 --main-gpu 1 --no-mmap
```

```bash
.\llama\llama-embedding.exe -m .\models\all-MiniLM-L6-v2-Q8_0.gguf -ngl 999 --flash-attn --split-mode layer --tensor-split 0,1 --main-gpu 1 --no-mmap
```

.\llama\llama-server.exe -m .\models\all-MiniLM-L6-v2-Q8_0.gguf -ngl 999 --flash-attn --split-mode layer --tensor-split 0,1 --main-gpu 1 --no-mmap --port 9527

```bash
.\llama\llama-server.exe -m .\models\Qwen3-30B-A3B-Q4_K_M.gguf -ngl 999 --flash-attn --split-mode layer --tensor-split 0,1 --main-gpu 1 --no-mmap --port 9527
```

在使用 llama.cpp 时，即使将大部分层（layers）通过 `-ngl` 和 `--tensor-split` 参数卸载到 GPU，模型的权重仍然会以记忆映射（mmap）或完整加载的形式驻留在主机内存中。这意味着：

- **模型权重常驻主机内存**：默认情况下，llama.cpp 会将模型文件通过 mmap 映射到进程地址空间，或者在使用 `--no-mmap` 时完整加载到 RAM 中，故模型大小（包括量化后）仍会占用等同大小的主机内存 ([Understanding memory usage · ggml-org llama.cpp - GitHub](https://github.com/ggml-org/llama.cpp/discussions/1876?utm_source=chatgpt.com))。  
- **未卸载层的权重在 CPU 上**：当 `-ngl` （`--n-gpu-layers`） 设置小于模型总层数时，剩余层会在 CPU 上运行，占用对应的 RAM；若将 `-ngl` 设置为模型总层数，RAM 使用可显著下降，但需足够的 GPU 显存 ([Questions related to llama.cpp options #3111 - GitHub](https://github.com/ggml-org/llama.cpp/discussions/3111?utm_source=chatgpt.com), [Questions related to llama.cpp options #3111 - GitHub](https://github.com/ggml-org/llama.cpp/discussions/3111?utm_source=chatgpt.com))。  
- **小张量和中间结果仍驻留主 GPU**：使用 `--split-mode layer` 时，除大型矩阵权重外的小张量（如 KV 缓存、偏置等）仍会常驻 `--main-gpu`，继续消耗部分 GPU 或主机内存 ([API Reference - llama-cpp-python](https://llama-cpp-python.readthedocs.io/en/latest/api-reference/?utm_source=chatgpt.com))。  
- **OS 会进行分页和缓存**：在内存紧张时，操作系统会将 mmap 的未访问页置于磁盘交换（swap）或延迟加载，但这会带来性能波动和潜在的分页开销 ([Understanding memory usage · ggml-org llama.cpp - GitHub](https://github.com/ggml-org/llama.cpp/discussions/1876?utm_source=chatgpt.com))。

因此，高内存占用既是设计使然，也是性能优化（mmap、mlock）的副作用——在不牺牲速度的前提下，llama.cpp 尽量避免多次磁盘 I/O。

## 内存占用对其他软件的影响

### 可能出现的资源争用  
- 当系统 RAM 被 llama.cpp 占满时，其他进程（如浏览器、IDE、数据库等）可用内存减少，若内存不足，系统会触发分页或 OOM 杀手，导致其他应用响应变慢或崩溃 ([Understanding memory usage · ggml-org llama.cpp - GitHub](https://github.com/ggml-org/llama.cpp/discussions/1876?utm_source=chatgpt.com))。  
- 在 Windows 平台，若 GPU VRAM 不足且开启了 “共享 GPU 内存” 功能，部分 GPU 请求会使用系统内存作为虚拟显存，会进一步加重 RAM 负担 ([llama.cpp: CPU vs GPU, shared VRAM and Inference Speed](https://dev.to/maximsaplin/llamacpp-cpu-vs-gpu-shared-vram-and-inference-speed-3jpl?utm_source=chatgpt.com))。

### 操作系统的缓解机制  
- **分页 / 交换（swap）**：操作系统会将长时间未访问的内存页置于磁盘，但会显著降低访问速度。  
- **内存回收**：释放 mmap 映射可以通过退出进程或在编译时禁用 mlock（`--mlock` 默认关闭），让 OS 更灵活地回收内存。  
- **内存监控**：建议使用系统监控工具（如 `htop`、Resource Monitor）实时观察内存使用，避免触发 OOM。

## 降低内存占用的优化方法

### 精确控制 GPU 卸载  
1. **将 `-ngl` 设置为模型层数**：若您的 GPU 显存足够（>模型量化后大小），可将 `-ngl` 设为总层数，**全部层**卸载到 GPU，从而大幅降低主机 RAM 占用 ([Questions related to llama.cpp options #3111 - GitHub](https://github.com/ggml-org/llama.cpp/discussions/3111?utm_source=chatgpt.com))。  
2. **调整 `--tensor-split`**：使用类似 `--tensor-split 1,0`（第一张 GPU 完全承担）或根据多卡显存按比例分配，以让更大比例的张量驻留在 GPU 而非 CPU ([Fine grained control of GPU offloading · ggml-org llama.cpp - GitHub](https://github.com/ggerganov/llama.cpp/discussions/7678?utm_source=chatgpt.com))。

### 利用 mmap 和 mlock 特性  
- **保留 mmap**（默认）：仅在访问时加载页，避免一次性占用全部 RAM，但需留意分页延迟。  
- **禁用 mmap**：使用 `--no-mmap` 参数可让 llama.cpp 在启动时一次性加载模型到 RAM，这在极度内存紧张但需保持稳定访问时有帮助；但若模型超出 RAM，总会加载失败 ([Understanding memory usage · ggml-org llama.cpp - GitHub](https://github.com/ggml-org/llama.cpp/discussions/1876?utm_source=chatgpt.com))。  
- **避免 mlock**：默认 `--mlock=false`，不将页锁定在内存中，可让 OS 回收不常访问的数据，适用于多应用同机场景。

### 量化与模型切分  
- 采用更低比特的量化方案（如 `Q4_K_M`、`Q5_K_M` 等）可以显著降低权重大小，从而减少 RAM + VRAM 双方压力 ([How is LLaMa.cpp possible? - Finbarr Timbers](https://finbarr.ca/how-is-llama-cpp-possible/?utm_source=chatgpt.com))。  
- 对大型模型执行 GGUF 分片（`gguf-split`），并利用 llama.cpp 的多文件加载支持，让 OS 以更小的页组分块映射，或更精细地按需加载 ([PR #6187 llama_model_loader: support multiple split/shard GGUFs](https://app.semanticdiff.com/gh/ggerganov/llama.cpp/pull/6187/overview?utm_source=chatgpt.com))。

### 增加系统资源或调整使用场景  
- **添加物理内存**：最直接的提升方式，尤其在多模型、多会话并行时。  
- **配置交换分区（swap）**：在内存耗尽时提供缓冲，但影响严重。  
- **专用推理服务器**：将 llama.cpp 部署到独立主机，避免与其他重内存应用共用，或使用容器化（Docker／Kubernetes）对资源进行限制。

---

通过上述方法，可以在保证 llama.cpp 性能的前提下，尽可能将内存占用和其对其他软件的影响降到最低。若仍有内存瓶颈，建议结合实际硬件条件，调整卸载策略或扩充物理内存。