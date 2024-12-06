### PRINCIPAIS IMPORTS, SEMPRE ATUALIZAR QUANDO REMOVER/ADICIONAR ALGUMA FUNÇÃO!
import streamlit as st
import pandas as pd
from streamlit import session_state as ss
import random
import copy
import sqlalchemy
import datetime

### CONFIGURAÇÃO DA PÁGINA TEM QUE SER, SEMPRE, O PRIMEIRO CÓDIGO APÓS OS IMPORTS

st.set_page_config(
    page_title='PDV - Admin',
    page_icon='📒',
    layout='wide',
)

### PRIMEIRA FUNÇÃO REAL É A CONEXÃO COM O BANCO DE DADOS
conn = st.connection("postgresql", type="sql")
### DEFINIÇÃO DE VARIÁVIES
### GERAÇÃO DE CHAVES ALEATÓRIAS CONSITENTES PARA OS WIDGETS DO STREAMLIT
random.seed(24)
keys = []
for i in range(110):
    keys.append(random.random())

### VARIÁVEIS 
vendname = str()
itemid = int()
qrcode = str()
itemcost = float()
itemprice = float()
itemaddinfo = str()
store1qty = float()
store2qty = float()
store3qty = float()
itemname = str()
itemsize = str()
colorid = str()

import loader
from err import errStorage
errStorage()

loader.loadParameters()
loader.loadErr()

lista = list(ss['dfParameters'].columns)
stores = [ss['dfParameters']['storename1'][0], ss['dfParameters']['storename2'][0], ss['dfParameters']['storename3'][0]]

#variaveis do vitor
sucesso = 'Sucesso!'

loader.loadLastItem()
lastitemid = int(max(ss['dfInventory_L']['itemid']))

### DECLARAÇÃO DE FUNÇÕES PRÓPRIAS
def addItem():
    with conn.session as sess:
        try:
            sess.execute(sqlalchemy.sql.text(f"INSERT INTO inventtable ({', '.join(variables)}) VALUES ({', '.join(target)});"), {
                'vendname': ss['vendname'],
                'qrcode': ss['qrcode'],
                'itemcost': ss['itemcost'],
                'itemprice': ss['itemprice'],
                'itemaddinfo': ss['itemaddinfo'],
                'store1qty': ss['store1qty'],
                'store2qty': ss['store2qty'],
                'store3qty': ss['store3qty'],
                'itemname': ss['itemname'],
                'itemsize': ss['itemsize'],
                'colorid': ss['colorid'],
                'minqty': ss['min_qty'],
            })
            sess.commit()
            st.success(sucesso)

        except Exception as e:
            sess.execute(sqlalchemy.sql.text(f"INSERT INTO errortable (resolved, message, errordate, errororigin) VALUES (resolved, message, errordate, errororigin);"), {
                'resolved': False, 
                'message': f"Add: {e}",  
                'errordate': datetime.datetime.now(), 
                'errororigin':__file__, 
                })
            sess.commit()


def dfInventory_Edit(u):
    with conn.session as sess:
        try:
            sess.execute(u)
            sess.commit()
            st.success(f"Inventário: {sucesso}")

        except Exception as e:
            sess.execute(sqlalchemy.sql.text(f"INSERT INTO errortable (resolved, message, errordate, errororigin) VALUES (resolved, message, errordate, errororigin);"), {
                'resolved': False, 
                'message': f"Edit: {e}", 
                'errordate': datetime.datetime.now(), 
                'errororigin':__file__, 
                })
            sess.commit()

def logInform():
    with conn.session as sess:
        try:
            sess.execute(sqlalchemy.sql.text(f"INSERT INTO errortable (inform) VALUES (:inform);"), {
                'inform': ss['inform'], 
                })
            sess.commit()
        except Exception as e:
            st.error(e)

### RODANDO FUNÇÕES INICIAIS (GERALMENTE DE LOAD)
loader.loadInventory()
loader.listVendor()
meta = sqlalchemy.MetaData()
meta.reflect(bind=conn.engine)
ss['inventtable'] = sqlalchemy.Table('inventtable', meta)

ss['vendor'] = list(set(ss['get_vendor']['vendname']))

variables = list(ss['dfInventory'].columns)
variables.remove('itemid')
variables.remove('vendid')
variables.remove('filename')
variables.remove('disabled')

target = [str(':')+str(x) for x in variables]

random.seed(111)
for w in range(len(ss['dfInventory']) + 1):
    prdt = str(int(round(random.random(),4)*10000))

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
            tabPreview, tabAdd, tabEdit, tabCode = st.tabs(['Visualizar Produtos', 'Cadastrar Produto', 'Editar Produto Cadastrado','QR Codes'])

            ### PRIMERA TABVIEW
            with tabPreview:
                if len(ss['dfInventory']) <= 0:
                    st.write(f':blue[Não] há itens para transferir')
                else:
                    ss['preview'] = st.data_editor(
                        ss['dfInventory'],
                        num_rows='fixed',
                        use_container_width=True,
                        column_config={
                            'disabled': st.column_config.CheckboxColumn('Off?', disabled=False),
                            'qrcode': st.column_config.Column('QR Code', disabled=True),
                            'itemname': st.column_config.Column('Nome', disabled=True),
                            'itemcost': st.column_config.NumberColumn(
                                'Custo', 
                                format="R$ %.2f",
                                disabled=True),
                            'itemprice': st.column_config.NumberColumn(
                                'Preço', 
                                format="R$ %.2f",
                                disabled=True),
                            'store1qty': st.column_config.Column(stores[0], disabled=True),
                            'store2qty': st.column_config.Column(stores[1], disabled=True),
                            'store3qty': st.column_config.Column(stores[2], disabled=True),
                            'minqty': st.column_config.Column('Mínimo', disabled=True),
                            'itemaddinfo': st.column_config.Column('Informações', disabled=True),
                            'itemsize': st.column_config.Column('Medida', disabled=True),
                            'colorid': st.column_config.Column('Cor', disabled=True),
                        },
                        hide_index=True,
                        key=keys[int(len(keys)/2)],
                        column_order=['disabled', 'qrcode', 'itemname', 'itemcost', 'itemprice', 'store1qty', 'store2qty', 'store3qty', 'minqty', 'itemaddinfo', 'itemsize', 'colorid',]
                    )

                    with st.popover('Desativar ITENS selecionados?'):
                        confirm = st.button('Sim!')
                        st.write('CANCELE clicando fora dessa caixa')
                        ss['disable_me'] = list()
                        if confirm:
                            for a in range(len(ss['preview']['disabled'])):
                                try:
                                    if ss['preview']['disabled'][a] == 1:
                                        ss['disable_me'].append(ss['preview']['itemid'][a])
                                except Exception as e:
                                    with conn.session as sess:
                                        sess.execute(sqlalchemy.sql.text(f"INSERT INTO errortable (resolved, message, errordate, errororigin) VALUES (resolved, message, errordate, errororigin);"), {
                                        'resolved': False, 
                                        'message': f"Popover: {e}", 
                                        'errordate': datetime.datetime.now(), 
                                        'errororigin':__file__, 
                                        })
                                    sess.commit()
                            if confirm:
                                for me in ss['disable_me']:
                                    u = sqlalchemy.update(ss['inventtable'])
                                    u = u.values({
                                        'disabled': True,
                                    })
                                    u = u.where(ss['inventtable'].c.itemid == int(me))
                                    dfInventory_Edit(u)
                                    st.rerun()

            ### SEGUNDA TABVIEW
            with tabAdd:
                with st.container():
                    with st.form(key='v_form', clear_on_submit=True):
                        col0, colN = st.columns([2,1])
                        with col0:
                            ss['itemname'] = st.text_input('Nome do Produto',key=keys[0], value='Padrão')
                        with colN:
                            ss['vendname'] = st.selectbox('Selecione o Fornecedor', key=keys[1], options=ss['vendor'], index=ss['vendor'].index('Padrão'))
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            ss['store1qty'] = st.number_input(f"Quantidade em :blue[{stores[0]}]", step=int(1), min_value=-500, key=keys[2], value=0)
                        with col2:
                            ss['store2qty'] = st.number_input(f"Quantidade em :blue[{stores[1]}]", step=int(1), min_value=-500, key=keys[3], value=0)
                        with col3:
                            ss['store3qty'] = st.number_input(f"Quantidade em :blue[{stores[2]}]", step=int(1), min_value=-500, key=keys[4], value=1)
                        with col4:
                            ss['min_qty'] = st.number_input('Quantidade Mínima', step=0, key=keys[10], value=int(1))

                        col3, col4, col5, col6 = st.columns(4)
                        with col3:
                            ss['itemcost'] = st.number_input('Custo do Produto (R$)', step=0.5, min_value=0.01, key=keys[6], value=0.1)

                        with col4:
                            ss['itemprice'] = st.number_input('Preço de Venda (R$)', step=0.5, min_value=0.01, key=keys[8], value=0.1)
                        
                        with col5:
                            ss['itemsize'] = st.text_input('Medida', key=keys[5], value='Padrão')
                        
                        with col6:
                            ss['colorid'] = st.text_input('Cor', key=keys[7], value='Padrão')

                        ss['itemaddinfo'] = st.text_area('Informações', key=keys[9], value='Padrão')
                        
                        submit = st.form_submit_button('Inserir Produto')
                        if submit:
                            ss['qrcode'] = 'PP' + str(lastitemid+1)
                            addItem()
                            st.rerun()

            ### TERCEIRA TABVIEW
            with tabEdit:
                if len(ss['dfInventory']) <= 0:
                    st.write('Não há itens para editar')
                else:
                    st.markdown('## Editar PRODUTO Cadastrado')
                    # Criando uma nova coluna combinada para exibição
                    ss['dfInventory']['display'] = ss['dfInventory'].apply(
                        lambda row: f"{row['qrcode']} - {row['itemname']} - {row['itemsize']} - {row['colorid']}", axis=1
                    )

                    sort_Edit = list(ss['dfInventory']['display'])
                    sort_Edit.sort()

                    colx1, colx2 = st.columns([3, 1])                        
                    with colx1:
                        ss['choose'] = st.selectbox(
                            'Selecione um :blue[PRODUTO]',
                            index=None,
                            key=keys[30], 
                            options=sort_Edit,
                            )
                                    
                    with colx2:                    
                        ss['scanner'] = st.text_input(label='Scanner', key='scan',)
                        if ss['scanner']:
                            ss['choose'] = str(ss['scanner']).upper()

                    colTainer1, colTainer2, colTainer3 = st.columns([0.62, 0.21, 0.17])
                    with colTainer1:
                        if ss['choose'] == None or len(ss['choose']) == 0:
                            st.write('Nenhum produto selecionado')
                        if ss['choose']:
                            selected_qrcode = ss['choose'].split(' - ')[0]  # Extrair o qrcode da seleção
                            ss['dfInventory_Ed'] = copy.deepcopy(ss['dfInventory'].copy(deep=True))
                            ss['dfInventory_Ed'] = ss['dfInventory_Ed'][ss['dfInventory_Ed']['qrcode'] == selected_qrcode]
                            ss['dfInventory_Ed'] = ss['dfInventory_Ed'].dropna(how='all')
                            ss['dfInventory_Ed'].reset_index(inplace=True, drop=True)

                            if not ss['dfInventory_Ed'].empty:
                                with st.form(key='ee_form', clear_on_submit=True):
                                    col0, colN = st.columns([2,1])
                                    with col0:
                                        ss['e_itemname'] = st.text_input('Nome do Produto', key=keys[90], value=ss['dfInventory_Ed']['itemname'][0])
                                    with colN:
                                        if ss['dfInventory_Ed']['vendname'][0] not in ss['vendor']:
                                            ss['e_vendname'] = st.selectbox('Selecione o Fornecedor', key=keys[98], options=ss['vendor'], index=ss['vendor'].index(ss['vendor'][7]))
                                        else:
                                            ss['e_vendname'] = st.selectbox('Selecione o Fornecedor', key=keys[98], options=ss['vendor'], index=ss['vendor'].index(ss['dfInventory_Ed']['vendname'][0]))

                                    col1, col2, col3, col4 = st.columns(4)
                                    
                                    with col1:
                                        ss['e_store1qty'] = st.number_input(f"Quantidade na :blue[{stores[0]}]", step=int(1), min_value=-500, key=keys[97], value=int(ss['dfInventory_Ed']['store1qty'][0]))
                                    with col2:
                                        ss['e_store2qty'] = st.number_input(f"Quantidade na :blue[{stores[1]}]", step=int(1), min_value=-500, key=keys[96], value=int(ss['dfInventory_Ed']['store2qty'][0]))
                                    with col3:
                                        ss['e_store3qty'] = st.number_input(f"Quantidade na :blue[{stores[2]}]", step=int(1), min_value=-500, key=keys[95], value=int(ss['dfInventory_Ed']['store3qty'][0]))
                                    with col4:
                                        ss['e_min_qty'] = st.number_input('Quantidade Mínima', step=0, key=keys[100], value=int(ss['dfInventory_Ed']['minqty'][0]))

                                    col3, col4, col5, col6 = st.columns(4)
                                    with col3:
                                        ss['e_itemcost'] = st.number_input('Custo (R$)', step=0.5, min_value=0.01, key=keys[93], value=float(ss['dfInventory_Ed']['itemcost'][0]))
                                    
                                    with col4:
                                        ss['e_itemprice'] = st.number_input('Preço (R$)', step=0.5, min_value=0.01, key=keys[91], value=float(ss['dfInventory_Ed']['itemprice'][0]))
                                    
                                    with col5:
                                        ss['e_itemsize'] = st.text_input('Medida', key=keys[94], value=ss['dfInventory_Ed']['itemsize'][0])
                                    
                                    with col6:
                                        
                                        ss['e_colorid'] = st.text_input('Cor', key=keys[92], value=ss['dfInventory_Ed']['colorid'][0])


                                    ss['e_itemaddinfo'] = st.text_area('Informações', key=keys[89], value=ss['dfInventory_Ed']['itemaddinfo'][0])
                                    ss['e_itemid'] = int(ss['dfInventory_Ed']['itemid'][0])
                                    ss['e_qrcode'] = ss['dfInventory_Ed']['qrcode'][0]

                                    e_submit = st.form_submit_button('Editar Produto')
                                    if e_submit:
                                        u = sqlalchemy.update(ss['inventtable'])
                                        u = u.values({
                                            'itemid': ss['e_itemid'],
                                            'vendname': ss['e_vendname'],
                                            'qrcode': ss['e_qrcode'],
                                            'itemcost': ss['e_itemcost'],
                                            'itemprice': ss['e_itemprice'],
                                            'itemaddinfo': ss['e_itemaddinfo'],
                                            'store1qty': ss['e_store1qty'],
                                            'store2qty': ss['e_store2qty'],
                                            'store3qty': ss['e_store3qty'],
                                            'itemname': ss['e_itemname'],
                                            'itemsize': ss['e_itemsize'],
                                            'colorid': ss['e_colorid'],
                                            'minqty': ss['e_min_qty'],
                                        })
                                        u = u.where(ss['inventtable'].c.itemid == ss['e_itemid'])
                                        dfInventory_Edit(u)
                                        st.rerun()

                    with colTainer2:
                        if ss['choose'] == None or len(ss['choose']) == 0:
                            st.write('Nenhum produto selecionado')
                        if ss['choose']:
                            selected_qrcode = ss['choose'].split(' - ')[0]  # Extrair o qrcode da seleção
                            ss['dfInventory_T'] = copy.deepcopy(ss['dfInventory'].copy(deep=True))
                            ss['dfInventory_T'] = ss['dfInventory_T'][ss['dfInventory_T']['qrcode'] == selected_qrcode]
                            ss['dfInventory_T'] = ss['dfInventory_T'].dropna(how='all')
                            ss['dfInventory_T'].reset_index(inplace=True, drop=True)

                            ss['store1qty'] = ss['dfInventory_T'].loc[0, 'store1qty']
                            ss['store2qty'] = ss['dfInventory_T'].loc[0, 'store2qty']
                            ss['store3qty'] = ss['dfInventory_T'].loc[0, 'store3qty']

                            lojas = {stores[0]: 'store1qty', stores[1]: 'store2qty', stores[2]: 'store3qty'}
                            ss['hld'] = list()

                            with st.form(key='m_form', clear_on_submit=True):
                                st.write('TRANSFERIR')

                                fromTo = list(lojas.keys())

                                if 'deLast' not in ss:
                                    ss['deLast'] = fromTo.index('Depósito')

                                if 'paraLast' not in ss:
                                    ss['paraLast'] = 0

                                ss['de'] = st.selectbox(':blue[Origem]', key=keys[31], options=fromTo, index=int(float(ss['deLast'])))

                                ss['para'] = st.selectbox(':blue[Destino]', key=keys[32], options=fromTo, index=int(float(ss['paraLast'])))

                                ss['transfer'] = st.number_input(':blue[Quantidade]', step=int(1), min_value=-500, key=keys[33], value=int(0), max_value=int(ss['dfInventory_T'].loc[0, 'store1qty'] + ss['dfInventory_T'].loc[0, 'store2qty'] + ss['dfInventory_T'].loc[0, 'store3qty']))

                                m_submit = st.form_submit_button('Movimentar Unidades')
                                if m_submit:
                                    ss['deLast'] = fromTo.index(ss['de'])
                                    ss['paraLast'] = fromTo.index(ss['para'])
                                    if ss['de'] == ss['para']:
                                        st.rerun()
            
                                    ss['hld'].append(ss['de'])
                                    ss['hld'].append(ss['para'])
            
                                    for n in list(lojas.keys()):
                                        if n not in ss['hld']:
                                            ss['neutro'] = n
            
                                    u = sqlalchemy.update(ss['inventtable'])
                                    u = u.values({
                                        str(lojas[ss['de']]): float(ss[lojas[ss['de']]] - ss['transfer']),
                                        str(lojas[ss['para']]): float(ss[lojas[ss['para']]] + ss['transfer']),
                                        str(lojas[ss['neutro']]): float(ss[lojas[ss['neutro']]])
                                    })

                                    u = u.where(ss['inventtable'].c.qrcode == selected_qrcode)
                                    dfInventory_Edit(u)

                                    ss['inform'] = str(ss['e_itemname'])+'¨'+str(ss['transfer'])+'¨'+str(ss['de'])+'¨'+(ss['para'])+'¨'+str(datetime.datetime.today().strftime('%d/%m/%Y'))+'¨'+str(datetime.datetime.today().strftime('%H:%M:%S'))

                                    logInform()
                                    st.rerun()

                        with colTainer3:
                            if ss['choose'] == None or len(ss['choose']) == 0:
                                st.write('Nenhum produto selecionado')
                            if ss['choose']:
                                with st.form(key='update_stock_form', clear_on_submit=True):
                                    st.write('ADICIONAR:')
                                    quantity_store1 = st.number_input(f":blue[{stores[0]}]", step=1)
                                    quantity_store2 = st.number_input(f":blue[{stores[1]}]", step=1)
                                    quantity_store3 = st.number_input(f":blue[{stores[2]}]", step=1)

                                    # Botão para submeter o formulário
                                    submit_button = st.form_submit_button(label='Adicionar Unidades')

                                    if submit_button:
                                        ss['e_itemid'] = int(ss['dfInventory_Ed']['itemid'][0])

                                        u = sqlalchemy.update(ss['inventtable'])
                                        u = u.values({
                                            'itemid': ss['e_itemid'],
                                            'store1qty': float(ss['dfInventory_Ed']['store1qty'][0]) + float(quantity_store1),
                                            'store2qty': float(ss['dfInventory_Ed']['store2qty'][0]) + float(quantity_store2),
                                            'store3qty': float(ss['dfInventory_Ed']['store3qty'][0]) + float(quantity_store3),
                                            })
                                        u = u.where(ss['inventtable'].c.itemid == ss['e_itemid'])
                                        dfInventory_Edit(u)
                                        st.rerun()

            ### QUARTA TABVIEW
            from PIL import Image, ImageDraw, ImageFont
            import qrcode as qrCreate
            import io

            def imagem_fundo():
                largura = 366
                altura = 201
                img_main = Image.new("RGB", (largura, altura), "white")
                return img_main

            def write_img(imgg, name, tam, preco):
                img = Image.open(imgg)
                draw = ImageDraw.Draw(img)
                fontN = ImageFont.truetype("/mount/src/pdv_bem_baiana/Arial.ttf", ss['name_font'])
                fontT = ImageFont.truetype("/mount/src/pdv_bem_baiana/Arial.ttf", ss['tam_font'])
                fontP = ImageFont.truetype("/mount/src/pdv_bem_baiana/Arial.ttf", ss['price_font'])

                lines = []
                words = name.split()
                current_line = words[0]
                for word in words[1:]:
                    if len(current_line) + len(word) < 12:
                        current_line += ' ' + word
                    else:
                        lines.append(current_line)
                        current_line = word
                lines.append(current_line)
            
                num_lines = len(lines)
                y = 10
                for line in lines:
                    draw.text((175, y), line, fill="black", font=fontN)
                    y += ss['name_font'] + 5
                
                draw.text((175, 95), tam, fill="black", font=fontT)
                draw.text((170, 120), preco, fill="black", font=fontP)
            
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)
                cols9, cols8 = st.columns(2)
                with cols9:
                    st.image(buf, caption=ss['dfInventory_QR']['display'][0])
                with cols8:
                    st.write('Nome: ', ss['name_font'])
                    st.write('Tamanho: ', ss['tam_font'])
                    st.write('Preço: ', ss['price_font'])

            def gerar_imagens():
                img_main = imagem_fundo()
                qrcode = ss['dfInventory_QR']['display'][0].split(' - ')[0]
                prdt = f"{qrcode}.png"
                name = ss['dfInventory_QR']['display'][0].split(' - ')[1]
                tam = str(ss['dfInventory_QR']['display'][0].split(' - ')[2]) + '_' + str(ss['dfInventory_QR']['display'][0].split(' - ')[3])
                n_preco = ss['dfInventory_QR']['display'][0].split(' - ')[4] if ss['dfInventory_QR']['display'][0].split(' - ')[4] else 0.0
                preco = f"R$ {float(n_preco):.2f}"
                img = qrCreate.make(qrcode, box_size=7)
            
                # Ajusta a posição para estar dentro dos limites
                img = img.resize((180, 180))  # Ajuste de tamanho se necessário
                img_main.paste(img, (0, 0))  # Cole no canto superior esquerdo
                
                # Ajusta a posição para estar dentro dos limites
                img_main.paste(img, (0, 0))  # Cole no canto superior esquerdo
            
                img_main.save(prdt)
                write_img(prdt, name, tam, preco)

            with tabCode:
                with st.form(key='font_form', clear_on_submit=True):
                    cols1, cols2, cols3 = st.columns(3)
                    with cols1:
                        ss['name_font'] = st.number_input(f":blue[Nome]", step=1, value=24)
                    with cols2:
                        ss['tam_font'] = st.number_input(f":blue[Tamanho e Cor]", step=1, value=24)
                    with cols3:
                        ss['price_font'] = st.number_input(f":blue[Preço]", step=1, value=45)
                
                    ss['dfInventory']['display'] = ss['dfInventory'].apply(
                        lambda row: f"{row['qrcode']} - {row['itemname']} - {row['itemsize']} - {row['colorid']} - {float(row['itemprice']):.2f}", axis=1
                    )
                
                    sort_Edit = list(ss['dfInventory']['display'])
                    sort_Edit.sort()
                
                    colx3, colx4 = st.columns([3, 1])
                    with colx3:
                        ss['printQR'] = st.selectbox(
                            'Selecione um :blue[PRODUTO]',
                            options=sort_Edit
                        )
                    with colx4:
                        ss['scanQR'] = st.text_input(label='Scanner', placeholder='QR Code')
                
                    gerar_qrcode = st.form_submit_button(label='Gerar QR Code')
                    if gerar_qrcode:
                        if ss['scanQR'] == '':
                            selected_qrcode = ss['printQR'].split(' - ')[0]
                        else:
                            selected_qrcode = str(ss['scanQR']).upper()
                
                        ss['dfInventory_QR'] = copy.deepcopy(ss['dfInventory'])
                        ss['dfInventory_QR'] = ss['dfInventory_QR'][ss['dfInventory_QR']['qrcode'] == selected_qrcode]
                        ss['dfInventory_QR'] = ss['dfInventory_QR'].dropna(how='all')
                        ss['dfInventory_QR'].reset_index(inplace=True, drop=True)
                        gerar_imagens()

                st.write("---")
                st.link_button('Acessar TODOS os QR Code', 'https://drive.google.com/drive/folders/1v6mbiNXMJxdiyJGzY3_-T2gz5O8kE_-7', use_container_width=True)

        fragment()
