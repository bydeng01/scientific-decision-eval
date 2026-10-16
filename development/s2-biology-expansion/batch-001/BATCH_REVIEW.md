# Biological S2 case review

The collection contains 16 non-biological groups and 4 biological groups: **20 total**. User-approved biological references cover 4 groups and 8 Choices. Review attribution for the original and non-biological expansion groups is recorded in their case packages.

| Group | Scientific distinction | Questions | Status |
| --- | --- | --- | --- |
| [B001](BATCH_REVIEW.md#b001) | Developmental exposure of future-generation germ cells | 2 | user_reviewed |
| [B002](BATCH_REVIEW.md#b002) | Clonal amplification separates mutation origins from colony counts | 2 | user_reviewed |
| [B003](BATCH_REVIEW.md#b003) | Pre-assay pooling merges outcomes and reuses the same contributors | 2 | user_reviewed |
| [B004](BATCH_REVIEW.md#b004) | Somatic mosaicism and a non-specific germline phenotype marker | 2 | user_reviewed |

<a id="b001"></a>

## B001: Prenatal dosing and the generations reached by one exposure window

Status: **user_reviewed**. User approval covers both Choices, reference answers, evidence scope, and inference boundary.

**Target treatment:** The original gestational dioxin (TCDD) injection regimen, distinguished from descendant lineage membership.

**Scope:** The Dioxin row in Supplemental Tables S1B and S1C, generations F1-F3, and the original F0 gestational exposure. Other chemicals, toxicity outcomes, effect sizes, and mechanisms of inheritance are outside this claim.

### Source evidence

[BIO-EXP-2012](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0031901): Manikkam et al. (2012). Transgenerational Actions of Environmental Compounds on Reproductive Disease and Identification of Epigenetic Biomarkers of Ancestral Exposures. PLOS ONE 7(2): e31901. DOI: 10.1371/journal.pone.0031901. Published article and linked Supplemental Table S1 (.s007).

**Evidence 1 — Main PDF p. 2, Results; p. 9, treatment and breeding methods**

Only pregnant F0 rats received the experimental injections, during embryonic days 8-14. F1 animals were bred within exposure lineage to produce F2, and F2 produced F3; sibling and cousin crosses were avoided. The paper distinguishes the injected F0 mother, the directly exposed F1 embryo, and the germ cells inside that embryo that will generate F2. F3 lies beyond this original direct-exposure window under the paper's generational definition.

**Evidence 2 — Supplemental Table S1B, PDF p. 1; Table S1C, PDF p. 2; Dioxin row**

The Dioxin lineage has 4, 14, and 14 weaned litters in F1, F2, and F3. Female/male pup counts are 15/20, 68/78, and 84/78, respectively. These are descendant census records, not a register of newly injected animals or individual pedigrees.

These passages are source-faithful adaptations, not verbatim quotations.

### Claim to assess

The 162 F3 Dioxin-lineage pups are 162 newly injected TCDD treatment units, and F2 is the first descendant generation beyond the original direct-exposure window.

This claim was constructed for the case; it is not attributed to the source authors.

### Structured source records

```json
{
  "census": [
    {
      "lineage": "Dioxin",
      "generation": 1,
      "weaned_litters": 4,
      "female_pups": 15,
      "male_pups": 20
    },
    {
      "lineage": "Dioxin",
      "generation": 2,
      "weaned_litters": 14,
      "female_pups": 68,
      "male_pups": 78
    },
    {
      "lineage": "Dioxin",
      "generation": 3,
      "weaned_litters": 14,
      "female_pups": 84,
      "male_pups": 78
    }
  ],
  "record_origin": "Selected Dioxin rows transcribed from rendered Supplemental Tables S1B/S1C; generation numbers encode the source F labels."
}
```

### Atomic Choices

#### B001-Q01

To which animals was the original experimental injection regimen administered? Select exactly one option using the supplied evidence and stated scope. Do not count records, perform arithmetic, or assign the final claim label; code does that. Choose conflicting before any other option if unresolved statements are incompatible about this judgment in this scope. Choose other only for an established substantive answer outside the listed alternatives. Choose not_stated when missing, partial, or ambiguous evidence prevents the requested judgment without a conflict. Partial evidence is sufficient for a substantive option only when it establishes that option as worded; do not infer missing details.

- **`f0_pregnant_dams`**: The pregnant F0 females received the regimen; descendants were not separately injected with that experimental regimen.
- **`each_generation`**: Animals in every generation from F0 through F3 separately received the regimen.
- **`f3_animals`**: The F3 animals received the regimen; the F0 females did not.
- **`isolated_germ_cells`**: Isolated germ cells received the regimen outside the animals; pregnant females were not injected.
- **`other`**: The evidence establishes a substantive answer outside the listed alternatives.
- **`not_stated`**: Missing, partial, or ambiguous evidence does not establish the requested judgment, and no unresolved contradiction is present.
- **`conflicting`**: Unresolved evidence gives incompatible accounts of this judgment within the stated scope.

#### B001-Q02

Which biological compartments does the source place within the original F0 gestational direct-exposure window? Select exactly one option using the supplied evidence and stated scope. Do not count records, perform arithmetic, or assign the final claim label; code does that. Choose conflicting before any other option if unresolved statements are incompatible about this judgment in this scope. Choose other only for an established substantive answer outside the listed alternatives. Choose not_stated when missing, partial, or ambiguous evidence prevents the requested judgment without a conflict. Partial evidence is sufficient for a substantive option only when it establishes that option as worded; do not infer missing details.

- **`maternal_soma_only`**: Only the F0 mother is within that window; neither the F1 embryo nor its developing germ cells is included.
- **`mother_and_fetal_soma_only`**: The F0 mother and F1 embryo are included, but the germ cells that will generate F2 are excluded.
- **`mother_embryo_and_fetal_germline`**: The F0 mother, F1 embryo, and germ cells within that embryo that will generate F2 are included.
- **`all_descendants`**: Every later descendant generation remains directly exposed to the original administered compound merely by belonging to the lineage.
- **`other`**: The evidence establishes a substantive answer outside the listed alternatives.
- **`not_stated`**: Missing, partial, or ambiguous evidence does not establish the requested judgment, and no unresolved contradiction is present.
- **`conflicting`**: Unresolved evidence gives incompatible accounts of this judgment within the stated scope.

### Accepted reference answers — evaluation only

**B001-Q01: `f0_pregnant_dams`** — user_reviewed

The treatment and breeding descriptions restrict experimental injections to F0 pregnant females. Descendant census entries do not record new administration.

Downstream role: Select administration recipients before code separates F3 census size from F3 injection count.

**B001-Q02: `mother_embryo_and_fetal_germline`** — user_reviewed

The Results explicitly include the F1 embryo and its F2-producing germ cells in the original exposure window. No repeat injection is required for that developmental exposure.

Downstream role: Map the biological compartments to generation indices; code finds the first later generation outside the original window.

### Deterministic derivation

Filter the Dioxin census and F3 rows; add female and male counts. Use the administration relation to derive the number of newly injected F3 animals. Encode the included developmental compartments as F0/F1/F2 and find the first later generation outside that window. Compare each clause separately.

Expected output with the accepted references:

```json
{
  "status": "derived",
  "semantic_choices": [
    "f0_pregnant_dams",
    "mother_embryo_and_fetal_germline"
  ],
  "counts": {
    "F3_pups": 162,
    "F3_weaned_litters": 14,
    "newly_injected_F3_animals": 0,
    "first_generation_beyond_original_window": 3,
    "distinct_F0_ancestors": null
  },
  "clauses": {
    "new_F3_injections": "inconsistent",
    "first_generation_beyond_window": "inconsistent"
  },
  "final_label": "inconsistent"
}
```

A missing or illegal answer is an input error. `conflicting`, `other`, and `not_stated` stop group-level composition, in that precedence order. Unknown scientific quantities remain null. With substantive answers, an inconsistent clause makes the conjunction inconsistent; an unknown clause remains separately visible.

### Inference boundary

This audits administration and developmental exposure accounting, not the reported toxicological effects or an epigenetic mechanism. F3 being outside the original window is a protocol-defined classification, not a chemical measurement or proof of inheritance. The number of distinct F0 ancestors represented by the selected F3 animals remains unknown; litter totals are not a pedigree.

---

<a id="b002"></a>

## B002: Culture growth histories and resistance-mutation origins

Status: **user_reviewed**. User approval covers both Choices, reference answers, evidence scope, and inference boundary.

**Target treatment:** Independent pre-selection culture growth histories and the interpretation of resistance after phage selection.

**Scope:** Table 1 experiment 11a versus Table 2 experiment 11, with the source's mutation-and-clonal-growth interpretation. Other experiment columns and mutation-rate estimation are excluded.

### Source evidence

[BIO-LD-1943](https://doi.org/10.1093/genetics/28.6.491): Luria and Delbrueck (1943). Mutations of Bacteria from Virus Sensitivity to Virus Resistance. Genetics 28: 491-511. DOI: 10.1093/genetics/28.6.491. Scan of the original 21-page article; public Pennsylvania State University mirror.

**Evidence 1 — Printed pp. 502-504 (PDF pp. 12-14), plating methods, Table 1 and Table 2**

Table 1 uses parallel platings of samples from the same grown culture to check sampling and plating variability. Table 2 uses cultures grown separately in parallel before testing. In experiment 11a the ten resistant-colony counts are 46, 56, 52, 48, 65, 44, 49, 51, 56, 47. In experiment 11 they are 30, 10, 40, 45, 183, 12, 173, 23, 57, 51.

**Evidence 2 — Printed pp. 493, 496 and 507-508 (PDF pp. 3, 6 and 17-18)**

Under the mutation interpretation, resistance can arise before virus exposure and be inherited by descendants. Early mutations can therefore contribute many resistant cells. The paper distinguishes mutation events from their descendants and interprets the fluctuations using clonal relatedness. Neither selected table assigns colonies to individual mutation origins.

These passages are source-faithful adaptations, not verbatim quotations.

### Claim to assess

The ten experiment-11a plates replicate ten independently grown cultures, and each resistant colony in the selected tables identifies a separate mutation origin.

This claim was constructed for the case; it is not attributed to the source authors.

### Structured source records

```json
{
  "series": [
    {
      "experiment": "11a",
      "table": "1",
      "row_numbers": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10
      ],
      "resistant_colonies": [
        46,
        56,
        52,
        48,
        65,
        44,
        49,
        51,
        56,
        47
      ]
    },
    {
      "experiment": "11",
      "table": "2",
      "row_numbers": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10
      ],
      "resistant_colonies": [
        30,
        10,
        40,
        45,
        183,
        12,
        173,
        23,
        57,
        51
      ]
    }
  ],
  "record_origin": "Original row order checked visually in both scanned tables. Experiment 11a and 11 are distinct source labels; row indices identify samples or cultures according to the table."
}
```

### Atomic Choices

#### B002-Q01

How do the pre-selection growth histories differ between the selected experiment-11a and experiment-11 series? Select exactly one option using the supplied evidence and stated scope. Do not count records, perform arithmetic, or assign the final claim label; code does that. Choose conflicting before any other option if unresolved statements are incompatible about this judgment in this scope. Choose other only for an established substantive answer outside the listed alternatives. Choose not_stated when missing, partial, or ambiguous evidence prevents the requested judgment without a conflict. Partial evidence is sufficient for a substantive option only when it establishes that option as worded; do not infer missing details.

- **`shared_then_separate`**: The 11a samples share one grown culture; the 11 samples come from cultures grown separately before selection.
- **`separate_then_shared`**: The 11a samples come from separately grown cultures; the 11 samples share one grown culture.
- **`both_separate`**: Every selected record in both series comes from a separate pre-selection culture.
- **`both_shared`**: Within each series, every selected record samples one common pre-selection culture.
- **`other`**: The evidence establishes a substantive answer outside the listed alternatives.
- **`not_stated`**: Missing, partial, or ambiguous evidence does not establish the requested judgment, and no unresolved contradiction is present.
- **`conflicting`**: Unresolved evidence gives incompatible accounts of this judgment within the stated scope.

#### B002-Q02

Under the source's mutation-and-growth interpretation, what relation can connect distinct resistant cells present at plating? Select exactly one option using the supplied evidence and stated scope. Do not count records, perform arithmetic, or assign the final claim label; code does that. Choose conflicting before any other option if unresolved statements are incompatible about this judgment in this scope. Choose other only for an established substantive answer outside the listed alternatives. Choose not_stated when missing, partial, or ambiguous evidence prevents the requested judgment without a conflict. Partial evidence is sufficient for a substantive option only when it establishes that option as worded; do not infer missing details.

- **`one_origin_per_cell`**: Each resistant cell necessarily represents a different mutation origin.
- **`clonal_descendants`**: Several resistant cells can descend from one earlier resistance mutation; cell or colony abundance does not identify the number of origins.
- **`selection_creates_each_origin`**: Each resistant cell acquires a new resistance mutation only when virus is added, independently of pre-selection ancestry.
- **`repeated_image`**: The reported colonies are repeated images of one physical colony, with no distinct resistant cells.
- **`other`**: The evidence establishes a substantive answer outside the listed alternatives.
- **`not_stated`**: Missing, partial, or ambiguous evidence does not establish the requested judgment, and no unresolved contradiction is present.
- **`conflicting`**: Unresolved evidence gives incompatible accounts of this judgment within the stated scope.

### Accepted reference answers — evaluation only

**B002-Q01: `shared_then_separate`** — user_reviewed

Table 1 tests sampling from one culture; Table 2 compares separate pre-selection cultures. The selected column headers retain that distinction.

Downstream role: Select the growth-history grouping; code counts the rows and groups each series.

**B002-Q02: `clonal_descendants`** — user_reviewed

The source distinguishes a mutation from its proliferating descendants. Colony abundance can therefore exceed the number of origins, without revealing the exact origin count.

Downstream role: Prevent colony totals from being used as an exact independent-mutation count.

### Deterministic derivation

Count selected table rows, sum colony records, group growth histories using Q01, and use Q02 to block a one-colony/one-origin identity. Do not invent colony-to-mutation links or estimate mutation rates.

Expected output with the accepted references:

```json
{
  "status": "derived",
  "semantic_choices": [
    "shared_then_separate",
    "clonal_descendants"
  ],
  "counts": {
    "platings": {
      "11a": 10,
      "11": 10
    },
    "growth_histories": {
      "11a": 1,
      "11": 10
    },
    "colony_totals": {
      "11a": 514,
      "11": 624
    },
    "exact_mutation_origins": null
  },
  "clauses": {
    "independent_histories_11a": "inconsistent",
    "one_colony_one_origin": "inconsistent"
  },
  "final_label": "inconsistent"
}
```

A missing or illegal answer is an input error. `conflicting`, `other`, and `not_stated` stop group-level composition, in that precedence order. Unknown scientific quantities remain null. With substantive answers, an inconsistent clause makes the conjunction inconsistent; an unknown clause remains separately visible.

### Inference boundary

Separate culture growth histories do not identify each mutation origin or certify all error-independence assumptions. The mutation interpretation is supplied by the source, not newly established by a variance calculation here. All colony totals and averages are bookkeeping only.

---

<a id="b003"></a>

## B003: Repeated RNA pools and the biological information retained by a library

Status: **user_reviewed**. User approval covers both Choices, reference answers, evidence scope, and inference boundary.

**Target treatment:** Brd1 genotype-group replication in the eight-animal RNA-pooling arm.

**Scope:** The four eight-animal pools: 8R pool 1/2 and 8W pool 1/2. The complete pooling figure is transcribed, but three-animal pools and individually sequenced libraries are filtered out of this claim. Genotype groups are inherited, not a claim of randomized drug administration.

### Source evidence

[BIO-RNA-2015](https://link.springer.com/article/10.1186/s12864-015-1767-y): Rajkumar et al. (2015). Experimental validation of methods for differential gene expression analysis and sample pooling in RNA-seq. BMC Genomics 16:548. DOI: 10.1186/s12864-015-1767-y. Published article and original Additional file 10 (JPEG).

**Evidence 1 — Main PDF p. 6, RNA samples and RNA-seq analysis; Additional file 10**

RNA was extracted from amygdala samples of eight female Brd1+/- mice and eight WT littermates. For each genotype, two eight-animal pools were prepared from equal RNA amounts from the same eight contributors. RNA was pooled before cDNA synthesis and library preparation. Additional file 10 labels the contributors R1-R8 and W1-W8 and shows both copies of each pool.

**Evidence 2 — Main PDF p. 6, DEG analyses; Figure 2 caption; Additional file 10**

The reported bulk analysis counts reads into gene-expression profiles for the prepared libraries. The study separately sequenced individual samples and three-animal pools for comparison. Those separate individual profiles are available in the study but are not observations produced by the four selected eight-animal pooled libraries.

These passages are source-faithful adaptations, not verbatim quotations.

### Claim to assess

The four selected eight-animal pools contribute 32 distinct mice and 32 separately observed mouse-level expression profiles in the pooled arm. The pooling is only numerical averaging after individual expression measurement.

This claim was constructed for the case; it is not attributed to the source authors.

### Structured source records

```json
{
  "pools": [
    {
      "pool_id": "3R pool 1",
      "genotype": "Brd1+/-",
      "pool_size": 3,
      "contributors": [
        "R1",
        "R2",
        "R3"
      ]
    },
    {
      "pool_id": "3R pool 2",
      "genotype": "Brd1+/-",
      "pool_size": 3,
      "contributors": [
        "R1",
        "R2",
        "R3"
      ]
    },
    {
      "pool_id": "8R pool 1",
      "genotype": "Brd1+/-",
      "pool_size": 8,
      "contributors": [
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
        "R7",
        "R8"
      ]
    },
    {
      "pool_id": "8R pool 2",
      "genotype": "Brd1+/-",
      "pool_size": 8,
      "contributors": [
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
        "R7",
        "R8"
      ]
    },
    {
      "pool_id": "3W pool 1",
      "genotype": "WT",
      "pool_size": 3,
      "contributors": [
        "W1",
        "W3",
        "W4"
      ]
    },
    {
      "pool_id": "3W pool 2",
      "genotype": "WT",
      "pool_size": 3,
      "contributors": [
        "W1",
        "W3",
        "W4"
      ]
    },
    {
      "pool_id": "8W pool 1",
      "genotype": "WT",
      "pool_size": 8,
      "contributors": [
        "W1",
        "W2",
        "W3",
        "W4",
        "W5",
        "W6",
        "W7",
        "W8"
      ]
    },
    {
      "pool_id": "8W pool 2",
      "genotype": "WT",
      "pool_size": 8,
      "contributors": [
        "W1",
        "W2",
        "W3",
        "W4",
        "W5",
        "W6",
        "W7",
        "W8"
      ]
    }
  ],
  "select_pool_size": 8,
  "record_origin": "All eight pool memberships transcribed from Additional file 10. Source pool labels and contributor IDs are preserved, including W1/W3/W4 in both three-animal WT pools."
}
```

### Atomic Choices

#### B003-Q01

At what stage are the animals' contributions combined in the selected pooled arm? Select exactly one option using the supplied evidence and stated scope. Do not count records, perform arithmetic, or assign the final claim label; code does that. Choose conflicting before any other option if unresolved statements are incompatible about this judgment in this scope. Choose other only for an established substantive answer outside the listed alternatives. Choose not_stated when missing, partial, or ambiguous evidence prevents the requested judgment without a conflict. Partial evidence is sufficient for a substantive option only when it establishes that option as worded; do not infer missing details.

- **`rna_before_library`**: RNA from different animals is physically combined before cDNA synthesis and library preparation.
- **`indexed_libraries_only`**: Each animal first receives its own separate library, and only those identifiable libraries are combined for sequencing.
- **`numerical_average_only`**: Animals are assayed separately throughout; only their final expression estimates are averaged in software.
- **`tissue_before_extraction`**: Intact tissues from different animals are combined before a single shared RNA extraction.
- **`other`**: The evidence establishes a substantive answer outside the listed alternatives.
- **`not_stated`**: Missing, partial, or ambiguous evidence does not establish the requested judgment, and no unresolved contradiction is present.
- **`conflicting`**: Unresolved evidence gives incompatible accounts of this judgment within the stated scope.

#### B003-Q02

What biological attribution is established for a gene-expression profile from one selected pooled library in the reported analysis? Select exactly one option using the supplied evidence and stated scope. Do not count records, perform arithmetic, or assign the final claim label; code does that. Choose conflicting before any other option if unresolved statements are incompatible about this judgment in this scope. Choose other only for an established substantive answer outside the listed alternatives. Choose not_stated when missing, partial, or ambiguous evidence prevents the requested judgment without a conflict. Partial evidence is sufficient for a substantive option only when it establishes that option as worded; do not infer missing details.

- **`pool_aggregate`**: The profile describes the combined contributors to that pool; it is not a separately observed profile for each contributor.
- **`all_individuals_resolved`**: The analysis assigns a separate complete expression profile to every contributing animal within that pooled library.
- **`some_individuals_resolved`**: The analysis assigns separate complete profiles to some contributors, while retaining an unresolved aggregate for the rest.
- **`new_single_animal`**: The library measures one new animal that is distinct from all animals used to make the pool.
- **`other`**: The evidence establishes a substantive answer outside the listed alternatives.
- **`not_stated`**: Missing, partial, or ambiguous evidence does not establish the requested judgment, and no unresolved contradiction is present.
- **`conflicting`**: Unresolved evidence gives incompatible accounts of this judgment within the stated scope.

### Accepted reference answers — evaluation only

**B003-Q01: `rna_before_library`** — user_reviewed

The methods place equal-RNA pooling before cDNA and library preparation. This differs from multiplexing separately indexed animal libraries.

Downstream role: Classify whether pooling precedes individual observation; code evaluates the claimed post-assay-only averaging, filters the selected pools, and deduplicates contributors.

**B003-Q02: `pool_aggregate`** — user_reviewed

The reported bulk profile belongs to the combined RNA preparation. Individual libraries are a separate arm and cannot be credited as profiles produced by the selected pooled libraries.

Downstream role: Keep pool-level profiles separate from source-animal counts and individually observed outcomes.

### Deterministic derivation

Filter pool_size=8, deduplicate contributor IDs within genotype and across selected pools, and count libraries. Use Q02 to record the profile level. Never expand one pooled expression vector into per-mouse observations.

Expected output with the accepted references:

```json
{
  "status": "derived",
  "semantic_choices": [
    "rna_before_library",
    "pool_aggregate"
  ],
  "counts": {
    "selected_libraries": 4,
    "distinct_contributors": 16,
    "distinct_contributors_by_genotype": {
      "Brd1+/-": 8,
      "WT": 8
    },
    "contributor_appearances": 32,
    "separately_observed_contributor_profiles": 0
  },
  "clauses": {
    "distinct_mice": "inconsistent",
    "individual_profiles": "inconsistent",
    "pooling_only_after_individual_measurement": "inconsistent"
  },
  "final_label": "inconsistent"
}
```

A missing or illegal answer is an input error. `conflicting`, `other`, and `not_stated` stop group-level composition, in that precedence order. Unknown scientific quantities remain null. With substantive answers, an inconsistent clause makes the conjunction inconsistent; an unknown clause remains separately visible.

### Inference boundary

The mice remain real biological contributors. Two preparations from the same contributors do not sample two new cohorts. The source includes individual sequencing elsewhere, so unavailable individual outcomes here refers only to the selected pooled-arm profiles. No effective sample size or general verdict on pooling is assigned; litter relationships are not reconstructed.

---

<a id="b004"></a>

## B004: Mosaic founders and validation of newly induced germline alleles

Status: **user_reviewed**. User approval covers both Choices, reference answers, evidence scope, and inference boundary. Source wording was qualified on 2026-09-21; Choices and reference answers retain their original review attribution. See [source_revisions.json](source_revisions.json).

**Target treatment:** Tyr-targeted CRISPR/Cas9 zygote treatment versus replication of a defined, heritable mutant genotype.

**Scope:** The hybrid (B6CBAF1/J x FVB/NJ) founder cohort: albino mouse #30 illustrates within-founder allele diversity; the germline question concerns the hybrid pigmentation mosaics. The C57BL/6N test crosses are retained as a contrasting cohort, not transferred to the hybrids.

### Source evidence

[BIO-TYR-2014](https://pmc.ncbi.nlm.nih.gov/articles/PMC4166609/): Yen et al. (2014). Somatic mosaicism and allele complexity induced by CRISPR/Cas9 RNA injections in mouse zygotes. Developmental Biology 393(1):3-9. DOI: 10.1016/j.ydbio.2014.06.017. NCBI BioC XML of PMC4166609 / NIHMS627582; primary author-manuscript text.

**Evidence 1 — Methods: RNA injections into mouse zygotes; Tyr mutation analysis. Results: Characterization of CRISPR/Cas9-induced Tyr mutations**

Tyr4a, Tyr4b, and Cas9 RNAs were introduced into zygotes. Tail-DNA analysis identified multiple mutant alleles in completely albino hybrid founder #30. The authors attribute the within-founder diversity to mosaicism, potentially arising from editing that persisted into cleavage stages. Deep sequencing reported 57 mutant alleles meeting its read-frequency threshold across 23 hybrid founders; these are not 57 injected animals.

**Evidence 2 — Results: Germ line transmission of targeted Tyr alleles. Discussion: paragraph beginning Complete albinism and pigmentation mosaicism**

C57BL/6N mosaics produced albino progeny in crosses with albino mates. The hybrid pigmentation mosaics were not tested this way: they already carried the FVB/NJ albino allele, which could produce albino offspring without demonstrating transmission of a newly induced allele. Somatic evidence and the C57BL/6N crosses do not establish new-allele transmission for those untested hybrids.

These passages are source-faithful adaptations, not verbatim quotations.

### Claim to assess

Every albino hybrid founder is a uniform defined Tyr genotype, and the reported 57 mutant alleles establish 57 separately injected, germline-validated mutant lines. Albino offspring from hybrid pigmentation mosaics would uniquely identify transmission of newly induced alleles.

This claim was constructed for the case; it is not attributed to the source authors.

### Structured source records

```json
{
  "deep_sequenced_hybrid_founders": 23,
  "reported_mutant_alleles_at_threshold": 57,
  "minimum_reported_read_fraction": 0.05,
  "illustrative_albino_founder_id": "30",
  "reported_alleles_in_founder_30": 5,
  "record_origin": "Source Results and Methods, as archived in NCBI BioC XML; published aggregate counts, not a new sequence reanalysis or unique-origin count. The value 5 for founder #30 is the author-manuscript prose report; publisher Figure 3C lists six allele entries. The exact total remains unresolved."
}
```

### Atomic Choices

#### B004-Q01

What does the reported tail-DNA evidence establish about genotype uniformity in albino hybrid founder #30? Select exactly one option using the supplied evidence and stated scope. Do not count records, perform arithmetic, or assign the final claim label; code does that. Choose conflicting before any other option if unresolved statements are incompatible about this judgment in this scope. Choose other only for an established substantive answer outside the listed alternatives. Choose not_stated when missing, partial, or ambiguous evidence prevents the requested judgment without a conflict. Partial evidence is sufficient for a substantive option only when it establishes that option as worded; do not infer missing details.

- **`uniform_one_allele_pair`**: All sampled cells can be represented by one common pair of Tyr alleles; albinism establishes a uniform mutant genotype.
- **`within_founder_mosaicism`**: Different mutant alleles occur within the same founder, so complete albinism does not establish one uniform mutant genotype.
- **`one_founder_per_allele`**: Each reported allele comes from a different injected animal; the animal identifier combines those founders.
- **`no_edit_detected`**: The tail-DNA evidence establishes only the unmodified reference sequence.
- **`other`**: The evidence establishes a substantive answer outside the listed alternatives.
- **`not_stated`**: Missing, partial, or ambiguous evidence does not establish the requested judgment, and no unresolved contradiction is present.
- **`conflicting`**: Unresolved evidence gives incompatible accounts of this judgment within the stated scope.

#### B004-Q02

Why would albino offspring from an albino-mate cross not, by phenotype alone, identify transmission of a newly induced allele in the hybrid pigmentation mosaics? Select exactly one option using the supplied evidence and stated scope. Do not count records, perform arithmetic, or assign the final claim label; code does that. Choose conflicting before any other option if unresolved statements are incompatible about this judgment in this scope. Choose other only for an established substantive answer outside the listed alternatives. Choose not_stated when missing, partial, or ambiguous evidence prevents the requested judgment without a conflict. Partial evidence is sufficient for a substantive option only when it establishes that option as worded; do not infer missing details.

- **`preexisting_albino_allele`**: The hybrid founders already carry an inherited albino allele, so the same offspring phenotype need not identify a newly induced allele.
- **`unique_new_allele_marker`**: Albinism uniquely marks the newly induced allele because the hybrid parents carry no prior albino allele.
- **`no_germline_possible`**: The hybrid founders are established to lack germ cells, making transmission biologically impossible.
- **`all_hybrid_alleles_verified`**: Allele-specific progeny sequencing already establishes transmission of every newly induced hybrid-founder allele.
- **`other`**: The evidence establishes a substantive answer outside the listed alternatives.
- **`not_stated`**: Missing, partial, or ambiguous evidence does not establish the requested judgment, and no unresolved contradiction is present.
- **`conflicting`**: Unresolved evidence gives incompatible accounts of this judgment within the stated scope.

### Accepted reference answers — evaluation only

**B004-Q01: `within_founder_mosaicism`** — user_reviewed

Multiple mutant alleles were reported within albino founder #30. A shared visible phenotype does not make those cells one uniform allelic treatment.

Downstream role: Reject phenotype-based homogeneous-genotype replication and keep founder counts separate from allele entries.

**B004-Q02: `preexisting_albino_allele`** — user_reviewed

The Discussion explicitly gives the inherited FVB/NJ allele as the reason these hybrid mosaics were not tested with albino mates. The positive C57BL/6N crosses do not validate the hybrids.

Downstream role: Evaluate whether offspring phenotype identifies a newly induced allele. Code keeps the unsupported exact number of validated lines unknown.

### Deterministic derivation

Compare the source-reported founder total with the claimed 57; retain the separately reported allele total. Use Q01 for genotype uniformity and Q02 for the need for discriminating germline evidence. Do not deduplicate alleles into founder IDs or infer an exact number of validated lines.

Expected output with the accepted references:

```json
{
  "status": "derived",
  "semantic_choices": [
    "within_founder_mosaicism",
    "preexisting_albino_allele"
  ],
  "counts": {
    "deep_sequenced_hybrid_founders": 23,
    "reported_mutant_alleles": 57,
    "validated_new_germline_lines": null
  },
  "clauses": {
    "every_albino_founder_uniform": "inconsistent",
    "separately_injected_founders": "inconsistent",
    "validated_new_germline_lines": "insufficient_evidence",
    "albino_offspring_uniquely_identify_new_allele": "inconsistent"
  },
  "final_label": "inconsistent"
}
```

A missing or illegal answer is an input error. `conflicting`, `other`, and `not_stated` stop group-level composition, in that precedence order. Unknown scientific quantities remain null. With substantive answers, an inconsistent clause makes the conjunction inconsistent; an unknown clause remains separately visible.

### Inference boundary

Reported alleles are neither cell counts nor independently validated lines. A 5% read threshold is an assay reporting rule, not a threshold for germline transmission or complete enumeration of mosaic cells. Germline-line counts remain unknown, not zero. Founder #30 and the untested hybrid mosaics are different scopes within the same intervention problem.
