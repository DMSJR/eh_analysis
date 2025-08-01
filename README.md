
# EH Analysis Pipeline

This repository documents the bioinformatics pipeline used for the analysis of metagenomic samples from the EH study.

## Overview

The raw data provided had already been:
- trimmed for quality,
- filtered for human contamination, and
- merged using **FLASH**.

The subsequent steps included assembly, binning, taxonomic identification, and viral sequence detection.

---

## 1. Assembly with MEGAHIT

Assembly was performed using **MEGAHIT v1.2.9** with the command:

```bash
megahit -r {merged_file}.fq -1 {filtered_paired_end_1} -2 {filtered_paired_end_2} -o {output_directory}
```

The resulting contigs file (`final.contigs.fa`) was used for binning.

---

## 2. Binning with MetaBAT2

**MetaBAT2 v2:2.15** was used to bin contigs. To do so, contig depth had to be calculated beforehand using **Bowtie2 v2.4.1** and **Samtools v1.13**.

### 2.1 Index the contigs

```bash
bowtie2-build {contigs_file}.fa {index_prefix}
```

### 2.2 Align reads to contigs

```bash
bowtie2 -x {index_prefix} -1 {filtered_paired_end_1} -2 {filtered_paired_end_2} -S {output}.sam --very-sensitive
```

### 2.3 Convert and sort alignments

```bash
samtools view -bS {output}.sam | samtools sort -o {output}.bam
```

### 2.4 Index sorted BAM

```bash
samtools index {output}.bam
```

### 2.5 Calculate contig depth

```bash
jgi_summarize_bam_contig_depths --outputDepth {depth}.txt {output}.bam
```

### 2.6 Run MetaBAT2

```bash
metabat2 -m 1500 -i {contigs_file}.fa -a {depth}.txt -o {output_prefix}
```

---

## 3. Taxonomic Identification of Bins

Bins were taxonomically classified using **DIAMOND v0.9.24** and **blast2lca** from **MEGAN v6.25.10**.

### 3.1 Align with DIAMOND

```bash
diamond blastx -q {bin_file}.fa -d {nr_database.dmnd} -o {output}.tsv \
--outfmt 6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore \
--max-target-seqs 10 --evalue 1e-5 --threads 8
```

### 3.2 Assign taxonomy with blast2lca

```bash
blast2lca -i {diamond_output}.tsv -o {taxonomic_table.txt} --mapDB megan-map-Feb2022.db
```

### 3.3 Extract dominant species

A custom Python script `get_species_from_blast2lca.py` (included in this repository) was used to generate a table containing:
- sample ID,
- bin ID,
- dominant species, and
- percentage of contigs assigned to that species.

---

## 4. Viral Contig Detection with VirFinder

To detect viral sequences, all contigs from MEGAHIT were analyzed using **VirFinder** via R:

```bash
Rscript virfinder_run.R {contigs}.fa
```

A Python script `get_viral_sequences_from_contigs.py` was used to filter for contigs with **p-value < 0.05**.

The significant viral contigs were extracted from the original FASTA files and re-analyzed using the **same DIAMOND + blast2lca workflow** described in section 3.

---

## Notes

- Scripts referenced in this pipeline (e.g., `get_species_from_blast2lca.py`, `get_viral_sequences_from_contigs.py`) are available in this repository.
- Ensure all required databases (e.g., `nr.dmnd`, `megan-map.db`) are downloaded and correctly referenced.
