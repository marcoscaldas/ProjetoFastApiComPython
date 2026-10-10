import sqlite3
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(titles="API de Tarefas com SQLite")
BANCO = Path(__file__).with_name("tarefas.db")

class Tarefa(BaseModel):
    id: Optional[int] = None
    titulo: str
    descricao: str
    concluida: bool = False


def conectar():
    conexao = sqlite3.connect(BANCO, timeout=10)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS tarefas(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                concluida INTERGER NOT NULL DEFAULT 0
            )        
        """)

criar_tabela()

def converter_tarefa(linha):
    return Tarefa(id=linha["id"],titulo=linha["titulo"],
                  descricao=linha["descricao"], concluida=bool(linha["concluida"]))


@app.get("/tarefas", response_model=List[Tarefa])
def listar_tarefas():
    with conectar() as conexao:
        linhas = conexao.execute('SELECT * FROM tarefas ORDER BY id').fetchall()

    return [converter_tarefa(linha) for linha in linhas]


@app.post("/tarefas",response_model=Tarefa, status_code=201)
def criar_tarefa(tarefa: Tarefa):
    with conectar() as conexao:
        cursor = conexao.execute(
            'INSERT INTO tarefas(titulo, descricao, concluida)  VALUES (?,?,?)',
            (tarefa.titulo, tarefa.descricao, int(tarefa.concluida)),            
        )
        novo_id = cursor.lastrowid
    return  Tarefa(id=novo_id, titulo=tarefa.titulo,
                    descricao=tarefa.descricao, concluida=tarefa.concluida)



@app.get("/tarefas/{tarefa_id}", response_model=Tarefa)
def obter_tarefa(tarefa_id: int):
    with conectar() as conexao:
        linha = conexao.execute("SELECT * FROM tarefas WHERE id = ?" , (tarefa_id,)).fetchone()
    if linha is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return converter_tarefa(linha)


@app.put("/tarefas/{tarefa_id}", response_model=Tarefa)
def atualizar_tarefa(tarefa_id: int, tarefa_atualizada: Tarefa):
    with conectar() as conexao:
        cursor = conexao.execute(
            "UPDATE tarefas SET titulo = ? , descricao = ? , concluida = ? WHERE id = ?",
            (tarefa_atualizada.titulo, tarefa_atualizada.descricao,
            int(tarefa_atualizada.concluida), tarefa_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return Tarefa(id=tarefa_id, titulo=tarefa_atualizada.titulo,
                  descricao = tarefa_atualizada.descricao,
                  concluida = tarefa_atualizada.concluida )

@app.delete("/tarefas/{tarefa_id}", status_code=204)
def deletar_tarefa(tarefa_id: int):
    with conectar() as conexao:
        cursor = conexao.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    return None
