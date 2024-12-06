import streamlit as st
import streamlit_authenticator as stauth
from streamlit import session_state as ss
from streamlit_extras.stylable_container import stylable_container as style
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from sqlalchemy import text, create_engine, MetaData, Table, update, insert
from sqlalchemy.orm import sessionmaker
import pandas as pd
import datetime

st.set_page_config(
    page_title='PDV - Admin',
    page_icon='👜',
    layout='wide',
)

#### CODE AFTER THIS LINE ####
import loader

dbUrl = st.secrets['vars']['database_url']
engine = create_engine(dbUrl)

with open('.streamlit/pswd.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    #config['preauthorized']
)

conn = st.connection("postgresql", type="sql")

### DEFINIÇÃO DE VARIÁVIES
def load_seller():
    try:
        with engine.connect() as connection:
            query = text("""SELECT
                         sellerid,
                         email,
                         phonenum,
                         address,
                         zipcode,
                         district, 
                         addressaddinfo,
                         birthdate,
                         hiringdate,
                         dismissaldate,
                         pixtype,
                         pixkey,
                         comission,
                         sellername,
                         disabled
                         FROM sellertable where disabled = False;""")
            result = connection.execute(query).mappings().all()
            ss['df2Seller'] = pd.DataFrame(data=result)
            print("Sucesso (Seller)!")

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return ss['df2Seller']

def load_invent():
    try:
        with engine.connect() as connection:
            # Exemplo de consulta: obtenha os dados da tabela inventtable
            query = text("""SELECT 
                         itemid,
                         itemname,
                         store1qty,
                         store2qty,
                         store3qty,
                         colorid,
                         itemsize,
                         qrcode,
                         itemprice,
                         itemcost,
                         vendid,
                         vendname,
                         filename,
                         minqty,
                         disabled 
                         FROM inventtable where disabled = False;""")
            result = connection.execute(query).mappings().all()
            ss['df2Inventory'] = pd.DataFrame(data=result)
            print("Sucesso (Inventory)!")

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return ss['df2Inventory'] 
    
def load_sales():
    try:
        with engine.connect() as connection:
            query = text("SELECT * FROM salestable where disabled = False;")
            result = connection.execute(query).mappings().all()
            ss['df2Sales'] = pd.DataFrame(data=result)
            print("Sucesso (Sales)!")

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return ss['df2Sales']

def load_config():
    try:
        with engine.connect() as connection:
            query = text("SELECT config_id, storename1, storename2, storename3, pix1, dinheiro1, debito1, credvista1, credparc1, dinheiro2, debito2, credvista2, pix2, taxcredvista, taxcred2x, taxcred3x, taxcred4x, taxcred5x, taxcred6x, taxcred7x, taxcred8x, taxcred9x, taxcred10x, purchpadrao, purchpix, purchcheque, purchduplicata, purchcredvista, purchcred2x, purchcred3x, purchcred4x FROM paramtable")
            result = connection.execute(query).mappings().all()
            df2Config = pd.DataFrame(data=result)
            df2Config['dia'] = datetime.date.today()
            df2Config['hora'] = datetime.datetime.now().hour
            ss['df2Config'] = df2Config
            print("Sucesso (Config)!")

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
    return ss['df2Config']

def resend(df):
    # Inicializa o mecanismo e a sessão
    Session = sessionmaker(bind=engine)
    
    # Reflete a tabela de inventário
    meta = MetaData()
    meta.reflect(bind=engine)
    invent = Table('inventtable', meta, autoload_with=engine)
    salestable = Table('salestable', meta, autoload_with=engine)

    try:
        with engine.connect() as connection:
            session = Session(bind=connection)
            transaction = connection.begin()  # Inicia a transação

            sales_data = []

            # Inserção em salestable
            for i, row in df.iterrows():
                sales_data.append({
                    'sellername': row['sellername'],
                    'qrcode': row['qrcode'],
                    'itemname': row['itemname'],
                    'storename': row['storename'],
                    'quantity': row['quantity'],
                    'payment1': row['payment1'],
                    'payment2': row['payment2'],
                    'salescode': row['salescode'],
                    'salesdate': row['salesdate'],
                    'totalamount': row['totalamount'],
                    'settledamount': row['settledamount'],
                    'disabled': row['disabled']
                })

            connection.execute(insert(salestable).values(sales_data))
            
            # Função auxiliar para atualizar o inventário
            def update_inventory(store_df, store_column):
                for _, row in store_df.iterrows():
                    current_qty = int(ss['df2Inventory'].loc[ss['df2Inventory']['qrcode'] == row['qrcode'], store_column].iloc[0])
                    new_qty = current_qty - row['quantity']
                    u = update(invent).values({store_column: new_qty}).where(invent.c.qrcode == row['qrcode'])
                    session.execute(u)
                    st.success(f"{store_column} atualizado: {row['qrcode']}")

            # Atualizar inventário para as store1 e store2
            dfs1 = df[df['storename'] == stores[0]][['qrcode', 'quantity']]
            dfs2 = df[df['storename'] == stores[1]][['qrcode', 'quantity']]

            st.write(dfs1)
            st.write(dfs2)

            update_inventory(dfs1, 'store1qty')
            update_inventory(dfs2, 'store2qty')

            # Commit todas as atualizações
            transaction.commit()  # Confirma a transação
    except Exception as e:
        st.write(f"Erro ao conectar ou processar o banco de dados: {e}")
        print(f"Erro ao conectar ou processar o banco de dados: {e}")
        transaction.rollback()  # Desfaz a transação em caso de erro
    finally:
        session.close()

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

loader.loadParameters()
lista = list(ss['dfParameters'].columns)
stores = [ss['dfParameters']['storename1'][0], ss['dfParameters']['storename2'][0], ss['dfParameters']['storename3'][0]]
colDown, colUP = st.columns([1, 3])

with colDown:
    load_seller()
    load_invent()
    load_sales()
    load_config()
    st.markdown('# :blue[**Download**]')
    for file in ['df2Config', 'df2Sales', 'df2Inventory', 'df2Seller']:

        z = file.replace('df2','').lower()
        csv = convert_df(ss[file])
        st.download_button(f"Download :blue[**{z}**]", data=csv, file_name=f"{z}.csv")

with colUP:
    st.markdown('# :blue[**Upload**]')
    uploaded_file = st.file_uploader("Adicione o arquivo :blue[**vendas.csv**]", key='delMe')
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)
        yup = st.button('Confirmado!')
        if yup:
            resend(df)
