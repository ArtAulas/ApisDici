from sqlalchemy import create_engine
from sqlalchemy.sql import text

# para rodar esse arquivo, instale a versão 1.4 do sqlalchemy
# python -m pip install sqlalchemy==1.4

class NotFoundError(Exception):
    pass

class IncompatibleError(Exception):
    pass


engine = create_engine('sqlite:///tinder.db')

#criar a tabela
with engine.connect() as con:    
    create_pessoas = """
    CREATE TABLE IF NOT EXISTS Pessoa (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        sexo TEXT,
        busca_homem BOOL,
        busca_mulher BOOL
    )
    """    
    rs = con.execute(create_pessoas)
    create_interesses = """
    CREATE TABLE IF NOT EXISTS Interesse (
        id_interessado INTEGER,
        id_alvo INTEGER,
        FOREIGN KEY (id_interessado) REFERENCES Pessoas(id),
        FOREIGN KEY (id_alvo) REFERENCES Pessoas(id)
    )
    """    
    rs = con.execute(create_interesses)

def adiciona_pessoa(dic_pessoa):
    with engine.connect() as con:    
        sql_criar = '''INSERT INTO Pessoa (id,nome,sexo, busca_homem, busca_mulher) 
                                   VALUES (:id,:nome,:sexo,:busca_homem,:busca_mulher)'''
        sexo = dic_pessoa.get("sexo")
        if sexo == "mulher":
            sexo = "M"
        if sexo == "homem":
            sexo = "H"
        buscando = dic_pessoa.get("buscando",[])
        busca_homem = ("homem" in buscando)
        busca_mulher = ("mulher" in buscando)
        con.execute(sql_criar, nome=dic_pessoa['nome'], id=dic_pessoa['id'], 
                               sexo=sexo, busca_homem=busca_homem, busca_mulher=busca_mulher)

def todas_as_pessoas():
    with engine.connect() as con:    
        statement = text ("""SELECT * FROM Pessoa""")
        rs = con.execute(statement) 
        resposta = []
        lista_linhas = rs.fetchall()
        for linha in lista_linhas:
            resposta.append(dict(linha))
        return resposta

def reseta():
    with engine.connect() as con:    
        statement = text ("""DELETE FROM Pessoa""")
        rs = con.execute(statement)
        statement = text ("""DELETE FROM Interesse""")
        rs = con.execute(statement)

def localiza_pessoa(id_pessoa):
    with engine.connect() as con:
        sql_localiza='''SELECT * FROM PESSOA
                        WHERE id=:id1'''
        rs=con.execute(sql_localiza,id1=id_pessoa)
        pessoa=rs.fetchall()
        if pessoa==[]:
            raise NotFoundError
        return dict(pessoa[0])


def adiciona_interesse(id1,id2):
    p1=localiza_pessoa(id1)
    p2=localiza_pessoa(id2)
    if p2['sexo']=='H':
        if p1['busca_homem'] == 0:
            raise IncompatibleError
    if p2['sexo']=='M':
        if p1['busca_mulher'] == 0:
            raise IncompatibleError
    

    with engine.connect() as con:
        sql_add='''INSERT INTO Interesse(id_interessado,id_alvo)
                    VALUES (:id_interessado,:id_alvo)'''
        rs=con.execute(sql_add,id_interessado=id1,id_alvo=id2)

def adiciona_interesse(id1,id2):
    localiza_pessoa(id1)
    localiza_pessoa(id2)

    with engine.connect() as con:
        sql_verifica='''SELECT *
                    FROM Pessoa AS p1 JOIN Pessoa AS p2
                    WHERE (p1.id=:id_interessado AND p1.busca_mulher=1 AND p2.id=:id_alvo AND p2.sexo='M')
                    OR (p1.id=:id_interessado AND p1.busca_homem=1 AND p2.id=:id_alvo AND p2.sexo='H')'''
        rs=con.execute(sql_verifica,id_interessado=id1,id_alvo=id2)
        if rs.fetchall()==[]:
            raise IncompatibleError
        
        sql_add='''INSERT INTO Interesse(id_interessado,id_alvo)
                    VALUES (:id_interessado,:id_alvo)'''
        con.execute(sql_add,id_interessado=id1,id_alvo=id2)


def consulta_interesses(id_pessoa):
    localiza_pessoa(id_pessoa)
    with engine.connect() as con:
        sql_consulta='''SELECT id_alvo FROM INTERESSE
                        WHERE id_interessado=:id1'''
        rs=con.execute(sql_consulta,id1=id_pessoa)
        interesses=rs.fetchall()
        list_interesses=[]
        for interesse in interesses:
            list_interesses.append(dict(interesse)['id_alvo'])
        return list_interesses

def remove_interesse(id1,id2):
    localiza_pessoa(id1)
    localiza_pessoa(id2)

    with engine.connect() as con:
        sql_remove='''DELETE FROM Interesse
                    WHERE id_interessado=:id1 AND id_alvo=:id2'''
        rs=con.execute(sql_remove,id1=id1,id2=id2)

def verifica_match(id1,id2):
    localiza_pessoa(id1)
    localiza_pessoa(id2)

    with engine.connect() as con:
        sql_verifica='''SELECT *
                        FROM Interesse AS i1 JOIN Interesse AS i2
                        WHERE i1.id_alvo=i2.id_interessado AND i2.id_alvo=i1.id_interessado 
                        AND i1.id_interessado=:id1 AND i1.id_alvo=:id2'''
        rs=con.execute(sql_verifica, id1=id1, id2=id2)
        match=rs.fetchall()
        if match==[]:
            return False
        return True

def lista_matches(id_pessoa):
    localiza_pessoa(id_pessoa)
    with engine.connect() as con:
        sql_consulta='''SELECT i1.id_alvo
                        FROM Interesse AS i1 JOIN Interesse AS i2
                        WHERE i1.id_alvo=i2.id_interessado AND i2.id_alvo=i1.id_interessado 
                        AND i1.id_interessado=:id1'''
        rs=con.execute(sql_consulta,id1=id_pessoa)
        matches=rs.fetchall()
        list_matches=[]
        for match in matches:
            list_matches.append(dict(match)['id_alvo'])
        return list_matches