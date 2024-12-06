### PRINCIPAIS IMPORTS, SEMPRE ATUALIZAR QUANDO REMOVER/ADICIONAR ALGUMA FUNÇÃO!
import streamlit as st
import pandas as pd
from streamlit import session_state as ss
import datetime
import random
import copy
import sqlalchemy
from err import errStorage

st.set_page_config(
    page_title='PDV - Admin',
    page_icon='📒',
    layout='wide'
)

### PRIMEIRA FUNÇÃO REAL É A CONEXÃO COM O BANCO DE DADOS
conn = st.connection("postgresql", type="sql")

### DEFINIÇÃO DE VARIÁVIES
today = datetime.datetime.today() # DATA DE HOJE PARA FUNÇÕES COM DATA

### GERAÇÃO DE CHAVES ALEATÓRIAS CONSITENTES PARA OS WIDGETS DO STREAMLIT
random.seed(24)
keys = []
for i in range(100):
    keys.append(random.random())

### COLUNAS PARA OS DF TEMPORÁRIOS 
dctVars = {
    'Email do Fornecedor': 'email',
    'Telefone': 'phonenum',
    'Endereço (Rua e Número)': 'address', 
    'Endereço (CEP)': 'zipcode', 
    'Endereço (Bairro)': 'district', 
    'Endereço (Complemento)': 'addressaddinfo', 
    'Data de Cadastro': 'admissiondate', 
    'Tipo chave pix' : 'pixtype',
    'Pix do Fornecedor': 'pixkey',
    'Nome do Fornecedor':'vendname', 
           }

variables = []
for k in dctVars.keys():
    variables.append(dctVars[k])
    if dctVars[k] not in ss:
        ss[dctVars[k]] = str('')

target = [str(':')+str(x) for x in variables]

ss['dfVendor'] = pd.DataFrame(columns=variables, index=[0])
ss['dfVendor_Ed'] = pd.DataFrame(columns=variables, index=[0])

vendid = int()
email = str()
phonenum = str()
address = str()
zipcode = str()
district = str()
addressaddinfo = str()
admissiondate = str()
pixtype = str()
pixkey = str()
vendname = str()

### DECLARAÇÃO DE FUNÇÕES PRÓPRIAS
def addVendor():
    try:
        with conn.session as sess:
            sess.execute(sqlalchemy.sql.text(f"INSERT INTO vendtable ({', '.join(variables)}) VALUES ({', '.join(target)});"), {
                'email': ss['email'],
                'phonenum': ss['phonenum'],
                'address': ss['address'],
				'zipcode': ss['zipcode'],
				'district': ss['district'],
                'addressaddinfo': ss['addressaddinfo'],
                'pixtype': ss['pixtype'],
                'pixkey': ss['pixkey'],
                'vendname': ss['vendname'],
                'admissiondate': ss['admissiondate']
            })
            sess.commit()
            st.success(f"Fornecedor adicionado com sucesso")

    except Exception as e:
        ss['err']['addVendor'].append(f"Add error: {e}")
        st.warning(ss['err']['addVendor'][len(ss['err']['addVendor'])-1])

def editVendor(u):
    try:
        with conn.session as sess:
            sess.execute(u)
            sess.commit()
            st.success(f"Fornecedor atualizado com sucesso")

    except Exception as e:
        ss['err']['editVendor'].append(f"Add error: {e}")
        st.warning(ss['err']['editVendor'][len(ss['err']['editVendor'])-1])

### RODANDO FUNÇÕES INICIAIS (GERALMENTE DE LOAD)
import loader
loader.loadVendor()
print(ss['dfVendor']['admissiondate'][0])

meta = sqlalchemy.MetaData()
meta.reflect(bind=conn.engine)
ss['vendtable'] = sqlalchemy.Table('vendtable', meta)

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
            tabPreview, tabAdd, tabEdit, = st.tabs(['Visualizar Fornecedores', 'Adicionar Fornecedor', 'Editar Fornecedor'])

            ### PRIMERA TABVIEW
            with tabPreview:
                ss['preview'] = copy.deepcopy(ss['dfVendor'].copy(deep=True))
                ss['preview'] = ss['preview'][ss['preview']['vendid'] != 1]
                ss['preview'].reset_index(inplace=True, drop=True)
                ss['preview'] = st.data_editor(
                        ss['preview'],
                        num_rows='fixed',
                        use_container_width=True,
                        column_config={
                        'disabled': st.column_config.CheckboxColumn('Off?', disabled=False),
                        'vendname': st.column_config.Column('Nome',disabled=True),
                        'pixkey': st.column_config.Column('Chave PIX', disabled=True),
                        'email': st.column_config.Column('E-mail', disabled=True),
                        'phonenum': st.column_config.Column('Telefone', disabled=True),
                        'address': st.column_config.Column('Endereço', disabled=True),
                        'addressaddinfo': st.column_config.Column('Complemento', disabled=True),
                        'district': st.column_config.Column('Bairro', disabled=True),
                        'zipcode': st.column_config.Column('CEP', disabled=True),
                        'admissiondate': st.column_config.Column('Data Cadastrada', disabled=True),
                        },
                        hide_index=True,
                        key=keys[int(len(keys)/2)],
                        column_order=['disabled','vendname', 'pixkey', 'email', 'phonenum', 'address', 'addressaddinfo', 'zipcode', 'district', 'admissiondate'])

                with st.popover('Desativar FORNECEDORES selecionados?'):
                    confirm = st.button('Sim!')
                    st.write('CANCELE clicando fora dessa caixa')
                    ss['disable_me'] = list()
                    if confirm:
                        for a in range(len(ss['preview']['disabled'])):
                            if ss['preview']['disabled'][a] == 1:
                                ss['disable_me'].append(ss['preview']['vendid'][a])
                        if confirm:
                            for me in ss['disable_me']:
                                u = sqlalchemy.update(ss['vendtable'])
                                u = u.values({
                                'disabled': True,
                                })
                                u = u.where(ss['vendtable'].c.vendid == int(me))
                                editVendor(u)
                                st.rerun()

            ### PRIMERA TABVIEW
            with tabAdd:
                st.markdown('## Cadastrar Fornecedor')

                # with st.expander('Selecionar Arquivo para Atualizar os Fornecedores'):
                #     upld_estq = st.file_uploader('Selecionar arquivo', type=['csv', 'CSV'], key='upld_estq', accept_multiple_files=False, label_visibility='collapsed')
                #     if upld_estq:
                #         df = pd.read_csv(upld_estq)
                #         st.data_editor(df)

                #         for col in df.columns:
                #             if col not in ss:
                #                 ss[col] = df[col][0]

                with st.container():
                    with st.form(key='f_form', clear_on_submit=True):
                        col0, col1, = st.columns([2,1])
                        with col0:
                            ss['vendname'] = st.text_input('Nome do Fornecedor', key=keys[0], value='Padrão')
                        with col1:
                            ss['pixkey'] = st.text_input('Pix do Fornecedor', key=keys[8], value='Padrão')

                        col2, col3, = st.columns([1,2])
                        with col2:
                            ss['phonenum'] = st.text_input('Telefone', key=keys[1], value='Padrão')
                        with col3:
                            ss['email'] = st.text_input('Email', key=keys[2], value='Padrão')

                        col4, col5, = st.columns([3,1])
                        with col4:
                            ss['address'] = st.text_input('Endereço (Rua e Número)', key=keys[3], value='Padrão')
                        with col5:
                            ss['district'] = st.text_input('Endereço (Bairro)', key=keys[9], value='Padrão')

                        col6, col7, col8 = st.columns([3, 1, 1])
                        with col6: 
                            ss['addressaddinfo'] = st.text_input('Endereço (Complemento)', key=keys[4], value='Padrão')
                        with col7:
                            ss['zipcode'] = st.text_input('Endereço (CEP)', key=keys[10], value='Padrão')
                        with col8:
                            ss['admissiondate'] = st.date_input('Data de Cadastro', key=keys[6], value=today, format='DD/MM/YYYY')           

                        submit = st.form_submit_button('Adicionar Fornecedor')
                        if submit:
                            if ss['pixkey'] == ss['email']:
                                ss['pixtype'] = 'Email'
                            if ss['pixkey'] == ss['phonenum']:
                                ss['pixtype'] = 'Telefone'
                            else:
                                ss['pixtype'] = 'Outro'
                            addVendor()
                            st.rerun()

            ### SEGUNDA TABVIEW
            with tabEdit:
                st.markdown('## Editar FORNECEDOR Cadastrado')
                sort_Edit = list(ss['dfVendor']['vendname'])
                sort_Edit.sort()
                ss['edit'] = st.selectbox('Selecione um FORNECEDOR para Editar', key=keys[99], options=sort_Edit)
                if ss['edit']:
                    ss['dfVendor_Ed'] = copy.deepcopy(ss['dfVendor'].copy(deep=True))
                    ss['dfVendor_Ed'] = ss['dfVendor_Ed'][ss['dfVendor_Ed']['vendname'] == ss['edit']]
                    ss['dfVendor_Ed'] = ss['dfVendor_Ed'].dropna(how='all')
                    ss['dfVendor_Ed'].reset_index(inplace=True, drop=True)
                    
                    with st.form(key='ef_form', clear_on_submit=True):
                            col0, col1, = st.columns([2,1])
                            with col0:
                                ss['e_vendname'] = st.text_input('Nome do Fornecedor', key=keys[98], value=ss['dfVendor_Ed']['vendname'][0])
                            with col1:
                                ss['e_pixkey'] = st.text_input('Pix do Fornecedor', key=keys[97], value=ss['dfVendor_Ed']['pixkey'][0])

                            col2, col3, = st.columns([1,2])
                            with col2:
                                ss['e_phonenum'] = st.text_input('Telefone', key=keys[96], value=ss['dfVendor_Ed']['phonenum'][0])
                            with col3:
                                ss['e_email'] = st.text_input('Email', key=keys[95], value=ss['dfVendor_Ed']['email'][0])

                            col4, col5, = st.columns([3,1])
                            with col4:
                                ss['e_address'] = st.text_input('Endereço (Rua e Número)', key=keys[94], value=ss['dfVendor_Ed']['address'][0])
                            with col5:
                                ss['e_district'] = st.text_input('Endereço (Bairro)', key=keys[93], value=ss['dfVendor_Ed']['district'][0])

                            col6, col7, col8 = st.columns([3, 1, 1])
                            with col6: 
                                ss['e_addressaddinfo'] = st.text_input('Endereço (Complemento)', key=keys[92], value=ss['dfVendor_Ed']['addressaddinfo'][0])
                            with col7:
                                ss['e_zipcode'] = st.text_input('Endereço (CEP)', key=keys[91], value=ss['dfVendor_Ed']['zipcode'][0])
                            with col8:
                                ss['e_admissiondate'] = st.date_input('Data', key=keys[90], format='DD/MM/YYYY', value=datetime.datetime.strptime(str(ss['dfVendor_Ed']['admissiondate'][0]),'%d/%m/%Y'))
                                print(ss['admissiondate'])
                                print(ss['e_admissiondate'])

                            e_submit = st.form_submit_button('Editar Fornecedor')
                            if e_submit:
                                if ss['pixkey'] == ss['email']:
                                    ss['e_pixtype'] = 'Email'
                                if ss['pixkey'] == ss['phonenum']:
                                    ss['e_pixtype'] = 'Telefone'
                                else:
                                    ss['e_pixtype'] = 'Outro'

                                ss['e_vendid'] = int(ss['dfVendor_Ed'].loc[ss['dfVendor_Ed']['vendname'] == ss['edit'], 'vendid'][0])

                                u = sqlalchemy.update(ss['vendtable'])
                                u = u.values({
                                    'vendid': ss['e_vendid'],
                                    'email': ss['e_email'],
                                    'phonenum': ss['e_phonenum'],
                                    'address': ss['e_address'],
                                    'zipcode': ss['e_zipcode'],
                                    'district': ss['e_district'],
                                    'addressaddinfo': ss['e_addressaddinfo'],
                                    'pixtype': ss['e_pixtype'],
                                    'pixkey': ss['e_pixkey'],
                                    'vendname': ss['e_vendname'],
                                    'admissiondate': ss['e_admissiondate']
                                    })
                                u = u.where(ss['vendtable'].c.vendid == ss['e_vendid'])
                                editVendor(u)
                                st.rerun()
        fragment()
