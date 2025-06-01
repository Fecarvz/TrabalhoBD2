-- Tabelas independentes primeiro (ou com menos dependências)

CREATE TABLE Paciente (
    CPF VARCHAR(11) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    endereco TEXT,
    idade INTEGER CHECK (idade >= 0),
    sexo VARCHAR(15) -- Ex: 'Masculino', 'Feminino', 'Outro'
);

CREATE INDEX idx_paciente_nome ON Paciente(nome);

CREATE TABLE Medico (
    CRM VARCHAR(20) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20)
);

CREATE INDEX idx_medico_nome ON Medico(nome);

CREATE TABLE Especialidade (
    idEspecialidade SERIAL PRIMARY KEY, -- Corresponde a "Indice" no diagrama
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL
);

CREATE INDEX idx_especialidade_nome ON Especialidade(nome);

CREATE TABLE Doenca (
    idDoenca SERIAL PRIMARY KEY,
    nome VARCHAR(255) UNIQUE NOT NULL
);

CREATE INDEX idx_doenca_nome ON Doenca(nome);

-- Tabelas com dependências

CREATE TABLE Agenda (
    idAgenda SERIAL PRIMARY KEY,
    diaSemana VARCHAR(20) NOT NULL, -- Ex: 'Segunda-feira', 'Terça-feira', etc.
    horaInicio TIME NOT NULL,
    horaFim TIME NOT NULL,
    medico_CRM VARCHAR(20) NOT NULL,
    CONSTRAINT fk_agenda_medico FOREIGN KEY (medico_CRM) REFERENCES Medico(CRM) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_agenda_medico_CRM ON Agenda(medico_CRM);
CREATE INDEX idx_agenda_diaSemana_horaInicio ON Agenda(diaSemana, horaInicio);

CREATE TABLE Consulta (
    idConsulta SERIAL PRIMARY KEY,
    dataInicio TIMESTAMP NOT NULL,
    dataFim TIMESTAMP,
    pago BOOLEAN DEFAULT FALSE NOT NULL,
    valorPago DECIMAL(10, 2),
    realizada BOOLEAN DEFAULT FALSE NOT NULL,
    medico_CRM VARCHAR(20) NOT NULL,
    paciente_CPF VARCHAR(11) NOT NULL,
    CONSTRAINT fk_consulta_medico FOREIGN KEY (medico_CRM) REFERENCES Medico(CRM) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_consulta_paciente FOREIGN KEY (paciente_CPF) REFERENCES Paciente(CPF) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_consulta_medico_CRM ON Consulta(medico_CRM);
CREATE INDEX idx_consulta_paciente_CPF ON Consulta(paciente_CPF);
CREATE INDEX idx_consulta_dataInicio ON Consulta(dataInicio);

CREATE TABLE Diagnostico (
    idDiagnostico SERIAL PRIMARY KEY,
    remediosReceitados TEXT,
    observacoes TEXT,
    tratamentoRecomendado TEXT,
    consulta_idConsulta INTEGER UNIQUE NOT NULL, -- Relação (1,1) com Consulta ("RealizadoEm")
    paciente_CPF VARCHAR(11) NOT NULL, -- Relação (1,1) Diagnostico -> (0,n) Paciente ("TemHistorico")
    CONSTRAINT fk_diagnostico_consulta FOREIGN KEY (consulta_idConsulta) REFERENCES Consulta(idConsulta) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_diagnostico_paciente FOREIGN KEY (paciente_CPF) REFERENCES Paciente(CPF) ON DELETE RESTRICT ON UPDATE CASCADE
    -- Observação: Pode ser necessário um TRIGGER ou lógica de aplicação para garantir que
    -- o paciente_CPF em Diagnostico seja o mesmo paciente_CPF da Consulta referenciada.
);

CREATE INDEX idx_diagnostico_consulta_idConsulta ON Diagnostico(consulta_idConsulta);
CREATE INDEX idx_diagnostico_paciente_CPF ON Diagnostico(paciente_CPF);

-- Tabelas de Junção (Muitos-para-Muitos)

CREATE TABLE Medico_Especialidade (
    medico_CRM VARCHAR(20) NOT NULL,
    especialidade_idEspecialidade INTEGER NOT NULL,
    CONSTRAINT pk_medico_especialidade PRIMARY KEY (medico_CRM, especialidade_idEspecialidade),
    CONSTRAINT fk_me_medico FOREIGN KEY (medico_CRM) REFERENCES Medico(CRM) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_me_especialidade FOREIGN KEY (especialidade_idEspecialidade) REFERENCES Especialidade(idEspecialidade) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_me_medico_CRM ON Medico_Especialidade(medico_CRM);
CREATE INDEX idx_me_especialidade_idEspecialidade ON Medico_Especialidade(especialidade_idEspecialidade);

CREATE TABLE Diagnostico_Doenca (
    diagnostico_idDiagnostico INTEGER NOT NULL,
    doenca_idDoenca INTEGER NOT NULL,
    CONSTRAINT pk_diagnostico_doenca PRIMARY KEY (diagnostico_idDiagnostico, doenca_idDoenca),
    CONSTRAINT fk_dd_diagnostico FOREIGN KEY (diagnostico_idDiagnostico) REFERENCES Diagnostico(idDiagnostico) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_dd_doenca FOREIGN KEY (doenca_idDoenca) REFERENCES Doenca(idDoenca) ON DELETE RESTRICT ON UPDATE CASCADE
    -- A cardinalidade (1,1) do lado do Diagnóstico na relação "Identifica" (um diagnóstico DEVE identificar pelo menos uma doença)
    -- precisaria ser tratada na lógica da aplicação ou com constraints mais complexas (Assertions, Triggers).
);

CREATE INDEX idx_dd_diagnostico_idDiagnostico ON Diagnostico_Doenca(diagnostico_idDiagnostico);
CREATE INDEX idx_dd_doenca_idDoenca ON Diagnostico_Doenca(doenca_idDoenca);
