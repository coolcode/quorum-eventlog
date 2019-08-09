import unittest
from service import ContractService


# python3 -m unittest test.test_init_project or python3 -m unittest test/test_init_project.py
class TestInitProject(unittest.TestCase):
    def test_deploy_and_init(self):

        # flag to force project redeployment
        force_redeploy = False

        cs = ContractService(force_redeploy)
        print('--> Successfully initialized the project ^_^')
