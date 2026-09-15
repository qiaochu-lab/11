# Protein design evaluation：benchmark landscape

内部汇报 · 2026-09-15

## 一、六类 task landscape

| 类别 | 考什么能力 | 输入 → 输出 | evaluation paradigm | 代表工作 | core metrics |
|---|---|---|---|---|---|
| **binder / miniprotein** | 给定靶点与表位，能否造出结合物 | 靶点结构 + hotspot → binder 序列 + 复合物坐标 | refolding / self-consistency（AF2-IG、Protenix、Boltz、Chai-1） | [AlphaProteo](https://arxiv.org/abs/2409.08022)、[ProtDBench](https://github.com/congliuUvA/ProtDBench)、[BindCraft](https://github.com/martinpacesa/BindCraft) | pLDDT、ipTM、ipAE、bound-unbound RMSD（后续标准化的 filter set）；簇级成功率 |
| **monomer / unconditional** | 无条件生成可折叠单体 | 只给长度 → 骨架（+ 序列） | refolding / self-consistency（ProteinMPNN → ESMFold） | [ProteinBench](https://arxiv.org/abs/2409.06744)、FrameFlow / FoldFlow 系惯例 | scRMSD、pLDDT；多样性、新颖性 |
| **motif scaffolding** | 给定功能位点，能否长出支撑它的支架 | motif 坐标 → 支架骨架 + 序列 | refolding / self-consistency + 唯一性聚类 | [MotifBench](https://arxiv.org/abs/2502.12479)、[La-Proteina](https://github.com/NVIDIA-BioNeMo/la-proteina) | motif RMSD、scRMSD；唯一解计数 |
| **peptide** | 小尺度 target-conditioned 设计；环化拓扑 | 受体结构 → 肽序列 + 结构 | native-structure comparison（对晶体肽）；大环另用环状预测器 | [PepGLAD](https://github.com/THUNLP-MT/PepGLAD)、RFpeptides | Cα RMSD、AAR、Rosetta ΔG |
| **enzyme / ligand** | 配体或底物条件下造催化环境 | 配体 + 催化残基（或 EC 号）→ 酶骨架 + 序列 | refolding + 配体位姿合法性；部分用实测活性校准 | [AME](https://github.com/RosettaCommons/RFdiffusion2)、[DISCO](https://arxiv.org/abs/2604.05181) | 催化重原子 RMSD、配体 RMSD、PoseBusters 合法性 |
| **antibody / nanobody** | 给定 framework 改 CDR | 天然复合物 + 完整 framework + 抗原 → CDR 序列 + 结构 | native-structure comparison（AAR、DockQ）；少数用实验标签 | [RAbD](https://github.com/THUNLP-MT/dyMEAN)、[CHIMERA](https://arxiv.org/abs/2603.13431) | AAR、CAAR、Cα RMSD、DockQ、表位 F1 |

> **不同 task family 用的是不同的 evaluation paradigm**——refolding / self-consistency、native-structure comparison、experimental labels 各自成体系。**不能默认它们共用同一套 verifier**，也不能把跨 paradigm 的成功率拿来横比。

---

## 二、各 family 的代表工作

### binder / miniprotein

| Work | Venue | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|---|
| [**AlphaProteo**](https://arxiv.org/abs/2409.08022) | arXiv 2024 | 提出 10-target panel，其中 8 个做过湿实验 | AF2 类重折 + 湿实验验证 | AF2 confidence / interface metrics；wet-lab binding | 这个 panel 的来源，被后续反复复用 |
| [**PXDesign**](https://github.com/bytedance/PXDesignBench) | bioRxiv 2025 | 同一 10-target panel（另有环肽档） | AF2-IG + Protenix 重折 | pLDDT、ipAE、binder RMSD；iptm_binder、ptm_binder | method 与 evaluation framework 合一 |
| [**A-CODE**](https://arxiv.org/abs/2605.03360) | arXiv 2026 | 同一 10-target panel | AF2-IG，单一判定档 | pLDDT、ipTM、ipAE、bound-unbound RMSD | 全原子一步 co-design；单验证器单档 |
| [**ProtDBench**](https://github.com/congliuUvA/ProtDBench) | arXiv 2026 | 同一 panel + Cao 靶点；另带 Cao 湿实验打分表 | 同一批设计并行喂给 AF2-IG / ColabFold / Protenix(-Mini) / Boltz / Chai-1 / ESMFold，多档并判；TMalign 聚类 | 上述全部 + unscaled ipAE；簇级成功率 | **multi-verifier**：换验证器与换档的影响可直接读出来 |
| [**BindCraft**](https://github.com/martinpacesa/BindCraft) | **Nature 2025** | **自有 panel**，不用上面那十个靶点 | AF2-multimer 设计环 → AF2 单体重预测；湿实验 | pLDDT、ipTM、ipAE、bound-unbound RMSD | 自成一套 panel + wet-lab |

该类任务的产物形态与全原子 co-design 最为接近。**AlphaProteo、PXDesign、A-CODE、ProtDBench 共用 AlphaProteo 的 10-target panel；BindCraft 使用自有 panel。** ProtDBench 不提出新方法，而是将同一批设计并行提交给多个验证器与多个判定档，因此是唯一可直接读出 verifier 选择与档位影响的条目。

### motif scaffolding

| Work | Venue | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|---|
| [**MotifBench**](https://arxiv.org/abs/2502.12479) | arXiv 2025 | 30 题固定题面 | ProteinMPNN → ESMFold → Kabsch 对齐；Foldseek 查唯一解 | motif RMSD、scRMSD；唯一成功解计数、novelty | **fixed benchmark**，有独立维护方与排行榜 |
| [**RFdiffusion motif 集**](https://github.com/RosettaCommons/RFdiffusion) | **Nature 2023** | 25 题，这一类的原始题面 | ProteinMPNN → AF2 | motif RMSD、scRMSD | **widely reused**：后续题面多由它派生 |
| [**La-Proteina**](https://github.com/NVIDIA-BioNeMo/la-proteina) | 预印本 2025 | 26 个全原子 motif 任务（含侧链原子） | 模型自产序列 → 全原子自洽比对 | 全原子 RMSD（含侧链）、motif RMSD | **all-atom**：侧链也算进判据 |

前两者判定骨架层面的自洽性，即重折序列与目标骨架的偏差；La-Proteina 将侧链原子纳入判据，是**本轮核实候选中最直接评估 all-atom co-designability 的代表工作**。三者题面部分重叠但判据层级不同，成功率不可直接比较。

### enzyme / ligand

| Work | Venue | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|---|
| [**AME**](https://github.com/RosettaCommons/RFdiffusion2) | 预印本 2025（随 RFdiffusion2） | 41 个活性位点（M-CSA × PARITY） | LigandMPNN 出序列 → Chai-1 折叠 → 催化位点比对 + 配体检查 | 催化重原子 RMSD、配体撞车检查 | **fixed benchmark**：酶线唯一跨论文可比的 |
| **four-ligand convention**（SAM / OQO / FAD / IAI） | 期刊 2024（刊名未核实） | 四个分子，**无固定清单** | 各家自选 AF2 / AF3 / Chai-1 / RF3，无统一流程 | **无统一指标**，各家自选 | **widely reused convention**：用得最多但数字不可横比 |
| [**DISCO / Studio-179**](https://arxiv.org/abs/2604.05181) | arXiv 2026 | Studio-179：170 个配体 + 9 个多配体组合 | Chai-1 折叠 + AF3 / ESMFold + PoseBusters | 骨架 RMSD、配体质心 RMSD、PoseBusters 合法性 | 规模最大，但尚无第三方复用 |

该类任务的前提是模型可读取配体。AME 题面固定、判据明确，具备跨论文可比性；four-ligand 仅是共同测试分子的惯例，样本数与验证器由各家自定，**数字不可横比**。

### peptide

| Work | Venue | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|---|
| [**PepGLAD / PepBench**](https://github.com/THUNLP-MT/PepGLAD) | 未核实 | 固定划分：PepBDB 划分随仓库，LNR 在 Zenodo；任务是天然肽–受体复合物**重建** | 无结构预测器，直接对晶体肽比 + PyRosetta | Cα RMSD、AAR、Rosetta ΔG | **fixed split + 有真值肽**，可直接量全原子差异 |
| **RFpeptides** | 未核实 | 4 个靶点的自有面板，**大环肽** de novo | 环状 AF2（AfCycDesign）+ Rosetta；湿实验 | iPAE、Cα RMSD、Rosetta interface metrics | 大环 de novo + **wet-lab** |

该类包含两种性质不同的任务。PepGLAD 属天然复合物重建，具真值肽，可直接量化全原子偏差——这是 binder 类基准无法提供的证据，代价是其评估对象为复现已知结构的能力；RFpeptides 为大环 de novo 设计，前提是环状拓扑表示。

### antibody / nanobody

| Work | Venue | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|---|
| [**RAbD**](https://github.com/THUNLP-MT/dyMEAN) | 期刊 2018（刊名未核实） | 60 个案例（ML 圈常用筛后 55）；给定 framework 的 CDR 重设计 | Rosetta 打分，直接对天然结构；只排名不设阈值 | Rosetta 能量、序列恢复率（AAR） | **事实标准案例集**，这一类复用最广 |
| [**CHIMERA-Bench**](https://arxiv.org/abs/2603.13431) | arXiv 2026 | 自建 2,922 个复合物，3 种互不相交划分；表位条件下的 CDR 共设计 | 对天然结构直接打分；11 个方法同设置重训 | AAR、CAAR、Cα RMSD、TM-score、Fnat、iRMSD、DockQ、表位 F1 | **leaderboard + 同设置基线**，可比性最强 |
| **AIntibody**（Nat Biotechnol） | **Nat Biotechnol** | 29 家机构、511 条 AI 设计抗体的盲测题面 | 真做实验（含 KinExA） | 实测结合亲和力 | **前瞻性盲测 wet-lab**，非可下载数据集 |

**本轮核实的主流 benchmark 以 framework-conditioned CDR redesign 为主**——framework 给定，仅 CDR 开放。RAbD 为该类的事实标准案例集；CHIMERA-Bench 自建更大规模集合，并提供排行榜与同设置重训基线；AIntibody 为前瞻性盲测挑战。抗体与纳米抗体不共用协议：纳米抗体无轻链，挖空档位与流程结构均不同。

---

## 三、小结

不同环节由不同 benchmark 分别覆盖：binder 与 motif 线主要判定骨架层面的自洽性，peptide 与 antibody 线多为对天然结构的重建比对，enzyme 线另加配体位姿合法性，此外有一批工作专门以实测标签校准打分器。**all-atom co-designability 是其中的一个维度**，本轮核实候选中以 La-Proteina 为代表，评估模型自产序列在侧链层面的自洽性——该维度目前只有少数协议在测。引用任何成功率时须一并说明两点：verifier 选择本身会移动结论（同一批设计换一个判定档，个别靶点成功率可相差两个数量级）；外部独立性只能由独立团队或独立实验 / 标签源提供，换 verifier family 只检验稳健性，不构成 independent validation。

---

小字：完整 inventory、逐条源码核对与 unresolved 清单见 `design_eval_summary.md` 与 `design_eval_landscape.md`。
