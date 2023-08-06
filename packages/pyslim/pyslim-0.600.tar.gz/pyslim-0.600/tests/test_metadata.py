"""
Test cases for the metadata reading/writing of pyslim.
"""
import os

import numpy as np
import pytest
import msprime
import tskit
import pyslim

import tests
from .recipe_specs import recipe_eq


class TestMetadataSchemas(tests.PyslimTestCase):

    def validate_table_metadata(self, table):
        ms = table.metadata_schema
        for j, row in enumerate(table):
            a = table.metadata_offset[j]
            b = table.metadata_offset[j+1]
            raw_md = table.metadata[a:b]
            # this checks to make sure metadata follows the schema
            enc_md = ms.validate_and_encode_row(row.metadata)
            assert bytes(raw_md) == enc_md

    def test_slim_metadata(self, recipe):
        tables = recipe["ts"].tables
        for t in (tables.populations, tables.individuals, tables.nodes, tables.edges,
                  tables.sites, tables.mutations, tables.migrations):
            self.validate_table_metadata(t)

    def test_default_metadata(self):
        for k in pyslim.slim_metadata_schemas:
            schema = pyslim.slim_metadata_schemas[k]
            entry = pyslim.default_slim_metadata(k)
            encoded = schema.validate_and_encode_row(entry)
            decoded = schema.decode_row(encoded)
            if entry is None:
                assert decoded is None
            else:
                assert entry == decoded

    def test_slim_metadata_schema_equality(self, recipe):
        t = recipe["ts"].tables
        assert t.metadata_schema == pyslim.slim_metadata_schemas['tree_sequence']
        assert t.edges.metadata_schema == pyslim.slim_metadata_schemas['edge']
        assert t.sites.metadata_schema == pyslim.slim_metadata_schemas['site']
        assert t.mutations.metadata_schema == pyslim.slim_metadata_schemas['mutation']
        assert t.nodes.metadata_schema == pyslim.slim_metadata_schemas['node']
        assert t.individuals.metadata_schema == pyslim.slim_metadata_schemas['individual']
        assert t.populations.metadata_schema == pyslim.slim_metadata_schemas['population']


class TestTreeSequenceMetadata(tests.PyslimTestCase):
    arbitrary_recipe = [next(recipe_eq())]  # for testing any one recipe

    def validate_slim_metadata(self, t):
        # t could be tables or a tree sequence
        schema = t.metadata_schema.schema
        assert 'SLiM' in schema['properties']
        assert 'SLiM' in t.metadata
        for k in pyslim.default_slim_metadata('tree_sequence')['SLiM']:
            assert k in schema['properties']['SLiM']['properties']
            assert k in t.metadata['SLiM']

    def validate_model_type(self, ts, model_type):
        assert ts.metadata['SLiM']['file_version'] == pyslim.slim_file_version
        assert ts.metadata['SLiM']['model_type'] == model_type
        assert ts.metadata['SLiM']['generation'] > 0
        assert ts.metadata['SLiM']['generation'] >= np.max(ts.tables.nodes.time)


    @pytest.mark.parametrize('recipe', arbitrary_recipe, indirect=True)    
    def test_set_tree_sequence_metadata_errors(self, recipe):
        tables = recipe["ts"].tables
        tables.metadata_schema = tskit.MetadataSchema(None)
        assert len(tables.metadata) > 0
        with pytest.raises(ValueError):
            pyslim.set_tree_sequence_metadata(tables, "nonWF", 0)

    @pytest.mark.parametrize('recipe', arbitrary_recipe, indirect=True)    
    def test_set_tree_sequence_metadata_keeps(self, recipe):
        # make sure doesn't overwrite other stuff
        dummy_schema = tskit.MetadataSchema({
                'codec': 'json',
                'type': 'object',
                'properties': { 'abc': { 'type': 'string' } }
                })
        dummy_metadata = { 'abc': 'foo' }
        tables = recipe["ts"].tables
        tables.metadata_schema = dummy_schema
        tables.metadata = dummy_metadata
        pyslim.set_tree_sequence_metadata(tables, "nonWF", 0)
        schema = tables.metadata_schema.schema
        for k in dummy_metadata:
            assert k in schema['properties']
            assert k in tables.metadata
            assert tables.metadata[k] == dummy_metadata[k]
        self.validate_slim_metadata(tables)
        assert tables.metadata['SLiM']['model_type'] == "nonWF"
        assert tables.metadata['SLiM']['generation'] == 0

    @pytest.mark.parametrize('recipe', arbitrary_recipe, indirect=True)    
    def test_set_tree_sequence_metadata(self, recipe):
        tables = recipe["ts"].tables
        pyslim.set_tree_sequence_metadata(
                tables, "WF", 99,
                spatial_dimensionality='xy',
                spatial_periodicity='y',
                separate_sexes=False,
                nucleotide_based=True)
        self.validate_slim_metadata(tables)
        assert tables.metadata['SLiM']['model_type'] == "WF"
        assert tables.metadata['SLiM']['generation'] == 99
        assert tables.metadata['SLiM']['spatial_dimensionality'] == 'xy'
        assert tables.metadata['SLiM']['spatial_periodicity'] == 'y'
        assert tables.metadata['SLiM']['separate_sexes'] == False
        assert tables.metadata['SLiM']['nucleotide_based'] == True



    @pytest.mark.parametrize('recipe', recipe_eq("WF"), indirect=True)    
    def test_WF_model_type(self, recipe):
        self.validate_model_type(recipe["ts"], "WF")
        
    @pytest.mark.parametrize('recipe', recipe_eq("nonWF"), indirect=True)    
    def test_nonWF_model_type(self, recipe):
        self.validate_model_type(recipe["ts"], "nonWF")
        
    @pytest.mark.parametrize(
        'recipe', recipe_eq(exclude="user_metadata"), indirect=True)    
    def test_recover_metadata(self, recipe):
        # msprime <=0.7.5 discards metadata, but we can recover it from provenance
        ts = recipe["ts"]
        tables = ts.tables
        tables.metadata_schema = tskit.MetadataSchema(None)
        tables.metadata = b''
        new_ts = pyslim.load_tables(tables)
        assert new_ts.metadata == ts.metadata

    @pytest.mark.parametrize('recipe', recipe_eq("user_metadata"), indirect=True)    
    def test_user_metadata(self, recipe):
        ts = recipe["ts"]
        md = ts.metadata["SLiM"]
        #print(md)
        assert "user_metadata" in md
        assert md['user_metadata'] == {
                "hello" : ["world"],
                "pi" : [3, 1, 4, 1, 5, 9]
                }


class TestDumpLoad(tests.PyslimTestCase):
    '''
    Test reading and writing.
    '''

    def verify_times(self, ts, slim_ts):
        gen = slim_ts.slim_generation
        assert ts.num_nodes == slim_ts.num_nodes
        # verify internal consistency
        for j in range(slim_ts.num_nodes):
            assert slim_ts.node(j).time == slim_ts.tables.nodes.time[j]
        # verify consistency between tree sequences
        for n1, n2 in zip(ts.nodes(), slim_ts.nodes()):
            assert n1.time == n2.time

    def test_load_tables(self, recipe):
        ts = recipe["ts"]
        assert isinstance(ts, pyslim.SlimTreeSequence)
        tables = ts.tables
        new_ts = pyslim.load_tables(tables)
        assert isinstance(new_ts, pyslim.SlimTreeSequence)
        new_tables = new_ts.tables
        assert tables == new_tables

    def test_load(self, recipe):
        fn = recipe["path"]["ts"]
        # load in msprime then switch
        msp_ts = tskit.load(fn)
        assert isinstance(msp_ts, tskit.TreeSequence)
        # transfer tables
        msp_tables = msp_ts.tables
        new_ts = pyslim.load_tables(msp_tables)
        assert isinstance(new_ts, pyslim.SlimTreeSequence)
        self.verify_times(msp_ts, new_ts)
        new_tables = new_ts.tables
        self.assertTableCollectionsEqual(msp_tables, new_tables)
        # convert directly
        new_ts = pyslim.SlimTreeSequence(msp_ts)
        assert isinstance(new_ts, pyslim.SlimTreeSequence)
        self.verify_times(msp_ts, new_ts)
        new_tables = new_ts.tables
        self.assertTableCollectionsEqual(msp_tables, new_tables)
        # load to pyslim from file
        slim_ts = pyslim.load(fn)
        assert isinstance(slim_ts, pyslim.SlimTreeSequence)
        slim_tables = slim_ts.tables
        self.assertTableCollectionsEqual(msp_tables, slim_tables)
        assert slim_ts.slim_generation == new_ts.slim_generation

    def test_dump_equality(self, recipe, tmp_path):
        """
        Test that we can dump a copy of the specified tree sequence
        to the specified file, and load an identical copy.
        """
        tmp_file = os.path.join(tmp_path, "test_dump.trees")
        ts = recipe["ts"]
        ts.dump(tmp_file)
        ts2 = pyslim.load(tmp_file)
        assert ts.num_samples == ts2.num_samples
        assert ts.sequence_length == ts2.sequence_length
        assert ts.tables == ts2.tables
        assert ts.reference_sequence == ts2.reference_sequence


class TestAlleles(tests.PyslimTestCase):
    '''
    Test nothing got messed up with haplotypes.
    '''

    def test_haplotypes(self, recipe):
        slim_ts = recipe["ts"]
        tables = slim_ts.tables
        ts = tables.tree_sequence()
        self.verify_haplotype_equality(ts, slim_ts)


class TestNucleotides(tests.PyslimTestCase):
    '''
    Test nucleotide support
    '''

    def test_nucleotides(self, recipe):
        '''
        Check that nucleotides are all valid, i.e.,
        -1, 0, 1, 2, or 3.
        '''
        ts = recipe["ts"]
        for mut in ts.mutations():
            # print(mut)
            for u in mut.metadata['mutation_list']:
                assert u["nucleotide"] >= -1
                assert u["nucleotide"] <= 3


class TestDecoding(tests.PyslimTestCase):
    '''
    Test by comparing decoding to our previous direct implementation of struct decoding.
    '''

    def verify_decoding(self, t, decoder):
        ms = tskit.MetadataSchema(None)
        nt = t.copy()
        nt.metadata_schema = ms
        for a, b in zip(t, nt):
            md = a.metadata
            with pytest.warns(FutureWarning):
                omd = decoder(b.metadata)
            if md is None:
                assert omd is None
            else:
                assert md == omd.asdict()

    def verify_mutation_decoding(self, t):
        ms = tskit.MetadataSchema(None)
        nt = t.copy()
        nt.metadata_schema = ms
        for a, b in zip(t, nt):
            md = a.metadata
            with pytest.warns(FutureWarning):
                omd = pyslim.decode_mutation(b.metadata)
            assert md == {"mutation_list": [u.asdict() for u in omd]}

    def test_decoding(self, recipe):
        tables = recipe["ts"].tables
        self.verify_decoding(tables.populations, pyslim.decode_population)
        self.verify_decoding(tables.individuals, pyslim.decode_individual)
        self.verify_decoding(tables.nodes, pyslim.decode_node)
        self.verify_mutation_decoding(tables.mutations)


@pytest.mark.parametrize('recipe', [next(recipe_eq())], indirect=True)    
class TestMetadataAttributeError(tests.PyslimTestCase):
    """
    These are all only tested on a single recipe, the first grabbed from recipe
    """
    
    def test_population_error(self, recipe):
        ts = recipe["ts"]
        for x in ts.populations():
            if x.metadata is not None:
                with pytest.raises(AttributeError) as exec_info:
                    _ = x.metadata.slim_id
                assert 'legacy' in str(exec_info)
                with pytest.raises(AttributeError) as exec_info:
                    _ = x.metadata.selfing_fraction
                assert 'legacy' in str(exec_info)
                with pytest.raises(AttributeError) as exec_info:
                    _ = x.metadata.sex_ratio
                assert 'legacy' in str(exec_info)
            with pytest.raises(AttributeError) as exec_info:
                _ = x.metadata.ping
            assert "has no attribute 'ping'" in str(exec_info)
            break

    def test_individual_error(self, recipe):
        ts = recipe["ts"]
        for x in ts.individuals():
            with pytest.raises(AttributeError) as exec_info:
                _ = x.metadata.pedigree_id
            assert 'legacy' in str(exec_info)
            with pytest.raises(AttributeError) as exec_info:
                _ = x.metadata.age
            assert 'legacy' in str(exec_info)
            with pytest.raises(AttributeError) as exec_info:
                _ = x.metadata.subpopulation
            assert 'legacy' in str(exec_info)
            with pytest.raises(AttributeError) as exec_info:
                _ = x.metadata.sex
            assert 'legacy' in str(exec_info)
            with pytest.raises(AttributeError) as exec_info:
                _ = x.metadata.flags
            assert 'legacy' in str(exec_info)
            with pytest.raises(AttributeError) as exec_info:
                _ = x.metadata.pong
            assert "has no attribute 'pong'" in str(exec_info)
            break

    def test_node_error(self, recipe):
        ts = recipe["ts"]
        for x in ts.nodes():
            if x.metadata is not None:
                with pytest.raises(AttributeError) as exec_info:
                    _ = x.metadata.slim_id
                assert 'legacy' in str(exec_info)
                with pytest.raises(AttributeError) as exec_info:
                    _ = x.metadata.is_null
                assert 'legacy' in str(exec_info)
                with pytest.raises(AttributeError) as exec_info:
                    _ = x.metadata.genome_type
                assert 'legacy' in str(exec_info)
            with pytest.raises(AttributeError) as exec_info:
                _ = x.metadata.pang
            assert "has no attribute 'pang'" in str(exec_info)
            break

    def test_mutation_error(self, recipe):
        ts = recipe["ts"]
        for x in ts.mutations():
            with pytest.raises(KeyError) as exec_info:
                _ = x.metadata[0]
            assert 'legacy' in str(exec_info)
            with pytest.raises(KeyError) as exec_info:
                _ = x.metadata[999]
            assert 'legacy' in str(exec_info)
            with pytest.raises(KeyError):
                _ = x.metadata['ping']
            break
