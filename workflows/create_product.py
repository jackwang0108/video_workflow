"""
create_product.py 用于从Task中创建Product

    @Time    : 2025/01/09
    @Author  : JackWang
    @File    : create_product.py
    @IDE     : VsCode
"""

# Standard Library

# My Library
from utils.helper import Task, Product


def create_product(task: Task) -> Product:
    product_dict = task.model_dump() | {"status": "created"}
    return Product(**product_dict)
