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
            conn.rollback() 
        result = None 
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
    """Retorna um paciente específico pelo CPF."""
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

def get_all_doencas():
    return execute_query("SELECT * FROM Doenca ORDER BY nome;", fetchall=True)

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

def get_consulta_by_id(id_consulta):
    return execute_query("SELECT * FROM Consulta WHERE idConsulta = %s;", (id_consulta,), fetchone=True)

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
    return execute_query("DELETE FROM Consulta WHERE idConsulta = %s;", (id_consulta,), commit=True)

# --- Funções para Agenda ---
def get_consultas_by_medico_and_date(medico_crm, data_agenda_str=None):
    """
    Retorna as consultas de um médico específico, opcionalmente filtradas por uma data específica.
    Se data_agenda_str não for fornecida, retorna todas as consultas futuras do médico.
    """
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
            # Converte a string da data para objeto date
            data_agenda = datetime.datetime.strptime(data_agenda_str, '%Y-%m-%d').date()
            # Filtra para consultas que iniciam no dia especificado
            query_base += " AND DATE(c.dataInicio) = %s"
            params.append(data_agenda)
        except ValueError:
            print(f"Formato de data inválido: {data_agenda_str}. Mostrando todas as consultas futuras.")
            # Se a data for inválida, comporta-se como se nenhuma data fosse fornecida
            query_base += " AND c.dataInicio >= CURRENT_DATE" # Mostra futuras se data inválida
    else:
        # Se nenhuma data for fornecida, mostra todas as consultas futuras (ou do dia atual em diante)
        query_base += " AND c.dataInicio >= CURRENT_DATE"

    query_base += " ORDER BY c.dataInicio ASC;" # Ordena pela data de início
    
    return execute_query(query_base, tuple(params), fetchall=True)


if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        print("Conexão com o banco de dados bem-sucedida!")
        conn.close()
    else:
        print("Falha na conexão com o banco de dados.")
