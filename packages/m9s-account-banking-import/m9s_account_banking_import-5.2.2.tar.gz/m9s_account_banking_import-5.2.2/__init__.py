# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import banking_import
from . import batch

__all__ = ['register']


def register():
    Pool.register(
        batch.BatchLine,
        banking_import.BankingImportConfiguration,
        banking_import.BankingImportLine,
        banking_import.RunImportInfoNoLines,
        banking_import.RunImportShow,
        banking_import.RunImportStart,
        module='account_banking_import', type_='model')
    Pool.register(
        banking_import.RunImport,
        module='account_banking_import', type_='wizard')
