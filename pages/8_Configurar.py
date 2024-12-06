 ### PRINCIPAIS IMPORTS, SEMPRE ATUALIZAR QUANDO REMOVER/ADICIONAR ALGUMA FUNÇÃO!
import streamlit as st
import pandas as pd
from streamlit import session_state as ss
import datetime
import random
import sqlalchemy
from sqlalchemy import text, create_engine, MetaData, Table, update, insert
from sqlalchemy.orm import sessionmaker

from err import errStorage

### CONFIGURAÇÃO DA PÁGINA TEM QUE SER, SEMPRE, O PRIMEIRO CÓDIGO APÓS OS IMPORTS
st.set_page_config(
    page_title='PDV - Admin',
    page_icon='📒', 
    layout='wide'
)

### PRIMEIRA FUNÇÃO REAL É A CONEXÃO COM O BANCO DE DADOS
conn = st.connection('postgresql', type='sql')

### DEFINIÇÃO DE VARIÁVIES
hoje = datetime.datetime.today() # DATA DE HOJE PARA FUNÇÕES COM DATA

random.seed(25)
keys = []
for i in range(100):
    keys.append(random.random())

sucesso = 'Sucesso!'

import loader
loader.loadParameters()

dbUrl = st.secrets['vars']['database_url']
engine = create_engine(dbUrl)
meta = sqlalchemy.MetaData()
meta.reflect(bind=conn.engine)
ss['paramtable'] = sqlalchemy.Table('paramtable', meta)

ss['config_id'] = ss['dfParameters']['config_id'][0]
ss['storename1'] = ss['dfParameters']['storename1'][0]
ss['storename2'] = ss['dfParameters']['storename2'][0]
ss['storename3'] = ss['dfParameters']['storename3'][0]
ss['pix1'] = ss['dfParameters']['pix1'][0]
ss['dinheiro1'] = ss['dfParameters']['dinheiro1'][0]
ss['debito1'] = ss['dfParameters']['debito1'][0]
ss['credvista1'] = ss['dfParameters']['credvista1'][0]
ss['credparc1'] = ss['dfParameters']['credparc1'][0]
ss['dinheiro2'] = ss['dfParameters']['dinheiro2'][0]
ss['debito2'] = ss['dfParameters']['debito2'][0]
ss['credvista2'] = ss['dfParameters']['credvista2'][0]
ss['pix2'] = ss['dfParameters']['pix2'][0]
ss['taxcredvista'] = ss['dfParameters']['taxcredvista'][0]
ss['taxcred2x'] = ss['dfParameters']['taxcred2x'][0]
ss['taxcred3x'] = ss['dfParameters']['taxcred3x'][0]
ss['taxcred4x'] = ss['dfParameters']['taxcred4x'][0]
ss['taxcred5x'] = ss['dfParameters']['taxcred5x'][0]
ss['taxcred6x'] = ss['dfParameters']['taxcred6x'][0]
ss['taxcred7x'] = ss['dfParameters']['taxcred7x'][0]
ss['taxcred8x'] = ss['dfParameters']['taxcred8x'][0]
ss['taxcred9x'] = ss['dfParameters']['taxcred9x'][0]
ss['taxcred10x'] = ss['dfParameters']['taxcred10x'][0]
ss['purchpadrao'] = ss['dfParameters']['purchpadrao'][0]
ss['purchpix'] = ss['dfParameters']['purchpix'][0]
ss['purchcheque'] = ss['dfParameters']['purchcheque'][0]
ss['purchduplicata'] = ss['dfParameters']['purchduplicata'][0]
ss['purchcredvista'] = ss['dfParameters']['purchcredvista'][0]
ss['purchcred2x'] = ss['dfParameters']['purchcred2x'][0]
ss['purchcred3x'] = ss['dfParameters']['purchcred3x'][0]
ss['purchcred4x'] = ss['dfParameters']['purchcred4x'][0]


listStore = ss['storename1'], ss['storename2'], ss['storename3']
listPay1 = ss['pix1'], ss['dinheiro1'], ss['debito1'], ss['credvista1'], ss['credparc1']
listPay2 = ss['dinheiro2'], ss['debito2'],ss['credvista2'], ss['pix2']

def update(u):
    try:
        with conn.session as sess:
            sess.execute(u)
            sess.commit()

            st.success(f"Inventário: {sucesso}")

    except Exception as e:
        ss['err']['update'].append(f"Update error: {e}")
        st.warning(ss['err']['update'][len(ss['err']['update'])-1])

### COLUNAS PARA OS DF TEMPORÁRIOS 
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

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
        @st.fragment
        def fragment():
            tabVars, tabAct, = st.tabs(['Definir Valor Padrão', 'Reabilitar Valores'])

            with tabVars:
                with st.form(key='p_form', clear_on_submit=True):
                    ss['config_id'] = 1
                    col0, col1, col2, = st.columns(3)
                    with col0:
                        ss['store1'] = st.text_input(f'Nome da :blue[Loja 1]', value = listStore[0])
                    with col1:
                        ss['store2'] = st.text_input(f'Nome da :blue[Loja 2]', value = listStore[1])
                    with col2:
                        ss['store3'] = st.text_input(f'Nome da :blue[Loja 3]', value = listStore[2])

                    st.write('---')
                    col3, col4 = st.columns(2)
                    with col3:
                        st.write('Meios de Pagamento ao :blue[Receber] (tipo 1)')
                        ss['pix1'] = st.checkbox('PIX', value = ss['pix1'], key=keys[1])
                        ss['dinheiro1'] = st.checkbox('Dinheiro', value = ss['dinheiro1'], key=keys[2])
                        ss['debito1'] = st.checkbox('Débito', value = ss['debito1'], key=keys[3])
                        ss['avista1'] = st.checkbox('Crédito a vista', value = ss['credvista1'], key=keys[4])
                        ss['parcelado1'] = st.checkbox('Crédito Parcelado', value = ss['credparc1'], key=keys[5])

                    with col4:
                        st.write('Meios Pagamento ao :blue[Receber] (tipo 2)')
                        ss['dinheiro2'] = st.checkbox('Dinheiro', value = ss['dinheiro2'], key=keys[6])
                        ss['debito2'] = st.checkbox('Débito', value = ss['debito2'], key=keys[7])
                        ss['avista2'] = st.checkbox('Crédito a vista', value = ss['credvista2'], key=keys[8])
                        ss['pix2'] = st.checkbox('PIX', value = ss['pix2'], key=keys[9])

                    st.write('---')
                    st.write('Porcentagem :blue[Dedutível] ao Parcelar')
                    col5, col6, col7, col8, col9 = st.columns(5)
                    with col5:
                        ss['c1'] = st.number_input(label='Crédito a vista/Débito', key=keys[10], value = ss['taxcredvista'])
                        ss['c6'] = st.number_input(label='Crédito, 6x', key=keys[11], value = ss['taxcred6x'])

                    with col6:
                        ss['c2'] = st.number_input(label='Crédito, 2x', key=keys[12], value = ss['taxcred2x'])
                        ss['c7'] = st.number_input(label='Crédito, 7x', key=keys[13], value = ss['taxcred7x'])

                    with col7:
                        ss['c3'] = st.number_input(label='Crédito, 3x', key=keys[14], value = ss['taxcred3x'])
                        ss['c8'] = st.number_input(label='Crédito, 8x', key=keys[15], value = ss['taxcred8x'])

                    with col8:
                        ss['c4'] = st.number_input(label='Crédito, 4x', key=keys[16], value = ss['taxcred4x'])
                        ss['c9'] = st.number_input(label='Crédito, 9x', key=keys[17], value = ss['taxcred9x'])
                    with col9:
                        ss['c5'] = st.number_input(label='Crédito, 5x', key=keys[18], value = ss['taxcred5x'])
                        ss['c10'] = st.number_input(label='Crédito, 10x', key=keys[19], value = ss['taxcred10x'])

                    st.write('---')
                    st.write('Meios de Pagamento ao :blue[Comprar]')
                    ss['cdefault'] = st.checkbox('Padrão', value = ss['purchpadrao'], key=keys[20])
                    ss['cpix'] = st.checkbox('PIX', value = ss['purchpix'], key=keys[21])
                    ss['ccpd'] = st.checkbox('Cheque Pré-Datado', value = ss['purchcheque'], key=keys[22])
                    ss['cd'] = st.checkbox('Duplicata', value = ss['purchduplicata'], key=keys[23])
                    ss['cv'] = st.checkbox('Crédito a vista', value = ss['purchcredvista'], key=keys[24])
                    ss['cc2'] = st.checkbox('Crédito, 2x', value = ss['purchcred2x'], key=keys[25])
                    ss['cc3'] = st.checkbox('Crédito, 3x', value = ss['purchcred3x'], key=keys[26])
                    ss['cc4'] = st.checkbox('Crédito, 4x', value = ss['purchcred4x'], key=keys[27])

                    ok = st.form_submit_button(':blue[Salvar] Configurações')
                    if ok:
                        u = sqlalchemy.update(ss['paramtable'])
                        u = u.values({
                            'config_id': 1, 
							ss['storename1']: ss['store1'],
							ss['storename2']: ss['store2'],
							ss['storename3']: ss['store3'],
							ss['pix1']: ss['pix1'],
							ss['dinheiro1']: ss['dinheiro1'],
							ss['debito1']: ss['debito1'],
							ss['credvista1']: ss['avista1'],
							ss['credparc1']: ss['parcelado1'],
							
							ss['dinheiro2']: ss['dinheiro2'],
							ss['debito2']: ss['debito2'],
							ss['credvista2']: ss['avista2'],
							ss['pix2']: ss['pix2'],
							ss['taxcredvista']: ss['c1'],
							ss['taxcred2x']: ss['c2'],
							ss['taxcred3x']: ss['c3'],
							ss['taxcred4x']: ss['c4'],
							ss['taxcred5x']: ss['c5'],
							ss['taxcred6x']: ss['c6'],
							ss['taxcred7x']: ss['c7'],
							ss['taxcred8x']: ss['c8'],
							ss['taxcred9x']: ss['c9'],
							ss['taxcred10x']: ss['c10'],
							ss['purchpadrao']: ss['cdefault'],
							ss['purchpix']: ss['cpix'],
							ss['purchcheque']: ss['ccpd'],
							ss['purchduplicata']: ss['cd'],
							ss['purchcredvista']: ss['cv'],
							ss['purchcred2x']: ss['cc2'],
							ss['purchcred3x']: ss['cc3'],
							ss['purchcred4x']: ss['cc4'],

                            })
                        u = u.where(ss['paramtable'].c.config_id == 1)
                        update(u)

            with tabAct:
                dfOptions = {'Estoque':'dfInventory_D', 'Fornecedor':'dfVendor_D', 'Vendedor':'dfSeller_D', 'Compras':'dfPurchase_D', 'Vendas':'dfSales_D'}

                tbl = {'inventtable':
                    ['itemid', 'itemname','qrcode'], 
                    'vendtable':
                    ['vendid', 'vendname', 'pixkey'], 
                    'sellertable':
                    ['sellerid', 'sellername','pixkey'], 
                    'purchtable':
                    ['purchid', 'vendname','purchdate'],
                    'salestable':
                    ['salesid', 'itemname', 'qrcode']}
                
                enable_Sort = list(dfOptions.keys())
                enable_Sort.sort()
                loads = [loader.loadInventory_D(), loader.loadVendor_D(), loader.loadSeller_D(), loader.loadPurchase_D(), loader.loadSales_D()]
                enableDf = st.selectbox('Definir sessão para :blue[HABILITAR]', options=enable_Sort)
                j = list(dfOptions.keys()).index(enableDf)
                loads[j]

                def enabler(df, table, idx, name, detail):
                    ss[table] = sqlalchemy.Table(table, meta)
                    df = st.data_editor(
                        df,
                        num_rows='fixed',
                        use_container_width=True,
                        column_config={
                        'disabled': st.column_config.CheckboxColumn('Reativar?', disabled=False),
                        name: st.column_config.Column('Nome',disabled=True),
                        idx: st.column_config.Column('Identificador',disabled=True),
                        detail: st.column_config.Column('Detalhe',disabled=True),
                        },
                        hide_index=True,
                        key=keys[28],
                        column_order=['disabled', name, idx, detail])

                    confirm = st.button('Reabilitar itens :blue[DESMARCADOS]')
                    enable_me = list()
                    if confirm:
                        for a in range(len(df['disabled'])):
                            if df['disabled'][a] == False:
                                enable_me.append(df[idx][a])
                        if confirm:
                            for me in enable_me:
                                u = sqlalchemy.update(ss[table])
                                u = u.values({
                                'disabled': False,
                                })
                                b = f"{tbl[list(tbl.keys())[j]][0]} = {int(me)}"
                                u = u.where(sqlalchemy.text(b))
                                try:
                                    with conn.session as sess:
                                        sess.execute(u)
                                        sess.commit()
                                        st.success(f"Inventário: {sucesso}")

                                except Exception as e:
                                    ss['err']['enabler'].append(f"Enabler error: {e}")
                                    st.warning(ss['err']['enabler'][len(ss['err']['enabler'])-1])
                            st.rerun()

                if enableDf == list(dfOptions.keys())[j]:
                    df = ss[dfOptions[enableDf]]
                    table = list(tbl.keys())[j]
                    idx = tbl[list(tbl.keys())[j]][0]
                    name = tbl[list(tbl.keys())[j]][1]
                    detail = tbl[list(tbl.keys())[j]][2]
                    enabler(df, table, idx, name, detail)

        fragment()
