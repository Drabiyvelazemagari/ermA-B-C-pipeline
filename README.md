erm Pipeline: Contextual Analysis of Mobile Genetic Elements Surrounding erm Resistance Genes

The ermA/B/C pipeline is a standalone Python application with a graphical user interface designed for the systematic characterization of the genomic context of macrolide resistance genes, including ermA, ermB, and ermC. The pipeline integrates mobile genetic element (MGE) predictions with insertion sequence (IS) family annotations and coordinate-based gene mapping to enable structured analysis of resistance gene mobility across bacterial genomes.

Overview and Design Principles

The pipeline operates under a coordinate-driven framework in which relationships between MGEs and resistance genes are defined based on genomic position. It does not perform de novo detection of MGEs or insertion sequences but instead consumes externally generated datasets (e.g., from MEFinder and ISFinder-derived mappings). All annotations are explicitly derived from input data, ensuring transparency and reproducibility.

The core workflow consists of three stages: (i) input validation and preprocessing, (ii) integration of MGE, IS family, and gene coordinate data, and (iii) classification of gene–MGE relationships at the accession level. All computations are deterministic and based on explicit positional rules.

Input Processing and Validation

The pipeline requires four input datasets:

MGE prediction table (e.g., from MEFinder)
IS family mapping table (derived from ISFinder annotations)
Metadata table (e.g., AlleleClust or BAKO-derived accession metadata)
Gene coordinate table (CDS coordinates for erm loci)

Each input is validated to ensure the presence of required columns, and execution is halted if structural inconsistencies are detected. Accessions are normalized to ensure consistent mapping across datasets.

MGE Filtering and Annotation

MGE predictions are filtered to remove low-confidence entries, specifically those labeled as putative. Remaining elements are annotated with IS family information by mapping element names to externally provided IS family classifications. Elements without a matching annotation are labeled as unknown.

Coordinate Mapping and Distance Calculation

Coordinates of erm genes are mapped to each accession, enabling calculation of spatial relationships between MGEs and resistance loci. For each MGE, the pipeline computes:

Distance to the erm gene
Relative position, classified as:
upstream
downstream
overlapping

Distance is defined as the minimal nucleotide separation between element and gene coordinates, with overlapping regions assigned a distance of zero.

Detection of Embedded Gene Context

The pipeline identifies cases in which the erm gene is fully contained within an MGE based on coordinate overlap. Such cases are classified as embedded, indicating potential association with larger mobile elements such as transposon-like structures.

Context Classification

For each accession, MGEs within a defined proximity (≤5 kb) or those embedding the gene are aggregated and classified into discrete categories:

single_IS — a single nearby insertion sequence
multiple_IS — multiple nearby insertion sequences
embedded_transposon — gene fully contained within an MGE

This classification provides a simplified representation of the genomic environment surrounding each resistance gene.

Metadata Integration

The pipeline integrates host and genomic context metadata from the provided metadata table, annotating each accession with:

species identity
genomic localization (e.g., chromosome, plasmid, phage)

This enables stratification of resistance gene contexts across host taxa and replicon types.

Output Structure and Reproducibility

The pipeline produces two primary outputs:

Full dataset (*_FULL.csv)
Contains per-element annotations, including distances, positional relationships, IS family assignments, and embedded status
Summary dataset (*_SUMMARY.csv)
Provides accession-level classifications of gene context, including category assignment and minimum distance to MGEs

All outputs are generated deterministically and reflect the exact input data and filtering criteria used during the analysis.

GUI

<img width="905" height="731" alt="image" src="https://github.com/user-attachments/assets/78916fc4-388d-41a2-81ff-261d98b6d1bb" />


Implementation

The pipeline is implemented in Python and provides a PyQt6-based graphical user interface for ease of use. It relies on the pandas library for data processing and operates entirely on locally provided datasets without requiring external API calls or services.

Scope and Limitations

The pipeline does not perform MGE or IS detection and depends on externally generated predictions. Classification of genomic context is based solely on coordinate relationships and does not include structural inference of transposons or mechanistic modeling of mobility.

As a result, interpretations should be understood as coordinate-based approximations of genomic context rather than definitive structural annotations.
