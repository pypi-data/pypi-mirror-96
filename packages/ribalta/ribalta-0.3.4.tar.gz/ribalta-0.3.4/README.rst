==========================
Document Management System
==========================

This is a library for creating RiBa CBI documents starting from Odoo 12 data.

**Table of contents**

.. contents::
   :local:

Installation
============

The library is available on PyPI and the suggested way of installing
it is by using pip:

.. code-block:: 

 pip install ribalta

Usage
=====

Import the Document and Receipt classes:

.. code-block:: python

 from ribalta import Document, Receipt

Create and instance of the Document class passing the required data:

.. code-block:: python

 riba_doc = Document(
    creditor_company = creditor_res_partner_obj,
    creditor_bank_account = creditor_res_partner_bank_obj
 )

Create a Receipt object for each receipt to be included in the CBI and
add it to the riba_doc:

.. code-block:: python

 rcpt_1 = Receipt(move_line_1, invoice_1, debtor_partner_1, debtor_bank_1)
 rcpt_2 = Receipt(move_line_2, invoice_2, debtor_partner_2, debtor_bank_2)
 
 riba_doc.add_receipt(rcpt_1)
 riba_doc.add_receipt(rcpt_2)

Render the CBI document (the result of the rendering is a string):

.. code-block:: python

 cbi_str = riba_doc.render_cbi()

See the docstring for details about the required arguments.

Known issues / Roadmap
======================

No known issues at the moment

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/LibrERP/Pylibs/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Do not contact contributors directly about support or help with technical issues.

License
=======
License: `LGPL-3 <http://www.gnu.org/licenses/lgpl-3.0-standalone.html>`_

Credits
=======

Authors
~~~~~~~

* Didotech s.r.l.
* SHS-AV s.r.l.

Contributors
~~~~~~~~~~~~

* Marco Tosato <marco.tosato@didotech.com>
