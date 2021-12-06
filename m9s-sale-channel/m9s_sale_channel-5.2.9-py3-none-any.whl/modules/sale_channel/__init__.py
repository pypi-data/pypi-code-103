# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool
from . import channel
from . import ir
from . import wizard
from . import product
from . import party
from . import sale
from . import user

__all__ = ['register']


def register():
    Pool.register(
        channel.SaleChannel,
        channel.TaxMapping,
        channel.ChannelException,
        channel.ChannelOrderState,
        ir.Cron,
        party.Party,
        party.PartySaleChannelListing,
        user.User,
        sale.Sale,
        sale.SaleLine,
        product.AddProductListingStart,
        product.ProductSaleChannelListing,
        product.Product,
        product.Template,
        product.TemplateSaleChannelListing,
        wizard.ImportDataWizardStart,
        wizard.ImportDataWizardSuccess,
        wizard.ImportDataWizardChooseAcccounts,
        wizard.ExportDataWizardStart,
        wizard.ExportDataWizardSuccess,
        wizard.ImportOrderStatesStart,
        wizard.ExportPricesStatus,
        wizard.ExportPricesStart,
        module='sale_channel', type_='model')
    Pool.register(
        product.AddProductListing,
        wizard.ImportDataWizard,
        wizard.ExportDataWizard,
        wizard.ImportOrderStates,
        wizard.ExportPrices,
        module='sale_channel', type_='wizard')
