# Protein design evaluation：benchmark landscape

内部汇报 · 2026-09-15

## 一、六类 task landscape

| 类别 | 考什么能力 | 输入 → 输出 | evaluation paradigm | 代表工作 | core metrics |
|---|---|---|---|---|---|
| **binder / miniprotein** | 给定靶点与表位，能否造出结合物 | 靶点结构 + hotspot → binder 序列 + 复合物坐标 | refolding / self-consistency（AF2-IG、Protenix、Boltz、Chai-1） | [AlphaProteo](https://arxiv.org/abs/2409.08022)、[ProtDBench](https://github.com/congliuUvA/ProtDBench)、[BindCraft](https://github.com/martinpacesa/BindCraft) | pLDDT、ipTM、ipAE、bound-unbound RMSD；簇级成功率 |
| **monomer / unconditional** | 无条件生成可折叠单体 | 只给长度 → 骨架（+ 序列） | refolding / self-consistency（ProteinMPNN → ESMFold） | [ProteinBench](https://arxiv.org/abs/2409.06744)、FrameFlow / FoldFlow 系惯例 | scRMSD、pLDDT；多样性、新颖性 |
| **motif scaffolding** | 给定功能位点，能否长出支撑它的支架 | motif 坐标 → 支架骨架 + 序列 | refolding / self-consistency + 唯一性聚类 | [MotifBench](https://arxiv.org/abs/2502.12479)、[La-Proteina](https://github.com/NVIDIA-BioNeMo/la-proteina) | motif RMSD、scRMSD；唯一解计数 |
| **peptide** | 小尺度 target-conditioned 设计；环化拓扑 | 受体结构 → 肽序列 + 结构 | native-structure comparison（对晶体肽）；大环另用环状预测器 | [PepGLAD](https://github.com/THUNLP-MT/PepGLAD)、RFpeptides | Cα RMSD、AAR、Rosetta ΔG |
| **enzyme / ligand** | 配体或底物条件下造催化环境 | 配体 + 催化残基（或 EC 号）→ 酶骨架 + 序列 | refolding + 配体位姿合法性；部分用实测活性校准 | [AME](https://github.com/RosettaCommons/RFdiffusion2)、[DISCO](https://arxiv.org/abs/2604.05181) | 催化重原子 RMSD、配体 RMSD、PoseBusters 合法性 |
| **antibody / nanobody** | 给定 framework 改 CDR | 天然复合物 + 完整 framework + 抗原 → CDR 序列 + 结构 | native-structure comparison（AAR、DockQ）；少数用实验标签 | [RAbD](https://github.com/THUNLP-MT/dyMEAN)、[CHIMERA](https://arxiv.org/abs/2603.13431) | AAR、CAAR、Cα RMSD、DockQ、表位 F1 |

> **不同 task family 用的是不同的 evaluation paradigm**——refolding / self-consistency、native-structure comparison、experimental labels 各自成体系。**不能默认它们共用同一套 verifier**，也不能把跨 paradigm 的成功率拿来横比。

---

## 二、各 family 的代表工作

### binder / miniprotein

| Work | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|
| [**AlphaProteo**](https://arxiv.org/abs/2409.08022) | 提出 10-target panel，其中 8 个做过湿实验 | AF2 类重折 + 湿实验验证 | pLDDT、ipTM、ipAE、bound-unbound RMSD | 这个 panel 的来源，被后续反复复用 |
| [**PXDesign**](https://github.com/bytedance/PXDesignBench) | 同一 10-target panel（另有环肽档） | AF2-IG + Protenix 重折 | pLDDT、ipAE、binder RMSD；iptm_binder、ptm_binder | method 与 evaluation framework 合一 |
| [**A-CODE**](https://arxiv.org/abs/2605.03360) | 同一 10-target panel | AF2-IG，单一判定档 | pLDDT、ipTM、ipAE、bound-unbound RMSD | 全原子一步 co-design；单验证器单档 |
| [**ProtDBench**](https://github.com/congliuUvA/ProtDBench) | 同一 panel + Cao 靶点；另带 Cao 湿实验打分表 | 同一批设计并行喂给 AF2-IG / ColabFold / Protenix(-Mini) / Boltz / Chai-1 / ESMFold，多档并判；TMalign 聚类 | 上述全部 + unscaled ipAE；簇级成功率 | **multi-verifier**：换验证器与换档的影响可直接读出来 |
| [**BindCraft**](https://github.com/martinpacesa/BindCraft) | **自有 panel**，不用上面那十个靶点 | AF2-multimer 设计环 → AF2 单体重预测；湿实验 | pLDDT、ipTM、ipAE、bound-unbound RMSD | 自成一套 panel + wet-lab |
这一类问的就是"给定靶点能不能造出结合物"，产物形态和我们在做的事最接近。**只有 AlphaProteo、PXDesign、A-CODE、ProtDBench 共用 AlphaProteo 那个 10-target panel；BindCraft 不用这十个靶点，有自己的一套。** ProtDBench 特殊的地方是它不出新方法，而是把同一批设计同时交给多个验证器打分，所以它是我们最容易对齐的参照。

### motif scaffolding

| Work | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|
| [**MotifBench**](https://arxiv.org/abs/2502.12479) | 30 题固定题面 | ProteinMPNN → ESMFold → Kabsch 对齐；Foldseek 查唯一解 | motif RMSD、scRMSD；唯一成功解计数、novelty | **fixed benchmark**，有独立维护方与排行榜 |
| [**RFdiffusion motif 集**](https://github.com/RosettaCommons/RFdiffusion) | 25 题，这一类的原始题面 | ProteinMPNN → AF2 | motif RMSD、scRMSD | **widely reused**：后续题面多由它派生 |
| [**La-Proteina**](https://github.com/NVIDIA-BioNeMo/la-proteina) | 26 个全原子 motif 任务（含侧链原子） | 模型自产序列 → 全原子自洽比对 | 全原子 RMSD（含侧链）、motif RMSD | **all-atom**：侧链也算进判据 |
这一类问的是"给一个功能位点，能不能长出撑住它的支架"。前两个判的是骨架自洽——序列重折回来像不像；La-Proteina 把侧链原子也算进去，是**本轮核实候选中最直接评估 all-atom co-designability 的代表工作**。对我们的意义就在这个差别上：前两者测不到全原子那一部分。

### enzyme / ligand

| Work | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|
| [**AME**](https://github.com/RosettaCommons/RFdiffusion2) | 41 个活性位点（M-CSA × PARITY） | LigandMPNN 出序列 → Chai-1 折叠 → 催化位点比对 + 配体检查 | 催化重原子 RMSD、配体撞车检查 | **fixed benchmark**：酶线唯一跨论文可比的 |
| **four-ligand convention**（SAM / OQO / FAD / IAI） | 四个分子，**无固定清单** | 各家自选 AF2 / AF3 / Chai-1 / RF3，无统一流程 | **无统一指标**，各家自选 | **widely reused convention**：用得最多但数字不可横比 |
| [**DISCO / Studio-179**](https://arxiv.org/abs/2604.05181) | Studio-179：170 个配体 + 9 个多配体组合 | Chai-1 折叠 + AF3 / ESMFold + PoseBusters | 骨架 RMSD、配体质心 RMSD、PoseBusters 合法性 | 规模最大，但尚无第三方复用 |
这一类的门槛是模型得看得懂配体。AME 有固定题面和明确判据，所以跨论文能比；four-ligand 只是大家默认用同几个分子，各家验证器都不一样，数字**没法**横比。这一类的前置条件是配体条件化，不是接口对不上的问题。

### peptide

| Work | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|
| [**PepGLAD / PepBench**](https://github.com/THUNLP-MT/PepGLAD) | 固定划分：PepBDB 划分随仓库，LNR 在 Zenodo；任务是天然肽–受体复合物**重建** | 无结构预测器，直接对晶体肽比 + PyRosetta | Cα RMSD、AAR、Rosetta ΔG | **fixed split + 有真值肽**，可直接量全原子差异 |
| **RFpeptides** | 4 个靶点的自有面板，**大环肽** de novo | 环状 AF2（AfCycDesign）+ Rosetta；湿实验 | AfCycDesign 置信度、Rosetta 界面能量 | 大环 de novo + **wet-lab** |
这一类实际是两件事。PepGLAD 是重建天然复合物，有真值肽，可以直接量全原子差多少——这是 binder 线给不了的证据，代价是它测的是"能否复现已知答案"。RFpeptides 是大环从头设计，前置条件是环状拓扑表示，属于另一种能力。

### antibody / nanobody

| Work | Test set / setting | Evaluation pipeline | Core metrics | Key point |
|---|---|---|---|---|
| [**RAbD**](https://github.com/THUNLP-MT/dyMEAN) | 60 个案例（ML 圈常用筛后 55）；给定 framework 的 CDR 重设计 | Rosetta 打分，直接对天然结构；只排名不设阈值 | Rosetta 能量、序列恢复率（AAR） | **事实标准案例集**，这一类复用最广 |
| [**CHIMERA-Bench**](https://arxiv.org/abs/2603.13431) | 自建 2,922 个复合物，3 种互不相交划分；表位条件下的 CDR 共设计 | 对天然结构直接打分；11 个方法同设置重训 | AAR、CAAR、Cα RMSD、TM-score、Fnat、iRMSD、DockQ、表位 F1 | **leaderboard + 同设置基线**，可比性最强 |
| **AIntibody**（Nat Biotechnol） | 29 家机构、511 条 AI 设计抗体的盲测题面 | 真做实验（含 KinExA） | 实测结合亲和力 | **前瞻性盲测 wet-lab**，非可下载数据集 |
**本轮核实的主流 benchmark 以 framework-conditioned CDR redesign 为主**——framework 给定，只改 CDR。RAbD 是大家都在用的那批案例，CHIMERA 自建了更大的集合还带排行榜，AIntibody 是真做实验的盲测挑战。这一类的前置条件是能在残基级固定 framework 并只放开 CDR；另外抗体与纳米抗体不共用协议，纳米抗体没有轻链，流程结构本身就不同。

---

## 三、五条 survey findings

**1. fixed benchmark ≠ widely reused convention。**
复用最广的往往不是最标准化的。酶线的 four-ligand 用得最多，却没有清单、各家验证器不同，数字没法横比；AME 反过来，题面固定判据明确，复用面窄一些但能跨论文比。

**2. wet-lab strong ≠ reproducible benchmark。**
湿实验强和能复跑经常是两回事。实验最硬的那几项（商业模型、盲测挑战）恰恰拿不到可复跑的 artifacts，而 artifacts 最规范的几个又没有湿实验。所以"这个 benchmark 可信吗"得拆成两个问题分别问。

**3. shared panel ≠ shared ecosystem。**
AlphaProteo 提供被复用的 10-target panel；PXDesign / A-CODE / ProtDBench 之间作者和生态重叠，因此**后三者不能视为完全独立的外部验证，但 direct baseline comparability 很高**。要补独立性，得换验证器族或换标签源。

**4. 换 verifier 会显著改变 success rate。**
常用的 AF2-IG verifier 放在八个打分器里只排第 6。同一批设计换一个判定档，有的靶点成功率差两个数量级，有的几乎不动。所以报成功率必须说清用的是哪个验证器、哪一档。

**5. 不同 task 的 conditioning requirement 不同。**
六类任务要求的条件化输入完全不是一回事：binder 和 motif 给的是结构坐标，peptide 重建给受体，enzyme 要能读配体或 EC 号，antibody 要能在残基级固定 framework 再只放开 CDR，大环肽还要环状拓扑表示。所以"支持条件生成"不是一个开关——判断一个模型能上哪些 benchmark，得按 conditioning 的类型逐个看。

---

小字：完整 inventory、逐条源码核对与 unresolved 清单见 `design_eval_summary.md` 与 `design_eval_landscape.md`。
