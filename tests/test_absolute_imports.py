#!/usr/bin/env python3
"""
Test script to verify absolute imports work correctly from different contexts.
"""

import sys
import importlib

def test_absolute_imports():
    """Test that all modules can be imported using absolute paths."""
    modules_to_test = [
        'ncbi_client',
        'ncbi_client.core.base_client',
        'ncbi_client.core.exceptions', 
        'ncbi_client.core.rate_limiter',
        'ncbi_client.eutils.esearch',
        'ncbi_client.eutils.efetch',
        'ncbi_client.parsers.xml_parser',
        'ncbi_client.parsers.fasta_parser',
        'ncbi_client.converters.format_converter',
        'ncbi_client.converters.sequence_tools',
        'ncbi_client.datasets.datasets_api',
        'ncbi_client.pubchem.pubchem_api',
        'ncbi_client.utils.cache',
        'ncbi_client.utils.helpers'
    ]
    
    print("🔍 Testing absolute imports for all modules...")
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            failed_imports.append(module_name)
    
    if not failed_imports:
        print("\n🎉 All modules imported successfully with absolute paths!")
        return True
    else:
        print(f"\n❌ Failed to import {len(failed_imports)} modules:")
        for module in failed_imports:
            print(f"   - {module}")
        return False

def test_functionality():
    """Test basic functionality works with absolute imports."""
    try:
        # Test direct module import
        from ncbi_client.core.base_client import NCBIClient
        from ncbi_client.eutils.esearch import ESearch
        from ncbi_client.parsers.xml_parser import XMLParser
        
        print("✅ Direct absolute imports work")
        
        # Test package-level imports  
        import ncbi_client
        client = ncbi_client.NCBIClient(email='test@example.com')
        
        print("✅ Package-level imports work")
        print(f"✅ Client created: {client}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Absolute Import Implementation")
    print("=" * 50)
    
    import_success = test_absolute_imports()
    print()
    
    functionality_success = test_functionality()
    print()
    
    print("=" * 50)
    if import_success and functionality_success:
        print("🎉 All tests passed! Absolute imports are working perfectly.")
        return 0
    else:
        print("❌ Some tests failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
