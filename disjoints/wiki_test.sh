#!/bin/bash
#SBATCH --job-name=wiki
#SBATCH --output=wikidata_truthy.txt
#SBATCH --error=wikidata_truthy.txt
#SBATCH --time=48:00:00
#SBATCH --partition=tier2
#SBATCH --nodes=1
#SBATCH --ntasks=1

cd /home/abmoreira/datasets
# Download the latest truthy dump with resume support
wget -c https://dumps.wikimedia.org/wikidatawiki/entities/latest-truthy.nt.bz2
