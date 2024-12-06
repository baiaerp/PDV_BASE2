import streamlit as st
import streamlit_authenticator as stauth
from streamlit_extras.stylable_container import stylable_container as style
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import datetime
from datetime import timedelta
from streamlit import session_state as ss
from err import errStorage
st.set_page_config(
    page_title='PDV - Admin',
    page_icon='👜',
    layout='wide',
)

#### CODE AFTER THIS LINE ####

import loader

ss['today'] = datetime.datetime.today()

paramList = list(ss['dfParameters'].columns)
listStore = [paramList[1], paramList[2], paramList[3]]

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

loader.loadErr()

@st.fragment
def fragment():
    with st.container(border=False):
        authenticator.login(fields={'Form name': 'Login', 'Username':'Nome de Usuário', 'Password': 'Senha'})
        if st.session_state['authentication_status'] is False:
            st.error('Usuário/Senha incorreto(s)')
        elif st.session_state['authentication_status'] is None:
            st.warning('Por favor entre com usuário e senha')
        elif st.session_state['authentication_status']:

            spl0 = list()
            spl1 = list()
            spl2 = list()
            spl3 = list()
            spl4 = list()
            spl5 = list()

            for i in range(len(ss['dfErr']['inform'])):

                spl0.append(ss['dfErr']['inform'][i].split('¨')[0])
                spl1.append(ss['dfErr']['inform'][i].split('¨')[1])
                spl2.append(ss['dfErr']['inform'][i].split('¨')[2])
                spl3.append(ss['dfErr']['inform'][i].split('¨')[3])
                spl4.append(ss['dfErr']['inform'][i].split('¨')[4])
                t = datetime.datetime.strptime(ss['dfErr']['inform'][i].split('¨')[5], '%H:%M:%S') - timedelta(hours=3)
                spl5.append(t.strftime('%H:%M:%S'))
            
            dct = {'Item':spl0,'Unidades':spl1,'De':spl2,'Para':spl3,'Dia':spl4, 'Hora': spl5,}
            logsDF = pd.DataFrame(dct)
            st.dataframe(logsDF, use_container_width=True, )

fragment()
