
The ermA/B/C pipeline is a GUI-based Python tool designed for the systematic analysis of the mobile genetic element (MGE) context of macrolide resistance genes, including ermA, ermB, and ermC. It integrates insertion sequence (IS) family annotation, coordinate-based gene mapping, and distance-driven relationship modeling to characterize the genomic environment surrounding antimicrobial resistance determinants. By combining outputs from MGE detection tools with IS family databases and allele metadata, the pipeline enables identification of IS elements and transposon structures associated with resistance genes and provides biologically meaningful interpretations of their mobility.

The pipeline processes MGE datasets by filtering low-confidence predictions, mapping IS elements to their respective families, and integrating gene coordinates to determine spatial relationships between MGEs and target genes. It calculates distances between MGEs and erm loci, classifies their positions as upstream, downstream, or overlapping, and detects cases where genes are embedded within transposons. Based on these features, the pipeline generates accession-level classifications describing the genetic context of each gene, such as single insertion sequences, multiple IS associations, or embedded transposon structures. In addition, it incorporates host metadata to annotate each accession with species information and genomic localization, allowing differentiation between chromosomal, plasmid, and phage-associated contexts.

The graphical user interface enables users to provide input files, specify output parameters, and execute the pipeline without requiring command-line interaction. Built-in validation ensures that input files contain the required structure, and stepwise logging provides transparency throughout the analysis. The pipeline outputs both detailed per-element datasets and summarized accession-level tables, facilitating downstream statistical analysis and interpretation. Overall, this tool is intended to support large-scale comparative studies of antimicrobial resistance gene mobility and to provide insights into the mechanisms underlying the dissemination of erm genes across diverse bacterial hosts.

How to run:


-- pip install pandas pyqt6
-- python erm_pipeline_gui.py
