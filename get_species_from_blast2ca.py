import os
import re
import pandas as pd
from collections import Counter

# === Function to extract species from taxonomy string ===
def extract_species(taxonomy_string):
    match = re.search(r's__([A-Za-z0-9_ -]+)', taxonomy_string)
    if match:
        name = match.group(1).strip()
        return "Unknown" if name.lower() == "unknown" else name
    else:
        return "Unknown"

# === PARAMETERS ===
blast2lca_folder = "."  # path where all *_blast2lca.txt files are stored
output_file = "bin_species_summary.tsv"
# ==================

results = []

for filename in os.listdir(blast2lca_folder):
    if filename.endswith("_blast2lca.txt"):
        file_path = os.path.join(blast2lca_folder, filename)

        # === Extract Sample and Bin ===
        match = re.match(r"(.*)_metabat\.(\d+)\.fa.*_blast2lca\.txt", filename)
        if not match:
            print(f"Skipping file with unexpected format: {filename}")
            continue

        sample_name = match.group(1)
        bin_number = match.group(2)
        bin_name = f"metabat.{bin_number}"

        # Read species list
        with open(file_path, 'r') as f:
            species_list = [extract_species(line.strip()) for line in f if line.strip()]

        total_contigs = len(species_list)
        if total_contigs == 0:
            continue

        species_counts = Counter(species_list)
        most_common_species, top_count = species_counts.most_common(1)[0]
        percentage = (top_count / total_contigs) * 100

        results.append({
            "Sample": sample_name,
            "Bin": bin_name,
            "Most_Abundant_Species": most_common_species,
            "Percentage_of_Contigs": round(percentage, 2),
            "Total_Contigs": total_contigs
        })
# Save final table
df = pd.DataFrame(results)
df.to_csv(output_file, sep='\t', index=False)
print(f"Summary saved to: {output_file}")
