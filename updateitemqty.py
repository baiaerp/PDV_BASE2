import pandas as pd
from sqlalchemy import create_engine, text


database_url = 'postgresql+psycopg2://postgres:wQdfjKRNUKFfhuelQAbyeOhxtILDNeYS@viaduct.proxy.rlwy.net:23717/bembaiana'

class InventtableConnection:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.df = pd.DataFrame()
        self.addqty_store1 = 0
        self.addqty_store2 = 0
        self.addqty_store3 = 0
        self.qrcode = "PADRÃO"

    def loadstoresqty(self):
        try:
            with self.engine.connect() as connection:
                query = text("""SELECT qrcode, store1qty, store2qty, store3qty
                                FROM public.inventtable
                                WHERE inventtable.qrcode = :qrcode
                            """)
                result = connection.execute(query, {"qrcode": self.qrcode})
                data = result.fetchall()
                self.df = pd.DataFrame(data, columns=['qrcode', 'store1qty', 'store2qty', 'store3qty'])
                print("Dados carregados com sucesso!")
                print(self.df.head())
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def storeqty_update(self):
        if not self.df.empty:
            try:
                with self.engine.connect() as connection:
                    print("Conexão estabelecida com sucesso!")
                    for index, row in self.df.iterrows():
                        try:
                            trans = connection.begin()
                            query = text("""
                                UPDATE public.inventtable
                                SET store1qty = :storeqty1, 
                                    store2qty = :storeqty2, 
                                    store3qty = :storeqty3
                                WHERE qrcode = :qrcode
                            """)
                            connection.execute(query, {
                                "qrcode": row['qrcode'],
                                "storeqty1": row['store1qty'] + self.addqty_store1,
                                "storeqty2": row['store2qty'] + self.addqty_store2,
                                "storeqty3": row['store3qty'] + self.addqty_store3
                            })
                            trans.commit()
                            print(f"Quantidade do item {row['qrcode']} atualizada!")
                        except Exception as e:
                            trans.rollback()
                            print(f"Erro ao atualizar a quantidade do item {row['qrcode']}: {e}")
            except Exception as e:
                print(f"Erro ao conectar ao banco de dados: {e}")
        else:
            print("DataFrame não carregado. Por favor, chame a função loadstoresqty primeiro.")
"""
item_conn = InventtableConnection(database_url)
item_conn.loadstoresqty()
item_conn.addqty_store1 = 10
item_conn.addqty_store2 = 7
item_conn.addqty_store3 = 0
item_conn.storeqty_update()
"""
