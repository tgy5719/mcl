# -*- coding: utf-8 -*-
{
    "name": "Automatic Customer Number",
    "version": "1.0.5",
    'license': 'LGPL-3',
    'author': 'Prixgen Tech Solutions.Pvt.Ltm',
    'website': 'https://www.prixgen.com',
    "summary": """
    Automatically create the customer number from a sequence when a customer is being created.
    """,
    "description": """
Automatic Customer Number
=========================
Automatically create the customer number from a sequence when a customer is being created.

The customer number can be configured in the sequence "Customer Number".
    """,
    "category": "Sales",
    "depends": [
        "base",
        "sale","contacts","product","purchase","account",
    ],
    "data": [
        "data/sequencer.xml",
        "views/partner.xml",
    ],
    "installable": True,
    "auto_install": False,
}
