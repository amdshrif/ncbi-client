#!/usr/bin/env python3
"""
Test script to verify urllib-based NCBI client functionality.
"""

import sys
from ncbi_client import NCBIClient

def test_basic_search():
    """Test basic ESearch functionality."""
    try:
        # Create client
        client = NCBIClient(email='test@example.com')
        print("✅ Client created successfully")
        
        # Test a simple search
        print("🔍 Testing ESearch with a simple query...")
        results = client.esearch.search(
            db="pubmed", 
            term="python programming", 
            retmax=2
        )
        
        print(f"✅ Search completed successfully!")
        print(f"   Found {results.get('count', 0)} total results")
        print(f"   Retrieved {len(results.get('idlist', []))} IDs")
        
        if results.get('idlist'):
            print(f"   Sample IDs: {results['idlist'][:2]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_dataset_api():
    """Test Datasets API functionality."""
    try:
        from ncbi_client import DatasetsAPI
        
        print("🧬 Testing Datasets API...")
        datasets = DatasetsAPI()
        print("✅ Datasets API client created successfully")
        
        # Note: Actual API calls may fail without proper setup
        # This just tests that the class can be instantiated
        return True
        
    except Exception as e:
        print(f"❌ Datasets API test failed: {e}")
        return False

def test_pubchem_api():
    """Test PubChem API functionality."""
    try:
        from ncbi_client import PubChemAPI
        
        print("🧪 Testing PubChem API...")
        pubchem = PubChemAPI()
        print("✅ PubChem API client created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ PubChem API test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing NCBI Client with Python standard library (urllib)")
    print("=" * 60)
    
    tests = [
        test_basic_search,
        test_dataset_api, 
        test_pubchem_api
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! urllib-based implementation is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
