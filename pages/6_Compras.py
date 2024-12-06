### PRINCIPAIS IMPORTS, SEMPRE ATUALIZAR QUANDO REMOVER/ADICIONAR ALGUMA FUNÇÃO!
import streamlit as st
import pandas as pd
from streamlit import session_state as ss
import datetime
import random
import copy
import sqlalchemy
from err import errStorage

### CONFIGURAÇÃO DA PÁGINA TEM QUE SER, SEMPRE, O PRIMEIRO CÓDIGO APÓS OS IMPORTS
st.set_page_config(
    page_title='PDV - Admin',
    page_icon='📒', 
    layout='wide'
)

### PRIMEIRA FUNÇÃO REAL É A CONEXÃO COM O BANCO DE DADOS
conn = st.connection("postgresql", type="sql")

### DEFINIÇÃO DE VARIÁVIES
hoje = datetime.datetime.today() # DATA DE HOJE PARA FUNÇÕES COM DATA

### GERAÇÃO DE CHAVES ALEATÓRIAS CONSITENTES PARA OS WIDGETS DO STREAMLIT
random.seed(24)
keys = []
for i in range(100):
    keys.append(random.random())

### COLUNAS PARA OS DF TEMPORÁRIOS 
dicVars = {'Código da Compra': 'purchid',
           'Fornecedor':'vendname', 
           'Valor Total': 'totalamount',
           'Forma de Pagamento': 'paymmode1',
           'Data da Compra': 'purchdate',
           }

### VARIÁVEIS RELATIVAS AS COLUNAS 
purchid = int()
totalamount = float()
vendname = str()
paymmode = str()
purchdate = str()

import loader

loader.loadParameters()

lista = list(ss['dfParameters'].columns)

paramList = list(ss['dfParameters'].columns)
paramList.remove('config_id')

stores = [ss['dfParameters'][lista[1]][0], ss['dfParameters'][lista[2]][0], ss['dfParameters'][lista[3]][0]]

# Padrão, pix, cheque, duplicata, a vista, 2x, 3x, 4x
#paymmode = [[lista[23]], ss['dfParameters'][lista[24]][0], ss['dfParameters'][lista[25]][0], ss['dfParameters'][lista[26]][0], ss['dfParameters'][lista[27]][0], ss['dfParameters'][lista[28]][0], ss['dfParameters'][lista[29]][0], ss['dfParameters'][lista[30]][0]]

paymmode = ['Padrão', 'PIX', 'Cheque', 'Duplicata', 'A vista', '2x', '3x', '4x']

### DECLARAÇÃO DE FUNÇÕES PRÓPRIAS
def addPurchase():
    try:
        with conn.session as sess:
            sess.execute(sqlalchemy.sql.text(f"INSERT INTO purchtable ({', '.join(variables)}) VALUES ({', '.join(target)});"), {
                'vendname': ss['vendname'],
                'paymmode1': ss['paymmode1'],
                'totalamount': ss['totalamount'],
                'purchdate': ss['purchdate'],
            })
            sess.commit()
            st.success(f"Compra realizada com sucesso")

    except Exception as e:
        ss['err']['addPurchase'].append(f"Add error: {e}")
        st.warning(ss['err']['addPurchase'][len(ss['err']['addPurchase'])-1])

def editPurchase(u):
    try:
        with conn.session as sess:
            sess.execute(u)
            sess.commit()

            st.success(f"Compra atualizada com sucesso")

    except Exception as e:
        ss['err']['editPurchase'].append(f"Add error: {e}")
        st.warning(ss['err']['editPurchase'][len(ss['err']['editPurchase'])-1])

### RODANDO FUNÇÕES INICIAIS (GERALMENTE DE LOAD)
loader.loadPurchase()
loader.listVendor()

meta = sqlalchemy.MetaData()
meta.reflect(bind=conn.engine)
ss['purchtable'] = sqlalchemy.Table('purchtable', meta)

ss['vendor'] = list(set(ss['get_vendor']['vendname']))

variables = list(ss['dfPurchase'].columns)
variables.remove('purchid')
variables.remove('identifier')
variables.remove('disabled')

target = [str(':')+str(x) for x in variables]

### DEFINIÇÃO DAS TABS PARA VISUALIZAÇÃO
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
            tab1, tab2, tab3, = st.tabs(['Visualizar Compras', 'Adicionar Compra', 'Editar Compra',])

            ### PRIMERA TABVIEW
            months = ['Todos']
            month = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro',11:'Novembro', 12:'Dezembro'}
            with tab1:
                filters = st.selectbox('Filtro de Relatório', options=[f'Ano = {hoje.year}', 'Fornecedor'])

                if filters == f'Ano = {hoje.year}':
                    ss['dfPurchase']['month'] = ss['dfPurchase']['purchdate'].apply(lambda x: datetime.datetime.strptime(x, '%d/%m/%Y').month)
                    
                    col0, col8 = st.columns([3,1])
                    with col0: 
                        st.markdown(f"### Ano em análise: :blue[{hoje.year}]")
                    with col8:
                        # Valor total no ano
                        total = ss['dfPurchase']['totalamount'].sum()

                        # Valor médio por compra 
                        if len(ss['dfPurchase']['totalamount']) > 0:
                            media_compra = total / len(ss['dfPurchase']['totalamount'])
                        else:
                            media_compra = 0

                        # Valor médio por dia
                        if len(ss['dfPurchase']['purchdate']) > 0:
                            media_dia_compra = total / len(set(ss['dfPurchase']['purchdate']))
                        else:
                            media_dia_compra  = 0

                        rs = 'R$'
                        # Cabeçalho do relatório
                        rprt = 'Relatório de Compras\n'
                        rprt += '-' * 40 + '\n'  # Linha divisória

                        # Soma total
                        txt1 = 'Valor total:'
                        rprt += f"{txt1:{' '}{'<'}{len(txt1)}}" + f"{rs + ' ' +str(round(total, 2)):{' '}{'>'}{40-len(txt1)}}"+'\n'

                        # Valor médio por compra
                        rprt += '-' * 40 + '\n'  # Linha divisória
                        txt2 = 'Valor médio por compra:'
                        rprt += f"{txt2:{' '}{'<'}{len(txt2)}}" + f"{rs + ' ' +str(round(media_compra, 2)):{' '}{'>'}{40-len(txt2)}}"+'\n'

                        # Valor médio por dia (dias com compras)
                        rprt += '-' * 40 + '\n'  # Linha divisória
                        txt3 = 'Valor médio por dia:'
                        rprt += f"{txt3:{' '}{'<'}{len(txt3)}}" + f"{rs + ' ' +str(round(media_dia_compra, 2)):{' '}{'>'}{40-len(txt3)}}"+'\n'

                        # Compras discriminadas por mês
                        rprt += '-' * 40 + '\n'  # Linha divisória
                        rprt += 'Compras discriminadas por mês:\n'
                        rprt += '-' * 40 + '\n'  # Linha divisória

                        for m in month.keys():
                            months.append(month[m])
                            valor_mes = ss['dfPurchase'].loc[ss['dfPurchase']['month'] == m].totalamount.sum()
                            rprt += f"{month[m]:{' '}{'<'}{10}}" + f"{'R$':{' '}{'>'}{20}}" + f"{round(valor_mes, 2):{' '}{'>'}{10}}"+'\n'

                        rprt += '-' * 40 + '\n'  # Linha final

                        st.download_button(
                        label='Baixar Relatório de Compras',
                        data=rprt,
                        file_name=f"Relatório_{hoje.year}_{hoje.month}_{hoje.day}.txt",
                        mime='text')

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**:blue[Valor total]**")
                        st.markdown(f"### R$ {ss['dfPurchase']['totalamount'].sum():.2f}")
                    with col2:
                        st.markdown(f"**:blue[Valor médio por compra:]**")
                        st.markdown(f"### R$ {ss['dfPurchase']['totalamount'].sum()/len(ss['dfPurchase']['totalamount']):.2f}")
                    with col3:
                        st.markdown(f"**:blue[Valor médio por dia:]**")
                        st.markdown(f"### R$ {ss['dfPurchase']['totalamount'].sum()/len(set(list(ss['dfPurchase']['purchdate']))):.2f}")

                    col4, col5, col6, col7 = st.columns(4)
                    for m in month.keys():
                        if m in [1, 5, 9]:
                            with col4:
                                with st.container(border=True):
                                    st.markdown(f"**:blue[{month[m]}]**")
                                    st.metric(label='R$', value=f"{ss['dfPurchase'].loc[ss['dfPurchase']['month'] == m].totalamount.sum():.2f}", delta='')
                        if m in [2, 6, 10]:
                            with col5:
                                with st.container(border=True):
                                    st.markdown(f"**:blue[{month[m]}]**")
                                    st.metric(label='R$', value=f"{ss['dfPurchase'].loc[ss['dfPurchase']['month'] == m].totalamount.sum():.2f}", delta='')
                        if m in [3, 7, 11]:
                            with col6:
                                with st.container(border=True):
                                    st.markdown(f"**:blue[{month[m]}]**")
                                    st.metric(label='R$', value=f"{ss['dfPurchase'].loc[ss['dfPurchase']['month'] == m].totalamount.sum():.2f}", delta='')
                        if m in [4, 8, 12]:
                            with col7:
                                with st.container(border=True):
                                    st.markdown(f"**:blue[{month[m]}]**")
                                    st.metric(label='R$', value=f"{ss['dfPurchase'].loc[ss['dfPurchase']['month'] == m].totalamount.sum():.2f}", delta='')

                    st.write("---")
                    ss['meses'] = st.selectbox('Filtrar por Mês', options=months)
                    if ss['meses'] == 'Todos':
                        if len(ss['dfPurchase']) <= 0:
                            st.markdown('Não há compras para visualizar')
                        else:
                            ss['preview'] = copy.deepcopy(ss['dfPurchase'].copy(deep=True))
                            ss['preview'] = ss['preview'][ss['preview']['purchid'] != 1]
                            ss['preview'].reset_index(inplace=True, drop=True)

                            ss['preview'] = st.data_editor(
                                ss['dfPurchase'],
                                num_rows='fixed',
                                use_container_width=True,
                                column_config={
                                'disabled': st.column_config.CheckboxColumn('Off?', disabled=False),
                                'identifier': st.column_config.Column('Compra',disabled=True),
                                'vendname': st.column_config.Column('Fornecedor', disabled=True),
                                'totalamount': st.column_config.NumberColumn('Valor pago (R$)', disabled=True, format="R$ %.2f"),
                                'paymmode1': st.column_config.Column('Pagamento', disabled=True),
                                'paymmode2': st.column_config.Column('Pagamento', disabled=True),
                                'purchdate': st.column_config.Column('Data da compra', disabled=True),
                                },
                                hide_index=True,
                                key=keys[int(len(keys)/2)],
                                column_order=['disabled', 'identifier', 'vendname', 'totalamount', 'paymmode1', 'paymmode2', 'purchdate'])

                    if ss['meses'] != 'Todos':
                        m = list(month.keys())[list(month.values()).index(ss['meses'])]
                        if len(ss['dfPurchase']) <= 0:
                            st.markdown('Não há compras para visualizar')
                        else:
                            ss['preview_M'] = copy.deepcopy(ss['dfPurchase'].copy(deep=True))
                            ss['preview_M'] = ss['preview_M'][ss['dfPurchase']['month'] == m]
                            ss['preview_M'] = ss['preview_M'][ss['preview_M']['purchid'] != 1]
                            ss['preview_M'].reset_index(inplace=True, drop=True)
                            ss['preview_M'] = st.data_editor(
                                ss['preview_M'],
                                num_rows='fixed',
                                use_container_width=True,
                                column_config={
                                'disabled': st.column_config.CheckboxColumn('Off?', disabled=False),
                                'identifier': st.column_config.Column('Compra',disabled=True),
                                'vendname': st.column_config.Column('Fornecedor', disabled=True),
                                'totalamount': st.column_config.Column('Valor pago (R$)', disabled=True),
                                'paymmode1': st.column_config.Column('Pagamento', disabled=True),
                                'paymmode2': st.column_config.Column('Pagamento', disabled=True),
                                'purchdate': st.column_config.Column('Data da compra', disabled=True),
                                },
                                hide_index=True,
                                key=keys[int(len(keys)/2)],
                                column_order=['disabled', 'identifier', 'vendname', 'totalamount', 'paymmode1',  'paymmode2', 'purchdate'])

                    with st.popover('Desativar COMPRAS selecionados?'):
                            confirm = st.button('Sim!')
                            st.write('CANCELE clicando fora dessa caixa')
                            ss['disable_me'] = list()
                            if confirm:
                                for a in range(len(ss['preview']['disabled'])):
                                    if ss['preview']['disabled'][a] == 1:
                                        ss['disable_me'].append(ss['preview']['purchid'][a])
                                if confirm:
                                    for me in ss['disable_me']:
                                        u = sqlalchemy.update(ss['purchtable'])
                                        u = u.values({
                                        'disabled': True,
                                        })
                                        u = u.where(ss['purchtable'].c.purchid == int(me))
                                        editPurchase(u)
                                        st.rerun()
                
                if filters == 'Fornecedor':
                    sort_Edit = list(ss['vendor'])
                    sort_Edit.sort()
                    ss['fornecedores'] = st.selectbox('Selecione um FORNECEDOR para Visualizar', key=keys[90], options=sort_Edit)
                    if ss['fornecedores']:
                        ss['dfPurchase_F'] = copy.deepcopy(ss['dfPurchase'].copy(deep=True))
                        ss['dfPurchase_F']['month'] = ss['dfPurchase']['purchdate'].apply(lambda x: datetime.datetime.strptime(x, '%d/%m/%Y').month)
                        ss['dfPurchase_F'] = ss['dfPurchase_F'][ss['dfPurchase']['vendname'] == ss['fornecedores']]
                        ss['dfPurchase_F'] = ss['dfPurchase_F'].dropna(how='all')
                        ss['dfPurchase_F'].reset_index(inplace=True, drop=True)
                    
                    if len(ss['dfPurchase_F']) <= 0:
                        st.markdown('Não há vendas para visualizar')
                    else:    
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**:blue[Valor total]**")
                            st.markdown(f"### R$ {ss['dfPurchase_F']['totalamount'].sum():.2f}")
                        with col2:
                            st.markdown(f"**:blue[Valor médio por compra:]**")
                            st.markdown(f"### R$ {ss['dfPurchase_F']['totalamount'].sum()/len(ss['dfPurchase_F']['totalamount']):.2f}")
                        with col3:
                            st.markdown(f"**:blue[Valor médio por dia:]**")
                            st.markdown(f"### R$ {ss['dfPurchase_F']['totalamount'].sum()/len(set(list(ss['dfPurchase_F']['purchdate']))):.2f}")
                        
                        col4, col5, col6, col7 = st.columns(4)
                        for m in month.keys():
                            if m in [1, 5, 9]:
                                with col4:
                                    with st.container(border=True):
                                        st.markdown(f"**:blue[{month[m]}]**")
                                        st.metric(label='R$', value=f"{ss['dfPurchase_F'].loc[ss['dfPurchase_F']['month'] == m].totalamount.sum():.2f}", delta='')
                            if m in [2, 6, 10]:
                                with col5:
                                    with st.container(border=True):
                                        st.markdown(f"**:blue[{month[m]}]**")
                                        st.metric(label='R$', value=f"{ss['dfPurchase_F'].loc[ss['dfPurchase_F']['month'] == m].totalamount.sum():.2f}", delta='')
                            if m in [3, 7, 11]:
                                with col6:
                                    with st.container(border=True):
                                        st.markdown(f"**:blue[{month[m]}]**")
                                        st.metric(label='R$', value=f"{ss['dfPurchase_F'].loc[ss['dfPurchase_F']['month'] == m].totalamount.sum():.2f}", delta='')
                            if m in [4, 8, 12]:
                                with col7:
                                    with st.container(border=True):
                                        st.markdown(f"**:blue[{month[m]}]**")
                                        st.metric(label='R$', value=f"{ss['dfPurchase_F'].loc[ss['dfPurchase_F']['month'] == m].totalamount.sum():.2f}", delta='')

            ### SEGUNDA TABVIEW
            with tab2:
                st.markdown('## Compras')
                with st.container():
                    with st.form(key='c_form', clear_on_submit=True):
                        col0, col1= st.columns([2,1])
                        with col0:
                            sort_Edit = list(ss['vendor'])
                            sort_Edit.sort()
                            ss['vendname'] = st.selectbox('Selecione o Fornecedor', key=keys[0], options=sort_Edit)
                            if ss['vendname'] not in ss['vendor']:
                                st.warning("Este fornecedor está desativado")
                        with col1:
                            ss['paymmode1'] = st.selectbox('Pagamento', key=keys[1], options=paymmode)
                        col3, col4, col5 = st.columns([2,2, 1])
                        with col3:
                            ss['totalamount'] = st.number_input('Valor (R$)', key=keys[2], step=float(0.5), min_value=float(0.01))
                        with col4:
                            ss['purchdate'] = st.date_input('Data', key=keys[4], value=hoje, format='DD/MM/YYYY')

                        submit = st.form_submit_button('Adicionar Compra')
                        if submit:
                            addPurchase()
                            st.rerun()

            ### TERCEIRA TABVIEW
            with tab3:
                if len(ss['dfPurchase']) <= 0:
                    st.markdown('Não há compra para editar')
                else:
                    st.markdown('## Editar COMPRA Cadastrada')
                    sort_Purch = list(ss['dfPurchase']['identifier'])
                    sort_Purch.sort()
                    ss['edit'] = st.selectbox('Selecione uma COMPRA para Editar', key=keys[99], options=sort_Purch)
                    if ss['edit']:
                        ss['dfPurchase_Ed'] = copy.deepcopy(ss['dfPurchase'].copy(deep=True))
                        ss['dfPurchase_Ed'] = ss['dfPurchase_Ed'][ss['dfPurchase']['identifier'] == ss['edit']]
                        ss['dfPurchase_Ed'] = ss['dfPurchase_Ed'].dropna(how='all')
                        ss['dfPurchase_Ed'].reset_index(inplace=True, drop=True)

                        with st.form(key='ec_form', clear_on_submit=True):
                            col0,  col1= st.columns([2,1])
                            with col0:
                                if ss['dfPurchase_Ed']['vendname'][0] not in ss['vendor']:
                                    ss['vendname'] = st.selectbox('Selecione o Fornecedor', key=keys[98], options=ss['vendor'], index=ss['vendor'].index(ss['vendor'][7]))
                                else:
                                    ss['vendname'] = st.selectbox('Selecione o Fornecedor', key=keys[98], options=ss['vendor'], index=ss['vendor'].index(ss['dfPurchase_Ed']['vendname'][0]))

                            with col1:
                                ss['e_paymmode1'] = st.selectbox('Pagamento', key=keys[97], options=paymmode, index=paymmode.index(ss['dfPurchase_Ed']['paymmode1'][0]))
                            
                            col3, col4, col5 = st.columns([2,2, 1])
                            with col3:
                                ss['e_totalamount'] = st.number_input('Valor (R$)', key=keys[96], step=float(0.5), min_value=float(0.01), value=float(ss['dfPurchase_Ed']['totalamount'][0]))
                            with col4:
                                ss['e_purchdate'] = st.date_input('Data', key=keys[95], format='DD/MM/YYYY', value=datetime.datetime.strptime(str(ss['dfPurchase_Ed']['purchdate'][0]),'%d/%m/%Y'))
                            
                            ss['e_purchid'] = int(str(ss['edit']).split('¨')[1])

                            e_submit = st.form_submit_button('Editar Compra')
                            if e_submit:
                                u = sqlalchemy.update(ss['purchtable'])
                                u = u.values({
                                    'purchid': ss['e_purchid'],
                                    'vendname': ss['vendname'],
                                    'paymmode1': ss['e_paymmode1'],
                                    'totalamount': ss['e_totalamount'],
                                    'purchdate': ss['e_purchdate'],
                                    })
                                u = u.where(ss['purchtable'].c.purchid == ss['e_purchid'])
                                editPurchase(u)
                                st.rerun()
        fragment()    

