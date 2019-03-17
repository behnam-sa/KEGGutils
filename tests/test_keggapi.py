import unittest
from unittest.mock import patch

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import KEGGutils.KEGGapi as kgapi

from tests.download_fresh_test_responses import unpickle_resp


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, url = None, json_data = None, text = None, status_code = 404, reason = 'Not Found'):
            self.url = url
            self.json_data = json_data
            self.status_code = status_code
            self.text = text
            self.reason = reason
            
            self.ok = status_code == 200
            
            
            if (self.ok):
                self.reason = 'OK'
            
        def json(self):
            return self.json_data
        
    
    if args[0] == "http://rest.kegg.jp/get/br:br08301/json":
        return MockResponse(url = args[0],
                            json_data = {"key1": "value1"},
                            status_code = 200)
    elif args[0] == 'http://rest.kegg.jp/get/hsa05130/image':
        return unpickle_resp("testpng")
    elif args[0] == "http://rest.kegg.jp/get/C00002/image":
        return unpickle_resp("testgif")
    elif args[0] ==  "http://rest.kegg.jp/list/hsa":
        return MockResponse(url = args[0],
                            text = "testgene1\ttestdescription1\ntestgene2\ttestdescription2",
                            status_code = 200)

    return MockResponse()


class KEGGapiTest(unittest.TestCase):
    
    @patch('requests.get', side_effect = mocked_requests_get)
    def test_download_json_file_doesnt_exist_yet(self, mockrequestsget):
        
        data = kgapi.download_json("http://rest.kegg.jp/get/br:br08301/json", "json_testing")
        self.assertEqual(data, {"key1": "value1"})
        
    @patch('KEGGutils.KEGGapi.get_organism_codes', return_value = ['hsa'])
    @patch('requests.get', side_effect = mocked_requests_get,)
    def test_process_request_text_wantdescrFalse(self, mocked_orgcodes, mockrequestget):
        itemlist = kgapi.keggapi_list("hsa", want_descriptions = False)
        test_genes = set(["testgene1", "testgene2"])
        self.assertEqual(set(itemlist), set(test_genes))
        
        
    @patch('KEGGutils.KEGGapi.get_organism_codes', return_value = ['hsa'])
    @patch('requests.get', side_effect = mocked_requests_get,)
    def test_process_request_text_wantdescrTrue(self, mocked_orgcodes, mockrequestget):
        itemlist, descriptionlist = kgapi.keggapi_list("hsa", want_descriptions = True)
        test_genes = set(["testgene1", "testgene2"])
        test_descriptions = set(["testdescription1", "testdescription2"])
        
        self.assertEqual(set(itemlist), set(test_genes))
        self.assertEqual(set(descriptionlist), set(test_descriptions))
        
        
        
        
        
        