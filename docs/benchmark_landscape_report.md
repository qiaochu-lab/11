# Protein design evaluation：benchmark landscape

**内部汇报版** · 2026-09-15 · 横向调研，非选型

这份是**调研汇报**：别人怎么 benchmark 蛋白设计。**不做 benchmark 选型，不给 RUN / DO NOT RUN，不排优先级。**

详细版留在 source of truth：`docs/design_eval_landscape.md`（逐条 recipe + 源码核对 + unresolved）、`docs/design_eval_summary.md`（59 条完整 inventory）。本文只取横向比较需要的那一层。

---

## 一、六类任务总览

蛋白设计的评估不是一套标准，而是**六类各自独立的评估传统**——考的能力不同、输入输出不同、验证器不同，数字之间基本不可横比。

| 类别 | 考什么能力 | 典型输入 | 典型输出 | 常见 evaluator / metric | 代表 benchmark / paper | 对 Proteo-AA 的意义 |
|---|---|---|---|---|---|---|
| **binder / miniprotein** | 给定靶点+表位，能否造出结合物 | 靶点结构 + 裁剪范围 + hotspot | binder 序列 + 复合物坐标 | AF2-IG / Protenix / Chai-1 / Boltz-2；pLDDT、ipTM、ipAE、bound-unbound RMSD | [AlphaProteo](https://arxiv.org/abs/2409.08022)、[PXDesign](https://doi.org/10.1101/2025.08.15.670450)、[A-CODE](https://arxiv.org/abs/2605.03360)、[ProtDBench](https://arxiv.org/abs/2605.04118)、[BindCraft](https://github.com/martinpacesa/BindCraft)、[BoltzGen](https://github.com/HannesStark/boltzgen) | **最直接**。靶点配置已复现，Protenix 本就是依赖，产物形态就是我们在做的事 |
| **monomer / unconditional** | 无条件生成可折叠的单体 | 只给长度 | 骨架（+ MPNN 序列） | ProteinMPNN → ESMFold，取最小 scRMSD < 2 Å；另报多样性/新颖性 | [ProteinBench](https://arxiv.org/abs/2409.06744)、FrameFlow / FoldFlow 系惯例 | 不需任何条件化接口，**形态上直接可跑**；但只测骨架自洽，测不到全原子 |
| **motif scaffolding** | 给定功能位点，能否长出支撑它的支架 | motif 残基坐标（部分含全原子） | 支架骨架 + 序列 | ProteinMPNN → ESMFold → Kabsch RMSD；Foldseek 查唯一性 | [MotifBench](https://arxiv.org/abs/2502.12479)、[RFdiffusion motif](https://github.com/RosettaCommons/RFdiffusion)、[La-Proteina](https://github.com/NVIDIA-BioNeMo/la-proteina) | 多数 **needs adapter**：motif 条件化与我们的推理语义不一致。La-Proteina 是唯一测**全原子 co-designability** 的，最贴我们的全原子 claim |
| **peptide** | 小尺度 target-conditioned 设计 / 环化拓扑 | 受体结构（多为天然复合物） | 肽序列 + 结构 | 多数**无结构预测器**，直接对晶体结构：Cα RMSD 分档、AAR、PyRosetta ΔG<0 | [PepGLAD / PepBench](https://github.com/THUNLP-MT/PepGLAD)、RFpeptides（大环，无公开 artifact） | 重建类任务**有真值肽**，能直接量全原子 RMSD——binder 线给不了这类证据。大环需环状位置编码，是独立能力 |
| **enzyme / ligand** | 配体/底物条件下造催化环境 | 配体 + 催化残基全原子（或 EC 号/底物） | 酶骨架 + 序列 | LigandMPNN → Chai-1；催化重原子 RMSD < 1.5–2 Å + 配体撞车 / PoseBusters | [AME](https://github.com/RosettaCommons/RFdiffusion2)、四配体 convention（SAM/OQO/FAD/IAI）、[Studio-179 / DISCO](https://arxiv.org/abs/2604.05181) | **future interface capability**：缺配体条件化；部分还要残基级原子固定，或 EC/功能条件化 |
| **antibody / nanobody** | 给定 framework 改 CDR（**不是完整抗体从头设计**） | 天然复合物 + **完整 framework** + 抗原 | CDR 序列 + 结构 | 多数**无结构预测器**，直接对天然结构：AAR、CAAR、DockQ、表位 F1 | [RAbD](https://github.com/THUNLP-MT/dyMEAN)、[CHIMERA-Bench](https://arxiv.org/abs/2603.13431)、AIntibody（Nat Biotechnol 盲测挑战） | **future interface capability**：缺残基级 framework 固定 + CDR mask + H/L 配对语义。VHH 单链离我们最近 |

> **一个贯穿全表的观察**：binder 和 motif 这两类靠**结构预测器重折**来判成功；antibody、peptide、enzyme 的主流反而是**直接对天然/晶体结构打分**。后者省掉一整套验证器环境，但它测的是"能否复现已知答案"，不是"能否设计新东西"。

---

## 二、代表性 benchmark 横向比较

**并列条目，不是发展路线。** AlphaProteo / PXDesign / A-CODE / ProtDBench 共用同一批十个靶点，但它们是**四个独立条目**——采样协议、过滤档、artifacts 状态各不相同；与我们的特殊关系只写在最后一列。

| Work | 类型 | cases | evaluator | threshold type | wet-lab / label grounding | independent reuse | artifacts reproducibility | Proteo-AA relevance |
|---|---|---|---|---|---|---|---|---|
| [**AlphaProteo**](https://arxiv.org/abs/2409.08022) | method + 靶点规格 | 10 靶点（8 做湿实验） | AF2 类 | 绝对 | ✅ 8 靶点，7 成功 | ✅ 被 2 个生态取用 | ⚠️ 无代码；**靶点规格可逐字符对上** | **very high**（我们复现的就是这批靶点） |
| [**PXDesign**](https://doi.org/10.1101/2025.08.15.670450) · [repo](https://github.com/bytedance/PXDesignBench) | method + evaluation framework | 10 蛋白 + 12 环肽 | AF2-IG、Protenix | 绝对 | ✅ | ⚠️ | ✅ 代码开放 | **very high** — **我们的 substrate 就是它** |
| [**A-CODE**](https://arxiv.org/abs/2605.03360) | method | 10 靶点，每靶点 328–728 条 | AF2-IG（`af2_easy` 档） | 绝对 | ❌ | ⚠️ 太新 | ⚠️ 无代码；经 ProtDBench 数据反查，Table 4 十靶点**两位小数全对上** | **very high** — 直接拿 PXDesign 当 baseline，与我们同坐标系 |
| [**ProtDBench**](https://arxiv.org/abs/2605.04118) · [repo](https://github.com/congliuUvA/ProtDBench) | **evaluation framework** | 同十靶点 + 5 Cao 靶点；22,720 条设计 | **一批设计同时五档打分**：AF2-IG / ColabFold / Protenix(-Mini) / Boltz / Chai-1 / ESMFold | 绝对（五档并列） | ⚠️ 借 Cao 标签，但**带 236,246 条设计 × 8 打分器** | ⚠️ 太新 | ✅✅ **本表最硬**：164 MB 数据随仓库，我们用它复算过 | **very high** — 判据全部源码可核，边际成本最低 |
| [**BindCraft**](https://github.com/martinpacesa/BindCraft) | method | 12 靶点 | AF2-multimer 设计 + AF2 单体重预测 | 绝对 | ✅ | ✅ 判据被 ProtDBench 收成一档 | ✅ | needs adapter |
| [**BoltzGen**](https://github.com/HannesStark/boltzgen) | method | 10 低同源新靶点 + 5 简单 | **Boltz-2** | 绝对（**ipAE 取最小值非均值**） | ✅ 8 场湿实验 / 26 靶点 | ⚠️ | ✅ | needs adapter — 但**换验证器族**的价值在这 |
| [**MotifBench**](https://arxiv.org/abs/2502.12479) · [repo](https://github.com/blt2114/MotifBench) | **benchmark** | **30 题** × 100 骨架 × 8 序列 | ProteinMPNN → ESMFold；Foldseek 查唯一性 | 绝对 | ❌ | ✅ | ✅ 题面随仓库 | needs adapter — **这一类唯一有独立维护方 + 排行榜的** |
| [**RFdiffusion motif 集**](https://github.com/RosettaCommons/RFdiffusion) | protocol | 25 题 | ProteinMPNN + AF2 | 绝对 | ✅ | ✅ 被 Genie2 等直接继承 | ⚠️ | needs adapter |
| [**La-Proteina**](https://github.com/NVIDIA-BioNeMo/la-proteina) | protocol | **26 个全原子 motif 任务** | **全原子 co-designability** 2.0 Å | 绝对 | ❌ | ⚠️ | ✅ `motif_dict.yaml` 随仓库 | needs adapter — **唯一测全原子 co-designability**，最贴我们的 claim |
| [**PepGLAD / PepBench**](https://github.com/THUNLP-MT/PepGLAD) | benchmark（固定划分） | 190（PepBDB，随仓库）/ 93（LNR，Zenodo） | **无结构预测器**，对晶体肽 | 绝对（RMSD 分档 + ΔG<0） | ❌ | ✅ LNR 被多家用 | ✅ 清单随仓库 | needs adapter — **有真值肽**，可直接量全原子 RMSD |
| [**AME**](https://github.com/RosettaCommons/RFdiffusion2) | **benchmark** | **41 个活性位点**（M-CSA × PARITY） | LigandMPNN → Chai-1；催化重原子 RMSD < 1.5 Å | 绝对 | ✅ | ✅ **×2 跨组** | ✅ JSON + 41 PDB，文档最全 | future interface（配体 + 残基级原子固定）— **酶线唯一有跨论文可比性的** |
| **四配体 convention**（SAM/OQO/FAD/IAI） | **convention**（非 benchmark） | 4 个分子 | **各家不同**：AF2 / AF3 / Chai-1 / RF3 | **无统一阈值** | ✅ 原文有 | ✅ **×3，复用最广** | ❌ **无清单、无统一样本数与验证器 → 数字不可横比** | future interface（配体） |
| [**Studio-179 / DISCO**](https://arxiv.org/abs/2604.05181) · [repo](https://github.com/DISCO-design/DISCO) | benchmark | 179 = 170 配体 + 9 组合 | Chai-1（骨架 + 配体质心 RMSD < 2 Å）、AF3、PoseBusters | 绝对 | ⚠️ benchmark 部分无 | ❌ **无第三方复用** | ⚠️ SDF 有、**任务 JSON 非法**（约十行代码可修） | future interface（配体） |
| [**RAbD**](https://github.com/THUNLP-MT/dyMEAN) | **事实标准案例集** | **60**（ML 圈常用筛后 55） | Rosetta 能量、序列恢复率 | **无，只排名** | ❌ | ✅✅ **×4+，全表最广** | ⚠️ 清单两处机器可读，但**60→55 的筛选规则未见定义** | future interface（framework 固定 + CDR mask） |
| [**CHIMERA-Bench**](https://arxiv.org/abs/2603.13431) · [repo](https://github.com/mansoor181/chimera-bench) | **benchmark + leaderboard** | **2,922 复合物**，3 种划分 | 无结构预测器，对天然结构 | **无，mean±std 排名** | ❌ | ⚠️ 太新 | ✅ splits JSON 最规范；**榜随仓库，11 个方法同设置重训** | future interface（+ 表位条件化） |
| **AIntibody**（Nat Biotechnol） | **社区盲测挑战** | 29 家机构 511 条 AI 设计抗体 | **真做实验**（含 KinExA） | 实测 | ✅✅ **前瞻性盲测** | ✅ 本身即多组共建 | ❌ 是竞赛，不是可下载数据集 | — |

---

## 三、这轮调研真正的发现

### 1. fixed benchmark ≠ widely reused convention

**复用最广的往往不是最标准化的。** 酶线的**四配体 convention** 跨 3 个独立组，是这一类里复用最广的；但它没有清单、没有统一样本数、没有统一验证器——**各家数字不可横比**。反过来 **AME** 清单固定、判据明确，复用面稍窄（×2）却是酶线唯一有跨论文可比性的。

单体线同理：**scRMSD < 2 Å 那套惯例**人人在用，但各家实现不统一，"横向对比数字"要打折看。

### 2. wet-lab strong ≠ reproducible benchmark

这两件事经常反向：

| | wet-lab | artifacts |
|---|---|---|
| Latent-X | ✅ 7 靶点 | ❌ 商业，代码权重都不公开 |
| AIntibody | ✅✅ 前瞻性盲测 | ❌ 是竞赛不是数据集 |
| 四配体 convention | ✅ | ❌ 无清单 |
| CHIMERA-Bench | ❌ | ✅ 榜 + splits 最规范 |
| MotifBench | ❌ | ✅ 题面随仓库 + 独立维护 |

所以「这个 benchmark 可信吗」要拆成两个问题分别问。我们加了一列专门问最硬的那个：**放出来的东西能不能把论文里的数算回来**。

### 3. same-group reuse ≠ independent validation

**AlphaProteo / PXDesign / A-CODE / ProtDBench 共用十个靶点，但这不构成互相验证**——它们作者与生态高度重叠。

这不影响它们是我们最重要的参考线：Proteo-AA 基于 PXDesign 改、A-CODE 直接拿 PXDesign 做 baseline、ProtDBench 把这套 evaluation 系统化可复跑,所以 **direct baseline comparability 极高**。但两件事要分开说：

> `Proteo-AA relevance: very high` · `direct baseline comparability: very high` · `reproducibility: high` · **`independent external validation: limited / same ecosystem`**

要补外部独立性，得**换验证器族**（Chai-1 / AF3 / Boltz-2）或**换标签源**（Cao、Adaptyv），不能在这四项内部互相印证。

### 4. 不同 verifier 会显著改变 success rate

这是最容易被忽略的一条，有三层：

**(a) 换打分器，方法排名就变。** 拿 236,246 条有湿实验标签的设计回测八个打分器的 ipAE AUC：ColabFold **0.801** 最高，而全领域事实标准、也是我们现在用的 **AF2-IG 只有 0.727，排第 6**。在 0.63% 的基础命中率下这个区分度是弱的。另外两条：ipAE 一致优于 ipTM、更优于 pLDDT；**新的不一定更好**——Boltz-2 (0.703) 低于 Boltz-1 (0.729)。

> 局限要一起说：Cao 的设计是 Rosetta 时代能量法的产物，排名未必能迁移到生成模型的设计上；ESMFold 是单序列模型，这里 AUC 低属预期，**不能据此否定它在单体自洽评估里的用途**。

**(b) 换过滤档，同一批设计的成功率差两个数量级。** ProtDBench 的五档是**同一批设计同时打的**，所以这是纯粹的判据效应，不掺方法差异：

| | 均值 | H1 | IL17A | PDL1 |
|---|---:|---:|---:|---:|
| `af2_easy` | 21.19 | 12.08 | 0.82 | 45.33 |
| `af2_opt` | 9.70 | **0.04** | **0.00** | 31.16 |

H1 从 12.08 掉到 0.04（约 300 倍），IL17A 直接归零，但 PDL1 只掉三成。**所以报成功率必须说明是哪一档**，而且不同靶点对档位的敏感度完全不同。

**(c) 量纲坑。** `ipAE` 有两套量纲（归一化 = 原始 / 31），所以 `0.35` 其实 ≈ 10.85 Å，比 `7.0` 更**松**而不是更严。`ipAE` 还分取**最小值**（Latent-X、BoltzGen）和取**均值**（RFdiffusion、Adaptyv）。直接比数字会得到相反结论。

另外 **threshold type 有三种哲学同时存在**：绝对固定、逐靶点相对浮动（BOND-PEP 要超过天然肽自己的 ipTM）、逐靶点重调。混报会让"成功率"无法解释。

### 5. 对 Proteo-AA：三层，缺口各不相同

| 层 | 哪些类别 | 缺什么 |
|---|---|---|
| **direct** | binder / miniprotein、unconditional monomer | 不缺能力。靶点配置已复现，Protenix 本就是依赖 |
| **needs adapter** | motif scaffolding、peptide（线性/重建） | 要写接入代码：motif 条件化语义、真值肽比对 |
| **future interface capability** | enzyme / ligand、antibody / nanobody、大环肽 | **缺的不是同一样东西** |

`future` 这一层的缺口必须按 task 分，不能归成一句"缺 ligand conditioning"：

| 缺什么 | 谁 |
|---|---|
| 配体条件化 + 残基级原子固定 | AME |
| 配体条件化 | 四配体 convention、DISCO、口袋重设计 |
| 底物 + EC/功能条件化 | EnzyBench、EnzyBind |
| **残基级 framework 固定 + CDR mask** | RAbD、CHIMERA、IgGM 等全部抗体线 |
| 再加 H/L 双链配对语义 | 抗体轨道（VHH 不需要） |
| 表位条件化 | CHIMERA-Bench |
| 环状位置编码 | 大环肽 |

**一处形态观察**：**VHH（单链纳米抗体）在接口上离我们最近**——单链 + 抗原上下文，与已有 binder 设计只差"framework 残基级固定 + CDR mask"两件事，不需要新的分子类型支持。抗体轨道还多一层 H/L 配对语义。

### 附：一个要先说清的术语

"designability" 在文献里有**三个不同意思**，混用会让数字不可比：

| 说法 | 序列从哪来 | 比什么 |
|---|---|---|
| designability | ProteinMPNN 重新生成 | 骨架 RMSD |
| co-designability | **模型自己产的序列** | 骨架 RMSD |
| **all-atom co-designability** | 模型自己产的序列 | **全原子 RMSD** |

**只有第三个测得到我们的全原子 claim**，而目前只有 La-Proteina 的协议在测它。

---

*完整 59 条 inventory、逐条源码核对、unresolved 清单见 `docs/design_eval_summary.md` 与 `docs/design_eval_landscape.md`。*
