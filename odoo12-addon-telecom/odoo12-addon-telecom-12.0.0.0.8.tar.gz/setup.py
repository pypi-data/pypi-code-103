import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'depends_override': {
            'product_contract': 'odoo12-addon-product-contract==12.0.5.2.1',
        },
    },
)
