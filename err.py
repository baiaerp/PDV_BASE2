import streamlit as st
from streamlit import session_state as ss

def errStorage():
    if 'err' not in ss:
        ss['err'] = {
            # Estoque
            'addItem': [],
            'editItem': [],
            'popover': [],

            # Fornecedor
            'addVendor': [],
            'editVendor': [],

            # Vendedor
            'addSeller': [],
            'editSeller': [],

            # Compras
            'addPurchase': [],
            'editPurchase': [],

            # Vendas
            'addSales': [],
            'editSales': [],

            # Configurar
            'update': [],
            'enabler': [],
            
            }
    return ss['err']
