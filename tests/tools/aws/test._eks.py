import os
import unittest
from unittest.mock import patch
from genia.tools.aws_client.eks.aws_client_eks import AWSClientEKS

class TestEKS(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PYTHON_E2E_TESTS") != None, "Not in e2e test environment")
    def setUp(self):
        self.api_client_eks = AWSClientEKS()

    @patch('boto3.client')
    def test_list_clusters_eks(self, mock_boto_client):
        mock_boto_client.return_value.list_clusters.return_value = {"clusters": ["cluster1", "cluster2"]}
        region_name = "us-west-2"
        clusters = self.api_client_eks.list_clusters_eks(region_name)
        self.assertEqual(clusters, ["cluster1", "cluster2"])

    @patch('boto3.client')
    def test_describe_cluster_eks(self, mock_boto_client):
        mock_boto_client.return_value.describe_cluster.return_value = {
            "cluster": {"name": "cluster1", "status": "ACTIVE"}
        }
        cluster_name = "cluster1"
        region_name = "us-west-2"
        cluster_info = self.api_client_eks.describe_cluster_eks(cluster_name, region_name)
        self.assertEqual(cluster_info, {"name": "cluster1", "status": "ACTIVE"})

    # Additional tests can be added here as needed

if __name__ == "__main__":
    unittest.main()
