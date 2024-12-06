### PRINCIPAIS IMPORTS, SEMPRE ATUALIZAR QUANDO REMOVER/ADICIONAR ALGUMA FUNÇÃO!
import streamlit as st
import pandas as pd
from streamlit import session_state as ss
import datetime
import random
import copy
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
conn = st.connection("postgresql", type="sql")

### DEFINIÇÃO DE VARIÁVIES
hoje = datetime.datetime.today() # DATA DE HOJE PARA FUNÇÕES COM DATA

### GERAÇÃO DE CHAVES ALEATÓRIAS CONSITENTES PARA OS WIDGETS DO STREAMLIT
random.seed(24)
keys = []
for i in range(110):
    keys.append(random.random())

### COLUNAS PARA OS DF TEMPORÁRIOS 
dicVars = {'Venda': 'salesid',
           'Vendedor':'sellername', 
           'QR Code':'qrcode',
           'Nome do Item':'itemname',
           'Nome da Loja':'storename',
           'Quantidade':'quantity',
           'Pagamento1':'payment1',
           'Pagamento2':'payment2',
           'Codigo Venda':'salescode',
           'Valor todal da Venda':'settledamount',
           'Valor Total dos Itens': 'totalamount',
           'Data da Venda': 'salesdate',
           'Desabilitado':'Disabled'
           }

### VARIÁVEIS RELATIVAS AS COLUNAS 
salesid = int()
sellername = str()
qrcode = str()
itemname = str()
storename = str()
quantity = int()
payment1 = str()
payment2 = str()
settledamount = float()
salescode = str()
salesdate = str()
disabled = bool()
identifier = str()

dbUrl = st.secrets['vars']['database_url']
engine = create_engine(dbUrl)
meta = MetaData()
meta.reflect(bind=engine)
ss['inventtable'] = Table('inventtable', meta, autoload_with=engine)
ss['salestable'] = Table('salestable', meta, autoload_with=engine)

import loader
loader.loadParameters()

lista = list(ss['dfParameters'].columns)

paramList = list(ss['dfParameters'].columns)
paramList.remove('config_id')

stores = [ss['dfParameters']['storename1'][0], ss['dfParameters']['storename2'][0], ss['dfParameters']['storename3'][0]]

paymmode = ['Dinheiro', 'PIX', 'Débito', 'Crédito a vista', 'Crédito2x','Crédito3x','Crédito4x','Crédito5x','Crédito6x','Crédito7x','Crédito8x','Crédito9x','Crédito10x']
paymmode2 = ['Padrão', 'Dinheiro', 'Débito', 'Crédito a vista', 'PIX']

def settling(arg1, arg2):
    ss['settle1'] = 0.0
    ss['settle2'] = 0.0
    ss['settledamount'] = 0.0

    if arg2 == 'Padrão':
        ss['settle2'] = 0
        match arg1:
            case 'Dinheiro':
                ss['settle1'] = (float(ss['totalamount']))

            case 'PIX':
                ss['settle1'] = (float(ss['totalamount']))

            case 'Débito':
                ss['settle1'] = (float(ss['totalamount']) * (1 - ss['dfParameters']['taxcredvista'][0]))

            case 'Crédito a vista':
                ss['settle1'] = float(ss['totalamount'] * (1 - ss['dfParameters']['taxcredvista'][0]))

            case 'Crédito2x':
                ss['settle1'] = float(ss['totalamount'] * (1 - ss['dfParameters']['taxcred2x'][0]))

            case 'Crédito3x':
                ss['settle1'] = float(ss['totalamount'] * (1 - ss['dfParameters']['taxcred3x'][0]))

            case 'Crédito4x':
                ss['settle1'] = float(ss['totalamount'] * (1 - ss['dfParameters']['taxcred4x'][0]))

            case 'Crédito5x':
                ss['settle1'] = float(ss['totalamount'] * (1 - ss['dfParameters']['taxcred5x'][0]))

            case 'Crédito6x':
                ss['settle1'] = float(ss['totalamount'] * (1 - ss['dfParameters']['taxcred6x'][0]))

            case 'Crédito7x':
                ss['settle1'] = float(ss['totalamount'] * (1 - ss['dfParameters']['taxcred7x'][0]))

            case 'Crédito8x':
                ss['settle1'] = float(ss['totalamount'] * (1 - ss['dfParameters']['taxcred8x'][0]))

            case 'Crédito9x':
                ss['settle1'] = float(ss['totalamount'] * (1 - ss['dfParameters']['taxcred9x'][0]))

            case 'Crédito10x':
                ss['settle1'] = float(ss['totalamount'] * (1 - ss['dfParameters']['taxcred10x'][0]))

            case _:
                return "Modo de pagamento inválido" 

    if arg2 != 'Padrão':
        match arg2:
            case 'Dinheiro':
                ss['settle2'] = (float(ss['amount2']))

            case 'PIX':
                ss['settle2'] = (float(ss['amount2']))

            case 'Débito':
                ss['settle2'] = (float(ss['amount2']) * (1 - ss['dfParameters']['taxcredvista'][0]))

            case 'Crédito a vista':
                ss['settle2'] = (float(ss['amount2']) * (1 - ss['dfParameters']['taxcredvista'][0]))

        match arg1:
            case 'Dinheiro':
                ss['settle1'] = (float(ss['amount1']))

            case 'PIX':
                ss['settle1'] = (float(ss['amount1']))

            case 'Débito':
                ss['settle1'] = (float(ss['amount1']) * (1 - ss['dfParameters']['taxcredvista'][0]))

            case 'Crédito a vista':
                ss['settle1'] = (float(ss['amount1']) * (1 - ss['dfParameters']['taxcredvista'][0]))

            case 'Crédito2x':
                ss['settle1'] = float(ss['amount1'] * (1 - ss['dfParameters']['taxcred2x'][0]))

            case 'Crédito3x':
                ss['settle1'] = float(ss['amount1'] * (1 - ss['dfParameters']['taxcred3x'][0]))

            case 'Crédito4x':
                ss['settle1'] = float(ss['amount1'] * (1 - ss['dfParameters']['taxcred4x'][0]))

            case 'Crédito5x':
                ss['settle1'] = float(ss['amount1'] * (1 - ss['dfParameters']['taxcred5x'][0]))

            case 'Crédito6x':
                ss['settle1'] = float(ss['amount1'] * (1 - ss['dfParameters']['taxcred6x'][0]))

            case 'Crédito7x':
                ss['settle1'] = float(ss['amount1'] * (1 - ss['dfParameters']['taxcred7x'][0]))

            case 'Crédito8x':
                ss['settle1'] = float(ss['amount1'] * (1 - ss['dfParameters']['taxcred8x'][0]))

            case 'Crédito9x':
                ss['settle1'] = float(ss['amount1'] * (1 - ss['dfParameters']['taxcred9x'][0]))

            case 'Crédito10x':
                ss['settle1'] = float(ss['amount1'] * (1 - ss['dfParameters']['taxcred10x'][0]))

            case _:
                return "Modo de pagamento inválido"

    if(ss['settle1'] + ss['settle2']) > ss['totalamount']:
        st.warning("A soma dos valores de pagamento não devem ser maior que o total dos itens")

    ss['settledamount'] = ss['settle1'] + ss['settle2']
    print(ss['settledamount'], ss['settle1'], ss['settle2'])

### DECLARAÇÃO DE FUNÇÕES PRÓPRIAS
def addSales():
    try:
        with conn.session as sess:
            sess.execute(sqlalchemy.sql.text(f"INSERT INTO salestable ({', '.join(variables)}) VALUES ({', '.join(target)});"), {
                'sellername': ss['sellername'],
                'qrcode': ss['qrcode'],
                'itemname' : ss['itemname'],
                'storename': ss['storename'],
                'quantity': ss['quantity'],
                'payment1': ss['payment1'],
                'payment2': ss['payment2'],
                'settledamount': ss['settledamount'],
                'totalamount' : ss['totalamount'],
                'salescode': ss['salescode'],
                'salesdate': ss['salesdate'],
            })
            sess.commit()
            st.success(f"Venda realizada com sucesso")

    except Exception as e:
        ss['err']['addSales'].append(f"Add error: {e}")
        st.warning(ss['err']['addSales'][len(ss['err']['addSales'])-1])

def editSales(u):
    try:
        with conn.session as sess:
            sess.execute(u)
            sess.commit()

            st.success(f"Venda atualizada com sucesso")

    except Exception as e:
        ss['err']['editSales'].append(f"Add error: {e}")
        st.warning(ss['err']['editSales'][len(ss['err']['editSales'])-1])

def updQty(main_df, store_df, add):
    Session = sessionmaker(bind=engine)
    try:
        with engine.connect() as connection:
            session = Session(bind=connection)
            transaction = connection.begin()  # Inicia a transação
            
            # Função auxiliar para atualizar o inventário
            for _, row in store_df.iterrows():
                if row['storename'] == stores[0]:
                    store_column = 'store1qty'
                if row['storename'] == stores[1]:
                    store_column = 'store2qty'
                current_qty = int(main_df.loc[main_df['qrcode'] == row['qrcode'], store_column].iloc[0])
                new_qty = current_qty + add * (row['quantity'])
                u = update(ss['inventtable']).values({store_column: new_qty}).where(ss['inventtable'].c.qrcode == row['qrcode'])
                session.execute(u)

            # Commit todas as atualizações
            transaction.commit()  # Confirma a transação
    except Exception as e:
        st.write(f"Erro ao conectar ou processar o banco de dados: {e}", store_df)
        print(f"Erro ao conectar ou processar o banco de dados: {e}")
        transaction.rollback()  # Desfaz a transação em caso de erro
    finally:
        session.close()
        
### RODANDO FUNÇÕES INICIAIS (GERALMENTE DE LOAD)
loader.loadSales()
loader.listSeller()
loader.loadInventory()

ss['get_seller']['name_id'] = ss['get_seller'].apply(lambda row: f"{str(row['sellername'])+str('¨')+str(row['sellerid'])}", axis=1)
ss['seller'] = list(ss['get_seller']['sellername'])

variables = list(ss['dfSales'].columns)
variables.remove('salesid')
variables.remove('salescode')
variables.remove('disabled')
variables.remove('identifier')

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
            tab1, tab2, tab3, = st.tabs(['Relatórios', 'Adicionar Venda', 'Editar Venda'])

            ### PRIMERA TABVIEW
            with tab1:
                month = {1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril', 5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro',11:'Novembro', 12:'Dezembro'}
                tabV, tabC, = st.tabs(['Vendas', 'Comissões',])
                with tabV:
                    col_f0, col_f1, col_f2, col_f3 = st.columns(4)
                    with st.form(key='vendasR', border=False):
                        with col_f0:
                            prices = st.toggle(':blue[Total]', key='prices')

                        with col_f1:
                            loja1 = st.toggle(f":blue[{stores[0]}]", key='loja1')

                        with col_f2:
                            loja2 = st.toggle(f":blue[{stores[1]}]", key='loja2')

                        colFrom, colTo = st.columns(2)
                        with colFrom:
                            ss['dataDeV'] = st.date_input(label=f"Data :blue[inicial]", value=None, format='DD/MM/YYYY', key='rd10')

                        with colTo:
                            ss['dataParaV'] = st.date_input(label=f"Data :blue[final]", value=None, format='DD/MM/YYYY', key='rd20')
                        if (loja1 == True and loja2 == True) or (loja1 == False and loja2 == False):
                            ss['dfStore'] = copy.deepcopy(ss['dfSales'].copy(deep=True))
                            
                        elif loja1 == True and loja2 == False:
                            ss['dfStore'] = ss['dfStore'][ss['dfStore']['storename'] == stores[0]]
                            ss['dfStore'].reset_index(inplace=True, drop=True)

                        elif loja2 == True and loja1 == False:
                            ss['dfStore'] = ss['dfStore'][ss['dfStore']['storename'] == stores[1]]
                            ss['dfStore'].reset_index(inplace=True, drop=True)

                        filtro = st.form_submit_button('Vendas')
                        if filtro:
                            ss['dfStore_DD'] = copy.deepcopy(ss['dfStore'].copy(deep=True))
                            ss['dfStore_DD']['salesdate'] = pd.to_datetime(ss['dfStore_DD']['salesdate'], dayfirst=True, format='%d/%m/%Y', errors='coerce').dt.date
                            ss['dfStore_DD']['month'] = pd.DatetimeIndex(ss['dfStore_DD']['salesdate']).month
                            ss['dfStore_DD'].reset_index(inplace=True, drop=True)

                            if ss['dataDeV'] == None or ss['dataParaV'] == None:
                                    ss['dataDeV'] = min(ss['dfStore_DD']['salesdate'])
                                    ss['dataParaV'] = max(ss['dfStore_DD']['salesdate'])

                            if ss['dataDeV'] != None or ss['dataParaV'] != None:
                                ss['dfStore_DD'] = ss['dfStore_DD'].loc[(ss['dfStore_DD']['salesdate'] >= pd.to_datetime(ss['dataDeV']).date()) & (ss['dfStore_DD']['salesdate'] <= pd.to_datetime(ss['dataParaV']).date())]
                                ss['dfStore_DD'].reset_index(inplace=True, drop=True)

                            if prices:
                                ss['p'] = 'totalamount'
                            else:
                                ss['p'] = 'settledamount'

                            col0, col8 = st.columns([3,1])
                            with col8:
                                # Valor total no ano
                                total = ss['dfStore_DD'][ss['p']].sum()

                                # Valor médio por venda 
                                if len(ss['dfStore_DD'][ss['p']]) > 0:
                                    media_venda = total / len(ss['dfStore_DD'][ss['p']])
                                else:
                                    media_venda = 0

                                # Valor médio por dia
                                if len(ss['dfStore_DD']['salesdate']) > 0:
                                    media_dia_venda = total / len(set(ss['dfStore_DD']['salesdate']))
                                else:
                                    media_dia_venda  = 0
                                rs = 'R$'
                                # Cabeçalho do relatório
                                ss['rprt'] = 'Relatório de Vendas\n'
                                ss['rprt'] += '-' * 40 + '\n'  # Linha divisória

                                # Soma total
                                txt1 = 'Valor total:'
                                ss['rprt'] += f"{txt1:{' '}{'<'}{len(txt1)}}" + f"{rs + ' ' +str(round(total, 2)):{' '}{'>'}{40-len(txt1)}}"+'\n'

                                # Valor médio por venda
                                ss['rprt'] += '-' * 40 + '\n'  # Linha divisória
                                txt2 = 'Valor médio por venda:'
                                ss['rprt'] += f"{txt2:{' '}{'<'}{len(txt2)}}" + f"{rs + ' ' +str(round(media_venda, 2)):{' '}{'>'}{40-len(txt2)}}"+'\n'

                                # Valor médio por dia (dias com vendas)
                                ss['rprt'] += '-' * 40 + '\n'  # Linha divisória
                                txt3 = 'Valor médio por dia:'
                                ss['rprt'] += f"{txt3:{' '}{'<'}{len(txt3)}}" + f"{rs + ' ' +str(round(media_dia_venda, 2)):{' '}{'>'}{40-len(txt3)}}"+'\n'

                                # Vendas discriminadas por mês
                                ss['rprt'] += '-' * 40 + '\n'  # Linha divisória
                                ss['rprt'] += 'Vendas discriminadas por mês:\n'
                                ss['rprt'] += '-' * 40 + '\n'  # Linha divisória

                                for m in month.keys():
                                    valor_mes = ss['dfStore_DD'].loc[ss['dfStore_DD']['month'] == m][ss['p']].sum()
                                    ss['rprt'] += f"{month[m]:{' '}{'<'}{10}}" + f"{'R$':{' '}{'>'}{20}}" + f"{round(valor_mes, 2):{' '}{'>'}{10}}"+'\n'

                                ss['rprt'] += '-' * 40 + '\n'  # Linha final

                            with st.container(border=True):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.markdown(f"**:blue[Valor total]**")
                                    st.markdown(f"### R$ {ss['dfStore_DD'][ss['p']].sum():.2f}")
                                with col2:
                                    st.markdown(f"**:blue[Valor médio por Venda:]**")
                                    if len(ss['dfStore_DD'][ss['p']]) > 0:
                                        st.markdown(f"### R$ {ss['dfStore_DD'][ss['p']].sum()/len(ss['dfStore_DD'][ss['p']]):.2f}")
                                    else:  
                                        st.markdown(f"### R$ 0")
                                with col3:
                                    st.markdown(f"**:blue[Valor médio por dia:]**")
                                    if len(set(list(ss['dfStore_DD']['salesdate']))) > 0:
                                        st.markdown(f"### R$ {ss['dfStore_DD'][ss['p']].sum()/len(set(list(ss['dfStore_DD']['salesdate']))):.2f}")
                                    else:  
                                        st.markdown(f"### R$ 0")

                            col4, col5, col6, col7 = st.columns(4)
                            for m in month.keys():
                                if m in [1, 5, 9]:
                                    with col4:
                                        with st.container(border=True):
                                            st.markdown(f"**:blue[{month[m]}]**")
                                            st.metric(label='R$', value=f"{ss['dfStore_DD'].loc[ss['dfStore_DD']['month'] == m][ss['p']].sum():.2f}", delta='')
                                if m in [2, 6, 10]:
                                    with col5:
                                        with st.container(border=True):
                                            st.markdown(f"**:blue[{month[m]}]**")
                                            st.metric(label='R$', value=f"{ss['dfStore_DD'].loc[ss['dfStore_DD']['month'] == m][ss['p']].sum():.2f}", delta='')
                                if m in [3, 7, 11]:
                                    with col6:
                                        with st.container(border=True):
                                            st.markdown(f"**:blue[{month[m]}]**")
                                            st.metric(label='R$', value=f"{ss['dfStore_DD'].loc[ss['dfStore_DD']['month'] == m][ss['p']].sum():.2f}", delta='')
                                if m in [4, 8, 12]:
                                    with col7:
                                        with st.container(border=True):
                                            st.markdown(f"**:blue[{month[m]}]**")
                                            st.metric(label='R$', value=f"{ss['dfStore_DD'].loc[ss['dfStore_DD']['month'] == m][ss['p']].sum():.2f}", delta='')

                            st.write("---")
                            ss['dfStore_DD']['payM'] = str()
                            for p in range(len(ss['dfStore_DD'])):
                                if (ss['dfStore_DD']['payment2'][p] == 'Padrão') or (ss['dfStore_DD']['payment2'][p] == None) or (ss['dfStore_DD']['payment2'][p] == ''):
                                    ss['dfStore_DD'].loc[p, 'payM'] = str(ss['dfStore_DD']['payment1'][p])
                                    
                                else:
                                    ss['dfStore_DD'].loc[p, 'payM'] = str(ss['dfStore_DD']['payment1'][p])+'¨'+ss['dfStore_DD']['payment2'][p]

                            ss['preview'] = copy.deepcopy(ss['dfStore_DD'].copy(deep=True))
                            ss['preview'].reset_index(inplace=True, drop=True)
                            ss['preview'] = st.data_editor(
                                ss['preview'],
                                num_rows='fixed',
                                use_container_width=True,
                                column_config={
                                'identifier': st.column_config.Column('Venda',disabled=True),
                                'qrcode': st.column_config.Column('QRCode', disabled=True),
                                'itemname': st.column_config.Column('Produto', disabled=True),
                                'storename': st.column_config.Column('Loja', disabled=True),
                                ss['p']: st.column_config.NumberColumn('Pago', disabled=True, format="R$ %.2f"),
                                'payM': st.column_config.Column('Pagamentos', disabled=True),
                                'salesdate': st.column_config.DateColumn('Data', disabled=True, format='DD/MM/YYYY'),
                                },
                                hide_index=True,
                                key=keys[int(len(keys)/2)],
                                column_order=['identifier', 'qrcode', 'itemname', 'storename', ss['p'], 'payM', 'salesdate'])

                if 'rprt' not in ss:
                    ss['rprt'] = ''

                with col_f3:
                    st.download_button(
                        label=f":blue[Relatório]",
                        data=ss['rprt'],
                        file_name=f"Relatório_{hoje.year}_{hoje.month}_{hoje.day}.txt",
                        mime='text')
                    
                with tabC:
                    ss['dfStore_DD'] = copy.deepcopy(ss['dfSales'].copy(deep=True))
                    if len(ss['dfStore_DD']) <= 0:
                        st.markdown('Não há vendas para visualizar')

                    else:
                        colFrom, colTo, colV, colL1, colL2 = st.columns([2,2,3,2,2])
                        with st.form(key='reporting', clear_on_submit=False, border=False):
                            with colFrom:
                                ss['dataDe'] = st.date_input(label=f"Data :blue[inicial]", value=None, format='DD/MM/YYYY', key='rd1')

                            with colTo:
                                ss['dataPara'] = st.date_input(label=f"Data :blue[final]", value=None, format='DD/MM/YYYY', key='rd2')

                            with colV:
                                ss['Vendedores'] = st.selectbox(f":blue[Vendedor]", key='keys[90]', options=list(ss['seller']), index=None, placeholder='Selecione um Vendedor')

                            with colL1:
                                loja1 = st.toggle(f":blue[{stores[0]}]", key='l1')

                            with colL2:
                                loja2 = st.toggle(f":blue[{stores[1]}]", key='l2')

                            if loja1 == True and loja2 == False:
                                ss['dfStore_DD'] = ss['dfStore_DD'][ss['dfStore_DD']['storename'] == stores[0]]
                                ss['dfStore_DD'].reset_index(inplace=True, drop=True)

                            elif loja2 == True and loja1 == False:
                                ss['dfStore_DD'] = ss['dfStore_DD'][ss['dfStore_DD']['storename'] == stores[1]]
                                ss['dfStore_DD'].reset_index(inplace=True, drop=True)

                            filtrar = st.form_submit_button('Comissões', )
                            if filtrar:
                                ss['dfStoreV'] = copy.deepcopy(ss['dfStore_DD'].copy(deep=True))
                                if ss['Vendedores'] != None:
                                    ss['dfStoreV'] = copy.deepcopy(ss['dfStore_DD'].copy(deep=True))
                                    ss['dfStoreV'] = ss['dfStoreV'][ss['dfStoreV']['sellername'] == ss['Vendedores']]

                                    ss['comission'] = (ss['get_seller'].loc[ss['get_seller']['sellername'] == str(ss['Vendedores']).split('¨')[0]].comission.sum())/100

                                else:
                                    pass

                                if 'comission' not in ss:
                                    ss['comission'] = 0

                                ss['dfStoreV']['salesdate'] = pd.to_datetime(ss['dfStoreV']['salesdate'], dayfirst=True, format='%d/%m/%Y', errors='coerce').dt.date
                                ss['dfStoreV']['month'] = pd.DatetimeIndex(ss['dfStoreV']['salesdate']).month
                                ss['dfStoreV'].reset_index(inplace=True, drop=True)

                                if ss['dataDe'] == None or ss['dataPara'] == None:
                                    ss['dataDe'] = min(ss['dfStoreV']['salesdate'])
                                    ss['dataPara'] = max(ss['dfStoreV']['salesdate'])

                                elif ss['dataDe'] != None or ss['dataPara'] != None:
                                    ss['dfStoreV'] = ss['dfStoreV'].loc[(ss['dfStoreV']['salesdate'] >= pd.to_datetime(ss['dataDe']).date()) & (ss['dfStoreV']['salesdate'] <= pd.to_datetime(ss['dataPara']).date())]
                                    ss['dfStoreV'].reset_index(inplace=True, drop=True)

                                ss['dfStoreV']['month'] = pd.to_datetime(ss['dfStoreV']['salesdate'], dayfirst=True).dt.month
                                ss['dfStoreV'] = ss['dfStoreV'].dropna(how='all')
                                ss['dfStoreV'].reset_index(inplace=True, drop=True)

                                report = list(set(list(ss['dfStoreV']['sellername'])))

                                ss['dfStoreV']['comission'] = ss['dfStoreV'].apply(lambda row: f"{row['settledamount']*ss['comission']:.2f}", axis=1)
                                ss['dfStoreV']['comission'] = ss['dfStoreV']['comission'].astype('float')

                                with st.container(border=True):
                                    st.markdown(f"**:blue[COMISSÃO]**")
                                    col4, col5, col6 = st.columns(3)
                                    with col4:
                                        st.markdown(f"**:blue[Valor total]**")
                                        st.markdown(f"### R$ {(ss['dfStoreV']['settledamount'].sum())*ss['comission']:.2f}")
                                    with col5:
                                        st.markdown(f"**:blue[Valor médio por venda:]**")
                                        st.markdown(f"### R$ {(ss['dfStoreV']['settledamount'].sum()/len(ss['dfStoreV']['settledamount']))*ss['comission']:.2f}")
                                    with col6:
                                        st.markdown(f"**:blue[Valor médio por dia:]**")
                                        st.markdown(f"### R$ {(ss['dfStoreV']['settledamount'].sum()/len(set(list(ss['dfStoreV']['salesdate']))))*ss['comission']:.2f}")

                                col4, col5, col6, col7 = st.columns(4)
                                for m in month.keys():
                                    if m in [1, 5, 9]:
                                        with col4:
                                            with st.container(border=True):
                                                st.markdown(f"**:blue[{month[m]}]**")
                                                st.metric(label='R$', value=f"{ss['dfStoreV'].loc[ss['dfStoreV']['month'] == m]['settledamount'].sum()*ss['comission']:.2f}", delta='')
                                    if m in [2, 6, 10]:
                                        with col5:
                                            with st.container(border=True):
                                                st.markdown(f"**:blue[{month[m]}]**")
                                                st.metric(label='R$', value=f"{ss['dfStoreV'].loc[ss['dfStoreV']['month'] == m]['settledamount'].sum()*ss['comission']:.2f}", delta='')
                                    if m in [3, 7, 11]:
                                        with col6:
                                            with st.container(border=True):
                                                st.markdown(f"**:blue[{month[m]}]**")
                                                st.metric(label='R$', value=f"{ss['dfStoreV'].loc[ss['dfStoreV']['month'] == m]['settledamount'].sum()*ss['comission']:.2f}", delta='')
                                    if m in [4, 8, 12]:
                                        with col7:
                                            with st.container(border=True):
                                                st.markdown(f"**:blue[{month[m]}]**")
                                                st.metric(label='R$', value=f"{ss['dfStoreV'].loc[ss['dfStoreV']['month'] == m]['settledamount'].sum()*ss['comission']:.2f}", delta='')

                                for u, r in zip(report, range(len(report))):
                                    vnds = len(ss['dfStoreV'][ss['dfStoreV']['sellername'] == u])

                                    dfR = ss['dfStoreV'][ss['dfStoreV']['sellername'] == u].groupby(['salesdate']).sum(numeric_only=True)
                                    dfR.sort_values(by=['salesdate'])

                                    st.write(f":blue[{u}], {vnds} vendas = R$ {dfR['comission'].sum():.2f}")

                                    st.data_editor(
                                        dfR,
                                        num_rows='fixed',
                                        use_container_width=True,
                                        column_config={
                                        'salesdate': st.column_config.DateColumn('Data', disabled=True, format='DD/MM/YYYY'),
                                        'totalamount': st.column_config.NumberColumn('Pago', disabled=True, format="R$ %.2f"),
                                        'settledamount': st.column_config.NumberColumn('Descontado', disabled=True, format="R$ %.2f"),
                                        'comission': st.column_config.NumberColumn('Comissão', disabled=True, format="R$ %.2f"),
                                        },
                                        hide_index=True,
                                        key='rd3'+str(r),
                                        column_order=['salesdate', 'totalamount', 'settledamount', 'comission', ])

                                dfStore_V_view = st.data_editor(
                                    ss['dfStoreV'],
                                    num_rows='fixed',
                                    use_container_width=True,
                                    column_config={
                                    'identifier': st.column_config.Column('Venda',disabled=True),
                                    'qrcode': st.column_config.Column('QR Code', disabled=True),
                                    'storename': st.column_config.Column('Loja', disabled=True),
                                    'totalamount': st.column_config.NumberColumn('Pago', disabled=True, format="R$ %.2f"),
                                    'settledamount': st.column_config.NumberColumn('Desconto', disabled=True, format="R$ %.2f"),
                                    'comission': st.column_config.NumberColumn('Comissão', disabled=True, format="R$ %.2f"),
                                    'payment1': st.column_config.Column('Pagamento1', disabled=True),
                                    'payment2': st.column_config.Column('Pagamento2', disabled=True),
                                    'salesdate': st.column_config.DateColumn('Data', disabled=True, format='DD/MM/YYYY'),
                                    },
                                    hide_index=True,
                                    key='dfStoreV_ed',
                                    column_order=['identifier', 'qrcode', 'storename', 'totalamount', 'settledamount', 'comission', 'payment1','payment2', 'salesdate'])

            ### SEGUNDA TABVIEW
            with tab2:
                st.markdown('## Vendas')
                ss['dfInventory']['display'] = ss['dfInventory'].apply(
                    lambda row: f"{row['qrcode']} - {row['itemname']} - {row['itemsize']} - {row['colorid']} - {row['itemprice']}", axis=1)
                colA, colB = st.columns([2,1])
                with colA:
                    ss['identifier'] = st.selectbox('Selecione o item',key=keys[3], options=list(ss['dfInventory']['display']))
                with colB:
                    ss['sellername'] = st.selectbox('Selecione o Vendedor', key=keys[0], options=ss['seller'])

                with st.container():
                    with st.form(key='c_form', clear_on_submit=True):
                        col2a, col3a, col4a, col5a, col6a = st.columns([1,2,1,1,1])
                        if ss['sellername'] not in ss['seller']:
                            st.warning("Este Vendedor está desativado")
                        if ss['identifier']:
                            ss['qrcode'] = str(ss['identifier']).split(' - ')[0]
                            ss['itemname'] = str(ss['identifier']).split(' - ')[1]
                            ss['itemprice'] = str(ss['identifier']).split(' - ')[4]

                        with col2a:
                            ss['salesdate'] = st.date_input('Data', key=keys[1], value=hoje, format='DD/MM/YYYY')

                        with col3a:
                            ss['storename'] = st.selectbox('Selecione a Loja',key=keys[6], options=list(stores)[:2])

                        with col4a:
                            ss['salescode'] = st.text_input('Status', key=keys[5])

                        with col5a:
                            ss['quantity'] = st.number_input('Quantidade',step=int(1), min_value=int(1))

                        with col6a:
                            ss['comiss'] = st.slider('Porcentagem de Comissão', step=1, min_value=0, max_value=25, format='%f%%', key=keys[89], value=int(ss['get_seller'].loc[ss['get_seller']['sellername'] == str(ss['sellername']), 'comission'].iloc[0]))

                        colx1, colx2, colx3, colx4 = st.columns(4)
                        with colx1:
                            ss['payment1'] = st.selectbox('Pagamento1', key=keys[4], options=paymmode)

                        with colx2:
                            ss['amount1'] = st.number_input('Valor (R$)', key=keys[2], step=float(0.5), min_value=float(0.01), value=float(ss['itemprice']))

                        with colx3:
                            ss['payment2'] = st.selectbox('Pagamento2', key=keys[8], options=paymmode2)

                        with colx4:
                            ss['amount2'] = st.number_input('Valor (R$)', key=keys[7], step=float(0.5), min_value=float(0.00))

                        ## inicializando variaveis
                        ss['totalamount'] = int(ss['quantity']) * (ss['amount1'] + ss['amount2'])
                        submit = st.form_submit_button('Adicionar Venda')
                        if submit:
                            settling(ss['payment1'], ss['payment2'])
                            addSales()
                            if ss['storename'] == stores[0]:
                                store = 'store1qty'
                            elif ss['storename'] == stores[1]:
                                store = 'store2qty'
                            try:
                                with conn.session as sess:
                                    u = sqlalchemy.update(ss['inventtable'])
                                    u = u.values({store: int(ss['dfInventory'].loc[ss['dfInventory']['qrcode'] == ss['qrcode'], store].iloc[0] - ss['quantity']),})
                                    u = u.where(ss['inventtable'].c.qrcode == ss['qrcode'])
                                    sess.execute(u)
                                    sess.commit()
                            except Exception as e:
                                ss['err']['addSales'].append(f"Add error: {e}")
                                st.warning(ss['err']['addSales'][len(ss['err']['addSales'])-1])
                            #st.rerun()

            ### TERCEIRA TABVIEW
            with tab3:
                if len(ss['dfSales']) <= 0:
                    st.markdown('Não há Venda para editar')
                else:
                    st.markdown('## Editar Venda Cadastrada')
                    sort_Sale = list(ss['dfSales']['identifier'])
                    sort_Sale.sort()
                    ss['edit'] = st.selectbox('Selecione uma Venda para Editar', key=keys[99], options=sort_Sale)
                    if ss['edit']:
                        ss['dfSales_Ed'] = copy.deepcopy(ss['dfSales'].copy(deep=True))
                        ss['dfSales_Ed'] = ss['dfSales_Ed'][ss['dfSales']['identifier'] == ss['edit']]
                        ss['dfSales_Ed'] = ss['dfSales_Ed'].dropna(how='all')
                        ss['dfSales_Ed'].reset_index(inplace=True, drop=True)

                        with st.form(key='ec_form', clear_on_submit=True):
                            col0, col1, colD = st.columns([2,1,1])
                            with col0:
                                if ss['dfSales_Ed']['sellername'][0] not in ss['seller']:
                                    ss['e_sellername'] = st.selectbox('Selecione o Vendedor', key=keys[98], options=ss['seller'], index=ss['seller'].index(ss['seller'][0]))
                                else:
                                    ss['e_sellername'] = st.selectbox('Selecione o Vendedor', key=keys[98], options=ss['seller'], index=ss['seller'].index(ss['dfSales_Ed']['sellername'][0]))

                            with col1:
                                ss['e_salesdate'] = st.date_input('Data', key=keys[95], format='DD/MM/YYYY', value=datetime.datetime.strptime(str(ss['dfSales_Ed']['salesdate'][0]),'%d/%m/%Y'))

                            with colD:
                                ss['disable_me'] = st.checkbox('Desabilitar?', key=keys[94], value=False)

                            ss['e_salesid'] = int(str(ss['edit']).split('¨')[1])

                            e_submit = st.form_submit_button('Editar Venda')
                            if e_submit:
                                updQty(ss['dfInventory'], ss['dfSales_Ed'], 1)
                                u = sqlalchemy.update(ss['salestable'])
                                u = u.values({
                                    'sellername': ss['e_sellername'],
                                    'salesdate': ss['e_salesdate'],
                                    'disabled': ss['disable_me'],
                                    })
                                u = u.where(ss['salestable'].c.salesid == ss['e_salesid'])
                                editSales(u)
                                st.rerun()

        fragment()
