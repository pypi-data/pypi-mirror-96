# Copied from cellSNP, https://github.com/single-cell-genetics/cellSNP/blob/feature-count/cellSNP/utils/count_utils.py
# Utilility functions for count reads in each feature
# Author: Yuanhua Huang
# Date: 27/04/2020

## Note, this is a very basic read counting for features

import numpy as np
from .base import id_mapping, unique_list
from .pileup import check_pysam_chrom

global CACHE_CHROM
global CACHE_SAMFILE
CACHE_CHROM = None
CACHE_SAMFILE = None

def fetch_reads(sam_file, region, cell_tag="CR", UMI_tag="UR", min_MAPQ=20, 
                max_FLAG=255, min_LEN=30):
    """ Fetch all reads mapped to a given region.
    Filtering is also applied, including cell and UMI tags and read mapping 
    quality.
    """
    if sam_file is None or region is None:
        if sam_file is None:
            print("Warning: samFile is None")
        if region is None:
            print("Warning: region is None")
        return np.array([]), np.array([])

    samFile, _chrom = check_pysam_chrom(sam_file, region.chrom)
    
    UMIs_list, cell_list = [], []
    for _read in samFile.fetch(_chrom, region.start - 1, region.end):
        ## filtering reads
        # this might be further speed up
        overhang = sum((np.array(_read.positions) >= (region.start - 1)) *   
                       (np.array(_read.positions) <= (region.end - 1)))

        if _read.mapq < min_MAPQ or _read.flag > max_FLAG or overhang < min_LEN: 
            continue
            
        if cell_tag is not None and _read.has_tag(cell_tag) == False: 
            continue
        if UMI_tag is not None and _read.has_tag(UMI_tag) == False: 
            continue
            
        if UMI_tag is not None:
            UMIs_list.append(_read.get_tag(UMI_tag))
        if cell_tag is not None:
            cell_list.append(_read.get_tag(cell_tag))

    if len(cell_list) > 0 and len(cell_list) == len(UMIs_list):
        UMI_cell = [UMIs_list[x] + cell_list[x] for x in range(len(UMIs_list))]
        UMI_cell, idx, cnt = unique_list(UMI_cell)
        cell_list = [cell_list[x] for x in idx]
    
    cell_list_uniq, idx, read_count = unique_list(cell_list)

    return cell_list_uniq, read_count

def feature_count(sam_file, barcodes, region, reg_index, cell_tag, UMI_tag, 
    min_MAPQ, max_FLAG, min_LEN):
    """Fetch read count for a given feature.
    """
    cell_list_uniq, read_count = fetch_reads(sam_file, region, cell_tag, UMI_tag, 
        min_MAPQ, max_FLAG, min_LEN)

    if len(cell_list_uniq) > 0:
        match_idx = id_mapping(cell_list_uniq, barcodes, uniq_ref_only=True, 
            IDs2_sorted=True)
        match_idx = np.array(match_idx, dtype = float)

        idx1 = np.where(match_idx == match_idx)[0] #remove None
        idx2 = match_idx[idx1].astype(int)
        
        out_list = []
        for j in range(len(idx2)):
            out_list.append("%d\t%d\t%d" %(reg_index, idx2[j], read_count[idx1[j]]))
        return "\n".join(out_list) + "\n"
    else:
        return None

