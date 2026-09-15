# 蛋白设计评估图谱：consolidation index

**这是索引，不是结论。** 详细 recipe、证据标记与核实过程在 [`design_eval_landscape.md`](design_eval_landscape.md)（2200+ 行），那份仍是 source of truth，本文件不替代也不删减它。每一行末尾的 `§` 指回详细节。

**日期**：2026-09-13　**覆盖**：五类源码级核实完成（binder / monomer-motif / peptide / enzyme / antibody-nanobody）

**本文件不做的事**：不给 RUN / DO NOT RUN，不排最终优先级，不挑选要复现的 benchmark。priority 和裁剪等这张表出来后统一做。

---

## 0. 怎么读这张表

一个 benchmark 一个 ID，四张表共用同一套 ID：

| 表 | 回答什么 |
|---|---|
| **表 1 身份与协议** | 它是什么、题面固定吗、给什么、要什么 |
| **表 2 评估与判据** | 谁打分、什么阈值、有没有榜和湿实验、被谁复用 |
| **表 3 可得性与成本** | 拿不拿得到、跑一次多贵、和谁重叠、还有什么没查清 |
| **表 4 credibility / maturity** | 六个子维度分开看，不做"大组/小组"二分 |

### ID 前缀

`B` binder / miniprotein　`M` monomer / unconditional / motif　`P` peptide　`E` enzyme / ligand　`A` antibody　`N` nanobody / VHH　`X` 横切工具与指标校准（不是设计 benchmark）

### 关键字段的取值约定

**fixed test set 还是 paper-specific protocol** —— 这一栏决定了跨论文可比性：

| 取值 | 含义 |
|---|---|
| `FIXED` | 固定题面，案例清单随仓库发布，别人跑的是同一批 |
| `FIXED*` | 题面固定，但清单要外部下载或按规则重建（Zenodo / Drive / 按论文过滤） |
| `PROTOCOL` | 论文自带协议，没有固定题面——靶点是作者自选的实验面板，换个人跑就是另一批 |
| `CONVENTION` | 连协议都算不上，只是大家默认用同几个分子/几个长度，样本数与验证器各家不同 |

**third-party reuse** —— **same-group 与 independent 分开标**，这是判断"是否真被领域接受"的关键：

| 取值 | 含义 |
|---|---|
| `indep ×N` | 有 N 个**独立课题组**在上面报过数 |
| `same-group` | 只有提出方自己或同生态/同作者的后续工作 |
| `none` | 截至本轮检索无第三方复用 |
| `—` | 不适用（工具类、数据集类） |

**approximate compute** —— 量级不是精确值，来自 §12.4：

`CPU` ／ `~1 GPU-天` ／ `几 GPU-天` ／ `几十 GPU-天` ／ `劝退级` ／ `不需生成`（现成标签数据，只算指标）

**Proteo-AA compatibility** —— **annotation，不是选型结论**：`DIRECT_NOW` / `NEEDS_ADAPTER` / `FUTURE` / `OUT_OF_SCOPE`，定义同 landscape 文首。

---

## 表 1　身份与协议

| ID | family | benchmark / protocol | provenance | 发表状态 | fixed? | 规模 / cases | input conditioning | output | § |
|---|---|---|---|---|---|---|---|---|---|
| **B01** | binder | **AlphaProteo 十靶点** | Google DeepMind | 预印本 2024 | `FIXED*` 清单在 Table S1 | **10 靶点**（8 个做过湿实验） | 靶点结构 + 裁剪范围 + hotspot | binder 序列 + 复合物坐标 | §9.1 |
| **B02** | binder | **ProtDBench** | 构建于 `bytedance/PXDesignBench` | **ICML 2026** | `FIXED` 随仓库 | 同 B01 十靶点 + 5 个 Cao 靶点；22,720 条设计 | 同 B01 | 同 B01 | §9.1 |
| **B03** | binder | **A-CODE** | PXDesign 同生态 | 预印本 2026 | `PROTOCOL`（靶点同 B01，采样协议自己的） | 10 靶点，每靶点 328–728 条 | 同 B01 | binder 序列 + 结构（两个 variant） | §9.1 |
| **B04** | binder | **PXDesign / PXDesignBench** | ByteDance | 预印本 2025 | `FIXED` 随仓库 | 10 蛋白 + 12 环肽 | 同 B01 | binder 序列 + 结构 | §9.1 |
| **B05** | binder | **BindCraft** | — | **期刊** Nature 2025 | `PROTOCOL` | **12 靶点**（v1 预印本 10） | 靶点结构 + hotspot | binder 序列 + 结构 | §9.2 |
| **B06** | binder | **BoltzGen** | — | 预印本 2025 | `PROTOCOL` | 10 低同源新靶点 + 5 简单；湿实验共 26 靶点 | 靶点结构 | binder 序列 + 结构 | §9.3 |
| **B07** | binder | **RFdiffusion binder 面板** | Baker lab | **期刊** Nature 2023 | `PROTOCOL` | 5 靶点 | 靶点结构 + hotspot | 骨架（序列走 ProteinMPNN） | §9.4 |
| **B08** | binder | **Latent-X** | 商业（Latent Labs） | 预印本 2025 | `PROTOCOL` | 7 湿实验靶点 + 200 结构 in-silico 集 | 靶点结构 | binder 序列 + 全原子结构 | §9.5 |
| **B09** | binder | **ODesign** | — | 预印本 2025 | `PROTOCOL` | 10 或 11（`UNRESOLVED`） | 靶点结构，只给靶点 MSA | binder 序列 + 结构 | §9.6 |
| **B10** | binder | **Cao et al. 2022 面板** | IPD | **期刊** Nature 2022 | `FIXED*` 六个 tar.gz | **12 蛋白 / 13 位点**，每位点 1.5 万–10 万条 | 靶点结构 | 设计 + 酵母展示标签 | §9.7 |
| **B11** | binder | **Adaptyv EGFR 竞赛**（两轮） | Adaptyv Bio | 预印本 2025 | `FIXED` 随仓库 | 1 靶点；R1 201 / R2 402 条已表征 | 靶点结构 | 设计 + BLI K_D 标签 | §9.8 |
| **B12** | binder | **BoltzDesign1** | — | 预印本 2025 | `PROTOCOL` | `UNRESOLVED` | 靶点结构 | binder 序列 + 结构 | §9.9 |
| **B13** | binder | **BindEnergyCraft** | — | 预印本 2025 | `PROTOCOL` | 8 靶点 | 靶点结构 | binder 序列 + 结构 | §3.1 |
| **B14** | binder | **Proteína-Complexa** | NVIDIA | 预印本 2026 | `PROTOCOL` | 19（12 easy + 7 hard）+ 4 小分子 + 41 AME | 靶点结构 / 配体 | 复合物 | §3.1 |
| **M01** | monomer | **MotifBench** | 社区（多组共建） | arXiv / whitepaper 2025 | `FIXED` 随仓库 | **30 题** × 100 骨架 × 8 序列 | motif 残基坐标 | 支架骨架 + 序列 | §13.1 |
| **M02** | monomer | **RFdiffusion motif 集** | Baker lab | **期刊** Nature 2023 | `FIXED*` | 25 题 | motif 坐标 | 骨架 | §3.2 |
| **M03** | monomer | **Genie2 motif 变体** | — | 预印本 2024 | `FIXED*` | 24（去掉 6VW1） | motif 坐标 | 骨架 | §3.2 |
| **M04** | monomer | **无条件生成的约定俗成协议**（FrameFlow / FoldFlow 系） | 无单一提出方 | — | `CONVENTION` | 长度 100/150/200/250/300 | **无条件** | 骨架（+ MPNN 序列） | §13.5 |
| **M05** | monomer | **ProteinBench** | — | 预印本 2024 | `FIXED` HF 榜 | 七类任务；抗体 55 / CAMEO2022 183 / apo-holo 91 / ATLAS 82 | 按任务不同 | 按任务不同 | §3.2 |
| **M06** | monomer | **La-Proteina motif 协议** | NVIDIA | **ICLR 2026** | `FIXED` 随仓库 | **26 个全原子 motif 任务** | motif 全原子坐标 | 全原子支架（含序列） | §13.2 |
| **P01** | peptide | **PepGLAD / PepBench 划分** | — | **NeurIPS 2024** | `FIXED` 190 随仓库 + LNR 93 在 Zenodo | 190 + 93 | 受体结构（天然复合物） | 肽序列 + 结构 | §14.3 |
| **P02** | peptide | **BOND-PEP** | — | 未核实 | `FIXED*` 仅 Zenodo | 193 对 | 受体结构 | **肽序列**（不评结构） | §14.2 |
| **P03** | peptide | **DiffPepBuilder PepPC-HF** | — | 未核实 | `FIXED*` PDB 号在论文 | 30（另有对接基准 174 随仓库） | 受体结构 | 肽序列 + 结构 | §14.3 |
| **P04** | peptide | **RFpeptides 面板** | Baker lab | **Nature Chem Biol 2025** | `PROTOCOL` | 4 靶点 | 受体结构 | **大环肽**序列 + 结构 | §14.4 |
| **P05** | peptide | **Latent-X 大环肽面板** | 商业 | 预印本 2025 | `PROTOCOL` | 3 靶点 | 受体结构 | 大环肽 | §14.4 |
| **E01** | enzyme | **AME（Atomic Motif Enzyme）** | Baker lab（随 RFdiffusion2） | **Nature Methods 2026** | `FIXED` 随仓库 JSON + 41 PDB | **41 个活性位点**（M-CSA × PARITY，EC 1–5） | 催化残基全原子 + 配体 | 酶骨架 + 序列 | §15.2 |
| **E02** | enzyme | **Studio-179（DISCO）** | DISCO | 预印本 2026 | `FIXED*` SDF 有、**任务 JSON 是坏的** | 179 = 170 配体 + 9 多配体组合 | 配体 | 结合该配体的蛋白 | §15.3 |
| **E03** | enzyme | **四配体惯例 SAM/OQO/FAD/IAI** | 源自 RFdiffusionAA | Multiple works / convention | `CONVENTION` | 4 个分子 | 配体 | 蛋白骨架 | §15.3 |
| **E04** | enzyme | **LigandMPNN 测试集** | Baker lab | 2023/25 | `FIXED` 随仓库 JSON | 317 小分子 + 74 核酸 + 83 金属（**并集 469 非 474**） | 骨架 + 配体 | **序列**（逆折叠） | §11.4 |
| **E05** | enzyme | **EnzyBench（EnzyGen）** | — | 预印本 2024 | `FIXED*` 仅 Google Drive | 3157 个四级 EC 家族，1500 测试 | EC 号 / 功能 | 酶序列 + 结构 | §15.4 |
| **E06** | enzyme | **EnzyBind（EnzyControl）** | — | 预印本 2025 | `FIXED*` Zenodo 1.34 GB | 11,100 对酶–底物 | 底物 + 功能 | 酶序列 + 结构 | §15.4 |
| **E07** | enzyme | **CrossDocked / Binding MOAD 口袋重设计** | PocketGen / PocketFlow（同作者） | 预印本 2024 | `FIXED*` 靠脚本重生成 | 各 100 对 | 配体 + 口袋外骨架 | 口袋序列 + 侧链 | §15.5 |
| **E08** | enzyme | **COMPSS** | — | **期刊** Nat Biotechnol 2025 | `FIXED*` Zenodo，**README 链接全坏** | 2 个酶家族，500+ 条表达纯化（144 条活性） | — | **不产设计**，校准打分器 | §15.6 |
| **A01** | antibody | **RAbD** | Rosetta 社区 | **PLOS Comput Biol 2018** | `FIXED` 事实标准，清单两处机器可读 | **60**（ML 圈常用筛后 55） | 天然复合物 + 完整 framework | CDR 序列（+ 结构） | §16.2 |
| **A02** | antibody | **dyMEAN 三任务协议** | THUNLP-MT | 未核实 2023 | `FIXED` `configs.py` 三清单 | CDR-H3 设计 **60** / 结构预测 **70** / 亲和力 **53** | 复合物，**framework 完全给定** | CDR-H3 序列 + 结构 | §16.2 |
| **A03** | antibody | **DiffAb 19 复合物** | — | 未核实 | `FIXED*` **仓库不带清单**，按抗原名过滤重建 | 19 | 复合物，framework 给定 | CDR 序列 + 结构 | §16.2 |
| **A04** | antibody | **ProteinBench 抗体分支** | — | 预印本 2024 | `FIXED*` = RAbD 60 减 5 | 55，每抗原 64 条 | 复合物，只重设计 CDR-H3 | CDR-H3 序列 + 结构 | §16.2 |
| **A05** | antibody | **CHIMERA-Bench** | — | **GEM @ ICLR 2026** | `FIXED` 三种划分 JSON | **2,922 复合物 / 2,721 PDB**（仓库带 12 条样本） | 复合物 + **表位**，framework 给定 | CDR 序列–结构共设计 | §16.4 |
| **A06** | antibody | **IgGM SAb-23H2-Ab** | — | 未核实 | `FIXED` Zenodo 13790269 | **60**，7 个挖空档 | framework **逐残基完整给出** + 抗原全给 | 被 `X` 挖空的 CDR | §16.2 |
| **A07** | antibody | **CDR 逆折叠基准（Fab 支）** | — | 未核实 | `FIXED` CSV 随仓库 | **203 Fab**（含"删掉抗原链"对照目录） | 复合物骨架 | 序列 | §16.3 |
| **A08** | antibody | **AbBiBench** | — | 预印本 2025 | `FIXED*` | 14 抗体 × 9 抗原，>184,500 条测量 | 完整复合物 | **不产设计**，算似然–亲和力相关 | §16.5 |
| **A09** | antibody | **FLAb** | — | 未核实 | `FIXED*` | 241 个数据集 / 7 类性质 / >300 万条 | — | **不产设计**，性质数据 | §16.5 |
| **A10** | antibody | **AIntibody** | 29 家机构共建 | **Nature Biotechnology 2026** | **社区盲测挑战** | 511 条 AI 设计抗体 | 竞赛题面 | 抗体序列，前瞻性湿测 | §16.1 |
| **A11** | antibody | **abag-benchmark-set** | — | 预印本 2026 | `FIXED` | 110 个低同源复合物，**明确排除纳米抗体** | 抗体 + 抗原序列 | **结构预测**，不设计 | §16.0 |
| **A12** | antibody | **ABAG-docking** | — | 未核实 | `FIXED*` | 112 核心案例（含 14 个单域抗体） | 未结合态结构 | **对接位姿**，不设计 | §16.0 |
| **N01** | nanobody | **IgGM SAb-23H2-Nano** | — | 未核实 | `FIXED` Zenodo，含预挖空 FASTA | **27**，**4 个**挖空档（无轻链） | framework 逐残基给出 + 抗原 | 被挖空的 CDR | §16.6 |
| **N02** | nanobody | **CDR 逆折叠基准（VHH 支）** | — | 未核实 | `FIXED` CSV 随仓库 | **61 VHH** | 骨架 | 序列 | §16.3 |
| **N03** | nanobody | **Germinal** | — | 未核实 | `PROTOCOL` | 4 靶点（**仓库只有 3 个 PDB**） | 抗原 + **通用 framework 模板**（`nb.pdb`） | de novo CDR（framework 拓扑写死） | §16.4 |
| **N04** | nanobody | **nanoFOLD** | — | 未核实 | `FIXED*` **无清单无仓库** | 43 晶体 + 1064 模型 | 骨架 | 序列 | §16.6 |
| **N05** | nanobody | **NbBench** | — | 未核实 | `FIXED` HF | 8 任务（**7 个是性质预测**） | 序列 | 多数是预测 | §16.6 |
| **N06** | nanobody | **EasyNano** | — | 未核实 | `PROTOCOL` | 5 + 1 靶点 | 抗原 + 模板 | de novo CDR | §16.6 |
| **N07** | nanobody | **Hitawala & Gray Nb 面板** | — | 未核实 | `FIXED*` | 49 Ab + **60 Nb**（两臂分开） | 复合物 | **对接**，不设计 | §16.0 |
| **X01** | 横切 | **PoseBusters** | 独立 | 未核实 | 检查器 | 检查项定义在仓库 | 配体构象 | **合法性判定** | §15.6 |
| **X02** | 横切 | **Overath 元分析** | — | 2025 | 标签数据 | 3,766 条实测 binder / 15 靶点 | — | 打分器 AP 对比（**ipSAE > ipAE，1.4×**） | §6 |
| **X03** | 横切 | **Rocklin 组零样本回测** | — | 2025 | 标签数据 | **614 个实测单体** / 11 项研究 | — | 指标区分成败的能力 | §6 |
| **X04** | 横切 | **ipSAE** | Dunbrack lab | 2025 | 指标 | — | pAE 矩阵 | 替代 ipTM 的界面分 | §6 |
| **X05** | 横切 | **Korbeld refolding 局限** | — | Protein Science 2026 | 结论 | — | — | 自洽指标被进化信息污染 | §6 |
| **X06** | 横切 | **Protein FID** | — | 2025/26 | 指标 | — | — | 是否覆盖训练分布 | §6 |
| **X07** | 横切 | **Domain Retrieval Rate** | — | 2026 | 指标 | — | — | 新颖性被高估 | §6 |

---

## 表 2　评估与判据

**两条读表提醒**：①「阈值类型」比阈值本身更重要——`绝对` / `相对（逐靶点浮动）` / `无（只排名）` 三种同时存在，混报会让"成功率"无法解释（§14.8）。②`ipAE` 有两套量纲（归一化 = 原始/31），直接比数字会得到相反结论（§8.3）。

| ID | benchmark | evaluator | 主指标 / 阈值 | 阈值类型 | published baselines | 榜 / 挑战 | wet-lab grounding | reuse: same-group | reuse: independent |
|---|---|---|---|---|---|---|---|---|---|
| **B01** | AlphaProteo 十靶点 | AF2 类 | 原文自报成功率 | 绝对 | — | 无 | **有**：8 靶点，7 成功 + TNFα 失败 | — | **`indep ×2`** ByteDance 生态、Latent Labs（表 S3 逐字符对上） |
| **B02** | ProtDBench | AF2-IG、ColabFold、Protenix(-Mini)、Boltz-1/2、Chai-1、ESMFold | **五档同时打**：`af2_easy`（pLDDT>0.8、i_pTM>0.5、i_pAE<0.35≈10.85 Å、bound_unbound_RMSD<3.5）／`af2_opt`（pLDDT>0.9、unscaled_i_pAE<7.0、binder RMSD<1.5）／`ptx`(0.85/0.88/2.5)／`ptx_mini`／`ptx_basic`(0.8/0.8/2.5)。簇级成功率用 **TMalign**（非 Foldseek），阈值 [0.6,0.8,1.0]，分母是骨架数 | 绝对 | **7 个方法逐条设计分数随仓库** | 无榜，但数据全开 | **另带** Cao 打分表 236,246 条 × 8 打分器 / 1,485 阳性 | PXDesignBench（同生态） | `UNRESOLVED`（2026 新出） |
| **B03** | A-CODE | AF2-IG，`af2_easy` 档 | 同 `af2_easy`（已用数据裁决：十靶点两位小数全对上，MAD 0.00，r=1.000） | 绝对 | 表 4 含多方法 | 无 | 无 | 同生态 | `UNRESOLVED` |
| **B04** | PXDesign / PXDesignBench | AF2-IG、Protenix；单体用 ESMFold | 同上五档来源 | 绝对 | 有 | 无 | 有（原文） | ProtDBench、A-CODE | `UNRESOLVED` |
| **B05** | BindCraft | AF2-multimer 设计环 + AF2 单体重预测 | `af2_easy` 那一档即源自它 | 绝对 | 有 | 无 | **有** | — | **`indep ×1+`**（ProtDBench 把它做成一档） |
| **B06** | BoltzGen | **Boltz-2** | refolding RMSD ≤2.5 + 设计单独重折 ≤2.5；`min_design_to_target_pae` 是**最小值不是均值** | 绝对 | 有 | 无 | **有**：8 场湿实验 / 26 靶点 | — | `UNRESOLVED` |
| **B07** | RFdiffusion binder 面板 | AF2 + initial guess + 靶点模板 | `pae_interaction`（**均值**）| 绝对 | 有 | 无 | **有** | RFdiffusion2/3 | **`indep ×多`**（AF2-IG 惯例被全领域继承） |
| **B08** | Latent-X | Chai-1（主）、Boltz-2 | `min_ipae<1`（**最小值**）、`ptm_binder>0.9`、`complex_rmsd<2`；大环肽档**弃用 ptm_binder** | 绝对 | 有 | 无 | **有**：7 靶点 | — | none（模型与权重都不公开） |
| **B09** | ODesign | **AF3**，只给靶点 MSA | `ipAE<10.85`、**`pLDDT>80`**（原文特意说明 AF3 的 pLDDT 不归一化）、`ipTM>0.5`、复合物 RMSD<2.5 | 绝对 | 有 | 无 | `UNRESOLVED` | — | `UNRESOLVED` |
| **B10** | Cao et al. 2022 | RIFDock + Rosetta，酵母展示 | `ddg<-30`、`contact_molecular_surface>450`、`score_per_res<-2.4`、`mismatch_probability<0.1`、`sap_score<35`、`binder_delta_sap<12`（XML 里 Ddg / CMS 带 `confidence="0"` = 只报不判） | 绝对 | — | 无 | **最强之一**：13 位点 × 1.5 万–10 万条，SC₅₀ | — | **`indep ×多`**——ProtDBench、Overath 等都拿它当标签源 |
| **B11** | Adaptyv EGFR | ColabFold（两轮设置不同） | BLI 的 **K_D**（真实测量，非 in-silico 判据） | 绝对（实测） | 601 条已表征 | **公开竞赛**（两轮） | **最强之一** | — | **`indep ×多`** |
| **B12** | BoltzDesign1 | Boltz-1 设计环 + AF3 验证 | `UNRESOLVED` | — | — | 无 | `UNRESOLVED` | — | `UNRESOLVED` |
| **B13** | BindEnergyCraft | AF2-Multimer、Rosetta、Boltz-1 | `UNRESOLVED` | — | 有 | 无 | `UNRESOLVED` | — | none（代码未放出） |
| **B14** | Proteína-Complexa | AF2-Multimer、RoseTTAFold3 | `UNRESOLVED` | — | 有 | 无 | `UNRESOLVED` | — | — |
| **M01** | MotifBench | ProteinMPNN → ESMFold → Kabsch RMSD；Foldseek 查唯一性与新颖性 | motif RMSD + scRMSD，**并把"唯一成功解"计数标准化** | 绝对 | 有 | **✅ 有排行榜，独立维护** | 无 | — | **`indep ×多`**——这一类唯一有榜的 |
| **M02** | RFdiffusion motif 集 | ProteinMPNN + AF2 | scRMSD < 2 Å | 绝对 | 有 | 无 | **有** | RFdiffusion2/3 | **`indep ×多`**（Genie2 等直接继承） |
| **M03** | Genie2 motif 变体 | ProteinMPNN + ESMFold | 同上 | 绝对 | 有 | 无 | 无 | — | `indep ×1+` |
| **M04** | 无条件生成约定俗成协议 | ProteinMPNN(T=0.1) 出 8 条 → ESMFold → 取最小 scRMSD | scRMSD < 2 Å；另报多样性与新颖性 | 绝对 | 各家自报 | 无 | 无 | — | **`indep ×多`**（事实惯例，但**不是固定题面**，数字不严格可比） |
| **M05** | ProteinBench | TM-score、RMSD、pLDDT、scTM；AF2 | 按任务不同 | 绝对 | 有 | **✅ HuggingFace 榜** | 无 | — | `indep ×1+` |
| **M06** | La-Proteina motif 协议 | 全原子 co-designability | **全原子** RMSD 2.0 Å | 绝对 | 有 | 无 | 无 | — | `UNRESOLVED` |
| **P01** | PepGLAD / PepBench | **无结构预测器**，直接对晶体结构 | RMSD ≤2/5/10 Å 分档；ΔG<0 | 绝对 | 有 | 无 | 无 | 同系列论文 | LNR 本身出自 Tsaban 2021，**被多家复用** |
| **P02** | BOND-PEP | AF-Multimer / ColabFold | **超过该靶点天然肽自己的 ipTM** | **相对（逐靶点浮动）** | 有 | 无 | 无 | — | `UNRESOLVED` |
| **P03** | DiffPepBuilder | **无结构预测器**，Rosetta | `ddG < 0` | 绝对 | 有 | 无 | `UNRESOLVED` | — | `UNRESOLVED` |
| **P04** | RFpeptides | AfCycDesign（环状 AF2）+ Rosetta | **绝对但逐靶点重调**（GABARAP 档比通用档严一倍以上） | 绝对·逐靶点重调 | 有 | 无 | **有** | — | `UNRESOLVED` |
| **P05** | Latent-X 大环肽 | Chai-1 | 见 B08，**大环肽弃用 ptm_binder** | 绝对 | 有 | 无 | **有**：3 靶点 | — | none |
| **E01** | AME | **LigandMPNN 出序列 → Chai-1 折叠** | 催化重原子 **RMSD < 1.5 Å** + 配体撞车检查 | 绝对 | 有（RFdiffusion3 报 37/41） | 无榜无维护方 | **有** | RFdiffusion2/3 | **`indep ×2`** ODesign、Proteína-Complexa(NVIDIA) ——**酶线唯一有跨组可比性的** |
| **E02** | Studio-179 | Chai-1（骨架 + 配体质心 RMSD < 2 Å）、AF3、ESMFold、PoseBusters | 绝对 2.0 Å | 绝对 | 有 | 无 | benchmark 部分无（DISCO 另有 TTN 4,050 的一次性实验） | — | **`none`**（截至本轮无第三方） |
| **E03** | 四配体惯例 | **各家不同**：AF2 / AF3 / Chai-1 / RF3 | **无统一阈值** | 无统一 | 各家自报 | 无 | 原文有 | RFAA | **`indep ×3`** AtomFlow、DISCO、ODesign ——**复用最广但数字不可横比** |
| **E04** | LigandMPNN 测试集 | — | 序列恢复率、χ1/χ2 恢复率 | 无（只排名） | 有 | 无 | 部分（配套论文） | — | **`indep ×多`**（作为序列设计步被几乎所有方法调用） |
| **E05** | EnzyBench | ESP score、AF2 pLDDT、Gnina docking | **ESP ≥ 0.6** | 绝对 | 有 | 无 | 无 | — | `UNRESOLVED` |
| **E06** | EnzyBind | ESMFold、ProteinMPNN、CLEAN、UniKP、Gnina | `UNRESOLVED` | — | 有 | 无 | 无 | — | `UNRESOLVED` |
| **E07** | CrossDocked / MOAD 口袋 | AAR、scRMSD、Vina、PoseBusters | 无统一 | 无（只排名） | 有 | 无 | 无 | **PocketGen + PocketFlow 同一作者** | 本语料内**未见独立组**；分子生成文献里数据集本身广泛使用 `UNRESOLVED` |
| **E08** | COMPSS | 拿 **20 个 in-silico 指标**去对实测活性 | AUC：**Rosetta-relax 0.76、ProteinMPNN 0.75**、MIF-ST 0.72、ESM-IF 0.70、AF2 pLDDT 0.66；净电荷/SASA 0.39。**序列同一性不能预测活性** | 校准（非设计判据） | — | 无 | **最强之一**：144 条表达纯化，过滤后 74% 有活性（Fisher P=0.00018） | — | `UNRESOLVED` |
| **A01** | RAbD | Rosetta 能量、序列恢复率 | 无统一 | 无（只排名） | 有 | 无榜，但**是事实标准案例集** | 无 | — | **`indep ×4+`** ProteinBench、dyMEAN、DiffAb、AbDPO、CHIMERA ——**全表复用最广的固定案例集** |
| **A02** | dyMEAN 三任务 | **无结构预测验证器**，直接对天然结构 | AAR、CAAR、Cα RMSD、TM-score、lDDT、DockQ | **无，只排名** | 有 | 无 | 无 | — | **`indep ×多`**——三任务协议被后续 co-design 论文大量沿用 |
| **A03** | DiffAb 19 | Rosetta | **IMP% = 设计 CDR 结合能优于原生的比例**，即 ΔΔG<0 | 绝对 | 有 | 无 | 无 | — | `indep ×1+` |
| **A04** | ProteinBench 抗体分支 | **IgFold**（H+L 同时输入，真实非 H3 结构作模板）→ Kabsch → **抗原存在下 Rosetta relax 5×200 步取最低能量** | 13 个指标分四组；**噪声下限已给出：IgFold 对天然结构 relax 后 1.77 Å** | 绝对 | 有 | ✅ HF 榜 | 无 | — | `indep ×1+` |
| **A05** | CHIMERA-Bench | 无结构预测器，对天然结构 | `aar,caar,ppl` / `rmsd,tm_score` / `fnat,irmsd,dockq` / `epitope_f1` / `n_liabilities` / `chimera_s`,`chimera_b`。**两套接触定义**：标注与 CAAR 用 4.5 Å 重原子，界面指标用 8.0 Å Cα–Cα | **无，mean±std 排名** | **11 个方法同设置重训** | **✅ 排行榜随仓库**：135 条数据行（11 方法 × 3 划分 × 6 CDR） | 无 | — | `UNRESOLVED`（2026 新出） |
| **A06** | IgGM SAb-23H2-Ab | — | 结构预测成功率 **DockQ > 0.23**；CDR-H3 设计报骨架 RMSD + AAR（36%） | 绝对 | 有 | 无 | 无 | — | `UNRESOLVED` |
| **A07** | CDR 逆折叠（Fab） | Boltz-1 重折 | 序列恢复率、BLOSUM62、关键残基准确率、对 ΔΔG 的 Spearman | **无** | **有**：AntiFold 0.703、LM-Design 0.597、ESM-IF 0.423、ProteinMPNN 0.349 | 无 | 无 | — | `UNRESOLVED` |
| **A08** | AbBiBench | — | **模型对完整复合物的对数似然 vs 实测亲和力的 Spearman**：ProteinMPNN 0.30、ESM-IF1 0.28、AntiFold 0.21（**纯序列语言模型接近零甚至为负**） | 校准 | 有 | 无 | **强**：>184,500 条测量 | — | `UNRESOLVED` |
| **A09** | FLAb | — | 7 类治疗性质 | 校准 | — | 无 | **强**：>300 万条 | — | `UNRESOLVED` |
| **A10** | AIntibody | **真做实验**（含 KinExA） | 盲测亲和力 | 实测 | 29 家机构 511 条 | **✅ CASP 式盲测社区挑战** | **最强**：前瞻性 | — | 本身就是多组共建 |
| **A11** | abag-benchmark-set | AF2.3 / AF3 / Boltz-1 / Chai-1 | DockQ、TM-score、ipSAE、pDockQ2 | 绝对 | 有 | 无 | 无 | — | `UNRESOLVED` |
| **A12** | ABAG-docking | 对接软件 | DockQ | 绝对 | 有 | 无 | 无 | — | `UNRESOLVED` |
| **N01** | IgGM SAb-23H2-Nano | — | 同 A06 | 绝对 | 有 | 无 | 无 | — | `UNRESOLVED`——但**是最大的带结构公开纳米抗体设计清单** |
| **N02** | CDR 逆折叠（VHH） | Boltz-1 重折 | **AntiFold 0.368 / ProteinMPNN 0.362**——抗体专用模型**迁移不过去** | 无 | 有 | 无 | 无 | — | `UNRESOLVED` |
| **N03** | Germinal | ColabDesign 幻觉 → **AbMPNN** → AF3 / Chai-1 / Protenix 共折叠 | **这一类唯一有完整阈值级联**：`sc_rmsd<6.0`、`interface_shape_comp≥0.6`、`interface_hbonds≥3`、`surface_hydrophobicity≤0.4`、`pdockq2>0.23`、`external_plddt>0.87`、`external_iptm>0.74`、`external_ptm>0.84`、`external_pae<7.5`。⚠️ 原文明写**阈值只对 AF3 校准过**，Chai-1/Protenix 后端未校准 | 绝对 | 有 | 无 | **有**：BLI 成功率 4–22%，最好 K_D 140–560 nM；**scFv 全部无显著结合** | — | `UNRESOLVED` |
| **N04** | nanoFOLD | — | 逆折叠恢复率 | 无 | 有 | 无 | 无 | — | none |
| **N05** | NbBench | — | 8 任务，多为性质预测 | 无 | 有 | HF | 无 | — | `UNRESOLVED` |
| **N06** | EasyNano | — | `UNRESOLVED` | — | — | 无 | `UNRESOLVED` | — | none（代码未发布） |
| **N07** | Hitawala & Gray | 对接 | DockQ | 绝对 | 有 | 无 | 无 | — | `UNRESOLVED` |
| **X01** | PoseBusters | 自身即检查器 | PB-valid 检查项；撞车判据 **0.75×vdW** | 绝对 | — | 无 | 无 | — | **`indep ×3`** RFAA、AtomFlow、DISCO |
| **X02** | Overath 元分析 | — | **ipSAE 平均精度是 ipAE 的 1.4 倍** | 校准 | — | — | **强**：3,766 条实测 | — | — |
| **X03** | Rocklin 组 | — | 所有指标区分成败的能力都只是中等；最好的单一指标是 ESMFold 平均 pLDDT | 校准 | — | — | **强**：614 个实测单体 | — | — |
| **X04** | ipSAE | — | 只看 pAE 低于阈值的残基对（ipTM 按整链算会被无序区压低） | 指标定义 | — | — | — | — | `indep ×1+` |
| **X05** | Korbeld | — | 设计与天然同源时 refolding 分数虚高 | 校准 | — | — | — | — | — |
| **X06** | Protein FID | — | 现有指标不衡量分布覆盖 | 指标定义 | — | — | — | — | — |
| **X07** | Domain Retrieval Rate | — | 新颖性被高估 | 指标定义 | — | — | — | — | — |

---

## 表 3　可得性、成本、重叠与未决项

**「清单在不在仓库里」决定能不能真复现**——这一栏比论文写得多详细更有决定性（§11.0、§12.3）。

| ID | benchmark | code / data 可得性 | 约计算量 | Proteo-AA 兼容性 *(annotation)* | 与其他 benchmark 的 overlap | unresolved |
|---|---|---|---|---|---|---|
| **B01** | AlphaProteo 十靶点 | 无代码；靶点规格在 Table S1 | 几 GPU-天（单长度） | `DIRECT_NOW`——十靶点已复现为可运行配置 `benchmarks/alphaproteo10/` | **B02/B03/B04 与它是同一批靶点**（三层壳） | 逐靶点长度排布 |
| **B02** | ProtDBench | ✅ **拿了就能跑**，`data/` 164 MB 随仓库（7 方法逐条分数 + Cao 表） | 打分便宜；生成 22,720 条是主要成本。**满五档需三次模型运行**（AF2、Protenix-Mini、Protenix 全量，最后一个默认关） | `DIRECT_NOW`——**Protenix 本就是我们依赖**，`ptx*` 三档边际成本最低 | 与 B01/B03/B04 同靶点；`af2_easy` = B05 那一档 | — |
| **B03** | A-CODE | 无代码 | 几 GPU-天 | `DIRECT_NOW` | 同上 | 逐靶点长度排布与样本分配 |
| **B04** | PXDesign / PXDesignBench | ✅ `bytedance/PXDesignBench` | 同 B02 | `DIRECT_NOW` | 同上；B02 构建于它 | — |
| **B05** | BindCraft | ✅ `martinpacesa/BindCraft` | 几 GPU-天 | `NEEDS_ADAPTER` | 判据已被 B02 收成 `af2_easy` 档 | — |
| **B06** | BoltzGen | ✅ `HannesStark/boltzgen` | 几 GPU-天 + Boltz-2 权重 | `NEEDS_ADAPTER` | 靶点独立（低同源新靶点） | — |
| **B07** | RFdiffusion 面板 | ✅ `RosettaCommons/RFdiffusion` | 几 GPU-天 | `NEEDS_ADAPTER` | AF2-IG 惯例是 B02 `af2_opt` 的来源 | — |
| **B08** | Latent-X | ❌ **跑不了**（商业，代码与权重都不公开） | — | `OUT_OF_SCOPE` | 靶点独立；表 S3 可用于**核对 B01 规格** | — |
| **B09** | ODesign | ⚠️ `UNRESOLVED` | 高（要 AF3） | `NEEDS_ADAPTER` | 靶点可能与 B01 重叠（10 或 11 未定） | 靶点数 |
| **B10** | Cao et al. 2022 | ⚠️ 要外部下载（IPD 六个 tar.gz）；过滤 notebook 已核实 | **不需生成**（标签数据） | 打分器校准 `DIRECT_NOW` | B02 直接带它的打分表 | — |
| **B11** | Adaptyv EGFR | ✅ `adaptyvbio/egfr_competition_{1,2}` | **不需生成** | 标签数据 `DIRECT_NOW` | 独立 | — |
| **B12** | BoltzDesign1 | ✅ `yehlincho/BoltzDesign1` | 几 GPU-天 | `NEEDS_ADAPTER` | — | 靶点与阈值 |
| **B13** | BindEnergyCraft | ❌ 未放出 | — | `NEEDS_ADAPTER` | — | 全部协议细节 |
| **B14** | Proteína-Complexa | ⚠️ 承诺放出 | 几十 GPU-天 | `NEEDS_ADAPTER` | **含 41 AME**（= E01） | 是否已放出 |
| **M01** | MotifBench | ✅ **拿了就能跑**：`test_cases.csv` + `motif_pdbs/` | **~1 GPU-天**（30×100×8 → ESMFold） | `NEEDS_ADAPTER`——motif 条件化与我们推理语义的差异见 §13.4 | 与 M02/M03 题面部分重叠但**判据不同** | — |
| **M02** | RFdiffusion motif 集 | ⚠️ 随 RFdiffusion 仓库 | ~1 GPU-天 | `NEEDS_ADAPTER` | M01/M03 的前身 | — |
| **M03** | Genie2 motif 变体 | ⚠️ | ~1 GPU-天 | `NEEDS_ADAPTER` | M02 去掉 6VW1 | — |
| **M04** | 无条件生成协议 | — 无需数据 | ~1 GPU-天 | **`DIRECT_NOW`**（无条件生成，不需任何条件化接口） | 与 M05 的无条件分支重叠 | 各家实现细节不统一 |
| **M05** | ProteinBench | ✅ HF | 几 GPU-天（七类任务） | 分任务不同 | 抗体分支 = A04；含无条件分支 | — |
| **M06** | La-Proteina motif | ✅ `NVIDIA-BioNeMo/la-proteina`，`motif_dict.yaml` | 几十 GPU-天（26×200） | `NEEDS_ADAPTER`——但**是唯一测全原子 co-designability 的**，最贴我们的全原子 claim | 与 M01 都是**纯蛋白原子无配体**，别归到酶 | — |
| **P01** | PepGLAD / PepBench | ✅ 190 随仓库；LNR 93 在 Zenodo 13373108 | 几 GPU-天 | `NEEDS_ADAPTER`——**有真值肽**，可直接量全原子 RMSD | 与 §9 binder 线**不重叠**（重建类，提供另一类证据） | — |
| **P02** | BOND-PEP | ⚠️ 仅 Zenodo 19841318，无 GitHub（本轮未下载） | 几 GPU-天 | `NEEDS_ADAPTER` | 与 §9 任务设定重叠度高（同为 target-conditioned，尺度更小） | 内容未核实 |
| **P03** | DiffPepBuilder | ✅ 对接基准 174 随仓库；PepPC-HF 30 在论文 Table S1 | 几 GPU-天 | `NEEDS_ADAPTER` | 对接基准**不是设计任务** | — |
| **P04** | RFpeptides | ⚠️ | 几 GPU-天 | **`FUTURE`**——环化需要环状位置编码，是独立拓扑能力 | 与 P05 同属大环肽 | — |
| **P05** | Latent-X 大环肽 | ❌ 商业 | — | `FUTURE` | 同上 | — |
| **E01** | AME | ✅ **拿了就能跑**，文档最全：`mcsa_41.json` + 41 个输入 PDB | **劝退级**：41×100×8 = **32,800 次 Chai 折叠**，README 自己写单机跑不完 | `FUTURE`——需**配体条件化 + 残基级原子固定** | 被 B14 收入 | — |
| **E02** | Studio-179 | ⚠️ SDF 有，**任务 JSON 非法**；236/239 能靠文件名找回，约十行代码 | 几十 GPU-天（179×150 → Chai-1） | `FUTURE`——需配体条件化 | 与 E03 是竞争关系（想取代那个惯例） | 修复后内容是否完整 |
| **E03** | 四配体惯例 | ⚠️ 无清单，只有 2 个示例 PDB | ~1 GPU-天 | `FUTURE`——需配体条件化 | — | 各家样本数与验证器不同，**数字不可横比** |
| **E04** | LigandMPNN 测试集 | ✅ `test_{small_molecule,nucleotide,metal}.json` | ~1 GPU-天 | `FUTURE` | 两处完整性问题：`2zio`/`3olt` 也在 train；5 个 PDB 跨两表 | 并集 469 vs 474 的口径 |
| **E05** | EnzyBench | ⚠️ 只能从 Google Drive 下 | 几十 GPU-天 | `FUTURE`——需 **EC / 功能条件化**（不是配体） | — | — |
| **E06** | EnzyBind | ⚠️ 仓库只有 190 行 demo；Zenodo 15462173（1.34 GB） | 几十 GPU-天 | `FUTURE`——需**底物 + 功能条件化** | — | — |
| **E07** | CrossDocked / MOAD 口袋 | ⚠️ PocketGen 靠脚本重生成（seed 2021）；**PocketFlow 仓库是空的** | 几 GPU-天 | `FUTURE`——需配体；但任务形态**最接近我们"给定上下文设计一部分"** | — | PocketFlow 不可复现 |
| **E08** | COMPSS | ⚠️ notebook + Zenodo，**README 链接全坏**，直接用 notebook | **不需生成** | 打分器校准 `DIRECT_NOW` | 与 X02/X03 同类（指标校准） | — |
| **A01** | RAbD | ✅ 清单两处机器可读：`dyMEAN/configs.py`、`MEAN/summaries/rabd_summary.jsonl` | 几 GPU-天 | `FUTURE`——需**残基级 framework 固定 + CDR mask** | **A02/A03/A04/A05 的共同底座** | **60→55 的原始筛选规则**（已知被排除五条及各自原因，规则本身未见定义） |
| **A02** | dyMEAN 三任务 | ✅ 三清单都在 `configs.py`（60/70/53） | 几 GPU-天 | `FUTURE`——另需 H/L 双链语义 | 底座 = A01；任务三 = SKEMPI 子集 | IgFold 测试集论文说 51、代码 70（**两个数都真实，引用要说明阶段**） |
| **A03** | DiffAb 19 | ⚠️ **仓库不带清单**，19 条已在 §10.3 重建列出 | 几 GPU-天 | `FUTURE` | 底座 = SAbDab | — |
| **A04** | ProteinBench 抗体分支 | ⚠️ = RAbD 60 减五个具名条目 | 几 GPU-天 | `FUTURE` | 底座 = A01；属 M05 的一个分支 | — |
| **A05** | CHIMERA-Bench | ✅ `sample_data/` 12 复合物（每划分 train4/val2/test6）+ 135 行榜；**全量 2,922 在 HF/Zenodo** | 几十 GPU-天（全量） | `FUTURE`——另需**表位条件化** | 与 A01 不重叠（自建 2,922） | 全量内容未下载 |
| **A06** | IgGM SAb-23H2-Ab | ✅ Zenodo 13790269，含结构 + **预挖空 FASTA** | 几 GPU-天 | `FUTURE` | 与 A01 不重叠（2023 时间留出） | — |
| **A07** | CDR 逆折叠（Fab） | ✅ CSV 随仓库，**含"删掉抗原链"对照目录** | ~1 GPU-天 | `FUTURE`——逆折叠不是我们的产物形态 | 与 N02 同一仓库两支 | — |
| **A08** | AbBiBench | ⚠️ | **不需生成** | 打分器校准 | **不含任何纳米抗体**（17 条全是配对 H/L） | — |
| **A09** | FLAb | ⚠️ | **不需生成** | 打分器校准 | 含 VHH 子集（AVIDa-hIL6 573,892 / SARS-CoV-2 77,004 / NbThermo 673） | — |
| **A10** | AIntibody | ❌ **是竞赛不是可下载测试集** | — | — | — | 题面是否可复用 |
| **A11** | abag-benchmark-set | ⚠️ | 几 GPU-天 | `OUT_OF_SCOPE`（结构预测） | **明确排除纳米抗体** | — |
| **A12** | ABAG-docking | ⚠️ | 几 GPU-天 | `OUT_OF_SCOPE`（对接） | 含 14 个单域抗体 | — |
| **N01** | IgGM Nano | ✅ Zenodo，含预挖空 FASTA | ~1 GPU-天（27 条） | `FUTURE`，但**接口上离我们最近**：单链 + 抗原上下文，只差 framework 残基级固定 + CDR mask | 与 A06 同一发布，但**挖空档 4 vs 7，协议不通用** | — |
| **N02** | CDR 逆折叠（VHH） | ✅ CSV 随仓库 | ~1 GPU-天 | `FUTURE` | 与 A07 同仓库 | — |
| **N03** | Germinal | ✅ 代码 + 配置 + 模板；**`pdbs/` 只有 pdl1 / il3 / insulin** | 几十 GPU-天（幻觉 + 共折叠） | `FUTURE`——但**是 de novo CDR 形态**，与 binder 设计最像 | 与 N01 不同任务（de novo vs 重设计） | **IL-20 与 BHRF1 靶点文件不在仓库**，需从预印本重建 |
| **N04** | nanoFOLD | ❌ **无清单无仓库** | — | — | — | 43 / 1064 具体是哪些 |
| **N05** | NbBench | ✅ HF | ~1 GPU-天 | 多数 `OUT_OF_SCOPE`（预测非设计） | — | — |
| **N06** | EasyNano | ❌ **代码未发布**（可用性声明里组织名占位符没填） | — | — | — | 是否会发布 |
| **N07** | Hitawala & Gray | ❌ | — | `OUT_OF_SCOPE`（对接） | 抗体/纳米抗体**两臂分开**，可作协议差异的旁证 | — |
| **X01** | PoseBusters | ✅ `pip install` 就完事；检查项定义在仓库 | **CPU（一杯咖啡）** | `DIRECT_NOW`（纯检查器） | 被 E01/E02 等直接调用 | — |
| **X02** | Overath | ⚠️ | **不需生成** | 打分器校准 `DIRECT_NOW` | 标签源与 B10 部分重叠 | — |
| **X03** | Rocklin 组 | ⚠️ | **不需生成** | 打分器校准 `DIRECT_NOW` | 单体线的标签源 | — |
| **X04** | ipSAE | ✅ `DunbrackLab/IPSAE` | **CPU** | `DIRECT_NOW`——**最低成本的可加项** | 可加在任何 AF2/AF3 输出上 | — |
| **X05–X07** | Korbeld / Protein FID / DRR | — | — | 结论性参考 | — | — |

---

## 表 4　source credibility / maturity（六个子维度分开看）

> **不做"大组 / 小组"二分。** 大组的东西也可能没清单、没独立复用、artifacts 对不上论文；小组的东西也可能题面固定、数据全开、被别人跑过。所以拆成六列各自判断，综合列只是把六列汇总，**不是权威性排序**。

六个子维度：**① provenance**（谁做的、是否有持续维护方）· **② 发表状态** · **③ wet-lab** · **④ 公开代码与数据** · **⑤ 独立组复用** · **⑥ 能否从 released artifacts 对上论文结果**

第 ⑥ 列是最硬的一条——它不问作者说了什么，只问**放出来的东西能不能把论文里的数算回来**。

| ID | benchmark | ① provenance | ② 发表 | ③ wet-lab | ④ 代码+数据 | ⑤ 独立复用 | ⑥ artifacts ↔ 论文 | 综合 |
|---|---|---|---|---|---|---|---|---|
| **B01** | AlphaProteo 十靶点 | 工业大组，无维护方 | 预印本 | ✅ 8 靶点 | ❌ 无代码 | ✅ ×2 | ⚠️ **靶点规格能逐字符对上**（Latent-X 表 S3 独立比对），成功率未复算 | **中高** |
| **B02** | ProtDBench | 有仓库、数据全开 | **ICML 2026** | ⚠️ 借 Cao 标签 | ✅ **164 MB 随仓库** | ⚠️ 太新 | ✅✅ **本表最硬的一条**：我们用它的数据复算 `af2_easy`，十靶点两位小数全部对上（MAD 0.00，r=1.000） | **高** |
| **B03** | A-CODE | 同生态 | 预印本 2026 | ❌ | ❌ 无代码 | ⚠️ 太新 | ✅ 经 B02 数据反查对上 Table 4 | **中高** |
| **B04** | PXDesign | 工业组，有仓库 | 预印本 2025 | ✅ | ✅ | ⚠️ | ⚠️ 未逐条复算 | **中高** |
| **B05** | BindCraft | 学术组 | ✅ **Nature 2025** | ✅ | ✅ | ✅ 判据被 B02 收录 | ⚠️ 未复算 | **高** |
| **B06** | BoltzGen | — | 预印本 2025 | ✅ **8 场 / 26 靶点** | ✅ | ⚠️ | ⚠️ | **中高** |
| **B07** | RFdiffusion | Baker lab | ✅ **Nature 2023** | ✅ | ✅ | ✅ 惯例被全领域继承 | ⚠️ | **高** |
| **B08** | Latent-X | 商业 | 预印本 | ✅ 7 靶点 | ❌ **完全不公开** | ❌ | ❌ 不可能 | **低**（作为可复现基准） |
| **B09** | ODesign | — | 预印本 | ⚠️ | ⚠️ | ⚠️ | ❌ 靶点数都未定 | **低中** |
| **B10** | Cao 2022 | IPD | ✅ **Nature 2022** | ✅✅ **13 位点 × 万级** | ⚠️ 要外部下载，过滤 notebook 可读 | ✅ 多组当标签源 | ✅ 过滤阈值已从 notebook 核实 | **高** |
| **B11** | Adaptyv EGFR | 公司 + 公开竞赛 | 预印本 | ✅✅ **601 条 BLI** | ✅ | ✅ | ✅ | **高** |
| **B12** | BoltzDesign1 | — | 预印本 | ⚠️ | ✅ | ⚠️ | ❌ 协议未查清 | **低中** |
| **B13** | BindEnergyCraft | — | 预印本 | ⚠️ | ❌ 未放出 | ❌ | ❌ | **低** |
| **B14** | Proteína-Complexa | NVIDIA | 预印本 2026 | ⚠️ | ⚠️ 承诺放出 | — | ❌ | **低中** |
| **M01** | **MotifBench** | **社区共建 + 独立维护** | arXiv / whitepaper 2025 | ❌ | ✅ 题面随仓库 | ✅ | ✅ 题面 + 榜都在 | **高**——这一类**唯一有独立维护方和榜的** |
| **M02** | RFdiffusion motif | Baker lab | ✅ Nature | ✅ | ✅ | ✅ | ⚠️ | **中高** |
| **M03** | Genie2 变体 | — | 预印本 | ❌ | ⚠️ | ⚠️ | ⚠️ | **中** |
| **M04** | 无条件生成协议 | **无提出方，是惯例** | — | ❌ | — 无需数据 | ✅ 人人在用 | ❌ **各家实现不统一，数字不严格可比** | **中**（普及度高、标准化低） |
| **M05** | ProteinBench | — | 预印本 2024 | ❌ | ✅ HF 榜 | ⚠️ | ⚠️ | **中高** |
| **M06** | La-Proteina | NVIDIA | **ICLR 2026** | ❌ | ✅ `motif_dict.yaml` | ⚠️ | ⚠️ | **中高**（**唯一测全原子 co-designability**） |
| **P01** | PepGLAD / PepBench | — | **NeurIPS 2024** | ❌ | ✅ 190 随仓库 | ✅ LNR 被多家用 | ✅ 清单可直接读 | **中高**——肽线里最接近标准的 |
| **P02** | BOND-PEP | — | 未核实 | ❌ | ⚠️ 仅 Zenodo | ⚠️ | ❌ 本轮未下载 | **低中** |
| **P03** | DiffPepBuilder | — | 未核实 | ⚠️ | ⚠️ 部分随仓库 | ⚠️ | ⚠️ | **中** |
| **P04** | RFpeptides | Baker lab | **Nature Chem Biol 2025** | ✅ | ⚠️ | ⚠️ | ❌ 逐靶点重调阈值 | **中** |
| **P05** | Latent-X 大环肽 | 商业 | 预印本 | ✅ | ❌ | ❌ | ❌ | **低** |
| **E01** | **AME** | Baker lab，随 RFdiffusion2 | **Nature Methods 2026** | ✅ | ✅ **JSON + 41 PDB，文档最全** | ✅ **×2 跨组** | ⚠️ 清单能对上，成绩未复算 | **高**——**酶线唯一有跨论文可比性的** |
| **E02** | Studio-179 | DISCO | 预印本 2026 | ⚠️ benchmark 部分无 | ⚠️ SDF 有、**JSON 坏** | ❌ **无第三方** | ❌ 任务文件不可直接解析 | **低中** |
| **E03** | 四配体惯例 | 源自 Baker lab | Multiple works / convention | ✅ | ❌ 无清单 | ✅ **×3，复用最广** | ❌ **无统一样本数与验证器，数字不可横比** | **中**（普及度最高、标准化最低） |
| **E04** | LigandMPNN 测试集 | Baker lab | 2023/25 | ⚠️ | ✅ JSON 随仓库 | ✅ | ⚠️ **并集 469 ≠ 论文 474**，且两条也在 train | **中高** |
| **E05** | EnzyBench | — | 预印本 | ❌ | ⚠️ 仅 Drive | ⚠️ | ❌ | **低中** |
| **E06** | EnzyBind | — | 预印本 | ❌ | ⚠️ 仓库只有 demo | ⚠️ | ❌ | **低中** |
| **E07** | CrossDocked / MOAD 口袋 | **PocketGen 与 PocketFlow 同一作者** | 预印本 | ❌ | ⚠️ 要重生成；**PocketFlow 仓库空** | ❌ 本语料内无独立组 | ❌ | **低中** |
| **E08** | COMPSS | — | ✅ **Nat Biotechnol 2025** | ✅✅ **144 条表达纯化** | ⚠️ **README 链接全坏**，notebook 可用 | ⚠️ | ⚠️ | **中高** |
| **A01** | **RAbD** | Rosetta 社区 | **PLOS Comput Biol 2018** | ❌ | ✅ 清单两处机器可读 | ✅✅ **×4+，全表最广** | ⚠️ **60→55 的筛选规则未见定义** | **高**——**事实标准案例集** |
| **A02** | dyMEAN 三任务 | 学术组 | 未核实 2023 | ❌ | ✅ 三清单在 `configs.py` | ✅ 协议被大量沿用 | ⚠️ **论文 51 vs 代码 70**，两个数都真实 | **高** |
| **A03** | DiffAb 19 | — | 未核实 | ❌ | ⚠️ **清单要重建** | ✅ | ⚠️ 已重建并列出 | **中** |
| **A04** | ProteinBench 抗体分支 | — | 预印本 2024 | ❌ | ⚠️ = RAbD 减 5 | ✅ | ✅ **给出了噪声下限 1.77 Å**（少见的好做法） | **中高** |
| **A05** | **CHIMERA-Bench** | — | **GEM @ ICLR 2026** | ❌ | ✅ **splits JSON 最规范** + 榜随仓库 | ⚠️ 太新 | ⚠️ 榜可读，全量未下载 | **中高**——**榜 + 11 个同设置重训基线** |
| **A06** | IgGM Ab | — | 未核实 | ❌ | ✅ Zenodo，含预挖空 FASTA | ⚠️ | ✅ 60 条可直接数出 | **中高** |
| **A07** | CDR 逆折叠 Fab | — | 未核实 | ⚠️ 借 ΔΔG | ✅ CSV 随仓库 | ⚠️ | ✅ 203 行可直接数出 | **中高** |
| **A08** | AbBiBench | — | 预印本 2025 | ✅✅ >184,500 条 | ⚠️ | ⚠️ | ⚠️ | **中高** |
| **A09** | FLAb | — | 未核实 | ✅✅ >300 万条 | ⚠️ | ⚠️ | ⚠️ | **中高** |
| **A10** | **AIntibody** | **29 家机构共建** | **Nature Biotechnology 2026** | ✅✅ **前瞻性盲测 + KinExA** | ❌ 是竞赛不是数据集 | ✅ 本身即多组 | — | **高**（作为**挑战**；不作为可下载基准） |
| **A11** | abag-benchmark-set | — | 预印本 2026 | ❌ | ⚠️ | ⚠️ | ⚠️ | **中** |
| **A12** | ABAG-docking | — | 未核实 | ❌ | ⚠️ | ⚠️ | ⚠️ | **中** |
| **N01** | IgGM Nano | — | 未核实 | ❌ | ✅ Zenodo | ⚠️ | ✅ 27 条可直接数出 | **中**——**但已是纳米抗体设计里最大的带结构公开清单** |
| **N02** | CDR 逆折叠 VHH | — | 未核实 | ⚠️ | ✅ CSV 随仓库 | ⚠️ | ✅ 61 行可直接数出 | **中高** |
| **N03** | **Germinal** | — | 未核实 | ✅ **BLI 4–22%，K_D 140–560 nM** | ✅ 代码 + 阈值配置 | ⚠️ | ⚠️ **缺 2 个靶点 PDB**；阈值只对 AF3 校准 | **中高**——**纳米抗体线唯一"有阈值又有湿实验"的** |
| **N04** | nanoFOLD | — | 未核实 | ❌ | ❌ **无清单无仓库** | ❌ | ❌ | **低** |
| **N05** | NbBench | — | 未核实 | ❌ | ✅ HF | ⚠️ | ⚠️ | **中**（但 8 任务里 7 个是预测） |
| **N06** | EasyNano | — | 未核实 | ⚠️ | ❌ **代码未发布** | ❌ | ❌ | **低** |
| **N07** | Hitawala & Gray | — | 未核实 | ❌ | ❌ | ⚠️ | ❌ | **低中** |
| **X01** | PoseBusters | 独立 | 未核实 | — | ✅ **pip 即得**，检查项在仓库 | ✅ ×3 | ✅ | **高** |
| **X02** | Overath | — | 2025 | ✅✅ 3,766 条 | ⚠️ | — | — | **高**（作为校准证据） |
| **X03** | Rocklin 组 | — | 2025 | ✅✅ 614 个 | ⚠️ | — | — | **高**（作为校准证据） |
| **X04** | ipSAE | Dunbrack lab | 2025 | — | ✅ `DunbrackLab/IPSAE` | ✅ | ✅ | **高** |

> `X05`–`X07`（Korbeld / Protein FID / Domain Retrieval Rate）不在本表——它们是**结论与指标定义**，不是可跑的 benchmark，六个维度对它们不适用。

---

## 表 5　对我们的特殊定位：PXDesign / A-CODE / ProtDBench

**这三项（B02 / B03 / B04）在本表里要单独标成 very high relevance**，理由不是它们独立性最高——恰恰相反，它们作者与生态高度重叠，**不能写成"独立第三方验证"**。理由是 baseline comparability：

| 链条 | |
|---|---|
| **Proteo-AA 本身就是基于 PXDesign 改的** | 我们的 substrate 就是它 |
| **A-CODE 直接拿 PXDesign 做 baseline** | 所以 A-CODE 的表和我们天然同坐标系 |
| **ProtDBench 又把这套 binder evaluation 系统化、可复跑** | 构建于 `bytedance/PXDesignBench`，数据 164 MB 全开 |

结论：**它们是我们最重要的参考线之一**，同时**不能用来主张外部独立验证**。两件事不冲突，分开标：

| 维度 | B02 ProtDBench | B03 A-CODE | B04 PXDesign |
|---|---|---|---|
| **source confidence** | **high** | **high** | **high** |
| **Proteo-AA relevance** | **very high** | **very high** | **very high** |
| **reproducibility** | **high**（数据随仓库，五档判据 `CODE_VERIFIED`） | **high**（经 B02 数据反查，Table 4 十靶点两位小数全对上） | **high** |
| **direct baseline comparability** | **very high** | **very high** | **very high**（我们的 substrate） |
| **independent external validation** | **limited / same ecosystem** | **limited / same ecosystem** | **limited / same ecosystem** |

> 要补外部独立性，得靠**换验证器族**（B08 Latent-X 的 Chai-1 档、B09 ODesign 的 AF3 档、B06 BoltzGen 的 Boltz-2 档）或**换标签源**（B10 Cao、B11 Adaptyv），而不是在这三项内部互相印证。

---

## 表 6　客观总结（只描述，不排优先级）

### ① 最标准化的

按「固定题面 + 清单公开 + 判据明确 + 有维护方或榜」四条同时满足来看：

| | 为什么 |
|---|---|
| **M01 MotifBench** | 唯一同时有独立维护方和排行榜的设计 benchmark |
| **A01 RAbD** | 事实标准案例集，清单两处机器可读，四家以上在同一批上报数 |
| **A05 CHIMERA-Bench** | 三种划分 JSON 最规范，11 个方法同设置重训，榜随仓库 |
| **E01 AME** | 酶线唯一有固定案例清单 + 明确判据的 |
| **B02 ProtDBench** | 五档判据全部 `CODE_VERIFIED`，逐条设计分数全开 |

**反例值得记**：**M04 无条件生成协议**和 **E03 四配体惯例**普及度最高，但标准化最低——前者各家实现不统一，后者连样本数和验证器都不统一，**这两类的"横向对比数字"要打折看**。

### ② 最容易复现的（清单随仓库、拿了就能跑）

`B02 ProtDBench`（含 164 MB 现成数据）· `M01 MotifBench` · `M06 La-Proteina` · `E01 AME`（文档最全）· `E04 LigandMPNN 测试集` · `A05 CHIMERA-Bench` · `A06/N01 IgGM`（含预挖空 FASTA）· `A07/N02 CDR 逆折叠`（203 + 61，CSV）· `X01 PoseBusters`（pip 即得）· `X04 ipSAE`

**最不容易的**：`E07 PocketFlow`（仓库空）· `N06 EasyNano`（代码未发布）· `B08/P05 Latent-X`（商业）· `N04 nanoFOLD`（无清单无仓库）· `B13 BindEnergyCraft`（未放出）。`E02 Studio-179` 卡在任务 JSON 非法，但约十行代码可修。

### ③ baseline 可比性最强的

- **对我们**：`B02 / B03 / B04`——见表 5，同 substrate、同靶点、同判据（但**非独立验证**）
- **对领域**：`A01 RAbD`（同一批 60/55 上四家以上的数）· `A05 CHIMERA-Bench`（11 个方法**同设置重训**，这是比"各报各的"强得多的可比性）· `E01 AME`（跨组、固定清单、判据统一）· `M01 MotifBench`（榜）

### ④ 被独立组复用最多的

| 排序线索 | |
|---|---|
| **A01 RAbD** | ProteinBench、dyMEAN、DiffAb、AbDPO、CHIMERA —— **×4+** |
| **E03 四配体惯例** | RFAA、AtomFlow、DISCO、ODesign —— **×3**，但数字不可横比 |
| **A02 dyMEAN 三任务协议** | 被后续 co-design 论文大量沿用（协议复用，不只是数据集复用） |
| **B07 AF2-IG 惯例 / M04 scRMSD 协议** | 事实上被全领域继承 |
| **E01 AME** | ODesign、Proteína-Complexa —— **×2 跨组**，酶线最高 |
| **X01 PoseBusters / E04 LigandMPNN** | 作为**工具**被到处调用 |

**注意与 ⑤ 的区别**：复用最多的不一定 wet-lab 最强，也不一定最标准化。

### ⑤ wet-lab grounding 最强的

分两类，用法完全不同（§12.5）：

**可复用的标签数据**（不需要任何湿实验能力就能用）：
`B02 的 Cao 打分表`（236,246 条 × 8 打分器 / 1,485 阳性）· `B10 Cao 2022`（13 位点 × 万级，SC₅₀）· `X02 Overath`（3,766 条）· `B11 Adaptyv`（601 条 BLI）· `X03 Rocklin 组`（614 个）· `E08 COMPSS`（144 条活性）· `A08/A09 AbBiBench / FLAb`（21 万行 / 300 万条）· `A10 AIntibody`（511 条盲测）

**一次性验证实验，不可复用**（别人没法在上面比，也不能跟我们的 in-silico 数对标）：
AME 的 kcat/KM 53,000 · DISCO 的 TTN 4,050 · Germinal 的 BLI 4–22% · RFdiffusionAA 的 Kd 10 nM

### ⑥ 与 Proteo-AA 最相关的

**这一列是 annotation，不是选型。** 按"要不要新能力"分三层：

| 层 | 有哪些 | 说明 |
|---|---|---|
| **不需新能力**（`DIRECT_NOW`） | `B01–B04` 十靶点线（配置已复现，Protenix 本就是依赖）· `M04` 无条件生成 · `X01/X04` 检查器与指标 · 全部标签数据（`B10/B11/X02/X03/E08`） | binder 线 + 无条件线 + 打分器校准 |
| **要写接入代码**（`NEEDS_ADAPTER`） | `M01/M02/M03/M06` motif 线 · `P01–P03` 肽线 · `B05–B07/B09/B12` 其他 binder 协议 | **`M06 La-Proteina` 单独提**：唯一测**全原子 co-designability**，最贴我们的全原子 claim |
| **依赖我们还没有的条件化**（`FUTURE`） | 酶线 `E01–E07`、抗体线 `A01–A07`、纳米抗体线 `N01–N03`、大环肽 `P04/P05` | **缺口各不相同**，见下 |

**`FUTURE` 的缺口按 task 分，不是一句"缺 ligand conditioning"**：

| 缺什么 | 谁 |
|---|---|
| 配体条件化 + 残基级原子固定 | `E01` AME |
| 配体条件化 | `E02` Studio-179、`E03` 四配体、`E07` 口袋重设计 |
| 底物 + EC/功能条件化 + 功能预测器接口 | `E05` EnzyBench、`E06` EnzyBind |
| **残基级 framework 固定 + CDR mask** | `A01–A06`、`N01`、`N03` |
| 另加 H/L 双链配对语义 | `A01–A06` 的抗体轨道 |
| 表位条件化 | `A05` CHIMERA-Bench |
| 环状位置编码（独立拓扑能力） | `P04/P05` 大环肽 |

**一处形态观察**（`INFERRED`）：**N01 / N03 纳米抗体线在接口上离我们最近**——单链 + 抗原上下文，与已有 binder 设计只差"framework 残基级固定 + CDR mask"两件事，不需要新的分子类型支持；抗体轨道还多一层 H/L 配对语义。

### ⑦ 计算 / 适配成本最高的

| 量级 | 谁 |
|---|---|
| **劝退级** | `E01 AME 全量` = 41 × 100 × 8 = **32,800 次 Chai 折叠**，README 自己写单机跑不完；**逐靶点长度扫描**（BHRF1 41 个长度、IL-17A 91 个长度，比单长度贵几十倍） |
| **几十 GPU-天** | `E02 Studio-179`（179 × 150 → Chai-1）· `M06 La-Proteina`（26 × 200）· `A05 CHIMERA 全量` · `N03 Germinal`（幻觉 + 共折叠）· `E05/E06` |
| **适配成本最高**（不是算力，是接口） | 抗体线——要 IMGT/Chothia 编号与 CDR 边界解析、残基级 framework 固定、H/L 语义，这三样我们**一个都没有** |
| **外部依赖最重** | `B09/N03` 需 **AF3**（自行申请安装 + 数据库 + HMMER）· `E01/E02/B08` 需 **Chai-1**（并非所有 GPU 架构能跑）· `B05/P01/P03/P04` 需 **PyRosetta**（非学术用途要商业授权） |

**反过来，边际成本最低的**：`X01 PoseBusters`（CPU）· `X04 ipSAE`（CPU，可加在任何 AF2/AF3 输出上）· `B02` 的 `ptx*` 三档（Protenix 本就在 `PXDesign-train/Protenix/`）· 全部标签数据（不需生成）。

---

## 不在本文件范围内

- **不给 RUN / DO NOT RUN。** 表 3 的 `Proteo-AA 兼容性`、表 4 的 `综合`、表 6 的七条都是**描述**，不是推荐。
- **不排最终优先级。** 等这张表被横向比较过之后统一做。
- **不追剩余 unresolved**（表 3 最后一列列全了）。五大类源码级核实到 §16 为止。
