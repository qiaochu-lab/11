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
| **antibody / nanobody** | 给定 framework 改 CDR | 天然复合物 + 完整 framework + 抗原 → CDR 序列 + 结构 | native-structure comparison（AAR、DockQ）；少数用实验标签 | [RAbD](https://github.com/THUNLP-MT/dyMEAN)、[抗体/VHH 逆折叠基准](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0324566) | AAR、CAAR、Cα RMSD、DockQ、表位 F1 |

> **不同 task family 用的是不同的 evaluation paradigm**——refolding / self-consistency、native-structure comparison、experimental labels 各自成体系。**不能默认它们共用同一套 verifier**，也不能把跨 paradigm 的成功率拿来横比。

---

## 二、各 family 的代表工作

### binder / miniprotein

| Work | Publication / Venue | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|---|
| [**AlphaProteo**](https://arxiv.org/abs/2409.08022) | arXiv 2024 | 提出 10-target panel，其中 8 个做过湿实验 | AF2 类重折 + 湿实验验证 | AF2 confidence / interface metrics；wet-lab binding | 这个 panel 的来源，被后续反复复用 |
| [**PXDesign**](https://github.com/bytedance/PXDesignBench) | bioRxiv 2025 | 同一 10-target panel（另有环肽档） | AF2-IG + Protenix 重折 | pLDDT、ipAE、binder RMSD；iptm_binder、ptm_binder | method 与 evaluation framework 合一 |
| [**A-CODE**](https://arxiv.org/abs/2605.03360) | arXiv 2026 | 同一 10-target panel | AF2-IG，单一判定档 | pLDDT、ipTM、ipAE、bound-unbound RMSD | 全原子一步 co-design；单验证器单档 |
| [**ProtDBench**](https://github.com/congliuUvA/ProtDBench) | **ICML 2026** | 同一 panel + Cao 靶点；另带 Cao 湿实验打分表 | 同一批设计并行喂给 AF2-IG / ColabFold / Protenix(-Mini) / Boltz / Chai-1 / ESMFold，多档并判；TMalign 聚类 | 上述全部 + unscaled ipAE；簇级成功率 | **multi-verifier**：换验证器与换档的影响可直接读出来 |
| [**BindCraft**](https://github.com/martinpacesa/BindCraft) | **Nature 2025** | **自有 panel**，不用上面那十个靶点 | AF2-multimer 设计环 → AF2 单体重预测；湿实验 | pLDDT、ipTM、ipAE、bound-unbound RMSD | 自成一套 panel + wet-lab |
| [**BenchBB**](https://www.adaptyvbio.com/blog/benchbb) | community paper（[bioRxiv 2025](https://www.biorxiv.org/content/10.1101/2025.04.17.648362)） | **7 个标准化靶点**：EGFR、IL-7Rα、PD-L1、BBF-14、BHRF1、MBP、Cas9 | **自带统一湿实验协议**：BLI / SPR 测 k_on、k_off 换算 K_D | K_D（k_on / k_off） | 少数自带标准化湿实验协议的靶点集；**已有独立使用**（TriFlow、Boolean VHH 竞赛与 BoltzGen 用 MBP），但**无公开排行榜**，发表成熟度低于同行评审 venue |

该类任务的产物形态与全原子 co-design 最为接近。**AlphaProteo、PXDesign、A-CODE、ProtDBench 共用 AlphaProteo 的 10-target panel；BindCraft 使用自有 panel。** ProtDBench 不提出新方法，而是将同一批设计并行提交给多个验证器与多个判定档，因此是唯一可直接读出 verifier 选择与档位影响的条目。BenchBB 的不同之处在于它自带统一湿实验协议，代价是尚无公开排行榜、发表成熟度较低。

### monomer / unconditional

| Work | Publication / Venue | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|---|
| [**ProteinBench**](https://arxiv.org/abs/2409.06744) | **ICLR 2025** | 七类任务的 holistic 套件，含无条件单体分支 | 多维评估（quality / novelty / diversity / robustness），配公开 leaderboard | scRMSD、scTM、pLDDT、TM-score | 覆盖面最广的一体化套件，且**有公开榜** |
| [**Scaffold-Lab**](https://github.com/Immortals-33/Scaffold-Lab) | **PLOS Comput Biol 2026** | 无条件生成重评 7 个方法；motif 分支沿用 RFdiffusion 的 24 题 | ProteinMPNN → ESMFold，Top-N 取最优 | sc-TM、sc-RMSD、pdb-TM（novelty）、Foldseek 聚类（diversity）、MolProbity、运行时 | 把既有方法放进**同一框架统一重评并排名**，含效率与结构合规性 |

这一类的判据是"不给条件也能生成可折叠的东西"。ProteinBench 面向多任务、带公开榜；Scaffold-Lab 的价值在于统一重评——各家原本用各自的长度、样本数与 Top-N 策略自报，横比本来就不成立。两者都把 novelty 与 diversity 当独立维度报，而不是只报单一成功率。

### motif scaffolding

| Work | Publication / Venue | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|---|
| [**MotifBench**](https://arxiv.org/abs/2502.12479) | arXiv / whitepaper 2025 | 30 题固定题面 | ProteinMPNN → ESMFold → Kabsch 对齐；Foldseek 查唯一解 | motif RMSD、scRMSD；唯一成功解计数、novelty | **fixed benchmark**，有独立维护方与排行榜 |
| [**RFdiffusion motif 集**](https://github.com/RosettaCommons/RFdiffusion) | **Nature 2023** | 25 题，这一类的原始题面 | ProteinMPNN → AF2 | motif RMSD、scRMSD | **widely reused**：后续题面多由它派生 |
| [**La-Proteina**](https://github.com/NVIDIA-BioNeMo/la-proteina) | **ICLR 2026** | 26 个全原子 motif 任务（含侧链原子） | 模型自产序列 → 全原子自洽比对 | 全原子 RMSD（含侧链）、motif RMSD | **all-atom**：侧链也算进判据 |
| [**GeomMotif**](https://openreview.net/forum?id=b4C3zAzRgH) | **ICLR 2026** | **57 个任务**，每题 1–2 个 motif、最多 7 段连续片段；自 PDB 采样并保证存在可解构象 | 与模态无关（序列式与结构式方法同台）；几何保真 + 聚类 | scRMSD、pLDDT、**SUN**（Successful / Unique / Novel 合成分） | 把**纯几何保持**从功能约束中剥离，与 function-focused 的 MotifBench **互补而非重复** |

前两者判定骨架层面的自洽性，即重折序列与目标骨架的偏差；La-Proteina 将侧链原子纳入判据，是**本轮核实候选中最直接评估 all-atom co-designability 的代表工作**。GeomMotif 则把几何保持与功能约束拆开，题面由 PDB 采样并保证存在可解构象。四者题面部分重叠但判据层级不同，成功率不可直接比较。

### enzyme / ligand

| Work | Publication / Venue | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|---|
| [**AME**](https://github.com/RosettaCommons/RFdiffusion2) | **Nature Methods 2026**（RFdiffusion2） | 41 个活性位点（M-CSA × PARITY） | LigandMPNN 出序列 → Chai-1 折叠 → 催化位点比对 + 配体检查 | 催化重原子 RMSD、配体撞车检查 | **fixed benchmark**：酶线唯一跨论文可比的 |
| **four-ligand convention**（SAM / OQO / FAD / IAI） | Multiple works / convention | 四个分子，**无固定清单** | 各家自选 AF2 / AF3 / Chai-1 / RF3，无统一流程 | **无统一指标**，各家自选 | **widely reused convention**：用得最多但数字不可横比 |
| [**DISCO / Studio-179**](https://arxiv.org/abs/2604.05181) | arXiv 2026 | Studio-179：170 个配体 + 9 个多配体组合 | Chai-1 折叠 + AF3 / ESMFold + PoseBusters | 骨架 RMSD、配体质心 RMSD、PoseBusters 合法性 | 规模最大，但尚无第三方复用 |

该类任务的前提是模型可读取配体。AME 题面固定、判据明确，具备跨论文可比性；four-ligand 仅是共同测试分子的惯例，样本数与验证器由各家自定，**数字不可横比**。

**几何 / proxy 指标与真实活性不是同一层证据。** 上表判的都是几何与位姿——催化重原子摆得对不对、配体容不容得下。[Riff-Diff](https://www.nature.com/articles/s41586-025-09747-9)（**Nature 2026**，649(8095):237–245）用 retro-aldol 与 Morita–Baylis–Hillman 两个反应做实测，速率加速超过 5×10⁶ 倍，说明几何过关之后仍有巨大的活性差异空间；[COMPSS](https://github.com/seanrjohnson/protein_scoring)（**Nat Biotechnol 2025**）反过来拿实测活性校准 20 个 in-silico 指标，最好的也只到中等区分度。**所以酶线的几何成功率不能当作活性预测来引用。**

### peptide

| Work | Publication / Venue | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|---|
| [**PepGLAD / PepBench**](https://github.com/THUNLP-MT/PepGLAD) | **NeurIPS 2024** | 固定划分：PepBDB 划分随仓库，LNR 在 Zenodo；任务是天然肽–受体复合物**重建** | 无结构预测器，直接对晶体肽比 + PyRosetta | Cα RMSD、AAR、Rosetta ΔG | **fixed split + 有真值肽**，可直接量全原子差异 |
| **RFpeptides** | **Nature Chem Biol 2025** | 4 个靶点的自有面板，**大环肽** de novo | 环状 AF2（AfCycDesign）+ Rosetta；湿实验 | iPAE、Cα RMSD、Rosetta interface metrics | 大环 de novo + **wet-lab** |
| [**BOND-PEP**](https://advanced.onlinelibrary.wiley.com/doi/10.1002/advs.77125) | **Advanced Science 2026** | **193 对非同源 held-out** 蛋白–肽；**仅序列**的线性 binder 设定 | AlphaFold-Multimer 共折叠，取末五次输出中最高 ipTM | ipTM（**reference-beating success@8**） | 判据是**相对天然肽**而非绝对阈值——换个参照就换个结论 |

该类包含三种性质不同的任务。PepGLAD 属天然复合物重建，具真值肽，可直接量化全原子偏差——这是 binder 类基准无法提供的证据，代价是其评估对象为复现已知结构的能力；RFpeptides 为大环 de novo 设计，前提是环状拓扑表示；BOND-PEP 只输出序列、不评价结构，且成功与否以能否超过天然肽的 ipTM 为准。

### antibody / nanobody

| Work | Publication / Venue | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|---|
| [**RAbD**](https://github.com/THUNLP-MT/dyMEAN) | **PLOS Comput Biol 2018** | 60 个案例（ML 圈常用筛后 55）；给定 framework 的 CDR 重设计 | Rosetta 打分，直接对天然结构；只排名不设阈值 | Rosetta 能量、序列恢复率（AAR） | **事实标准案例集**，这一类复用最广 |
| [**抗体 / VHH 逆折叠基准**](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0324566) | **PLOS ONE 2025** | **203 Fab + 61 VHH**；CDR 序列设计（逆折叠） | 无结构预测器，直接对天然序列比；另用 Boltz-1 重折 | 序列恢复率、BLOSUM62 相似度、关键残基准确率 | 公开代码与数据，且**把 Fab 与 VHH 分开报**——少数覆盖纳米抗体的 |
| **AIntibody** | **Nature Biotechnology 2026** | 29 家机构、511 条 AI 设计抗体的盲测题面 | 真做实验（含 KinExA） | 实测结合亲和力 | **前瞻性盲测 wet-lab**，非可下载数据集 |

**本轮核实的主流 benchmark 以 framework-conditioned CDR redesign 为主**——framework 给定，仅 CDR 开放。RAbD 为该类的事实标准案例集；PLOS ONE 的逆折叠基准公开代码与数据，且把 Fab 与 VHH 分开报，是少数覆盖纳米抗体的；AIntibody 为前瞻性盲测挑战。抗体与纳米抗体不共用协议：纳米抗体无轻链，挖空档位与流程结构均不同。

---

## 三、小结

**1. Protein design 没有一套通用 benchmark。** 不同任务实际在测不同东西：binder / monomer / motif 常依赖 refolding 与 self-consistency；有天然参考答案的 peptide / antibody benchmark 可以直接做 sequence / structure recovery；enzyme / ligand-conditioned design 还需要评价 catalytic geometry、ligand pose，并可能最终依赖实验活性。All-atom co-designability 是其中一个评价维度，而不是统一总指标。

**2. 同一个 test set 也不代表结果可以直接横比。** Sampling protocol、sequence-design route、verifier、metric 和 threshold 都会改变最终 success rate。尤其 verifier 或 filter setting 改变时，同一批设计的结论都可能明显变化，因此引用 success rate 时必须同时说明评价协议。

**3. Benchmark 的"可信"也不是一个维度。** 正式发表、wet-lab grounding、公开 artifacts、独立复用分别回答不同问题。换 verifier 可以检验 robustness，但 independent validation 必须来自独立团队或独立实验 / 标签源。

---

小字：完整 inventory、逐条源码核对与 unresolved 清单见 `design_eval_summary.md` 与 `design_eval_landscape.md`。
