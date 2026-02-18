#IMPORTAR O FASTAPI 
from fastapi import FastAPI, HTTPException
#SERVE PARA DEFINIR O FORMADO DOS DADOS
from pydantic import BaseModel
#AJDUAR NA TIPAGEM
from typing import List, Optional

#CRIAR A API
app  = FastAPI (title="API de Tarefas")

#MODELO DE DADOS
class Tarefa(BaseModel):
    id: Optional[int] = None
    titulo: str
    descricao: str
    concluida: bool = False

#BANCO EM MEMORIA
db_tarefas = []


#ROTA PARA LISTAR TODAS AS TAREFAS
@app.get('/tarefas', response_model=List[Tarefa])
async def listar_tarefas():
    return db_tarefas

#ROTA PARA CRIAR TAREFA
@app.post('/tarefas', response_model=Tarefa, status_code=201)

async def criar_tarefa(tarefa: Tarefa):
    tarefa.id = len(db_tarefas) + 1
    db_tarefas.append(tarefa)
    return tarefa


#BUSCAR TAREFA POR ID
@app.get('/tarefas/{tarefa_id}', response_model=Tarefa)
async def obter_tarefa(tarefa_id: int):
    for t in db_tarefas:
        if t.id == tarefa_id:
            return t
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")


#ROTA PARA ALTERAR TAREFA
@app.put('/tarefas/{tarefa_id}', response_model=Tarefa)
async def atualizar_tarefa(tarefa_id: int, tarefa_atualizada: Tarefa):
    for index, t in enumerate(db_tarefas):
        if t.id == tarefa_id:
            tarefa_atualizada.id = tarefa_id

            db_tarefas[index] = tarefa_atualizada

            return tarefa_atualizada
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")

#ROTA PARA DELETAR
@app.delete('/tarefas/{tarefa_id}', status_code=204)
async def deletar_tarefa(tarefa_id: int):
    for t in db_tarefas:
        if t.id == tarefa_id:
            db_tarefas.remove(t)
            return
    raise HTTPException(status_code=404, detail="Tarefa não encontrada")











