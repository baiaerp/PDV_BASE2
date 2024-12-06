import streamlit as st
from streamlit_extras.stylable_container import stylable_container as style
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import datetime
from streamlit import session_state as ss
from err import errStorage
st.set_page_config(
    page_title='PDV - Admin',
    page_icon='👜',
    layout='wide',
    initial_sidebar_state='collapsed',
)

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

#### CODE AFTER THIS LINE ####

import loader

ss['today'] = datetime.datetime.today()

loader.loadInventory()
loader.loadParameters()

paramList = list(ss['dfParameters'].columns)
listStore = [paramList[1], paramList[2], paramList[3]]

with open('.streamlit/pswd.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    #config['preauthorized']
)
with st.container(border=False):
    authenticator.login(fields={'Form name': 'Login', 'Username':'Nome de Usuário', 'Password': 'Senha'})
    if st.session_state['authentication_status'] is False:
        st.error('Usuário/Senha incorreto(s)')
    elif st.session_state['authentication_status'] is None:
        st.warning('Por favor entre com usuário e senha')
    elif st.session_state['authentication_status']:
        st.write("---")
        ft = authenticator.logout(key='logout1')
        st.write("---")

        dfInitial = ss['dfInventory'][['qrcode', 'itemname', 'itemsize', 'colorid', 'minqty', 'store1qty', 'store2qty']]

        ss['s1'] = 0
        ss['s2'] = 0

        for q in range(len(dfInitial)):
            if dfInitial['minqty'][q] > dfInitial['store1qty'][q]:
                ss['s1'] += 1
            if dfInitial['minqty'][q] > dfInitial['store2qty'][q]:
                ss['s2'] += 1

        col_s1, col_s2 = st.columns([1,3])
        with col_s1:
            if st.button(":blue[Início]"):
                st.switch_page("Inicial.py")
            if st.button(":blue[Estoque]"):
                st.switch_page("pages/3_Estoque.py")
            if st.button(":blue[Fornecedor]"):
                st.switch_page("pages/4_Fornecedor.py")
            if st.button(":blue[Vendedor]"):
                st.switch_page("pages/5_Vendedor.py")
            if st.button(":blue[Compras]"):
                st.switch_page("pages/6_Compras.py")
            if st.button(":blue[Vendas]"):
                st.switch_page("pages/7_Vendas.py")
            if st.button(":blue[Configurar]"):
                st.switch_page("pages/8_Configurar.py")

        with col_s2:
            dt1a = list()
            dt2a = list()
            dt3a = list()
            with st.expander(f":blue[{ss['dfParameters'][paramList[1]][0]}], {ss['s1']}"):
                rprt = f"{ss['dfParameters'][paramList[1]][0]}\nQuantidades: Atual vs Mínima\n"
                for q1 in range(len(dfInitial)):
                    if dfInitial['minqty'][q1] > dfInitial['store1qty'][q1]:
                        msg = f"{dfInitial['qrcode'][q1]} | {dfInitial['itemname'][q1]} | {dfInitial['itemsize'][q1]} | {dfInitial['colorid'][q1]} \n\nMínimo: {dfInitial['minqty'][q1]}, Atual: {dfInitial['store1qty'][q1]}"
                        d1a = f"{dfInitial['qrcode'][q1]} | {dfInitial['itemname'][q1]} | {dfInitial['itemsize'][q1]} | {dfInitial['colorid'][q1]}"
                        d2a = f"{dfInitial['minqty'][q1]}" 
                        d3a = f"{dfInitial['store1qty'][q1]}"
                        rprt += str(msg).strip() + '\n'
                        # st.warning(str(msg).strip())
                        rprt += '-' * 65 + '\n'  # Linha divisória
                        dt1a.append(d1a)
                        dt2a.append(d2a)
                        dt3a.append(d3a)

                ss['df1'] = pd.DataFrame(data={'Item':dt1a, 'Mínimo':dt2a, 'Atual':dt3a})
                st.data_editor(ss['df1'],
                num_rows='fixed',
                use_container_width=True,
                hide_index=True,
                key='k1',)

            st.download_button(
                label=f"Baixar Relatório da :blue[{ss['dfParameters'][paramList[1]][0]}]",
                key=f"{paramList[1]}",
                data=rprt,
                file_name=f"{ss['dfParameters'][paramList[1]][0]}_{ss['s1']}.txt",
                mime='text')

            with st.expander(f":blue[{ss['dfParameters'][paramList[2]][0]}], {ss['s2']}"):
                dt1b = list()
                dt2b = list()
                dt3b = list()
                rprt = f"{ss['dfParameters'][paramList[2]][0]}\nQuantidades: Atual vs Mínima\n"
                for q2 in range(len(dfInitial)):
                    if dfInitial['minqty'][q2] > dfInitial['store2qty'][q2]:
                        msg = f"{dfInitial['qrcode'][q2]} | {dfInitial['itemname'][q2]} | {dfInitial['itemsize'][q2]} | {dfInitial['colorid'][q2]} \n\nMínimo: {dfInitial['minqty'][q2]}, Atual: {dfInitial['store2qty'][q2]}"
                        d1b = f"{dfInitial['qrcode'][q2]} | {dfInitial['itemname'][q2]} | {dfInitial['itemsize'][q2]} | {dfInitial['colorid'][q2]}"
                        d2b = f"{dfInitial['minqty'][q2]}" 
                        d3b = f"{dfInitial['store2qty'][q2]}"
                        rprt += str(msg).strip() + '\n'
                        # st.warning(str(msg).strip())
                        rprt += '-' * 65 + '\n'  # Linha divisória
                        dt1b.append(d1b)
                        dt2b.append(d2b)
                        dt3b.append(d3b)
                ss['df2'] = pd.DataFrame(data={'Item':dt1b, 'Mínimo':dt2b, 'Atual':dt3b})
                st.data_editor(ss['df2'],
                num_rows='fixed',
                use_container_width=True,
                hide_index=True,
                key='k2',)

            st.download_button(
                label=f"Baixar Relatório da :blue[{ss['dfParameters'][paramList[2]][0]}]",
                key=f"{paramList[2]}",
                data=rprt,
                file_name=f"{ss['dfParameters'][paramList[2]][0]}_{ss['s2']}.txt",
                mime='text')
            
    # with st.expander('Mudar a senha'):
    #     if st.session_state["authentication_status"]:
    #         try:
    #             if authenticator.reset_password(st.session_state["username"], fields={'Form name':'', 'Current password':'Senha atual', 'New password':'Nova senha', 'Repeat password': 'Repetir nova senha', 'Reset':'Mudar'}, clear_on_submit=True):
    #                 with open('.streamlit/pswd.yaml', 'w') as file:
    #                     yaml.dump(config, file, default_flow_style=False)
    #                     st.success('Senha alterada!')

    #         except Exception as e:
    #             st.error(e)
