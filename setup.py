from setuptools import setup, find_packages

setup(
    name="spca_crm",
    version="0.1.0",
    description="ERPNext Helpdesk module for SPCA cruelty report management",
    author="SPCA Digital Team",
    author_email="dev@spca.org.za",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
)
