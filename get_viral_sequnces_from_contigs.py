import pandas as pd
from Bio import SeqIO
import os

# Load table of significant contigs
df = pd.read_csv("significant_viral_contigs.tsv", sep="\t")

# Group contigs by sample
grouped = df.groupby("Sample")

output_dir = "."
os.makedirs(output_dir, exist_ok=True)

for sample, group in grouped:
    contig_ids = set(group["Contig"])
    input_fasta = f"../megahit/{sample}_megahit/final.contigs.fa"
    output_fasta = os.path.join(output_dir, f"{sample}_viral_contigs.fa")

    if not os.path.exists(input_fasta):
        print(f"FASTA file not found: {input_fasta}")
        continue

    with open(output_fasta, "w") as out_f:
        for record in SeqIO.parse(input_fasta, "fasta"):
            if record.id in contig_ids:
                SeqIO.write(record, out_f, "fasta")

    print(f"Saved viral contigs for {sample} to {output_fasta}")

