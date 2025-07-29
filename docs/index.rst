NCBI Client Documentation
========================

Welcome to the NCBI Client documentation! This Python library provides a comprehensive interface to NCBI's databases and web services, including PubMed, PMC, GenBank, and more.

.. note::
   This documentation is for NCBI Client version |version|. For the latest updates and source code, visit our `GitHub repository <https://github.com/your-username/ncbi-client>`_.

Quick Links
-----------

* :doc:`user-guide/installation` - Get started with installation
* :doc:`user-guide/quick-start` - 5-minute quick start guide  
* :doc:`user-guide/cli` - Command-line interface documentation
* :doc:`api-reference/core` - Complete API reference
* :doc:`tutorials/literature-search` - Step-by-step tutorials
* :doc:`examples/README` - Code examples and use cases

Features Overview
-----------------

🔍 **Search & Retrieve**
   Search across 40+ NCBI databases and retrieve records in multiple formats

📊 **Data Processing** 
   Built-in parsers for XML, JSON, FASTA, and GenBank formats

🛠️ **Developer Tools**
   Command-line interface, caching, rate limiting, and error handling

🔬 **Extended APIs**
   NCBI Datasets API and PubChem API integration

⚡ **Performance**
   Efficient batch operations, history tracking, and concurrent requests

What's New
----------

.. versionadded:: 1.0.0
   - SSL certificate verification options
   - Enhanced CLI with more output formats
   - Comprehensive documentation system
   - Extended API coverage for NCBI Datasets and PubChem

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user-guide/installation
   user-guide/quick-start
   user-guide/cli

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api-reference/core
   api-reference/eutils
   api-reference/parsers
   api-reference/converters
   api-reference/utils

.. toctree::
   :maxdepth: 2
   :caption: Tutorials

   tutorials/literature-search
   tutorials/sequence-analysis
   tutorials/data-mining
   tutorials/batch-processing

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/README
   examples/basic-usage
   examples/advanced-usage
   examples/integration

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide

   developer/contributing
   developer/testing
   developer/architecture
   developer/api-design

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   changelog
   troubleshooting
   faq
   glossary

Getting Help
------------

If you're having trouble with NCBI Client, try these resources:

1. **Documentation**: Start with our :doc:`user-guide/quick-start` guide
2. **Examples**: Browse our :doc:`examples/README` for common use cases  
3. **Troubleshooting**: Check our :doc:`troubleshooting` guide for common issues
4. **FAQ**: See :doc:`faq` for frequently asked questions
5. **Issues**: Report bugs or request features on `GitHub Issues <https://github.com/your-username/ncbi-client/issues>`_

Contributing
------------

We welcome contributions! Please see our :doc:`developer/contributing` guide for:

* Setting up a development environment
* Running tests
* Code style guidelines
* Submitting pull requests

License
-------

This project is licensed under the MIT License. See the `LICENSE <https://github.com/your-username/ncbi-client/blob/main/LICENSE>`_ file for details.

Citation
--------

If you use NCBI Client in your research, please cite:

.. code-block:: bibtex

   @software{ncbi_client,
     title = {NCBI Client: A Python Library for NCBI Database Access},
     author = {NCBI Client Contributors},
     year = {2024},
     url = {https://github.com/your-username/ncbi-client},
     version = {1.0.0}
   }

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. include:: ../README.md
   :parser: myst_parser.sphinx_
