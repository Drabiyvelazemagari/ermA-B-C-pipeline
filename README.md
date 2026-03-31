MGE Context Pipeline: Coordinate-Based Analysis of Mobile Genetic Elements Surrounding Target Genes

The MGE context pipeline is a standalone Python application with a graphical user interface designed for the systematic characterization of the genomic environment surrounding user-defined genes of interest. While originally developed for the analysis of macrolide resistance genes (e.g., ermA, ermB, ermC), the pipeline is fully generalizable and can be applied to any gene for which genomic coordinates are available.

Overview and Design Principles

The pipeline operates under a coordinate-driven framework in which relationships between mobile genetic elements (MGEs) and target genes are defined strictly based on genomic position. It does not perform de novo detection of MGEs or insertion sequences but instead consumes externally generated datasets (e.g., from MEFinder and ISFinder-derived annotations).

All annotations are explicitly derived from input data, and no heuristic or model-based inference is applied. This ensures transparency, reproducibility, and compatibility with diverse upstream workflows.

The core functionality consists of three stages: (i) input validation and preprocessing, (ii) integration of MGE, IS family, and gene coordinate data, and (iii) classification of gene–MGE relationships at the accession level.

Input Processing and Validation

The pipeline requires four input datasets:

MGE prediction table (e.g., from MEFinder)
IS family mapping table (derived from ISFinder annotations)
Metadata table (e.g., from AlleleClust or BAKO outputs)
Target gene coordinate table (CDS coordinates for the gene of interest)

Each dataset is validated to ensure the presence of required columns. Accessions are normalized to ensure consistent mapping across all inputs, and execution is halted if structural inconsistencies are detected.

MGE Filtering and Annotation

MGE predictions are filtered to remove low-confidence entries (e.g., elements labeled as putative). Remaining elements are annotated with IS family information by mapping element identifiers to externally provided IS family classifications. Elements without a matching annotation are labeled as unknown.

Coordinate Mapping and Distance Calculation

Coordinates of the target gene are mapped to each accession, enabling calculation of spatial relationships between MGEs and the gene of interest.

For each MGE, the pipeline computes:

Distance to the target gene
Relative position, classified as:
upstream
downstream
overlapping

Distance is defined as the minimal nucleotide separation between element and gene coordinates, with overlapping regions assigned a distance of zero.

Detection of Embedded Gene Context

The pipeline identifies cases in which the target gene is fully contained within an MGE based on coordinate overlap. Such cases are classified as embedded, indicating potential association with larger mobile elements (e.g., transposon-like structures).

Context Classification

For each accession, MGEs within a defined proximity threshold (default: ≤5 kb) or those embedding the gene are aggregated and classified into discrete categories:

single_IS — a single nearby insertion sequence
multiple_IS — multiple nearby insertion sequences
embedded_transposon — gene fully contained within an MGE

These categories provide a simplified and standardized representation of the genomic context of the target gene.

Metadata Integration

The pipeline integrates host and genomic context metadata from the provided metadata table, annotating each accession with:

species identity
genomic localization (e.g., chromosome, plasmid, phage)

This enables stratification of gene contexts across host taxa and replicon types.

Output Structure and Reproducibility

The pipeline produces two primary outputs:

Full dataset (*_FULL.csv)
Contains per-element annotations, including distances, positional relationships, IS family assignments, and embedded status
Summary dataset (*_SUMMARY.csv)
Provides accession-level classifications of gene context, including category assignment and minimum distance to MGEs

All outputs are generated deterministically and directly reflect the input data and filtering criteria.

GUI

<img width="900" height="734" alt="image" src="https://github.com/user-attachments/assets/daa3629a-e48e-4856-9c4f-cbc7189cf907" />


Implementation

The pipeline is implemented in Python and provides a PyQt6-based graphical user interface for ease of use. It relies on the pandas library for data processing and operates entirely on locally provided datasets without requiring external services.

Scope and Limitations

The pipeline does not perform MGE or IS detection and depends entirely on externally generated predictions. Classification of genomic context is based solely on coordinate relationships and does not include structural inference of transposons or mechanistic modeling of gene mobility.

As a result, interpretations should be understood as coordinate-based approximations of genomic context rather than definitive structural annotations.
