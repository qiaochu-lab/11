# Protein design evaluation：benchmark landscape

内部汇报 · 2026-09-15 · 横向调研

**这份只回答一个问题：别人现在有哪些 benchmark、分别在考什么、怎么评。** 不做 benchmark 选型，不排优先级。

具体 sample 数、阈值、artifact 复现细节一律不进正文——需要时点论文 / GitHub 链接，或查 source of truth：`design_eval_summary.md`（完整 inventory）、`design_eval_landscape.md`（逐条 recipe 与源码核对）。

`interface` 一列只标与我们现有管线的**接口距离**，不是质量评分、不是优先级：**direct** = 产物形态已对上 · **adapter** = 任务能做但要写接入代码 · **future** = 依赖我们还没有的条件化能力。

---

## 一、六类 task landscape

| 类别 | 考什么能力 | 输入 → 输出 | evaluation paradigm | 代表工作 | interface |
|---|---|---|---|---|---|
| **binder / miniprotein** | 给定靶点与表位，能否造出结合物 | 靶点结构 + hotspot → binder 序列 + 复合物坐标 | refolding / self-consistency（AF2-IG、Protenix、Boltz、Chai-1） | [AlphaProteo](https://arxiv.org/abs/2409.08022)、[ProtDBench](https://github.com/congliuUvA/ProtDBench)、[BindCraft](https://github.com/martinpacesa/BindCraft) | **direct** |
| **monomer / unconditional** | 无条件生成可折叠单体 | 只给长度 → 骨架（+ 序列） | refolding / self-consistency（ProteinMPNN → ESMFold） | [ProteinBench](https://arxiv.org/abs/2409.06744)、FrameFlow / FoldFlow 系惯例 | **direct** |
| **motif scaffolding** | 给定功能位点，能否长出支撑它的支架 | motif 坐标 → 支架骨架 + 序列 | refolding / self-consistency + 唯一性聚类 | [MotifBench](https://arxiv.org/abs/2502.12479)、[La-Proteina](https://github.com/NVIDIA-BioNeMo/la-proteina) | **adapter** |
| **peptide** | 小尺度 target-conditioned 设计；环化拓扑 | 受体结构 → 肽序列 + 结构 | native-structure comparison（对晶体肽）；大环另用环状预测器 | [PepGLAD](https://github.com/THUNLP-MT/PepGLAD)、RFpeptides | **adapter**（大环 future） |
| **enzyme / ligand** | 配体或底物条件下造催化环境 | 配体 + 催化残基（或 EC 号）→ 酶骨架 + 序列 | refolding + 配体位姿合法性；部分用实测活性校准 | [AME](https://github.com/RosettaCommons/RFdiffusion2)、[DISCO](https://arxiv.org/abs/2604.05181) | **future** |
| **antibody / nanobody** | 给定 framework 改 CDR。**没有基准在做完整抗体从头设计** | 天然复合物 + 完整 framework + 抗原 → CDR 序列 + 结构 | native-structure comparison（AAR、DockQ）；少数用实验标签 | [RAbD](https://github.com/THUNLP-MT/dyMEAN)、[CHIMERA](https://arxiv.org/abs/2603.13431) | **future** |

> **不同 task family 用的是不同的 evaluation paradigm**——refolding / self-consistency、native-structure comparison、experimental labels 各自成体系。**不能默认它们共用同一套 verifier**，也不能把跨 paradigm 的成功率拿来横比。

---

## 二、各 family 的代表工作

### binder / miniprotein

这五项共用同一批十个靶点，但是**五个独立条目**——采样协议与判定档各不相同，不是一条演进线。

| Work | 类型 | 在考什么 | 怎么评 | interface |
|---|---|---|---|---|
| [**AlphaProteo**](https://arxiv.org/abs/2409.08022) | method + 靶点规格 | 提出了这批靶点与设计规格 | AF2 类重折；有湿实验 | direct |
| [**PXDesign**](https://github.com/bytedance/PXDesignBench) | method + evaluation framework | 同批靶点上的设计与打分流程 | AF2-IG、Protenix | direct |
| [**A-CODE**](https://arxiv.org/abs/2605.03360) | method | 全原子一步 co-design | AF2-IG 单一档 | direct |
| [**ProtDBench**](https://github.com/congliuUvA/ProtDBench) | **evaluation framework** | **同一批设计同时按多档、多验证器打分** | AF2-IG / ColabFold / Protenix / Boltz / Chai-1 / ESMFold | direct |
| [**BindCraft**](https://github.com/martinpacesa/BindCraft) | method | 幻觉式 binder 设计 | AF2-multimer 设计 + 单体重预测；有湿实验 | adapter |

### motif scaffolding

| Work | 类型 | 在考什么 | 怎么评 | interface |
|---|---|---|---|---|
| [**MotifBench**](https://arxiv.org/abs/2502.12479) | **benchmark** | 固定题面上的 motif 支架能力 | ProteinMPNN → ESMFold；Foldseek 查唯一解 | adapter |
| [**RFdiffusion motif 集**](https://github.com/RosettaCommons/RFdiffusion) | protocol | 这一类的原始题面，被后续直接继承 | ProteinMPNN + AF2 | adapter |
| [**La-Proteina**](https://github.com/NVIDIA-BioNeMo/la-proteina) | protocol | **全原子** motif（含侧链原子） | **all-atom co-designability** | adapter |

> 这三者的差别不只是题目数量：前两者判的是骨架自洽，La-Proteina 判的是**全原子**自洽——**只有后者测得到全原子 co-design 的 claim**。

### enzyme / ligand

| Work | 类型 | 在考什么 | 怎么评 | interface |
|---|---|---|---|---|
| [**AME**](https://github.com/RosettaCommons/RFdiffusion2) | **benchmark** | 催化位点支架：能否摆对催化残基并容纳配体 | LigandMPNN → Chai-1；催化重原子 RMSD + 配体撞车 | future（配体 + 残基级原子固定） |
| **four-ligand convention**（SAM / OQO / FAD / IAI） | **convention**，非 benchmark | 配体条件生成，事实上的共同测试分子 | **各家验证器与样本数都不同** | future（配体） |
| [**DISCO / Studio-179**](https://arxiv.org/abs/2604.05181) | benchmark | 大规模配体条件生成 | Chai-1 + 配体位姿合法性检查 | future（配体） |

### peptide

| Work | 类型 | 在考什么 | 怎么评 | interface |
|---|---|---|---|---|
| [**PepGLAD / PepBench**](https://github.com/THUNLP-MT/PepGLAD) | benchmark（固定划分） | 天然肽–受体复合物的**重建** | **无结构预测器**，直接对晶体肽比 | adapter |
| **RFpeptides** | protocol | **大环肽** de novo 设计 | 环状 AF2 + Rosetta；有湿实验 | future（需环状位置编码） |

> 重建类有真值肽，可直接量全原子 RMSD——这是 binder 线给不了的一类证据；代价是它测"能否复现已知答案"。

### antibody / nanobody

| Work | 类型 | 在考什么 | 怎么评 | interface |
|---|---|---|---|---|
| [**RAbD**](https://github.com/THUNLP-MT/dyMEAN) | **事实标准案例集** | 给定 framework 的 CDR 重设计 | Rosetta 能量、序列恢复率；只排名 | future |
| [**CHIMERA-Bench**](https://arxiv.org/abs/2603.13431) | **benchmark + leaderboard** | 表位条件下的 CDR 序列–结构共设计 | 对天然结构：AAR、DockQ、表位 F1 | future（+ 表位条件化） |
| **AIntibody**（Nat Biotechnol） | **社区盲测挑战** | 多机构 AI 设计抗体的前瞻性对比 | **真做实验** | — |

> 抗体与纳米抗体**不共用协议**：纳米抗体没有轻链，挖空档位与流程结构本身就不同，抗体专用模型迁移到 VHH 上性能明显下降。

---

## 三、五条 survey findings

**1. fixed benchmark ≠ widely reused convention.**
复用最广的常常不是最标准化的。酶线的 four-ligand convention 跨最多独立组，却没有清单、没有统一验证器，数字不可横比；AME 反过来——清单固定、判据明确，复用面窄但可比。单体线的 scRMSD 惯例同理：人人在用，各家实现不统一。

**2. wet-lab strong ≠ reproducible benchmark.**
这两件事经常反向。湿实验最强的几项（商业模型、社区盲测挑战、four-ligand convention）恰恰拿不到可复跑的 artifacts；artifacts 最规范的几项（MotifBench、CHIMERA-Bench）反而没有湿实验。**"这个 benchmark 可信吗"要拆成两个问题分别问。**

**3. same-group reuse ≠ independent validation.**
AlphaProteo / PXDesign / A-CODE / ProtDBench 共用同一批靶点，但作者与生态高度重叠，**这不构成互相验证**。它们对我们的价值在于 baseline 同坐标系（Proteo-AA 基于 PXDesign），这与"外部独立验证"是两件事。要补独立性得**换验证器族**或**换标签源**，不能在这几项内部互相印证。

**4. 不同 verifier 会显著改变 success rate。**
拿实测标签回测，全领域事实标准 AF2-IG 在八个打分器里只排第 6。同一批设计换一个判定档，个别靶点的成功率能差两个数量级，而另一些靶点几乎不动。**报成功率必须说明用的是哪个验证器、哪一档**，否则数字无法解释。（细节见 source of truth。）

**5. 对我们，三类接口距离不同，缺口也各不相同。**
binder 与无条件单体是 **direct**（产物形态已对上）；motif 与线性肽多为 **adapter**（要写接入代码）；enzyme、antibody、大环肽是 **future**——但**缺的不是同一样东西**：酶线缺配体条件化（AME 还要残基级原子固定）、抗体线缺 framework 残基级固定与 CDR mask、大环缺环状位置编码。**归成一句"缺条件化"会掩盖真实工作量。**

---

*完整 inventory、逐条源码核对与 unresolved 清单见 `design_eval_summary.md` 与 `design_eval_landscape.md`。*
