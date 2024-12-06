### PRINCIPAIS IMPORTS, SEMPRE ATUALIZAR QUANDO REMOVER/ADICIONAR ALGUMA FUNÇÃO!
import streamlit as st
from streamlit_extras.stylable_container import stylable_container as style
from streamlit import session_state as ss
from sqlalchemy import create_engine, text
import pandas as pd

### PRIMEIRA FUNÇÃO REAL É A CONEXÃO COM O BANCO DE DADOS

database_url = 'postgresql+psycopg2://postgres:reWchpesoUGUmqirjmCoUfcXIXAntRWj@junction.proxy.rlwy.net:22310/railway'

engine = create_engine(database_url)

conn = st.connection("postgresql", type="sql")

### DEFINIÇÃO DE VARIÁVIES

def loadErr():
    with engine.connect() as connection:
        query = text("""SELECT * FROM public.errortable;""")
        result = connection.execute(query).mappings().all()
        ss['dfErr'] = pd.DataFrame(data=result)
    
def listVendor():
    with engine.connect() as connection:
        query = text("""SELECT vendname, vendid FROM public.vendtable where disabled = False;""")
        result = connection.execute(query).mappings().all()
        ss['get_vendor'] = pd.DataFrame(data=result)

def listSeller():
    with engine.connect() as connection:
        query = text("""SELECT sellername, comission, sellerid FROM public.sellertable where disabled = False;""")
        result = connection.execute(query).mappings().all()
        ss['get_seller'] = pd.DataFrame(data=result)

def loadInventory():
    with engine.connect() as connection:
        query = text("""SELECT * FROM public.inventtable where disabled = False;""")
        result = connection.execute(query).mappings().all()
        ss['dfInventory'] = pd.DataFrame(data=result)
    ss['dfInventory'] = ss['dfInventory'][ss['dfInventory']['itemid'] != 1]
    ss['dfInventory'].reset_index(inplace=True, drop=True)
       
def loadVendor():
    with engine.connect() as connection:
        query = text("""SELECT disabled, vendid, email, phonenum, address, zipcode, district, addressaddinfo, pixtype, pixkey, vendname, TO_CHAR(admissiondate, 'DD/MM/YYYY') AS admissiondate FROM public.vendtable where disabled = False;""")
        result = connection.execute(query).mappings().all()
        ss['dfVendor']= pd.DataFrame(data=result)
    ss['dfVendor'] = ss['dfVendor'][ss['dfVendor']['vendid'] != 1]
    ss['dfVendor'].reset_index(inplace=True, drop=True)

def loadSeller():
    with engine.connect() as connection:
        query = text("""SELECT disabled, sellerid, email, phonenum, address, zipcode, district, addressaddinfo, TO_CHAR(birthdate, 'DD/MM/YYYY') AS birthdate, TO_CHAR(hiringdate, 'DD/MM/YYYY') AS hiringdate, TO_CHAR(dismissaldate, 'DD/MM/YYYY') AS dismissaldate, pixtype, pixkey, comission, sellername FROM public.sellertable where disabled = False;""")
        result = connection.execute(query).mappings().all()
        ss['dfSeller'] = pd.DataFrame(data=result)
    ss['dfSeller'] = ss['dfSeller'][ss['dfSeller']['sellerid'] != 1]
    ss['dfSeller'].reset_index(inplace=True, drop=True)

def loadPurchase():
    with engine.connect() as connection:
        query = text("""SELECT disabled, purchid, totalamount, vendname, paymmode1, TO_CHAR(purchdate, 'DD/MM/YYYY') AS purchdate FROM public.purchtable where disabled = False;""")
        result = connection.execute(query).mappings().all()
        ss['dfPurchase'] = pd.DataFrame(data=result)
    ss['dfPurchase']['identifier'] = str()
    for i, j in zip(range(len(ss['dfPurchase']['vendname'])), range(len(ss['dfPurchase']['purchid']))):
        ss['dfPurchase'].loc[i, 'identifier'] = str(ss['dfPurchase'].loc[i, 'vendname']) + '¨' + str(ss['dfPurchase'].loc[j, 'purchid'])
    ss['dfPurchase'] = ss['dfPurchase'][ss['dfPurchase']['purchid'] != 1]
    ss['dfPurchase'].reset_index(inplace=True, drop=True)

def loadSales():
    with engine.connect() as connection:
        query = text("""SELECT salescode, totalamount, settledamount, disabled, salesid, sellername, qrcode, itemname, storename, quantity, payment1, payment2, TO_CHAR(salesdate, 'DD/MM/YYYY') AS salesdate from public.salestable where disabled = False;""")
        result = connection.execute(query).mappings().all()
        ss['dfSales'] = pd.DataFrame(data=result)
    ss['dfSales']['identifier'] = str()
    for i, j in zip(range(len(ss['dfSales']['sellername'])), range(len(ss['dfSales']['salesid']))):
        ss['dfSales'].loc[i, 'identifier'] = str(ss['dfSales'].loc[i, 'sellername']) + '¨' + str(ss['dfSales'].loc[j, 'salesid'])
    ss['dfSales'] = ss['dfSales'][ss['dfSales']['salesid'] != 1]
    ss['dfSales'].reset_index(inplace=True, drop=True)

def loadInventory_D():
    with engine.connect() as connection:
        query = text("""SELECT * FROM public.inventtable where disabled = True;""")
        result = connection.execute(query).mappings().all()
        ss['dfInventory_D'] = pd.DataFrame(data=result)
    ss['dfInventory_D'] = ss['dfInventory_D'][ss['dfInventory_D']['itemid'] != 1]
    ss['dfInventory_D'].reset_index(inplace=True, drop=True)
    
def loadVendor_D():
    with engine.connect() as connection:
        query = text("""SELECT * FROM public.vendtable where disabled = True;""")
        result = connection.execute(query).mappings().all()
        ss['dfVendor_D'] = pd.DataFrame(data=result)
    ss['dfVendor_D'] = ss['dfVendor_D'][ss['dfVendor_D']['vendid'] != 1]
    ss['dfVendor_D'].reset_index(inplace=True, drop=True)

def loadSeller_D():
    with engine.connect() as connection:
        query = text("""SELECT * FROM public.sellertable where disabled = True;""")
        result = connection.execute(query).mappings().all()
        ss['dfSeller_D'] = pd.DataFrame(data=result)
    ss['dfSeller_D'] = ss['dfSeller_D'][ss['dfSeller_D']['sellerid'] != 1]
    ss['dfSeller_D'].reset_index(inplace=True, drop=True)

def loadPurchase_D():
    with engine.connect() as connection:
        query = text("""SELECT * FROM public.purchtable where disabled = True;""")
        result = connection.execute(query).mappings().all()
        ss['dfPurchase_D'] = pd.DataFrame(data=result)
    ss['dfPurchase_D'] = ss['dfPurchase_D'][ss['dfPurchase_D']['purchid'] != 1]
    ss['dfPurchase_D'].reset_index(inplace=True, drop=True)

def loadSales_D():
    with engine.connect() as connection:
        query = text("""SELECT * FROM public.salestable where disabled = True;""")
        result = connection.execute(query).mappings().all()
        ss['dfSales_D'] = pd.DataFrame(data=result)
    ss['dfSales_D'] = ss['dfSales_D'][ss['dfSales_D']['salesid'] != 1]
    ss['dfSales_D'].reset_index(inplace=True, drop=True)

def loadParameters():
    with engine.connect() as connection:
        query = text("""SELECT config_id, storename1, storename2, storename3, pix1, dinheiro1, debito1, credvista1, credparc1, dinheiro2, debito2, credvista2, pix2, taxcredvista, taxcred2x, taxcred3x, taxcred4x, taxcred5x, taxcred6x, taxcred7x, taxcred8x, taxcred9x, taxcred10x, purchpadrao, purchpix, purchcheque, purchduplicata, purchcredvista, purchcred2x, purchcred3x, purchcred4x FROM public.paramtable;""")
        result = connection.execute(query).mappings().all()
        ss['dfParameters'] = pd.DataFrame(data=result)

def loadLastItem():
    with engine.connect() as connection:
        query = text("""SELECT * FROM  public.inventtable order by itemid desc limit 1;""")
        result = connection.execute(query).mappings().all()
        ss['dfInventory_L'] = pd.DataFrame(data=result)

