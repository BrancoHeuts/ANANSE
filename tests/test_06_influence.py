import os

import pandas as pd
import pytest

import ananse.influence


@pytest.fixture
def influence_obj(outdir):
    i = ananse.influence.Influence(
        outfile=os.path.join(outdir, "influence.tsv"),
        degenes="tests/data/influence/degenes.tsv",
        grn_target_file="tests/data/influence/network.tsv",
        edges=10,
        gene_gtf="tests/data/GRCz11_chr9/GRCz11/GRCz11.annotation.gtf",
    )
    return i


@pytest.fixture
def source_network():
    return "tests/data/influence/ES.full.small.txt"


@pytest.fixture
def target_network():
    return "tests/data/influence/KC.full.small.txt"


@pytest.fixture
def diff_exp():
    return "tests/data/influence/DEG.small.tsv"


def test_read_network_to_graph():
    grn = ananse.influence.read_network_to_graph(
        "tests/data/influence/network.tsv", edges=10, full_output=False
    )
    assert len(grn.edges) == 10  # 1 TF + 10 target genes
    assert len(grn.nodes) == 11  # 1 TF + 10 target genes
    # full_output=False
    assert "tf_activity" not in grn["FOXK2"]["AL935186.11"].keys()

    top_int = ["FOXK2—AL935186.11", "FOXK2—ABCA7"]
    grn = ananse.influence.read_network_to_graph(
        "tests/data/influence/network.tsv", interactions=top_int, full_output=True
    )
    assert len(grn.nodes) == 3  # 1 TF + 2 target genes
    # full_output=True
    assert "tf_activity" in grn["FOXK2"]["AL935186.11"].keys()


def test_difference():
    pass  # TODO


def test_read_expression(influence_obj):
    scores = influence_obj.expression_change["foxg1b"]
    assert round(scores.score, 2) == 1.83
    assert round(scores.absfc, 2) == 1.83
    assert round(scores.realfc, 2) == 1.83


def test_influence_scores(influence_obj):
    de_genes = set(
        g
        for g in influence_obj.expression_change
        if influence_obj.expression_change[g].score > 0
    )
    de_genes = de_genes & influence_obj.grn.nodes
    line = ananse.influence.influence_scores(
        "FOXK2", influence_obj.grn, influence_obj.expression_change, de_genes
    )
    assert line[0] == "FOXK2"
    assert line[1] == 10  # all test edges
    assert len(line) == 8


def test_filter_tf():
    pass  # TODO


def test_run_target_score(outdir):
    i = ananse.influence.Influence(
        outfile=os.path.join(outdir, "influence.tsv"),
        degenes="tests/data/influence/degenes.tsv",
        grn_target_file="tests/data/influence/network.tsv",
        edges=10,
        gene_gtf="tests/data/GRCz11_chr9/GRCz11/GRCz11.annotation.gtf",
        padj_cutoff=0.05,
    )
    i.run_target_score()
    assert os.path.exists(i.outfile)
    df = pd.read_table(i.outfile, index_col=0)
    assert df.loc["FOXK2"]["direct_targets"] == 10
    assert round(df.loc["FOXK2"]["pval"], 2) == 0.15

    # same output with multiprocessing
    os.remove(i.outfile)
    i.ncore = 2
    i.run_target_score()
    assert os.path.exists(i.outfile)
    df2 = pd.read_table(i.outfile, index_col=0)
    assert all(df.eq(df2))


def test_run_influence_score():
    pass  # TODO


def test_run_influence(source_network, target_network, diff_exp, outdir):
    for params in (True, (2, 9), (26, 3)), (False, (2, 9), (21, 3)):
        outfile = os.path.join(outdir, "out.txt")
        i = ananse.influence.Influence(
            outfile,
            diff_exp,
            grn_source_file=source_network,
            grn_target_file=target_network,
            edges=30,
            full_output=False,
            select_after_join=params[0],
        )
        i.run_influence()
        df = pd.read_table(outfile)
        assert df.shape == params[1]

        df = pd.read_table(os.path.splitext(outfile)[0] + "_diffnetwork.tsv")
        assert df.shape == params[2]


def test_command_influence():
    pass  # TODO
