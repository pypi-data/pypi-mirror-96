#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Copyright (C) 2019 Satria A. Kautsar
# Wageningen University & Research
# Bioinformatics Group
"""bigslice.modules.data.bgc

Handle manipulation and storing of 'bgc' table
"""

from os import path
from Bio import SeqIO, SeqFeature
from typing import List
from .database import Database


class BGC:
    """Represents a BGC in the database"""

    def __init__(self, properties: dict):
        self.id = properties.get("id", -1)
        self.name = properties["name"]
        self.type = properties["type"]
        self.on_contig_edge = properties["on_contig_edge"]
        self.length_nt = properties["length_nt"]
        self.orig_folder = properties["orig_folder"]
        self.orig_filename = properties["orig_filename"]
        self.chem_subclasses = properties["chem_subclasses"]
        self.cds = properties["cds"]

    def save(self, dataset_id: int, database: Database):
        """commits bgc data"""

        existing = database.select(
            "bgc",
            "WHERE name=? AND dataset_id=?",
            parameters=(self.name, dataset_id)
        )
        if existing:
            # for now, this should not get called
            raise Exception("not_implemented")
            # current behavior: check if there is conflict
            # don't do anything if the same bgc exists
            assert len(existing) == 1
            existing = existing[0]
            if self.length_nt != existing["length_nt"]:
                raise Exception("conflicting BGC entry for " +
                                self.name)
            else:
                self.id = existing["id"]
                # TODO: load exisiting data into the object
        else:
            # insert new BGC
            self.id = database.insert(
                "bgc",
                {
                    "dataset_id": dataset_id,
                    "name": self.name,
                    "type": self.type,
                    "on_contig_edge": self.on_contig_edge,
                    "length_nt": self.length_nt,
                    "orig_folder": self.orig_folder,
                    "orig_filename": self.orig_filename
                }
            )
            # insert classes
            for cc in self.chem_subclasses:
                chem_subclass_object = BGC.ChemSubclass.search(
                    database, cc, self.type)
                chem_subclass_object.bgc_id = self.id
                chem_subclass_object.__save__(database)
            # insert cds
            for cds in self.cds:
                cds.bgc_id = self.id
                cds.__save__(database)

    @staticmethod
    def parse_gbk(gbk_path: str, orig_gbk_path: str=None):
        """Load BGCs from a gbk file, return a list of BGC
        objects (one gbk file can contain multiple BGCs e.g.
        in the case of antiSMASH5 GBKs"""

        if not orig_gbk_path:
            orig_gbk_path = gbk_path

        results = []

        gbk_type = None
        records = SeqIO.parse(gbk_path, "gb")
        for gbk in records:

            # fetch type-specific information
            antismash_dict = gbk.annotations.get(
                "structured_comment", {}).get(
                "antiSMASH-Data", {})
            antismash_version = antismash_dict.get("Version", "")
            if antismash_version.split(".")[0] in ["5", "6"]:
                for feature in gbk.features:
                    if feature.type == "protocluster":
                        # is antiSMASH5/6 clustergbk
                        gbk_type = "as" + antismash_version.split(".")[0]
                        break
                    elif feature.type == "subregion":
                        if "aStool" in feature.qualifiers and \
                                feature.qualifiers["aStool"][0] == "mibig":
                            gbk_type = "mibig"
                            break
                if not gbk_type:
                    print(orig_gbk_path +
                          " is not a recognized antiSMASH clustergbk")
                    # not recognized, skip for now
                    pass

                elif gbk_type == "mibig":
                    for feature in gbk.features:
                        qual = feature.qualifiers
                        if feature.type == "subregion" and \
                            "aStool" in qual and \
                                qual["aStool"][0] == "mibig":
                            subreg = feature
                            name = gbk.id
                            on_edge = True
                            loc = subreg.location
                            len_nt = loc.end - loc.start
                            chem_subclasses = [label.strip() for label in
                                               qual["label"][0].split(",")]
                            cds_features = [f for f in
                                            gbk[loc.start:loc.end].features if
                                            f.type == "CDS"]
                            results.append(BGC({
                                "name": name,
                                "type": gbk_type,
                                "on_contig_edge": on_edge,
                                "length_nt": len_nt,
                                "orig_folder": path.dirname(orig_gbk_path),
                                "orig_filename": path.basename(orig_gbk_path),
                                "chem_subclasses": chem_subclasses,
                                "cds": [BGC.CDS.from_feature(f)
                                        for f in cds_features]
                            }))
                            break

                elif gbk_type in ["as5", "as6"]:
                    # get all regions
                    for feature in gbk.features:
                        qual = feature.qualifiers
                        if feature.type == "region":
                            reg = feature
                            name = path.splitext(orig_gbk_path)[0]
                            on_edge = qual["contig_edge"][0] == "True"
                            loc = reg.location
                            len_nt = loc.end - loc.start
                            chem_subclasses = qual["product"]
                            cds_features = [f for f in
                                            gbk[loc.start:loc.end].features if
                                            f.type == "CDS"]
                            results.append(BGC({
                                "name": name,
                                "type": gbk_type,
                                "on_contig_edge": on_edge,
                                "length_nt": len_nt,
                                "orig_folder": path.dirname(orig_gbk_path),
                                "orig_filename": path.basename(orig_gbk_path),
                                "chem_subclasses": chem_subclasses,
                                "cds": [BGC.CDS.from_feature(f)
                                        for f in cds_features]
                            }))

            else:  # assume antiSMASH 4
                cluster = None
                for feature in gbk.features:
                    if feature.type == "cluster":
                        if cluster:  # contain 2 or more clusters
                            cluster = None
                            break
                        else:
                            cluster = feature
                if not cluster:
                    print(orig_gbk_path +
                          " is not a recognized antiSMASH clustergbk")
                    break
                qual = cluster.qualifiers
                for note in qual["note"]:
                    if note.startswith("Detection rule(s) for this " +
                                       "cluster type: plants/"):
                        gbk_type = "plant"
                        break
                if not gbk_type:
                    gbk_type = "as4"
                name = path.splitext(orig_gbk_path)[0]
                on_edge = None
                loc = cluster.location
                len_nt = loc.end - loc.start
                chem_subclasses = qual["product"]
                cds_features = [f for f in
                                gbk[loc.start:loc.end].features if
                                f.type == "CDS"]
                results.append(BGC({
                    "name": name,
                    "type": gbk_type,
                    "on_contig_edge": on_edge,
                    "length_nt": len_nt,
                    "orig_folder": path.dirname(orig_gbk_path),
                    "orig_filename": path.basename(orig_gbk_path),
                    "chem_subclasses": chem_subclasses,
                    "cds": [BGC.CDS.from_feature(f)
                            for f in cds_features]
                }))

            break

        return results

    def get_all_cds_fasta(bgc_ids: List[int], database: Database):
        """query database, get all aa sequences
        of the CDS into a multifasta string
        e.g. for the purpose of doing hmmscan"""

        rows = database.select(
            "cds",
            "WHERE bgc_id IN (" + ",".join(map(str, bgc_ids)) + ")",
            props=["id", "bgc_id", "aa_seq"]
        )

        multifasta = ""
        for row in rows:
            multifasta += ">bgc:{}|cds:{}|hsp:0|{}-{}\n".format(
                row["bgc_id"], row["id"],
                0, len(row["aa_seq"]))
            multifasta += "{}\n".format(row["aa_seq"])
        return multifasta

    def get_all_aligned_hsp(bgc_ids: List[int], hmm_ids: List[int],
                            database: Database):
        """query database, get all aligned hsp
        hits from the list of hmm ids"""

        rows = database.select(
            "cds,hsp,hsp_alignment",
            "WHERE cds.id=hsp.cds_id" +
            " AND hsp.id=hsp_alignment.hsp_id" +
            " AND cds.bgc_id IN (" + ",".join(map(str, bgc_ids)) + ")" +
            " AND hsp.hmm_id IN (" + ",".join(map(str, hmm_ids)) + ")",
            props=["bgc_id", "hsp.id as hsp_id", "hmm_id", "cds.id",
                   "aa_seq", "hsp_alignment.*"]
        )

        results = {}
        for row in rows:
            bgc_id = row["bgc_id"]
            hmm_id = row["hmm_id"]
            if hmm_id not in results:
                results[hmm_id] = ""

            # restore aligned-to-model sequences
            aln = ""
            hit_prot = row["aa_seq"][row["cds_start"]:row["cds_end"]]
            skips = 0
            cds_gaps = [int(gap)
                        for gap in row[
                        "cds_gaps"].split(",") if len(gap) > 0]
            model_gaps = [int(gap)
                          for gap in row[
                          "model_gaps"].split(",") if len(gap) > 0]
            len_full = row["cds_end"] - row["cds_start"] + len(cds_gaps)

            for i in range(len_full):
                if i not in model_gaps:
                    if i not in cds_gaps:
                        aln += hit_prot[i - skips]
                    else:
                        skips += 1

            results[hmm_id] += ">bgc:{}|cds:{}|hsp:{}|{}-{}\n".format(
                bgc_id, row["id"], row["hsp_id"],
                row["cds_start"],
                row["cds_end"])
            results[hmm_id] += "{}\n".format(aln)
        return results

    class ChemSubclass:
        """Chemical subclass mapping"""

        def __init__(self, properties: dict):
            self.subclass_id = properties["subclass_id"]
            self.subclass_name = properties["subclass_name"]
            self.class_id = properties["class_id"]
            self.class_name = properties["class_name"]
            self.orig_class = properties["class_source"]

        def __save__(self, database: Database):
            """commit bgc_class
            this only meant to be called from BGC.save()"""
            existing = database.select(
                "bgc_class",
                "WHERE bgc_id=? AND chem_subclass_id=?",
                parameters=(self.bgc_id, self.subclass_id)
            )
            if existing:
                # for now, this should not get called
                raise Exception("not_implemented")
                # current behavior: skip if exist
                assert len(existing) == 1
                pass
            else:
                # insert new map
                database.insert(
                    "bgc_class",
                    {
                        "bgc_id": self.bgc_id,
                        "chem_subclass_id": self.subclass_id
                    }
                )

        @staticmethod
        def search(database: Database, name: str, source_type: str):
            rows = database.select(
                "chem_class,chem_subclass,chem_subclass_map",
                "WHERE chem_subclass_map.subclass_id=chem_subclass.id AND " +
                "chem_class.id=chem_subclass.class_id " +
                "AND chem_subclass_map.type_source=? AND class_source=?",
                parameters=(source_type, name),
                props=["subclass_id", "class_id", "class_source",
                       "chem_class.name as class_name",
                       "chem_subclass.name as subclass_name"]
            )
            if rows:
                # if >1, something is wrong with chem_class_map.tsv
                assert len(rows) == 1
                row = rows[0]
                return BGC.ChemSubclass(row)
            else:
                # assign Unknown-unknown
                rows_unknown = database.select(
                    "chem_class,chem_subclass",
                    "WHERE chem_class.id=chem_subclass.class_id" +
                    " AND class_name=? AND subclass_name=?",
                    parameters=("Unknown", "unknown"),
                    props=["chem_subclass.id as subclass_id", "class_id",
                           "chem_class.name as class_name",
                           "chem_subclass.name as subclass_name"]
                )
                # if != 1, something is wrong with the database
                assert len(rows_unknown) == 1
                row = rows_unknown[0]
                row["class_source"] = name
                return BGC.ChemSubclass(row)

    class CDS:
        """Represents a CDS in the database
        CDS can't exists without a BGC"""

        def __init__(self, properties: dict):
            self.id = properties.get("id", -1)
            self.nt_start = properties["nt_start"]
            self.nt_end = properties["nt_end"]
            self.strand = properties["strand"]
            self.locus_tag = properties["locus_tag"]
            self.protein_id = properties["protein_id"]
            self.product = properties["product"]
            self.aa_seq = properties["aa_seq"]

        def __save__(self, database: Database):
            """commit cds
            this only meant to be called from BGC.save()"""
            existing = database.select(
                "cds",
                "WHERE bgc_id=?" +
                " AND nt_start=? AND nt_end=?",
                parameters=(self.bgc_id, self.nt_start, self.nt_end),
                props=["id"]
            )
            if existing:
                # for now, this should not get called
                raise Exception("not_implemented")
                # current behavior: check if there is conflict
                # don't do anything if the same cds exists
                assert len(existing) == 1
                existing = existing[0]
                self.id = existing["id"]
            else:
                # insert new CDS
                self.id = database.insert(
                    "cds",
                    {
                        "bgc_id": self.bgc_id,
                        "nt_start": self.nt_start,
                        "nt_end": self.nt_end,
                        "strand": self.strand,
                        "locus_tag": self.locus_tag,
                        "protein_id": self.protein_id,
                        "product": self.product,
                        "aa_seq": self.aa_seq
                    }
                )

        @staticmethod
        def from_feature(feature: SeqFeature):
            def get_prop(prop):
                return feature.qualifiers.get(prop, [None])[0]
            loc = feature.location
            properties = {
                "nt_start": loc.start,
                "nt_end": loc.end,
                "strand": feature.strand,
                "locus_tag": get_prop("locus_tag"),
                "protein_id": get_prop("protein_id"),
                "product": get_prop("product"),
                "aa_seq": get_prop("translation")
            }
            return BGC.CDS(properties)
