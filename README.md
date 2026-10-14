# LeanProofAgent

**基于大语言模型与 Lean 4 形式化验证的自动定理证明 Agent**

LeanProofAgent 是一个正在开发中的 AI4Math 项目，旨在探索大语言模型（LLM）与形式化证明系统 Lean 4 的结合，实现数学定理的自动证明、验证与迭代修复。

项目目前使用 DeepSeek 作为证明生成模型，以 Lean 4 和 Mathlib 作为形式化验证环境，构建了初步的 **Generate–Verify–Repair（生成–验证–修复）** 闭环。

## 1. 项目背景

大语言模型具备一定的数学推理与代码生成能力，但其生成的数学证明可能存在逻辑错误、遗漏条件或形式化表达不正确等问题。

Lean 4 是一种交互式定理证明语言，能够通过严格的类型检查验证形式化证明的正确性。

本项目尝试结合两者的优势：

- **LLM**：负责探索证明思路、生成 Lean 证明代码。
- **Lean 4**：负责检查生成的证明是否满足形式化要求。
- **Repair Agent**：根据 Lean 返回的错误信息，尝试修复失败的证明。

项目的基本思想是：利用形式化验证产生的反馈，引导大语言模型改进证明，从而提高自动定理证明的成功率。

## 2. 系统架构

```text
             输入 Lean 定理
                   |
                   v
            LLM Proof Generator
                   |
                   v
              生成 Proof
                   |
                   v
              Lean Verifier
                   |
             +-----+-----+
             |           |
           Success     Failure
             |           |
             v           v
         输出证明     Lean Error
                         |
                         v
                   LLM Repair
                         |
                         v
                     新 Proof
                         |
                         +----> Lean Verifier
```

系统首先将待证明的 Lean 定理发送给大语言模型，生成候选证明。随后通过 Python 调用 Lean 编译器进行验证。

如果验证失败，系统会提取 Lean 返回的错误信息，并将错误信息与原证明一起提供给模型进行修复。

该过程会在预设的最大尝试次数内重复执行，直到证明通过验证或达到尝试次数上限。

## 3. 已实现功能

### 3.1 LLM 证明生成

通过 DeepSeek API，根据输入的 Lean 定理生成候选证明。

支持：

- 使用系统提示词约束证明输出格式。
- 指定可用的 Lean 和 Mathlib 导入模块。
- 提取模型输出的 Lean 证明代码。
- 对初始生成结果进行基本格式检查。

### 3.2 Lean 形式化验证

通过 Python 的 `subprocess` 模块调用 Lean 编译器。

主要功能包括：

- 将定理与候选证明组合成完整的 Lean 代码。
- 在项目环境中运行 Lean 验证。
- 获取验证结果及编译器输出。
- 解析错误位置与错误信息。
- 设置验证超时时间。
- 删除验证过程中生成的临时文件。

### 3.3 基于编译器反馈的证明修复

当 Lean 验证失败时，将以下内容发送给大语言模型：

- 原始定理
- 上一次生成的证明
- Lean 编译器错误信息

模型根据反馈重新生成证明，并再次提交 Lean 验证。

目前支持设置最大证明尝试次数，形成基础的迭代修复机制。

## 4. 项目结构

```text
LeanProofAgent/
├── LeanProofAgent/       # Lean 库源文件
├── LeanProofAgent.lean   # Lean 库入口
├── Main.lean             # Lean 示例文件
│
├── generator.py          # LLM 证明生成与修复
├── verifier.py           # Lean 验证及错误解析
├── main.py               # Agent 主流程
├── test_api.py           # API 连接测试
│
├── lakefile.toml         # Lean 项目配置
├── lake-manifest.json    # Lake 依赖清单
├── lean-toolchain        # Lean 工具链版本
├── requirements.txt      # Python 依赖
├── .env.example          # 环境变量示例
└── README.md             # 项目说明
```

核心模块：

| 模块 | 功能 |
|---|---|
| `generator.py` | 生成 Lean 证明，并根据错误反馈修复证明 |
| `verifier.py` | 调用 Lean 编译器验证证明，解析错误信息 |
| `main.py` | 组织生成、验证与修复的迭代流程 |

## 5. 环境配置

### 5.1 环境要求

当前项目主要在 Windows 11 环境下开发和测试。

推荐环境：

- Python 3.11
- Lean 4
- Lake
- Mathlib
- DeepSeek API Key

Lean 和 Mathlib 的具体版本由项目中的 `lean-toolchain`、`lakefile.toml` 和 `lake-manifest.json` 管理。

### 5.2 克隆项目

```powershell
git clone https://github.com/shangzhijian285-bit/LeanProofAgent.git
cd LeanProofAgent
```

### 5.3 配置 Python 环境

创建并激活虚拟环境：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装 Python 依赖：

```powershell
python -m pip install -r requirements.txt
```

### 5.4 配置 Lean 环境

需要预先安装 [Lean 4 / elan](https://lean-lang.org/)。

在项目根目录执行：

```powershell
lake update
lake exe cache get
```

然后可以通过以下命令构建 Lean 项目：

```powershell
lake build
```

首次运行可能需要下载工具链和 Mathlib 相关依赖。

### 5.5 配置 DeepSeek API

复制环境变量示例文件：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`：

```dotenv
DEEPSEEK_API_KEY=your_api_key_here
LLM_MODEL=deepseek-flash
```

请将 `your_api_key_here` 替换为自己的 API Key。

**注意：不要将包含真实 API Key 的 `.env` 文件提交到公开仓库。**

## 6. 运行项目

当前版本通过编辑 `main.py` 中的定理来指定证明任务。

在项目根目录运行：

```powershell
lake env python main.py
```

该命令在 Lake 配置的 Lean 环境下运行 Python Agent，使其能够调用对应的 Lean 编译器。

程序会输出每次尝试生成的证明及相应的验证结果。

## 7. 证明示例

考虑以下数学问题：

已知实数 \(x\) 满足

\[
x^4-10x^2+9=0,
\]

证明

\[
x\in\{-3,-1,1,3\}.
\]

对应的 Lean 定理为：

```lean
example (x : ℝ)
    (h : x^4 - 10*x^2 + 9 = 0) :
    x = 1 ∨ x = -1 ∨ x = 3 ∨ x = -3
```

在一次测试中，模型首次生成的证明未通过 Lean 验证。

系统随后将错误信息返回给模型，触发证明修复。

第二次尝试中，模型调整了证明策略：首先将原多项式分解为

\[
(x^2-1)(x^2-9)=0,
\]

再利用零乘积性质进行分类讨论，最终完成证明。

测试输出摘要：

```text
=== Attempt 1 ===
✗ Proof failed.

=== Attempt 2 ===
✓ Proof verified!
```

该案例展示了 Lean 编译器反馈在证明修复中的作用。

需要注意，这只是一次成功的实验案例，并不代表系统对一般数学定理具有稳定的证明能力。

## 8. 当前局限性

本项目仍处于早期原型阶段，存在以下限制：

- 目前主要通过代码中预设的定理运行实验，尚未提供通用的命令行输入接口。
- 证明生成效果依赖大语言模型的能力以及可用的 Mathlib 环境。
- 当前证明修复主要依赖原始编译器错误文本，尚未实现结构化错误分类。
- 目前尚未建立标准化的定理测试集，也缺少系统性的成功率评估。
- 验证环境配置、证明占位符检查与异常处理仍有进一步完善的空间。

## 9. 后续开发计划

项目计划逐步实现以下功能：

- [ ] **Experiment Logger**：记录每次证明尝试、验证结果、错误信息与执行时间。
- [ ] **Benchmark**：建立难度分层的 Lean 定理测试集。
- [ ] **Evaluation**：统计 Pass@1、修复成功率、平均尝试次数及 API Token 消耗。
- [ ] **Structured Feedback**：对 Lean 编译器错误进行分类和结构化处理。
- [ ] **Retrieval-Augmented Proving**：检索 Mathlib 中相关定理、引理及历史证明案例，辅助模型生成证明。
- [ ] **Multi-Model Evaluation**：比较不同模型在 Lean 定理证明任务上的表现。
- [ ] **Agent Optimization**：探索更有效的证明搜索与迭代修复策略。

长期目标是将项目扩展为一个结合 **LLM、形式化验证和检索增强生成（RAG）** 的自动定理证明实验平台。

## 10. 技术栈

| 技术 | 用途 |
|---|---|
| Python | Agent 工作流与 API 调用 |
| Lean 4 | 形式化证明检查 |
| Mathlib | 数学定理与证明工具库 |
| DeepSeek API | 证明生成及修复 |
| Lake | Lean 项目与依赖管理 |
| Git / GitHub | 版本管理与项目协作 |

## 11. 项目定位

LeanProofAgent 是一个用于学习、实验与探索的开源原型项目。

项目重点关注以下问题：

1. 大语言模型能否生成可通过 Lean 形式化验证的证明？
2. Lean 编译器反馈能够在多大程度上提高证明成功率？
3. 如何利用相关定理检索、历史证明和错误反馈改进证明生成？
4. 如何对自动定理证明 Agent 的效果进行可复现的实验评估？

项目将随着后续实验与开发逐步完善。