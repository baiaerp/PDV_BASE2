import streamlit as st
import pandas as pd
import numpy as np
from streamlit import session_state as ss
import datetime
import random
import copy
import sqlalchemy
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)
from err import errStorage

# CONFIGURAÇÃO DA PÁGINA TEM QUE SER, SEMPRE, O PRIMEIRO CÓDIGO APÓS OS IMPORTS
st.set_page_config(
    page_title='PDV - Admin',
    page_icon='📒',
    layout='wide',
) 

#PRIMEIRA FUNÇÃO REAL É A CONEXÃO COM O BANCO DE DADOS
conn = st.connection("postgresql", type="sql")

today = datetime.datetime.today()

#widget keys
random.seed(24)
keys = []
for i in range(100):
    keys.append(random.random())

#COLUNAS PARA OS DF TEMPORÁRIOS 
dctVars = {
    'Email do Vendedor': 'email',
    'Telefone': 'phonenum',
    'Endereço (Rua e Número)': 'address', 
    'Endereço (CEP)': 'zipcode', 
    'Endereço (Bairro)': 'district', 
    'Endereço (Complemento)': 'addressaddinfo', 
    'Data de Nascimento': 'birthdate', 
    'Data de Admissão': 'hiringdate', 
    'Data de Desligamento': 'dismissaldate', 
    'Tipo chave pix': 'pixtype',
    'Pix do Vendedor': 'pixkey', 
    'Porcentagem de Comissão': 'comission',
    'Nome do Vendedor':'sellername', }

variables = []
for k in dctVars.keys():
    variables.append(dctVars[k])
    if dctVars[k] not in ss:
        ss[dctVars[k]] = str('')

target = [str(':')+str(x) for x in variables]

ss['dfSeller'] = pd.DataFrame(columns=variables, index=[0])
ss['dfSeller_ed'] = pd.DataFrame(columns=variables, index=[0])

email = str()
phonenum = str()
address = str()
zipcode = str()
district = str()
addressaddinfo = str()
birthdate = str()
hiringdate = str()
dismissaldate = str()
pixtype = str()
pixkey = str()
comission= float()
sellername = str()

def addSeller():
    try:
        with conn.session as sess:
            sess.execute(sqlalchemy.sql.text(f"INSERT INTO sellertable ({', '.join(variables)}) VALUES ({', '.join(target)});"), {
                'email': ss['email'],
                'phonenum': ss['phonenum'],
                'address': ss['address'],
				'zipcode': ss['zipcode'],
				'district': ss['district'],
                'addressaddinfo': ss['addressaddinfo'],
                'birthdate': ss['birthdate'],
                'hiringdate': ss['hiringdate'],
                'dismissaldate': ss['dismissaldate'],
                'pixtype': ss['pixtype'],
                'pixkey': ss['pixkey'],
                'comission': ss['comission'],
                'sellername': ss['sellername'],
            })
            sess.commit()
            st.success(f"Vendedor adicionado com sucesso")

    except Exception as e:
        ss['err']['addSeller'].append(f"Add error: {e}")
        st.warning(ss['err']['addSeller'][len(ss['err']['addSeller'])-1])

def editSeller(u):
    try:
        with conn.session as sess:
            sess.execute(u)
            sess.commit()
            st.success(f"Vendedor atualizado com sucesso")

    except Exception as e:
        ss['err']['editSeller'].append(f"Add error: {e}")
        st.warning(ss['err']['editSeller'][len(ss['err']['editSeller'])-1])


import loader
loader.loadSeller()
meta = sqlalchemy.MetaData()
meta.reflect(bind=conn.engine)
ss['sellertable'] = sqlalchemy.Table('sellertable', meta)

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
            tabPreview, tabAdd, tabEdit, = st.tabs(['Visualizar Vendedores','Adicionar Vendedor', 'Editar Vendedor', ])

            with tabPreview:
                ss['preview'] = copy.deepcopy(ss['dfSeller'].copy(deep=True))
                ss['preview'] = ss['preview'][ss['preview']['sellerid'] != 1]
                ss['preview'].reset_index(inplace=True, drop=True)
                ss['preview'] = st.data_editor(
                    ss['preview'],
                    num_rows='fixed',
                    use_container_width=True,
                    column_config={
                    'disabled': st.column_config.CheckboxColumn('Off?', disabled=False),
                    'sellername': st.column_config.Column('Nome', disabled=True),
                    'pixkey': st.column_config.Column('Chave PIX', disabled=True),
                    'email': st.column_config.Column('E-mail', disabled=True),
                    'phonenum': st.column_config.Column('Telefone', disabled=True),
                    'address': st.column_config.Column('Endereço', disabled=True),
                    'district': st.column_config.Column('Bairro', disabled=True),
                    'zipcode': st.column_config.Column('CEP', disabled=True),
                    'birthdate': st.column_config.Column('Nascimento', disabled=True),
                    'hiringdate': st.column_config.Column('Contratação', disabled=True),
                    'comission': st.column_config.Column('Comissão %', disabled=True),
                    },
                    hide_index=True,
                    key=keys[int(len(keys)/2)],
                    column_order=['disabled', 'sellername', 'comission', 'pixkey', 'email', 'phonenum', 'address', 'zipcode', 'district', 'birthdate', 'hiringdate'])

                with st.popover('Desativar VENDEDORES selecionados?'):
                    confirm = st.button('Sim!')
                    st.write('CANCELE clicando fora dessa caixa')
                    ss['disable_me'] = list()
                    if confirm:
                        for a in range(len(ss['preview']['disabled'])):
                            if ss['preview']['disabled'][a] == 1:
                                ss['disable_me'].append(ss['preview']['sellerid'][a])
                        if confirm:
                            for me in ss['disable_me']:
                                u = sqlalchemy.update(ss['sellertable'])
                                u = u.values({
                                'disabled': True,
                                })
                                u = u.where(ss['sellertable'].c.sellerid == int(me))
                                editSeller(u)
                                st.rerun()

            with tabAdd:
                st.markdown('## Cadastrar Vendedor')
                
                with st.form(key='v_form', clear_on_submit=True):
                    ss['sellername'] = st.text_input('Nome do Vendedor', key=keys[0], value='Padrão')
                    col2, col3, = st.columns([1,2])
                    with col2:
                        ss['phonenum'] = st.text_input('Telefone', key=keys[1], value='Padrão')
                    with col3:
                        ss['email'] = st.text_input('Email do Vendedor', key=keys[2], value='Padrão')

                    col4, col5, = st.columns([3,1])
                    with col4:
                        ss['address'] = st.text_input('Endereço (Rua e Número)', key=keys[3], value='Padrão')
                        ss['addressaddinfo'] = st.text_input('Endereço (Complemento)', key=keys[9], value='Padrão')
                    with col5:
                        ss['district'] = st.text_input('Endereço (Bairro)', key=keys[4], value='Padrão')
                        ss['zipcode'] = st.text_input('Endereço (CEP)', key=keys[10], value='Padrão')
                    
                    col6, col7, col8, = st.columns(3)
                    with col6:
                        ss['birthdate'] = st.date_input('Data de Nascimento', key=keys[5], value=datetime.date(datetime.datetime.today().year-18, datetime.datetime.today().month, datetime.datetime.today().day), format='DD/MM/YYYY')
                    with col7:
                        ss['hiringdate'] = st.date_input('Data de Admissão', key=keys[6], value='today', format='DD/MM/YYYY')
                    with col8:
                        ss['dismissaldate'] = st.date_input('Data de Desligamento', key=keys[7], value=datetime.date(datetime.datetime.today().year+1, datetime.datetime.today().month, datetime.datetime.today().day), format='DD/MM/YYYY')

                    col9, col10, = st.columns([3,1])
                    with col9:
                        ss['pixkey'] = st.text_input('Pix do Vendedor', key=keys[8], value='Padrão')
                    with col10:
                        ss['comission'] = st.slider('Porcentagem de Comissão', min_value=0, max_value=25, format='%f%%', value=8, key=keys[11])

                    submit = st.form_submit_button('Adicionar Vendedor')
                    if submit:
                            if ss['pixkey'] == ss['email']:
                                ss['pixtype'] = 'Email'
                            if ss['pixkey'] == ss['phonenum']:
                                ss['pixtype'] = 'Telefone'
                            else:
                                ss['pixtype'] = 'Outro'
                            addSeller()
                            st.rerun()
                            

            with tabEdit:
                vStr = ['sellername', 'email', 'address', 'zipcode', 'pixkey', 'comission', 'codVnddr', 'district', 'addressaddinfo']
                vDttm = ['birthdate', 'hiringdate', 'dismissaldate']
                vN = ['comission']

                st.markdown('## Editar Vendedor Cadastrado')
                sort_Edit = list(ss['dfSeller']['sellername'])
                sort_Edit.sort()

                ss['edit'] = st.selectbox('Selecione um VENDEDOR para Editar', key=keys[12], options=sort_Edit)
                if ss['edit']:
                    ss['dfSeller_Ed'] = copy.deepcopy(ss['dfSeller'].copy(deep=True))
                    ss['dfSeller_Ed'] = ss['dfSeller_Ed'][ss['dfSeller']['sellername'] == ss['edit']]
                    ss['dfSeller_Ed'] = ss['dfSeller_Ed'].dropna(how='all')
                    ss['dfSeller_Ed'].reset_index(inplace=True, drop=True)

                    with st.form(key='ev_form', clear_on_submit=True):
                        ss['e_sellername'] = st.text_input('Nome do Vendedor', key=keys[88], value=ss['dfSeller_Ed']['sellername'][0])
                        col2, col3, = st.columns([1,2])
                        with col2:
                            ss['e_phonenum'] = st.text_input('Telefone', key=keys[99], value=ss['dfSeller_Ed']['phonenum'][0])
                        with col3:
                            ss['e_email'] = st.text_input('Email do Vendedor', key=keys[98], value=ss['dfSeller_Ed']['email'][0])

                        col4, col5, = st.columns([3,1])
                        with col4:
                            ss['e_address'] = st.text_input('Endereço (Rua e Número)', key=keys[97], value=ss['dfSeller_Ed']['address'][0])
                            ss['e_addressaddinfo'] = st.text_input('Endereço (Complemento)', key=keys[96], value=ss['dfSeller_Ed']['addressaddinfo'][0])
                        with col5:
                            ss['e_district'] = st.text_input('Endereço (Bairro)', key=keys[95], value=ss['dfSeller_Ed']['district'][0])
                            ss['e_zipcode'] = st.text_input('Endereço (CEP)', key=keys[94], value=ss['dfSeller_Ed']['zipcode'][0])
                        
                        col6, col7, col8, = st.columns(3)
                        with col6:
                            ss['e_birthdate'] = st.date_input('Data de Nascimento', key=keys[93], value=datetime.datetime.strptime(ss['dfSeller_Ed']['birthdate'][0], '%d/%m/%Y'), format='DD/MM/YYYY') 
                        with col7:
                            ss['e_hiringdate'] = st.date_input('Data de Admissão', key=keys[92], value=datetime.datetime.strptime(ss['dfSeller_Ed']['hiringdate'][0], '%d/%m/%Y'), format='DD/MM/YYYY')
                        with col8:
                            ss['e_dismissaldate'] = st.date_input('Data de Desligamento', key=keys[91], value=datetime.datetime.strptime(ss['dfSeller_Ed']['dismissaldate'][0], '%d/%m/%Y'), format='DD/MM/YYYY')

                        col9, col10, = st.columns([3,1])
                        with col9:
                            ss['e_pixkey'] = st.text_input('Pix do Vendedor', key=keys[90], value=ss['dfSeller_Ed']['pixkey'][0])
                        with col10:
                            ss['e_comission'] = st.slider('Porcentagem de Comissão', step=1, min_value=0, max_value=25, format='%f%%', key=keys[89], value=int(ss['dfSeller_Ed']['comission'][0]))
                        ss['e_sellerid'] = ss['dfSeller_Ed']['sellerid'][0]

                        e_submit = st.form_submit_button('Editar Vendedor')
                        if e_submit:
                            if e_submit:
                                u = sqlalchemy.update(ss['sellertable'])
                                u = u.values({
                                    'sellerid': ss['e_sellerid'],
                                    'email': ss['e_email'],
                                    'phonenum': ss['e_phonenum'],
                                    'address': ss['e_address'],
                                    'zipcode': ss['e_zipcode'],
                                    'district': ss['e_district'],
                                    'addressaddinfo': ss['e_addressaddinfo'],
                                    'birthdate': ss['e_birthdate'],
                                    'hiringdate': ss['e_hiringdate'],
                                    'dismissaldate': ss['e_dismissaldate'],
                                    'pixtype': 'Outro',
                                    'pixkey': ss['e_pixkey'],
                                    'comission': ss['e_comission'],
                                    'sellername': ss['e_sellername'],
                                    })
                                u = u.where(ss['sellertable'].c.sellerid == ss['e_sellerid'])
                                editSeller(u)
                                st.rerun()
        fragment()
