# Copied from cellSNP, https://github.com/single-cell-genetics/cellSNP/blob/purePython/cellSNP/cellSNP.py
# pileup SNPs across the genome with pysam's fetch or pileup reads
# Author: Yuanhua Huang
# Date: 21-12-2018
# Modified by: Xianjie Huang

# pileup --uniq 
#   - uniquely pileup each SNP: if one read covers more than one SNPs, then this 
#     read would only be counted once for the SNP with the smallest pos. Then the
#     double counting problem is solved this way.
#   - now it only supports mode 1a and mode 1b (pileup SNPs) while not support mode
#     2 (pileup chromosomes)

import os
import sys
import gzip
import time
import pysam
import subprocess
import numpy as np
import multiprocessing
from optparse import OptionParser, OptionGroup

from .config import APP
from ..config import VERSION
from ..utils.pileup import fetch_positions
from ..utils.pileup_regions import pileup_regions
from ..utils.vcf import load_VCF, merge_vcf, VCF_to_sparseMat

COMMAND = "pileup"

DEF_FLAG_WITH_UMI = 4096       # default value of max_FLAG when using UMIs, i.e., UMI_tag is not None
DEF_FLAG_WITHOUT_UMI = 255     # default value of max_FLAG when not using UMIs, i.e., UMI_tag is None

START_TIME = time.time()

def show_progress(RV=None):
    return RV

def pileup(argv):
    # import warnings
    # warnings.filterwarnings('error')

    # parse command line options
    if len(argv) < 3:
        print("Welcome to %s %s v%s!\n" %(APP, COMMAND, VERSION))
        print("use -h or --help for help on argument.")
        sys.exit(1)

    parser = OptionParser(usage = "Usage: %s %s [options]" % (APP, COMMAND))
    parser.add_option("--samFile", "-s", dest="sam_file", default=None,
        help=("Indexed sam/bam file(s), comma separated multiple samples. "
              "Mode 1&2: one sam/bam file with single cell barcode; "
              "Mode 3: one or multiple bulk sam/bam files, no barcodes needed, "
              "but sample ids and regionsVCF."))
    parser.add_option("--samFileList", "-S", dest="sam_file_list", default=None,
        help=("A list file containing bam files, each per line, for Mode 3."))
    parser.add_option("--outDir", "-O", dest="sparse_dir", default=None,
        help=("Output directory for VCF and sparse matrices: AD, DP, OTH."))
    parser.add_option("--outVCF", "-o", dest="out_file", default=None,
        help=("Output full path with file name for VCF file. Only use if not "
              "given outDir. [optional]"))
    
    parser.add_option("--regionsVCF", "-R", dest="region_file", default=None,
        help=("A sorted vcf file listing all candidate SNPs, for fetch each variants. "
              "If None, pileup the genome. Needed for bulk samples."))
    parser.add_option("--barcodeFile", "-b", dest="barcode_file", default=None,
        help=("A plain file listing all effective cell barcode."))
    parser.add_option("--sampleIDs", "-I", dest="sample_ids", default=None,
        help=("Comma separated sample ids. Only use it when you input multiple "
              "bulk sam files."))
    
    group1 = OptionGroup(parser, "Optional arguments")
    group1.add_option("--nproc", "-p", type="int", dest="nproc", default=1,
        help="Number of subprocesses [default: %default]")
    group1.add_option("--chrom", dest="chrom_all", default=None, 
        help="The chromosomes to use, comma separated [default: 1 to 22]")
    group1.add_option("--cellTAG", dest="cell_tag", default="CB", 
        help="Tag for cell barcodes, turn off with None [default: %default]")
    group1.add_option("--UMItag", dest="UMI_tag", default="Auto", 
        help="Tag for UMI: UR, Auto, None. For Auto mode, use UR if barcodes "
        "is inputted, otherwise use None. None mode means no UMI but read "
        "counts [default: %default]")
    group1.add_option("--minCOUNT", type="int", dest="min_COUNT", default=20, 
        help="Minimum aggragated count [default: %default]")
    group1.add_option("--minMAF", type="float", dest="min_MAF", default=0.0, 
        help="Minimum minor allele frequency [default: %default]")

    group1.add_option("--doubletGL", dest="doubletGL", action="store_true", 
        default=False, 
        help="If use, keep doublet GT likelihood, i.e., GT=0.5 and GT=1.5")
    group1.add_option("--saveHDF5", dest="save_HDF5", action="store_true", 
        default=False, help="If use, save an output file in HDF5 format.")
    group1.add_option("--uniqCOUNT", dest="uniq_count", action="store_true", 
        default=False, help="If use, read covering more than one SNPs would be counted only once.")
    
    group2 = OptionGroup(parser, "Read filtering")
    group2.add_option("--minLEN", type="int", dest="min_LEN", default=30, 
        help="Minimum mapped length for read filtering [default: %default]")
    group2.add_option("--minMAPQ", type="int", dest="min_MAPQ", default=20, 
        help="Minimum MAPQ for read filtering [default: %default]")
    group2.add_option("--maxFLAG", type="int", dest="max_FLAG", default=None, 
        help="Maximum FLAG for read filtering [default: %d (when use UMI) or %d (otherwise)]" % (DEF_FLAG_WITH_UMI, DEF_FLAG_WITHOUT_UMI))
    
    parser.add_option_group(group1)
    parser.add_option_group(group2)

    # check options and args
    (options, args) = parser.parse_args(args = argv[2:])
    if options.sam_file is None and options.sam_file_list is None:
        print("Error: need samFile for sam file.")
        sys.exit(1)
    elif options.sam_file is not None:
        sam_file_list = options.sam_file.split(",")
    else:
        fid = open(options.sam_file_list, "r")
        sam_file_list = [x.rstrip() for x in fid.readlines()]
        fid.close()
    for sam_file in sam_file_list:
        if os.path.isfile(sam_file) == False:
            print("Error: No such file\n    -- %s" %sam_file)
            sys.exit(1)
        
    if options.barcode_file is None:
        barcodes = None
        if options.sample_ids is None:
            sample_ids = ["Sample_%d" %x for x in range(len(sam_file_list))]
        elif os.path.isfile(options.sample_ids):
            fid = open(options.sample_ids, "r")
            sample_ids = [x.rstrip() for x in fid.readlines()]
            fid.close()
        else:
            sample_ids = options.sample_ids.split(",")
        if len(sample_ids) != len(sam_file_list):
            print('[cellSNP] Error: %d sample ids, %d sam files, not equal.' 
                  %(len(sample_ids), len(sam_file_list)))
            sys.exit(1)
    elif os.path.isfile(options.barcode_file) == False:
        print("Error: No such file\n    -- %s" %options.barcode_file)
        sys.exit(1)
    else:
        sample_ids = None
        # fid = open(options.barcode_file, "r")
        # barcodes = [x.rstrip() for x in fid.readlines()] #.split("-")[0]
        # fid.close()
        barcodes = list(np.genfromtxt(options.barcode_file, 
                                      dtype="str", delimiter="\t"))
        barcodes = sorted(barcodes)
        
    if options.sparse_dir is not None:
        if not os.path.exists(options.sparse_dir):
            os.mkdir(options.sparse_dir)
        out_file = options.sparse_dir + "/cellSNP.cells.vcf.gz"
    elif options.out_file is None:
        print("Error: need outFile for output file path and name.")
        sys.exit(1)
    elif os.path.dirname(options.out_file) == "":
        out_file = "./" + options.out_file
    else:
        out_file = options.out_file
    if os.path.isdir(os.path.dirname(out_file)) == False:
        print("Error: No such directory for file\n -- %s" %out_file)
        sys.exit(1)        
      
    if options.region_file is None or options.region_file == "None":
        region_file = None
        if options.chrom_all is None:
            chrom_all = [str(x) for x in range(1, 23)]
        else:
            chrom_all = options.chrom_all.split(",")
        if barcodes is not None:
            print("[cellSNP] mode 2: pileup %d whole chromosomes in %d single "
                "cells." %(len(chrom_all), len(barcodes)))
        else:
            print("[cellSNP] mode 2: pileup %d whole chromosomes in one "
                "bulk sample." %(len(chrom_all)))
    elif os.path.isfile(options.region_file) == False:
        print("Error: No such file\n    -- %s" %options.region_file)
        sys.exit(1)
    else:
        if barcodes is not None:
            print("[cellSNP] mode 1: fetch given SNPs in %d single cells."
                  %(len(barcodes)))
        else:
            print("[cellSNP] mode 3: fetch given SNPs in %d bulk samples." 
                  %(len(sam_file_list)))
        print("[cellSNP] loading the VCF file for given SNPs ...")
        region_file = options.region_file
        vcf_RV = load_VCF(region_file, biallelic_only=True, 
                          load_sample=False)['FixedINFO']
        pos_list = vcf_RV["POS"]
        REF_list = vcf_RV["REF"]
        ALT_list = vcf_RV["ALT"]
        chrom_list = vcf_RV["CHROM"]
        print("[cellSNP] fetching %d candidate variants ..." %len(pos_list))
    
    if options.cell_tag.upper() == "NONE" or barcodes is None:
        cell_tag = None
    else:
        cell_tag = options.cell_tag
    if options.UMI_tag.upper() == "AUTO":
        if barcodes is None:
            UMI_tag = None
        else:
            UMI_tag = "UR"
    elif options.UMI_tag.upper() == "NONE":
        UMI_tag = None
    else:
        UMI_tag = options.UMI_tag
    
    nproc = options.nproc
    min_MAF = options.min_MAF
    min_LEN = options.min_LEN
    min_MAPQ = options.min_MAPQ
    min_COUNT = options.min_COUNT
    doubletGL = options.doubletGL
    max_FLAG = options.max_FLAG
    uniq_count = options.uniq_count
    if options.max_FLAG is None:
        max_FLAG = DEF_FLAG_WITHOUT_UMI if UMI_tag is None else DEF_FLAG_WITH_UMI

    result, out_files = [], []
    if region_file is None:
        # pileup in each chrom
        if nproc > 1:
            pool = multiprocessing.Pool(processes=nproc)
            for _chrom in chrom_all:
                chr_out_file = out_file + ".temp_%s_" %(_chrom)
                out_files.append(chr_out_file)
                result.append(pool.apply_async(pileup_regions, (sam_file_list[0], 
                    barcodes, chr_out_file, _chrom, cell_tag, UMI_tag, 
                    min_COUNT, min_MAF, min_MAPQ, max_FLAG, min_LEN, doubletGL, 
                    True), 
                    callback=show_progress))
            pool.close()
            pool.join()
        else:
            for _chrom in chrom_all:
                chr_out_file = out_file + ".temp_%s_" %(_chrom)
                out_files.append(chr_out_file)
                pileup_regions(sam_file_list[0], barcodes, chr_out_file, _chrom, 
                               cell_tag, UMI_tag, min_COUNT, min_MAF, min_MAPQ, 
                               max_FLAG, min_LEN, doubletGL, True)
                show_progress(1)
        result = [res.get() if nproc > 1 else res for res in result]
        print("")
        print("[cellSNP] Whole genome pileupped, now merging all variants ...")
    else:
        # fetch each position
        if (nproc == 1):
            out_file_tmp = out_file + ".temp_0_"
            out_files.append(out_file_tmp)
            result = fetch_positions(sam_file_list,                 
                chrom_list, pos_list, REF_list, ALT_list, barcodes, sample_ids, 
                out_file_tmp, cell_tag, UMI_tag, min_COUNT, min_MAF, 
                min_MAPQ, max_FLAG, min_LEN, doubletGL, True, uniq_count) 
            show_progress(1)
        else:
            LEN_div = int(len(chrom_list) / nproc)
            pool = multiprocessing.Pool(processes=nproc)
            for ii in range(nproc):
                out_file_tmp = out_file + ".temp_%d_" %(ii)
                out_files.append(out_file_tmp)

                if ii == nproc - 1:
                    _pos = pos_list[LEN_div * ii : len(pos_list)]
                    _chrom = chrom_list[LEN_div * ii : len(chrom_list)]
                    _REF_list = REF_list[LEN_div * ii : len(REF_list)]
                    _ALT_list = ALT_list[LEN_div * ii : len(ALT_list)]
                else:
                    _pos = pos_list[LEN_div * ii : LEN_div * (ii+1)]
                    _chrom = chrom_list[LEN_div * ii : LEN_div * (ii+1)]
                    _REF_list = REF_list[LEN_div * ii : LEN_div * (ii+1)]
                    _ALT_list = ALT_list[LEN_div * ii : LEN_div * (ii+1)]

                result.append(pool.apply_async(fetch_positions, (sam_file_list,                 
                    _chrom, _pos, _REF_list, _ALT_list, barcodes, sample_ids, 
                    out_file_tmp, cell_tag, UMI_tag, min_COUNT, min_MAF, 
                    min_MAPQ, max_FLAG, min_LEN, doubletGL, True, uniq_count), 
                    callback=show_progress))

            pool.close()
            pool.join()
            result = [res.get() for res in result]
            print("")
        print("[cellSNP] fetched %d variants, now merging temp files ... " 
              %(len(pos_list)))
    
    merge_vcf(out_file, out_files, options.save_HDF5)

    if options.sparse_dir is not None:
        VCF_to_sparseMat(out_file, tags=["AD", "DP", "OTH"], 
            out_dir=options.sparse_dir)
    
    run_time = time.time() - START_TIME
    print("[cellSNP] All done: %d min %.1f sec" %(int(run_time / 60), 
                                                  run_time % 60))
if __name__ == "__main__":
    pileup(sys.argv)
