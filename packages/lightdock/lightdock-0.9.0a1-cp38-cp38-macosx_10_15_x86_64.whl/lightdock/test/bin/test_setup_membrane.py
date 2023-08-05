"""Regression tests for testing simulation setup using membrane"""

import shutil
import os
import filecmp
from pathlib import Path
from lightdock.test.bin.regression import RegressionTest


class TestSetupWithMembrane(RegressionTest):

    def __init__(self):
        super().__init__()
        self.path = Path(__file__).absolute().parent
        self.test_path = self.path / 'scratch_setup_membrane'
        self.golden_data_path = self.path / 'golden_data' / 'regression_setup_membrane'

    def setup(self):
        self.ini_path()
        shutil.copy(self.golden_data_path / '3x29_receptor_membrane.pdb', self.test_path)
        shutil.copy(self.golden_data_path / '3x29_ligand.pdb', self.test_path)

    def teardown(self):
        self.clean_path()

    def test_lightdock_setup_with_membrane_automatic(self):
        os.chdir(self.test_path)

        num_swarms = 400
        num_glowworms = 50

        command = f"lightdock3_setup.py 3x29_receptor_membrane.pdb 3x29_ligand.pdb -g {num_glowworms} "
        command += f" -s {num_swarms} --noxt --noh -membrane >> test_lightdock.out"
        os.system(command)

        assert filecmp.cmp(self.golden_data_path / 'init' / 'swarm_centers.pdb',
                           self.test_path / 'init' / 'swarm_centers.pdb')
        assert filecmp.cmp(self.golden_data_path / 'setup.json',
                           self.test_path / 'setup.json')
        assert filecmp.cmp(self.golden_data_path / 'init' / 'initial_positions_0.dat',
                           self.test_path / 'init' / 'initial_positions_0.dat')
        assert filecmp.cmp(self.golden_data_path / 'init' / 'initial_positions_35.dat',
                           self.test_path / 'init' / 'initial_positions_35.dat')
        assert filecmp.cmp(self.golden_data_path / 'init' / 'initial_positions_139.dat',
                           self.test_path / 'init' / 'initial_positions_139.dat')
        assert filecmp.cmp(self.golden_data_path / 'lightdock_3x29_receptor_membrane.pdb',
                           self.test_path / 'lightdock_3x29_receptor_membrane.pdb')
        assert filecmp.cmp(self.golden_data_path / 'lightdock_3x29_ligand.pdb',
                           self.test_path / 'lightdock_3x29_ligand.pdb')



class TestSetupWithMembraneAndRestraints(RegressionTest):

    def __init__(self):
        super().__init__()
        self.path = Path(__file__).absolute().parent
        self.test_path = self.path / 'scratch_setup_membrane_restraints'
        self.golden_data_path = self.path / 'golden_data' / 'regression_setup_membrane_restraints'

    def setup(self):
        self.ini_path()
        shutil.copy(self.golden_data_path / '3x29_receptor_membrane.pdb', self.test_path)
        shutil.copy(self.golden_data_path / '3x29_ligand.pdb', self.test_path)
        shutil.copy(self.golden_data_path / 'restraints.list', self.test_path)

    def teardown(self):
        self.clean_path()

    def test_lightdock_setup_with_membrane_automatic(self):
        os.chdir(self.test_path)

        num_swarms = 400
        num_glowworms = 50

        command = f"lightdock3_setup.py 3x29_receptor_membrane.pdb 3x29_ligand.pdb -g {num_glowworms} "
        command += f" -s {num_swarms} --noxt --noh -membrane -rst restraints.list >> test_lightdock.out"
        os.system(command)

        assert filecmp.cmp(self.golden_data_path / 'init' / 'swarm_centers.pdb',
                           self.test_path / 'init' / 'swarm_centers.pdb')
        assert filecmp.cmp(self.golden_data_path / 'setup.json',
                           self.test_path / 'setup.json')
        assert filecmp.cmp(self.golden_data_path / 'init' / 'initial_positions_0.dat',
                           self.test_path / 'init' / 'initial_positions_0.dat')
        assert filecmp.cmp(self.golden_data_path / 'init' / 'initial_positions_5.dat',
                           self.test_path / 'init' / 'initial_positions_5.dat')
        assert filecmp.cmp(self.golden_data_path / 'lightdock_3x29_receptor_membrane.pdb',
                           self.test_path / 'lightdock_3x29_receptor_membrane.pdb')
        assert filecmp.cmp(self.golden_data_path / 'lightdock_3x29_ligand.pdb',
                           self.test_path / 'lightdock_3x29_ligand.pdb')
