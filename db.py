import psycopg2
import psycopg2.extras # Para usar RealDictCursor

# --- IMPORTANTE: Configure suas credenciais do banco de dados aqui ---
DB_NAME = "teste"  # Nome do seu banco de dados
DB_USER = "felipe"    # Seu usuário do PostgreSQL
DB_PASSWORD = "102030" # Sua senha do PostgreSQL
DB_HOST = "192.168.1.15"   # Geralmente 'localhost'
DB_PORT = "5432"        # Porta padrão do PostgreSQL

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

    Args:
        query (str): A string da query SQL.
        params (tuple, optional): Parâmetros para a query. Defaults to None.
        fetchone (bool, optional): True para retornar uma única linha. Defaults to False.
        fetchall (bool, optional): True para retornar todas as linhas. Defaults to False.
        commit (bool, optional): True para commitar a transação (INSERT, UPDATE, DELETE). Defaults to False.

    Returns:
        tuple or list or None: Resultado da query ou None em caso de erro.
    """
    conn = None
    cur = None
    result = None
    try:
        conn = get_db_connection()
        if conn:
            # Usar RealDictCursor para obter resultados como dicionários
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(query, params)

            if fetchone:
                result = cur.fetchone()
            elif fetchall:
                result = cur.fetchall()

            if commit:
                conn.commit()
    except psycopg2.Error as e:
        print(f"Erro ao executar query: {e}")
        if conn:
            conn.rollback() # Desfaz a transação em caso de erro
        result = None # Garante que None seja retornado em caso de erro
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return result

# --- Funções CRUD para Paciente ---

def get_all_pacientes():
    """Retorna todos os pacientes do banco de dados."""
    return execute_query("SELECT CPF, nome FROM Paciente ORDER BY nome;", fetchall=True) # Modificado para pegar só CPF e nome para dropdowns

def get_paciente_by_cpf(cpf):
    """Retorna um paciente específico pelo CPF."""
    return execute_query("SELECT * FROM Paciente WHERE CPF = %s;", (cpf,), fetchone=True)

def add_paciente(cpf, nome, telefone, endereco, idade, sexo):
    """Adiciona um novo paciente ao banco de dados."""
    query = """
        INSERT INTO Paciente (CPF, nome, telefone, endereco, idade, sexo)
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    return execute_query(query, (cpf, nome, telefone, endereco, idade, sexo), commit=True)

def update_paciente(cpf, nome, telefone, endereco, idade, sexo):
    """Atualiza os dados de um paciente existente."""
    query = """
        UPDATE Paciente
        SET nome = %s, telefone = %s, endereco = %s, idade = %s, sexo = %s
        WHERE CPF = %s;
    """
    return execute_query(query, (nome, telefone, endereco, idade, sexo, cpf), commit=True)

def delete_paciente(cpf):
    """Remove um paciente do banco de dados."""
    return execute_query("DELETE FROM Paciente WHERE CPF = %s;", (cpf,), commit=True)


# --- Funções CRUD para Medico ---

def get_all_medicos():
    """Retorna todos os médicos do banco de dados."""
    return execute_query("SELECT CRM, nome FROM Medico ORDER BY nome;", fetchall=True) # Modificado para pegar só CRM e nome para dropdowns

def get_medico_by_crm(crm):
    """Retorna um médico específico pelo CRM."""
    return execute_query("SELECT * FROM Medico WHERE CRM = %s;", (crm,), fetchone=True)

def add_medico(crm, nome, telefone):
    """Adiciona um novo médico ao banco de dados."""
    query = "INSERT INTO Medico (CRM, nome, telefone) VALUES (%s, %s, %s);"
    return execute_query(query, (crm, nome, telefone), commit=True)

def update_medico(crm, nome, telefone):
    """Atualiza os dados de um médico existente."""
    query = "UPDATE Medico SET nome = %s, telefone = %s WHERE CRM = %s;"
    return execute_query(query, (nome, telefone, crm), commit=True)

def delete_medico(crm):
    """Remove um médico do banco de dados."""
    return execute_query("DELETE FROM Medico WHERE CRM = %s;", (crm,), commit=True)


# --- Funções CRUD para Especialidade ---

def get_all_especialidades():
    """Retorna todas as especialidades."""
    return execute_query("SELECT * FROM Especialidade ORDER BY nome;", fetchall=True)

def get_especialidade_by_id(id_especialidade):
    """Retorna uma especialidade pelo ID."""
    return execute_query("SELECT * FROM Especialidade WHERE idEspecialidade = %s;", (id_especialidade,), fetchone=True)

def add_especialidade(codigo, nome):
    """Adiciona uma nova especialidade."""
    query = "INSERT INTO Especialidade (codigo, nome) VALUES (%s, %s) RETURNING idEspecialidade;"
    result = execute_query(query, (codigo, nome), commit=True, fetchone=True)
    return result['idespecialidade'] if result else None


def update_especialidade(id_especialidade, codigo, nome):
    """Atualiza uma especialidade."""
    query = "UPDATE Especialidade SET codigo = %s, nome = %s WHERE idEspecialidade = %s;"
    return execute_query(query, (codigo, nome, id_especialidade), commit=True)

def delete_especialidade(id_especialidade):
    """Remove uma especialidade."""
    return execute_query("DELETE FROM Especialidade WHERE idEspecialidade = %s;", (id_especialidade,), commit=True)


# --- Funções CRUD para Doenca ---

def get_all_doencas():
    """Retorna todas as doenças."""
    return execute_query("SELECT * FROM Doenca ORDER BY nome;", fetchall=True)

def get_doenca_by_id(id_doenca):
    """Retorna uma doença pelo ID."""
    return execute_query("SELECT * FROM Doenca WHERE idDoenca = %s;", (id_doenca,), fetchone=True)

def add_doenca(nome):
    """Adiciona uma nova doença."""
    query = "INSERT INTO Doenca (nome) VALUES (%s) RETURNING idDoenca;"
    result = execute_query(query, (nome,), commit=True, fetchone=True)
    return result['iddoenca'] if result else None


def update_doenca(id_doenca, nome):
    """Atualiza uma doença."""
    query = "UPDATE Doenca SET nome = %s WHERE idDoenca = %s;"
    return execute_query(query, (nome, id_doenca), commit=True)

def delete_doenca(id_doenca):
    """Remove uma doença."""
    return execute_query("DELETE FROM Doenca WHERE idDoenca = %s;", (id_doenca,), commit=True)

# --- Funções para Tabelas de Junção e Relacionamentos ---

def get_especialidades_for_medico(medico_crm):
    """Retorna as especialidades de um médico específico."""
    query = """
        SELECT e.idEspecialidade, e.codigo, e.nome
        FROM Especialidade e
        JOIN Medico_Especialidade me ON e.idEspecialidade = me.especialidade_idEspecialidade
        WHERE me.medico_CRM = %s
        ORDER BY e.nome;
    """
    return execute_query(query, (medico_crm,), fetchall=True)

def add_especialidade_to_medico(medico_crm, especialidade_id):
    """Associa uma especialidade a um médico."""
    query = "INSERT INTO Medico_Especialidade (medico_CRM, especialidade_idEspecialidade) VALUES (%s, %s);"
    try:
        return execute_query(query, (medico_crm, especialidade_id), commit=True)
    except psycopg2.IntegrityError: 
        print(f"Médico {medico_crm} já possui a especialidade {especialidade_id}.")
        return False 

def remove_especialidade_from_medico(medico_crm, especialidade_id):
    """Remove a associação de uma especialidade de um médico."""
    query = "DELETE FROM Medico_Especialidade WHERE medico_CRM = %s AND especialidade_idEspecialidade = %s;"
    return execute_query(query, (medico_crm, especialidade_id), commit=True)

# --- Funções CRUD para Consulta ---

def get_all_consultas_details():
    """Retorna todas as consultas com detalhes do paciente e médico."""
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

def get_consulta_by_id(id_consulta):
    """Retorna uma consulta específica pelo ID."""
    return execute_query("SELECT * FROM Consulta WHERE idConsulta = %s;", (id_consulta,), fetchone=True)

def add_consulta(data_inicio, data_fim, pago, valor_pago, realizada, medico_crm, paciente_cpf):
    """Adiciona uma nova consulta ao banco de dados."""
    query = """
        INSERT INTO Consulta (dataInicio, dataFim, pago, valorPago, realizada, medico_CRM, paciente_CPF)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING idConsulta;
    """
    # Convertendo strings vazias para None para campos opcionais
    data_fim = data_fim if data_fim else None
    valor_pago = valor_pago if valor_pago else None

    result = execute_query(query, (data_inicio, data_fim, pago, valor_pago, realizada, medico_crm, paciente_cpf), commit=True, fetchone=True)
    return result['idconsulta'] if result else None

def update_consulta(id_consulta, data_inicio, data_fim, pago, valor_pago, realizada, medico_crm, paciente_cpf):
    """Atualiza os dados de uma consulta existente."""
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
    """Remove uma consulta do banco de dados."""
    # Cuidado: ON DELETE RESTRICT na FK para Diagnostico pode impedir a deleção.
    return execute_query("DELETE FROM Consulta WHERE idConsulta = %s;", (id_consulta,), commit=True)


if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        print("Conexão com o banco de dados bem-sucedida!")
        conn.close()
    else:
        print("Falha na conexão com o banco de dados.")
