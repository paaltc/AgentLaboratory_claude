# Dataset Summary: IDM-CICDFL Research

**Date**: November 17, 2025  
**Status**: Data Preparation Phase Complete  
**Output File**: `/home/user/AgentLaboratory_claude/multiagent_test/dataset_info.md`

---

## Key Findings

### Recommended Datasets by Priority

#### 1. HIGHEST PRIORITY - AgentErrorBench
- **Status**: Recently published (Sept 29, 2025)
- **Size**: 1000+ annotated failure trajectories
- **Perfect Alignment**: Directly tests agent failure learning and debugging
- **Key Advantage**: Comes with AgentErrorTaxonomy (memory, reflection, planning, action, system failures)
- **Mapping**: Can be directly adapted to CI/CD failure layers
- **Performance Baseline**: AgentDebug framework achieves 24% improvement over baseline
- **Repository**: https://github.com/thinkwee/AgentErrorBench

**Why HIGHEST**: This is the primary dataset that validates your core hypothesis about failure learning in agentic systems. It's state-of-the-art and directly applicable.

#### 2. HIGH PRIORITY - Defects4J  
- **Size**: 854 real bugs from 17 Java projects
- **Real-World Data**: Production-quality bug dataset from established research
- **Per-Bug Artifacts**: Buggy code, fixed code, failing test cases, full test suite
- **Coverage**: 85%+ are test failures (matches Phase 1 target)
- **Transfer Learning**: Enables leave-one-project-out cross-validation
- **Repository**: https://github.com/rjust/defects4j

**Why HIGH**: Provides real, reproducible failures with ground-truth fixes for validating hierarchical analysis and transfer learning hypotheses.

#### 3. HIGH PRIORITY - Log Anomaly Datasets
- **HDFS Logs**: 575k sequences from distributed systems
- **BGL Logs**: 4.7M messages from supercomputers  
- **LO2 Dataset**: Modern microservice logs with metrics + traces
- **Coverage**: Infrastructure layer failures (5-10% of CI/CD benchmark)
- **Authenticity**: Real system-level failures, not synthetic

**Why HIGH**: Addresses infrastructure layer requirements and enables multi-modal failure analysis (logs + metrics + traces).

#### 4. MEDIUM PRIORITY - CodeXGLUE
- **Size**: 1M+ code examples across 14 tasks
- **Key Task**: Code Repair (Bugs2Fix) - buggy code → fixed code
- **Languages**: Java, Python, C#, JavaScript, PHP, Go, Ruby, Rust
- **Defect Detection**: Binary classification of buggy vs. clean code
- **Source**: Microsoft Research, established benchmark

**Why MEDIUM**: Provides code-level repair patterns and defect detection, useful for application and compilation layers.

#### 5. MEDIUM PRIORITY - BART Maven Dataset
- **Specialization**: Maven build-specific failures
- **Failure Types**: Compilation, testing, dependencies, plugins, code analysis
- **Key Feature**: Raw logs (40k lines) → concise summaries (14 lines)
- **Effectiveness**: 41% average build-fix time reduction in user studies
- **Replication Package**: https://zenodo.org/record/3346615

**Why MEDIUM**: Build layer specificity valuable for Phase 1 benchmark compilation error component (20-25%).

---

## Coverage Analysis

### Research Objectives Coverage

| Objective | Supporting Datasets | Coverage |
|-----------|-------------------|----------|
| H1: Dynamic Memory Organization | AgentErrorBench, Defects4J | Strong - both have failure trajectories |
| H2: Hierarchical Analysis | All (layer-specific datasets) | Strong - can map across 5 CI/CD layers |
| H3: Step-wise RL Learning | LiveCodeBench, HumanEval, CodeXGLUE | Strong - clear test feedback signals |
| H4: Linguistic Feedback | AgentErrorBench, BART, Reflexion | Strong - explanations documented |
| H5: Cross-project Transfer | Defects4J (17 projects), multiple datasets | Strong - enables LOPO evaluation |
| Phase 1: 500+ failure benchmark | All datasets combined | Achievable - 500-1000 failures available |

### CI/CD Layer Coverage

| Layer | Primary Dataset | Secondary Datasets |
|-------|-----------------|-------------------|
| Application | Defects4J | CodeXGLUE, Deep-Bench |
| Build | BART Maven | CodeXGLUE, Defects4J |
| Test | Defects4J, LiveCodeBench | CodeXGLUE, MBPP, HumanEval |
| Deployment | Log datasets | BART, CodeXGLUE |
| Infrastructure | HDFS, BGL, LO2 | Log Anomaly tools |

---

## Quantitative Summary

### Total Dataset Capacity

```
AgentErrorBench:      ~1,000 trajectories
Defects4J:            854 bugs
HDFS Logs:            575,061 sequences
BGL Logs:             4,700,000 messages
CodeXGLUE:            1,000,000+ examples
BART:                 Variable (hundreds of build failures)
LiveCodeBench:        612 problems
HumanEval:            164 problems
StaQC:                268,000 Q&A pairs
LO2:                  Production-scale

TOTAL: 7M+ data points across multiple modalities
```

### Storage Estimates

| Dataset | Size | Storage |
|---------|------|---------|
| AgentErrorBench | Small (~1k) | <1GB |
| Defects4J | Medium (854) | ~10GB |
| Log Datasets | Large (5.7M+) | ~50-100GB |
| CodeXGLUE | Very Large (1M+) | ~20-50GB |
| BART Maven | Medium | ~5GB |
| Others | Combined | ~100GB |
| **TOTAL** | **7M+ items** | **200-300GB** |

**Infrastructure Requirements**: 500GB-1TB recommended for full preparation + preprocessing

---

## Preprocessing Workflow (Months 1-3)

### Week 1-2: Dataset Acquisition
- [ ] Download all primary datasets (parallel, may take 24-48 hours)
- [ ] Verify checksums and integrity
- [ ] Extract and organize in consistent directory structure
- [ ] Document license and citation requirements

### Week 3-4: Unified Framework Creation
- [ ] Implement DatasetLoader classes for each source
- [ ] Define unified failure schema (13 key fields)
- [ ] Create mapping functions for heterogeneous formats
- [ ] Implement preprocessing pipelines

### Week 5-6: Annotation and Integration
- [ ] Apply layer classification (5-layer CI/CD hierarchy)
- [ ] Extract root causes and failure types
- [ ] Perform inter-rater reliability checks (if team available)
- [ ] Generate statistics and coverage reports

### Week 7-8: Validation and Optimization
- [ ] Verify annotation consistency
- [ ] Create train/val/test splits (70%/15%/15%)
- [ ] Perform baseline system validation
- [ ] Document final benchmark characteristics

---

## Implementation Priority

### Immediate Actions (This Week)

1. **Download AgentErrorBench** (HIGHEST PRIORITY)
   ```bash
   git clone https://github.com/thinkwee/AgentErrorBench.git
   ```
   
2. **Get Defects4J Framework**
   ```bash
   git clone https://github.com/rjust/defects4j.git
   # Follow installation: https://github.com/rjust/defects4j#getting-started
   ```

3. **Access Log Datasets**
   - HDFS/BGL: https://github.com/ait-aecid/anomaly-detection-log-datasets
   - LO2: https://arxiv.org/abs/2504.12067 (latest 2025 release)

### Short-term (Weeks 2-4)

4. **Load CodeXGLUE** from HuggingFace
   ```python
   from datasets import load_dataset
   codexglue = load_dataset("microsoft/codeXGLUE")
   ```

5. **Get BART Replication Package**
   - https://zenodo.org/record/3346615

### Medium-term (Weeks 5-8)

6. **Create Unified Benchmark**
   - Merge 5 primary datasets into single annotated collection
   - Target: 500-1000 failures with consistent schema

---

## Key Strengths of Selected Datasets

1. **Real-World Data**: All primary datasets contain production failures
2. **Comprehensive Annotations**: Failure types, root causes, fixes well-documented
3. **Multi-Modal**: Supports logs, code, trajectories, metrics
4. **Established Benchmarks**: Used in published research (reduces validation work)
5. **Scalability**: Total capacity of 7M+ data points allows:
   - Large-scale pretraining (if needed)
   - Robust evaluation across subsets
   - Transfer learning across projects/systems
6. **Layer Alignment**: Can map to 5-layer CI/CD hierarchy
7. **Cross-Project Opportunities**: Multiple projects enable LOPO validation

---

## Potential Challenges & Mitigations

| Challenge | Mitigation |
|-----------|-----------|
| Storage requirements (500GB-1TB) | Use cloud storage, incremental loading, compression |
| Java-heavy (Defects4J) | Supplement with Python/multi-language datasets (CodeXGLUE) |
| Different annotation formats | Create unified schema + mapping functions |
| Log dataset complexity (HDFS/BGL) | Pre-built anomaly labels + parsing tools available |
| AgentErrorBench freshness | Recent paper (Sept 2025) - API may still be evolving |
| Processing time | Parallelize across cores; use existing preprocessing tools |

---

## Success Metrics for Data Preparation

**Phase 1 Success Criteria** (3 months):

- [x] Identified 13+ suitable datasets with clear relevance
- [x] Documented loading code for each dataset  
- [x] Mapped datasets to 5-layer CI/CD hierarchy
- [x] Planned unified benchmark schema
- [ ] Downloaded and verified dataset integrity
- [ ] Implemented loading utilities for all datasets
- [ ] Created merged benchmark (500+ failures)
- [ ] Validated annotations and generated statistics
- [ ] Baseline systems operational on benchmark

---

## Alignment with Research Plan

This dataset preparation directly supports:

✓ **Phase 1 Architecture Design** (Months 1-3)
  - Datasets provide real failure examples for architecture validation
  - Benchmark suite creation supported by existing datasets

✓ **Phase 2 Hypothesis Testing** (Months 4-8)
  - AgentErrorBench: Tests H1 (dynamic memory) and agent learning
  - Defects4J: Tests H2 (hierarchical analysis) and H5 (cross-project transfer)
  - Log datasets: Tests infrastructure layer detection
  - CodeXGLUE: Tests H3 (step-wise RL) with clear test feedback

✓ **Phase 3 Industrial Validation** (Months 9-12)
  - Real datasets provide authentic failure patterns
  - Log datasets enable deployment on real systems

---

## Next Steps

### Week 1 Actions:
1. Share this summary with advisor for dataset confirmation
2. Verify computational resources (storage, bandwidth)
3. Begin downloading primary datasets in parallel
4. Review data licenses and terms of use

### Week 2-3:
5. Implement unified DatasetLoader framework
6. Create preprocessing pipelines for each dataset
7. Begin annotation schema refinement

### Week 4 onwards:
8. Execute full data preparation workflow
9. Generate statistics and coverage reports
10. Validate with baseline systems

---

## References and Resources

**Primary Papers**:
- Zhu et al. (2025): AgentErrorBench - arXiv:2509.25370
- Just et al. (2014): Defects4J - ISSTA 2014
- Deng et al. (2021): CodeXGLUE - arXiv:2102.04664
- Vassallo et al. (2019): BART - Empirical Software Engineering

**Repository Links**:
- Dataset Documentation: `/home/user/AgentLaboratory_claude/multiagent_test/dataset_info.md` (814 lines, 28KB)
- Research Plan: `/home/user/AgentLaboratory_claude/multiagent_test/research_plan.md`

---

**Prepared by**: ML Engineer (Data Preparation Phase)  
**Date**: November 17, 2025  
**Status**: Ready for advisor review and implementation approval
