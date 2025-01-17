from loguru import logger

import ananse.influence
from ananse.utils import check_path


@logger.catch
def influence(args):
    a = ananse.influence.Influence(
        ncore=args.ncore,
        grn_source_file=check_path(args.source_file),
        grn_target_file=check_path(args.target_file),
        outfile=check_path(args.outfile, error_missing=False),
        full_output=args.full_output,
        sort_by=args.sort_column,
        padj_cutoff=args.padj_cutoff,
        degenes=check_path(args.expression),
        gene_gtf=check_path(args.gene_gtf),
        edges=args.edges,
        select_after_join=args.select_after_join,
    )
    a.run_influence()
