import psycopg2
import psycopg2.extras 

DB_NAME = "teste"  
DB_USER = "felipe"    
DB_PASSWORD = "102030"
DB_HOST = "192.168.1.15"   
DB_PORT = "5432"       
def get_db_connection():
    """Estabelece uma conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Executa uma query SQL no banco de dados.
    Retorna o resultado da query ou o cursor em caso de commit bem-sucedido,
    ou None em caso de erro.
    """
    conn = None
    cur = None
    result = None
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(query, params)

            if fetchone:
                result = cur.fetchone()
            elif fetchall:
                result = cur.fetchall()
            
            if commit:
                conn.commit()
                # Para INSERT/UPDATE/DELETE, podemos retornar True ou o cursor se quisermos o rowcount, etc.
                # Para RETURNING, o fetchone/fetchall já terá pego o resultado.
                # Se não for RETURNING e for commit, o resultado ainda será None a menos que explicitamente peguemos algo.
                # Para simplificar, se o commit for bem-sucedido e não houver fetch, podemos retornar True.
                # No entanto, as funções add_... com RETURNING já retornam o ID.
                # Se não for RETURNING, o resultado será None por padrão, o que é ok para indicar sucesso se não houver erro.
                if not fetchone and not fetchall: # Se foi apenas um commit sem fetch
                    result = True # Indica sucesso da operação de escrita

    except psycopg2.Error as e:
        print(f"Erro ao executar query: {e}")
        if conn:
            conn.rollback() 
        result = None # Garante que None seja retornado em caso de erro
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return result

# --- Funções CRUD para Paciente ---

def get_all_pacientes():
    """Retorna todos os pacientes (CPF e nome) para dropdowns."""
    return execute_query("SELECT CPF, nome FROM Paciente ORDER BY nome;", fetchall=True)

def get_all_pacientes_details():
    """Retorna todos os detalhes de todos os pacientes."""
    return execute_query("SELECT * FROM Paciente ORDER BY nome;", fetchall=True)


def get_paciente_by_cpf(cpf):
    return execute_query("SELECT * FROM Paciente WHERE CPF = %s;", (cpf,), fetchone=True)

def add_paciente(cpf, nome, telefone, endereco, idade, sexo):
    query = """
        INSERT INTO Paciente (CPF, nome, telefone, endereco, idade, sexo)
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    return execute_query(query, (cpf, nome, telefone, endereco, idade, sexo), commit=True)

def update_paciente(cpf, nome, telefone, endereco, idade, sexo):
    query = """
        UPDATE Paciente
        SET nome = %s, telefone = %s, endereco = %s, idade = %s, sexo = %s
        WHERE CPF = %s;
    """
    return execute_query(query, (nome, telefone, endereco, idade, sexo, cpf), commit=True)

def delete_paciente(cpf):
    return execute_query("DELETE FROM Paciente WHERE CPF = %s;", (cpf,), commit=True)


# --- Funções CRUD para Medico ---

def get_all_medicos():
    """Retorna todos os médicos (CRM e nome) para dropdowns."""
    return execute_query("SELECT CRM, nome FROM Medico ORDER BY nome;", fetchall=True)

def get_all_medicos_details():
    """Retorna todos os detalhes de todos os médicos."""
    return execute_query("SELECT * FROM Medico ORDER BY nome;", fetchall=True)


def get_medico_by_crm(crm):
    return execute_query("SELECT * FROM Medico WHERE CRM = %s;", (crm,), fetchone=True)

def add_medico(crm, nome, telefone):
    query = "INSERT INTO Medico (CRM, nome, telefone) VALUES (%s, %s, %s);"
    return execute_query(query, (crm, nome, telefone), commit=True)

def update_medico(crm, nome, telefone):
    query = "UPDATE Medico SET nome = %s, telefone = %s WHERE CRM = %s;"
    return execute_query(query, (nome, telefone, crm), commit=True)

def delete_medico(crm):
    return execute_query("DELETE FROM Medico WHERE CRM = %s;", (crm,), commit=True)


# --- Funções CRUD para Especialidade ---

def get_all_especialidades():
    return execute_query("SELECT * FROM Especialidade ORDER BY nome;", fetchall=True)

def get_especialidade_by_id(id_especialidade):
    return execute_query("SELECT * FROM Especialidade WHERE idEspecialidade = %s;", (id_especialidade,), fetchone=True)

def add_especialidade(codigo, nome):
    query = "INSERT INTO Especialidade (codigo, nome) VALUES (%s, %s) RETURNING idEspecialidade;"
    result = execute_query(query, (codigo, nome), commit=True, fetchone=True)
    return result['idespecialidade'] if result else None


def update_especialidade(id_especialidade, codigo, nome):
    query = "UPDATE Especialidade SET codigo = %s, nome = %s WHERE idEspecialidade = %s;"
    return execute_query(query, (codigo, nome, id_especialidade), commit=True)

def delete_especialidade(id_especialidade):
    return execute_query("DELETE FROM Especialidade WHERE idEspecialidade = %s;", (id_especialidade,), commit=True)


# --- Funções CRUD para Doenca ---

def get_all_doencas(): # Usado para listar doenças para seleção
    return execute_query("SELECT idDoenca, nome FROM Doenca ORDER BY nome;", fetchall=True)

def get_doenca_by_id(id_doenca):
    return execute_query("SELECT * FROM Doenca WHERE idDoenca = %s;", (id_doenca,), fetchone=True)

def add_doenca(nome):
    query = "INSERT INTO Doenca (nome) VALUES (%s) RETURNING idDoenca;"
    result = execute_query(query, (nome,), commit=True, fetchone=True)
    return result['iddoenca'] if result else None


def update_doenca(id_doenca, nome):
    query = "UPDATE Doenca SET nome = %s WHERE idDoenca = %s;"
    return execute_query(query, (nome, id_doenca), commit=True)

def delete_doenca(id_doenca):
    return execute_query("DELETE FROM Doenca WHERE idDoenca = %s;", (id_doenca,), commit=True)

# --- Funções para Tabelas de Junção e Relacionamentos ---

def get_especialidades_for_medico(medico_crm):
    query = """
        SELECT e.idEspecialidade, e.codigo, e.nome
        FROM Especialidade e
        JOIN Medico_Especialidade me ON e.idEspecialidade = me.especialidade_idEspecialidade
        WHERE me.medico_CRM = %s
        ORDER BY e.nome;
    """
    return execute_query(query, (medico_crm,), fetchall=True)

def add_especialidade_to_medico(medico_crm, especialidade_id):
    query = "INSERT INTO Medico_Especialidade (medico_CRM, especialidade_idEspecialidade) VALUES (%s, %s);"
    try:
        return execute_query(query, (medico_crm, especialidade_id), commit=True)
    except psycopg2.IntegrityError: 
        print(f"Médico {medico_crm} já possui a especialidade {especialidade_id}.")
        return False 

def remove_especialidade_from_medico(medico_crm, especialidade_id):
    query = "DELETE FROM Medico_Especialidade WHERE medico_CRM = %s AND especialidade_idEspecialidade = %s;"
    return execute_query(query, (medico_crm, especialidade_id), commit=True)

# --- Funções CRUD para Consulta ---

def get_all_consultas_details():
    query = """
        SELECT 
            c.idConsulta, c.dataInicio, c.dataFim, c.pago, c.valorPago, c.realizada,
            p.nome AS paciente_nome, p.CPF AS paciente_CPF,
            m.nome AS medico_nome, m.CRM AS medico_CRM
        FROM Consulta c
        JOIN Paciente p ON c.paciente_CPF = p.CPF
        JOIN Medico m ON c.medico_CRM = m.CRM
        ORDER BY c.dataInicio DESC;
    """
    return execute_query(query, fetchall=True)

def get_consulta_by_id(id_consulta): # Usado para buscar detalhes da consulta para a página de diagnóstico
    query = """
        SELECT 
            c.idConsulta, c.dataInicio, c.dataFim, c.pago, c.valorPago, c.realizada,
            p.nome AS paciente_nome, p.CPF AS paciente_CPF,
            m.nome AS medico_nome, m.CRM AS medico_CRM
        FROM Consulta c
        JOIN Paciente p ON c.paciente_CPF = p.CPF
        JOIN Medico m ON c.medico_CRM = m.CRM
        WHERE c.idConsulta = %s;
    """
    return execute_query(query, (id_consulta,), fetchone=True)


def add_consulta(data_inicio, data_fim, pago, valor_pago, realizada, medico_crm, paciente_cpf):
    query = """
        INSERT INTO Consulta (dataInicio, dataFim, pago, valorPago, realizada, medico_CRM, paciente_CPF)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING idConsulta;
    """
    data_fim = data_fim if data_fim else None
    valor_pago = valor_pago if valor_pago else None

    result = execute_query(query, (data_inicio, data_fim, pago, valor_pago, realizada, medico_crm, paciente_cpf), commit=True, fetchone=True)
    return result['idconsulta'] if result else None

def update_consulta(id_consulta, data_inicio, data_fim, pago, valor_pago, realizada, medico_crm, paciente_cpf):
    query = """
        UPDATE Consulta
        SET dataInicio = %s, dataFim = %s, pago = %s, valorPago = %s, 
            realizada = %s, medico_CRM = %s, paciente_CPF = %s
        WHERE idConsulta = %s;
    """
    data_fim = data_fim if data_fim else None
    valor_pago = valor_pago if valor_pago else None
    return execute_query(query, (data_inicio, data_fim, pago, valor_pago, realizada, medico_crm, paciente_cpf, id_consulta), commit=True)

def delete_consulta(id_consulta):
    # Antes de deletar a consulta, é preciso deletar o diagnóstico associado, se houver,
    # devido à FK em Diagnostico (consulta_idConsulta) ser ON DELETE RESTRICT.
    # Ou alterar a FK para ON DELETE CASCADE no schema.
    # Por agora, vamos assumir que a lógica de deleção do diagnóstico será tratada antes na app.
    diagnostico = get_diagnostico_by_consulta_id(id_consulta)
    if diagnostico:
        delete_diagnostico(diagnostico['iddiagnostico']) # Deleta o diagnóstico e suas doenças associadas

    return execute_query("DELETE FROM Consulta WHERE idConsulta = %s;", (id_consulta,), commit=True)

# --- Funções para Agenda ---
def get_consultas_by_medico_and_date(medico_crm, data_agenda_str=None):
    params = [medico_crm]
    query_base = """
        SELECT 
            c.idConsulta, c.dataInicio, c.dataFim, c.pago, c.valorPago, c.realizada,
            p.nome AS paciente_nome, p.CPF AS paciente_CPF,
            m.nome AS medico_nome, m.CRM AS medico_CRM
        FROM Consulta c
        JOIN Paciente p ON c.paciente_CPF = p.CPF
        JOIN Medico m ON c.medico_CRM = m.CRM
        WHERE c.medico_CRM = %s
    """
    
    if data_agenda_str:
        try:
            data_agenda = datetime.datetime.strptime(data_agenda_str, '%Y-%m-%d').date()
            query_base += " AND DATE(c.dataInicio) = %s"
            params.append(data_agenda)
        except ValueError:
            print(f"Formato de data inválido: {data_agenda_str}. Mostrando todas as consultas futuras.")
            query_base += " AND c.dataInicio >= CURRENT_DATE"
    else:
        query_base += " AND c.dataInicio >= CURRENT_DATE"

    query_base += " ORDER BY c.dataInicio ASC;" 
    
    return execute_query(query_base, tuple(params), fetchall=True)

# --- Funções CRUD para Diagnostico ---

def get_diagnostico_by_consulta_id(consulta_id):
    """Retorna um diagnóstico pela ID da consulta."""
    return execute_query("SELECT * FROM Diagnostico WHERE consulta_idConsulta = %s;", (consulta_id,), fetchone=True)

def get_diagnostico_by_id(id_diagnostico):
    """Retorna um diagnóstico pelo seu ID primário."""
    return execute_query("SELECT * FROM Diagnostico WHERE idDiagnostico = %s;", (id_diagnostico,), fetchone=True)


def add_diagnostico(remedios, observacoes, tratamento, consulta_id, paciente_cpf):
    """Adiciona um novo diagnóstico."""
    query = """
        INSERT INTO Diagnostico (remediosReceitados, observacoes, tratamentoRecomendado, consulta_idConsulta, paciente_CPF)
        VALUES (%s, %s, %s, %s, %s) RETURNING idDiagnostico;
    """
    result = execute_query(query, (remedios, observacoes, tratamento, consulta_id, paciente_cpf), commit=True, fetchone=True)
    return result['iddiagnostico'] if result else None

def update_diagnostico(id_diagnostico, remedios, observacoes, tratamento):
    """Atualiza um diagnóstico existente."""
    query = """
        UPDATE Diagnostico 
        SET remediosReceitados = %s, observacoes = %s, tratamentoRecomendado = %s
        WHERE idDiagnostico = %s;
    """
    return execute_query(query, (remedios, observacoes, tratamento, id_diagnostico), commit=True)

def delete_diagnostico(id_diagnostico):
    """Deleta um diagnóstico. Também remove associações em Diagnostico_Doenca devido ao ON DELETE CASCADE."""
    # A tabela Diagnostico_Doenca tem ON DELETE CASCADE para diagnostico_idDiagnostico,
    # então as associações de doenças serão removidas automaticamente.
    return execute_query("DELETE FROM Diagnostico WHERE idDiagnostico = %s;", (id_diagnostico,), commit=True)


# --- Funções para Diagnostico_Doenca ---

def get_doencas_for_diagnostico(id_diagnostico):
    """Retorna todas as doenças associadas a um diagnóstico."""
    query = """
        SELECT d.idDoenca, d.nome
        FROM Doenca d
        JOIN Diagnostico_Doenca dd ON d.idDoenca = dd.doenca_idDoenca
        WHERE dd.diagnostico_idDiagnostico = %s
        ORDER BY d.nome;
    """
    return execute_query(query, (id_diagnostico,), fetchall=True)

def add_doenca_to_diagnostico(id_diagnostico, id_doenca):
    """Associa uma doença a um diagnóstico."""
    query = "INSERT INTO Diagnostico_Doenca (diagnostico_idDiagnostico, doenca_idDoenca) VALUES (%s, %s);"
    try:
        return execute_query(query, (id_diagnostico, id_doenca), commit=True)
    except psycopg2.IntegrityError: # Caso a associação já exista
        print(f"Diagnóstico {id_diagnostico} já está associado à doença {id_doenca}.")
        return False # Indica que não foi uma nova inserção

def remove_doenca_from_diagnostico(id_diagnostico, id_doenca):
    """Remove a associação de uma doença de um diagnóstico."""
    query = "DELETE FROM Diagnostico_Doenca WHERE diagnostico_idDiagnostico = %s AND doenca_idDoenca = %s;"
    return execute_query(query, (id_diagnostico, id_doenca), commit=True)

def set_doencas_for_diagnostico(id_diagnostico, lista_ids_doencas):
    """
    Define a lista de doenças para um diagnóstico.
    Remove as antigas não presentes na nova lista e adiciona as novas.
    """
    # 1. Buscar doenças atuais
    doencas_atuais_dicts = get_doencas_for_diagnostico(id_diagnostico)
    ids_doencas_atuais = {d['iddoenca'] for d in doencas_atuais_dicts} if doencas_atuais_dicts else set()
    
    ids_doencas_novas = set(lista_ids_doencas)

    # 2. Doenças para remover
    ids_para_remover = ids_doencas_atuais - ids_doencas_novas
    for id_doenca_remover in ids_para_remover:
        remove_doenca_from_diagnostico(id_diagnostico, id_doenca_remover)

    # 3. Doenças para adicionar
    ids_para_adicionar = ids_doencas_novas - ids_doencas_atuais
    for id_doenca_adicionar in ids_para_adicionar:
        add_doenca_to_diagnostico(id_diagnostico, id_doenca_adicionar)
    
    return True


if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        print("Conexão com o banco de dados bem-sucedida!")
        conn.close()
    else:
        print("Falha na conexão com o banco de dados.")
