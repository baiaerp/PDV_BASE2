import streamlit as st
from updateitemqty import InventtableConnection

database_url = 'postgresql+psycopg2://postgres:reWchpesoUGUmqirjmCoUfcXIXAntRWj@junction.proxy.rlwy.net:22310/railway'

# Inicialização do estado da sessão
if 'show_popup' not in st.session_state:
    st.session_state['show_popup'] = False

# Função para mostrar a janela de atualização de estoque
def show_update_stock_popup():
    with st.form(key='update_stock_form'):
        qrcode = st.text_input("Código QR do item: ")
        quantity_store1 = st.number_input("Quantidade na Loja 1", min_value=0, step=1)
        quantity_store2 = st.number_input("Quantidade na Loja 2", min_value=0, step=1)
        quantity_store3 = st.number_input("Quantidade na Loja 3", min_value=0, step=1)
        
        # Botão para submeter o formulário
        submit_button = st.form_submit_button(label='Salvar')
        
        if submit_button:
            # Exibir mensagens de sucesso
            st.success(f"Item '{qrcode}' salvo com sucesso!")
            st.write(f"Quantidade na Loja 1: {quantity_store1}")
            st.write(f"Quantidade na Loja 2: {quantity_store2}")
            st.write(f"Quantidade na Loja 3: {quantity_store3}")
            
            # Chamar a função de atualização de estoque
            item_conn = InventtableConnection(database_url)
            item_conn.loadstoresqty()
            item_conn.addqty_store1 = quantity_store1 
            item_conn.addqty_store2 = quantity_store2
            item_conn.addqty_store3 = quantity_store3
            item_conn.storeqty_update()

# Título da aplicação
st.title("Gerenciamento de Estoque")

# Mostrar o "popup" se o botão foi clicado
if st.session_state.show_popup:
    show_update_stock_popup()
    close_button = st.button("Fechar")
    if close_button:
        st.session_state.show_popup = False
