from flask import Flask, render_template, request, redirect, url_for, flash
import db # Importa o módulo db.py
import datetime # Importar o módulo datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui' # Necessário para flash messages

# Processador de contexto para injetar variáveis em todos os templates
@app.context_processor
def inject_now():
    """Injeta a data e hora atuais (ou apenas o ano) no contexto do template."""
    return {'current_year': datetime.datetime.now().year}

# --- Rotas Principais ---
@app.route('/')
def index():
    """Página inicial da aplicação."""
    return render_template('index.html')

# --- Rotas para Pacientes ---
@app.route('/pacientes')
def pacientes_list():
    """Exibe a lista de todos os pacientes."""
    pacientes = db.get_all_pacientes() # Agora retorna apenas CPF e nome
    # Para a lista completa, precisaríamos de outra função ou ajustar get_all_pacientes
    # Por ora, vamos buscar todos os dados para a lista de pacientes.
    # Idealmente, teríamos get_all_pacientes_summary() e get_all_pacientes_details()
    # Mas para simplificar, vamos rebuscar todos os dados aqui se necessário para a view.
    # No entanto, o template pacientes_list.html usa os campos completos.
    # Vamos criar uma função get_all_pacientes_details() em db.py ou ajustar a existente.
    # Por enquanto, vou assumir que get_all_pacientes() retorna todos os campos para a lista.
    # Para evitar confusão, vou reverter a mudança em db.py para get_all_pacientes e get_all_medicos
    # e criar funções separadas para pegar apenas nome/id para formulários.
    # Esta é uma decisão de design. Para este exemplo, manterei simples e buscarei todos os dados.
    # Se a performance fosse crítica, otimizaríamos as queries.
    
    # Revertendo a lógica para get_all_pacientes e get_all_medicos em db.py para buscar todos os campos.
    # As funções para formulários serão get_pacientes_for_select() e get_medicos_for_select().
    # No entanto, para manter o código já fornecido consistente, vou usar o que já está lá
    # e ajustar o template pacientes_list se necessário, ou assumir que o db.py foi ajustado.
    # Assumindo que db.get_all_pacientes() retorna todos os campos necessários para pacientes_list.html.
    
    pacientes_data = db.execute_query("SELECT * FROM Paciente ORDER BY nome;", fetchall=True) # Usando execute_query diretamente para clareza
    if pacientes_data is None: 
        flash('Erro ao buscar pacientes do banco de dados.', 'error')
        pacientes_data = []
    return render_template('pacientes/pacientes_list.html', pacientes=pacientes_data)


@app.route('/pacientes/add', methods=['GET', 'POST'])
def paciente_add():
    """Adiciona um novo paciente."""
    if request.method == 'POST':
        cpf = request.form['cpf']
        nome = request.form['nome']
        telefone = request.form.get('telefone') 
        endereco = request.form.get('endereco')
        idade_str = request.form.get('idade')
        sexo = request.form.get('sexo')

        if not cpf or not nome:
            flash('CPF e Nome são campos obrigatórios!', 'error')
            return render_template('pacientes/paciente_form.html', form_action='Adicionar')

        if db.get_paciente_by_cpf(cpf):
            flash(f'Paciente com CPF {cpf} já existe!', 'error')
            return render_template('pacientes/paciente_form.html', paciente=request.form, form_action='Adicionar')

        try:
            idade = int(idade_str) if idade_str and idade_str.strip() else None
            if idade is not None and idade < 0:
                flash('Idade não pode ser negativa.', 'error')
                return render_template('pacientes/paciente_form.html', paciente=request.form, form_action='Adicionar')
        except ValueError:
            flash('Idade deve ser um número.', 'error')
            return render_template('pacientes/paciente_form.html', paciente=request.form, form_action='Adicionar')

        if db.add_paciente(cpf, nome, telefone, endereco, idade, sexo) is not None:
            flash('Paciente adicionado com sucesso!', 'success')
            return redirect(url_for('pacientes_list'))
        else:
            flash('Erro ao adicionar paciente. Verifique os logs do servidor.', 'error')
            return render_template('pacientes/paciente_form.html', paciente=request.form, form_action='Adicionar')

    return render_template('pacientes/paciente_form.html', form_action='Adicionar')

@app.route('/pacientes/edit/<string:cpf>', methods=['GET', 'POST'])
def paciente_edit(cpf):
    """Edita um paciente existente."""
    paciente = db.get_paciente_by_cpf(cpf)
    if not paciente:
        flash('Paciente não encontrado!', 'error')
        return redirect(url_for('pacientes_list'))

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form.get('telefone')
        endereco = request.form.get('endereco')
        idade_str = request.form.get('idade')
        sexo = request.form.get('sexo')

        if not nome: 
            flash('Nome é obrigatório!', 'error')
            return render_template('pacientes/paciente_form.html', paciente=paciente, form_action='Editar', cpf_original=cpf)

        try:
            idade = int(idade_str) if idade_str and idade_str.strip() else None
            if idade is not None and idade < 0:
                flash('Idade não pode ser negativa.', 'error')
                # Passar os dados atuais do formulário de volta, não o 'paciente' original do GET
                form_data = dict(request.form)
                form_data['CPF'] = cpf # Adicionar CPF pois ele é readonly no form
                return render_template('pacientes/paciente_form.html', paciente=form_data, cpf_original=cpf, form_action='Editar')
        except ValueError:
            flash('Idade deve ser um número.', 'error')
            form_data = dict(request.form)
            form_data['CPF'] = cpf
            return render_template('pacientes/paciente_form.html', paciente=form_data, cpf_original=cpf, form_action='Editar')


        if db.update_paciente(cpf, nome, telefone, endereco, idade, sexo) is not None:
            flash('Paciente atualizado com sucesso!', 'success')
            return redirect(url_for('pacientes_list'))
        else:
            flash('Erro ao atualizar paciente.', 'error')
            current_form_data = dict(request.form)
            current_form_data['CPF'] = cpf
            return render_template('pacientes/paciente_form.html', paciente=current_form_data, cpf_original=cpf, form_action='Editar')

    return render_template('pacientes/paciente_form.html', paciente=paciente, cpf_original=cpf, form_action='Editar')


@app.route('/pacientes/delete/<string:cpf>', methods=['POST'])
def paciente_delete(cpf):
    paciente = db.get_paciente_by_cpf(cpf)
    if not paciente:
        flash('Paciente não encontrado!', 'error')
        return redirect(url_for('pacientes_list'))

    if db.delete_paciente(cpf) is not None:
        flash('Paciente removido com sucesso!', 'success')
    else:
        flash('Erro ao remover paciente. Verifique se há consultas ou diagnósticos associados (ON DELETE RESTRICT).', 'error')
    return redirect(url_for('pacientes_list'))


# --- Rotas para Médicos ---
@app.route('/medicos')
def medicos_list():
    medicos_data = db.execute_query("SELECT * FROM Medico ORDER BY nome;", fetchall=True)
    if medicos_data is None:
        flash('Erro ao buscar médicos do banco de dados.', 'error')
        medicos_data = []
    return render_template('medicos/medicos_list.html', medicos=medicos_data)

@app.route('/medicos/add', methods=['GET', 'POST'])
def medico_add():
    if request.method == 'POST':
        crm = request.form['crm']
        nome = request.form['nome']
        telefone = request.form.get('telefone')

        if not crm or not nome:
            flash('CRM e Nome são campos obrigatórios!', 'error')
            return render_template('medicos/medico_form.html', form_action='Adicionar')

        if db.get_medico_by_crm(crm):
            flash(f'Médico com CRM {crm} já existe!', 'error')
            return render_template('medicos/medico_form.html', medico=request.form, form_action='Adicionar')

        if db.add_medico(crm, nome, telefone) is not None:
            flash('Médico adicionado com sucesso!', 'success')
            return redirect(url_for('medicos_list'))
        else:
            flash('Erro ao adicionar médico.', 'error')
            return render_template('medicos/medico_form.html', medico=request.form, form_action='Adicionar')

    return render_template('medicos/medico_form.html', form_action='Adicionar')

@app.route('/medicos/edit/<string:crm>', methods=['GET', 'POST'])
def medico_edit(crm):
    medico = db.get_medico_by_crm(crm)
    if not medico:
        flash('Médico não encontrado!', 'error')
        return redirect(url_for('medicos_list'))

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form.get('telefone')

        if not nome: 
            flash('Nome é obrigatório!', 'error')
            return render_template('medicos/medico_form.html', medico=medico, form_action='Editar', crm_original=crm)

        if db.update_medico(crm, nome, telefone) is not None:
            flash('Médico atualizado com sucesso!', 'success')
            return redirect(url_for('medicos_list'))
        else:
            flash('Erro ao atualizar médico.', 'error')
            current_form_data = dict(request.form)
            current_form_data['CRM'] = crm
            return render_template('medicos/medico_form.html', medico=current_form_data, crm_original=crm, form_action='Editar')

    return render_template('medicos/medico_form.html', medico=medico, crm_original=crm, form_action='Editar')

@app.route('/medicos/delete/<string:crm>', methods=['POST'])
def medico_delete(crm):
    medico = db.get_medico_by_crm(crm)
    if not medico:
        flash('Médico não encontrado!', 'error')
        return redirect(url_for('medicos_list'))

    if db.delete_medico(crm) is not None:
        flash('Médico removido com sucesso!', 'success')
    else:
        flash('Erro ao remover médico. Verifique se há agendas ou consultas associadas (ON DELETE RESTRICT).', 'error')
    return redirect(url_for('medicos_list'))

# --- Rotas para Especialidades ---
@app.route('/especialidades')
def especialidades_list():
    especialidades = db.get_all_especialidades()
    if especialidades is None:
        flash('Erro ao buscar especialidades.', 'error')
        especialidades = []
    return render_template('especialidades/especialidades_list.html', especialidades=especialidades)

@app.route('/especialidades/add', methods=['GET', 'POST'])
def especialidade_add():
    if request.method == 'POST':
        codigo = request.form['codigo']
        nome = request.form['nome']

        if not codigo or not nome:
            flash('Código e Nome são obrigatórios!', 'error')
            return render_template('especialidades/especialidade_form.html', form_action='Adicionar')
        
        new_id = db.add_especialidade(codigo, nome)
        if new_id:
            flash('Especialidade adicionada com sucesso!', 'success')
            return redirect(url_for('especialidades_list'))
        else:
            flash('Erro ao adicionar especialidade. Verifique se o código já existe ou houve outro erro.', 'error')
            return render_template('especialidades/especialidade_form.html', especialidade=request.form, form_action='Adicionar')

    return render_template('especialidades/especialidade_form.html', form_action='Adicionar')

@app.route('/especialidades/edit/<int:id_especialidade>', methods=['GET', 'POST'])
def especialidade_edit(id_especialidade):
    especialidade = db.get_especialidade_by_id(id_especialidade)
    if not especialidade:
        flash('Especialidade não encontrada!', 'error')
        return redirect(url_for('especialidades_list'))

    if request.method == 'POST':
        codigo = request.form['codigo']
        nome = request.form['nome']

        if not codigo or not nome:
            flash('Código e Nome são obrigatórios!', 'error')
            return render_template('especialidades/especialidade_form.html', especialidade=especialidade, form_action='Editar')

        if db.update_especialidade(id_especialidade, codigo, nome) is not None:
            flash('Especialidade atualizada com sucesso!', 'success')
            return redirect(url_for('especialidades_list'))
        else:
            flash('Erro ao atualizar especialidade. Verifique se o novo código já existe.', 'error')
            current_form_data = dict(request.form)
            current_form_data['idEspecialidade'] = id_especialidade
            return render_template('especialidades/especialidade_form.html', especialidade=current_form_data, form_action='Editar')

    return render_template('especialidades/especialidade_form.html', especialidade=especialidade, form_action='Editar')

@app.route('/especialidades/delete/<int:id_especialidade>', methods=['POST'])
def especialidade_delete(id_especialidade):
    especialidade = db.get_especialidade_by_id(id_especialidade)
    if not especialidade:
        flash('Especialidade não encontrada!', 'error')
        return redirect(url_for('especialidades_list'))

    if db.delete_especialidade(id_especialidade) is not None:
        flash('Especialidade removida com sucesso!', 'success')
    else:
        flash('Erro ao remover especialidade. Verifique se está associada a algum médico (ON DELETE CASCADE deve cuidar disso, mas verifique).', 'error')
    return redirect(url_for('especialidades_list'))

# --- Rotas para Doenças ---
@app.route('/doencas')
def doencas_list():
    doencas = db.get_all_doencas()
    if doencas is None:
        flash('Erro ao buscar doenças.', 'error')
        doencas = []
    return render_template('doencas/doencas_list.html', doencas=doencas)

@app.route('/doencas/add', methods=['GET', 'POST'])
def doenca_add():
    if request.method == 'POST':
        nome = request.form['nome']
        if not nome:
            flash('Nome é obrigatório!', 'error')
            return render_template('doencas/doenca_form.html', form_action='Adicionar')

        new_id = db.add_doenca(nome)
        if new_id:
            flash('Doença adicionada com sucesso!', 'success')
            return redirect(url_for('doencas_list'))
        else:
            flash('Erro ao adicionar doença. Verifique se o nome já existe ou houve outro erro.', 'error')
            return render_template('doencas/doenca_form.html', doenca=request.form, form_action='Adicionar')
    return render_template('doencas/doenca_form.html', form_action='Adicionar')

@app.route('/doencas/edit/<int:id_doenca>', methods=['GET', 'POST'])
def doenca_edit(id_doenca):
    doenca = db.get_doenca_by_id(id_doenca)
    if not doenca:
        flash('Doença não encontrada!', 'error')
        return redirect(url_for('doencas_list'))

    if request.method == 'POST':
        nome = request.form['nome']
        if not nome:
            flash('Nome é obrigatório!', 'error')
            return render_template('doencas/doenca_form.html', doenca=doenca, form_action='Editar')

        if db.update_doenca(id_doenca, nome) is not None:
            flash('Doença atualizada com sucesso!', 'success')
            return redirect(url_for('doencas_list'))
        else:
            flash('Erro ao atualizar doença. Verifique se o novo nome já existe.', 'error')
            current_form_data = dict(request.form)
            current_form_data['idDoenca'] = id_doenca
            return render_template('doencas/doenca_form.html', doenca=current_form_data, form_action='Editar')
    return render_template('doencas/doenca_form.html', doenca=doenca, form_action='Editar')

@app.route('/doencas/delete/<int:id_doenca>', methods=['POST'])
def doenca_delete(id_doenca):
    doenca = db.get_doenca_by_id(id_doenca)
    if not doenca:
        flash('Doença não encontrada!', 'error')
        return redirect(url_for('doencas_list'))

    if db.delete_doenca(id_doenca) is not None:
        flash('Doença removida com sucesso!', 'success')
    else:
        flash('Erro ao remover doença. Verifique se está associada a algum diagnóstico (ON DELETE RESTRICT).', 'error')
    return redirect(url_for('doencas_list'))


# --- Rotas para Medico_Especialidade ---
@app.route('/medicos/<string:crm>/especialidades', methods=['GET', 'POST'])
def medico_manage_especialidades(crm):
    medico = db.get_medico_by_crm(crm)
    if not medico:
        flash('Médico não encontrado!', 'error')
        return redirect(url_for('medicos_list'))

    if request.method == 'POST':
        especialidade_id_str = request.form.get('especialidade_id')
        action = request.form.get('action') 

        if not especialidade_id_str:
            flash('Selecione uma especialidade.', 'error')
        else:
            try:
                especialidade_id = int(especialidade_id_str)
                if action == 'add':
                    if db.add_especialidade_to_medico(crm, especialidade_id):
                        flash('Especialidade associada com sucesso!', 'success')
                    else:
                        flash('Erro ao associar especialidade. Pode já estar associada.', 'warning')
                elif action == 'remove':
                    if db.remove_especialidade_from_medico(crm, especialidade_id):
                        flash('Especialidade desassociada com sucesso!', 'success')
                    else:
                        flash('Erro ao desassociar especialidade.', 'error')
            except ValueError:
                flash('ID de especialidade inválido.', 'error')
        return redirect(url_for('medico_manage_especialidades', crm=crm))

    medico_especialidades = db.get_especialidades_for_medico(crm)
    todas_especialidades = db.get_all_especialidades()
    
    ids_medico_especialidades = {e['idespecialidade'] for e in medico_especialidades} if medico_especialidades else set()
    especialidades_disponiveis = [
        e for e in todas_especialidades if e['idespecialidade'] not in ids_medico_especialidades
    ] if todas_especialidades else []

    return render_template('medicos/medico_especialidades.html',
                           medico=medico,
                           medico_especialidades=medico_especialidades or [],
                           especialidades_disponiveis=especialidades_disponiveis)

# --- Rotas para Consultas ---
@app.route('/consultas')
def consultas_list():
    """Exibe a lista de todas as consultas."""
    consultas = db.get_all_consultas_details()
    if consultas is None:
        flash('Erro ao buscar consultas.', 'error')
        consultas = []
    return render_template('consultas/consultas_list.html', consultas=consultas)

@app.route('/consultas/add', methods=['GET', 'POST'])
def consulta_add():
    """Adiciona uma nova consulta."""
    pacientes = db.get_all_pacientes() # Para o dropdown de pacientes
    medicos = db.get_all_medicos()     # Para o dropdown de médicos

    if request.method == 'POST':
        data_inicio_str = request.form.get('dataInicio')
        data_fim_str = request.form.get('dataFim')
        pago = 'pago' in request.form # Checkbox
        valor_pago_str = request.form.get('valorPago')
        realizada = 'realizada' in request.form # Checkbox
        medico_crm = request.form.get('medico_CRM')
        paciente_cpf = request.form.get('paciente_CPF')

        if not data_inicio_str or not medico_crm or not paciente_cpf:
            flash('Data de Início, Médico e Paciente são obrigatórios!', 'error')
            return render_template('consultas/consulta_form.html', 
                                   form_action='Adicionar', 
                                   pacientes=pacientes, 
                                   medicos=medicos,
                                   consulta=request.form) # Repopular form com dados atuais
        
        # Conversão e validação de data/hora
        try:
            data_inicio = datetime.datetime.fromisoformat(data_inicio_str)
            data_fim = datetime.datetime.fromisoformat(data_fim_str) if data_fim_str else None
            if data_fim and data_fim < data_inicio:
                flash('Data de Fim não pode ser anterior à Data de Início.', 'error')
                return render_template('consultas/consulta_form.html', form_action='Adicionar', pacientes=pacientes, medicos=medicos, consulta=request.form)
        except ValueError:
            flash('Formato de Data de Início ou Data de Fim inválido.', 'error')
            return render_template('consultas/consulta_form.html', form_action='Adicionar', pacientes=pacientes, medicos=medicos, consulta=request.form)

        # Conversão de valorPago
        valor_pago = None
        if valor_pago_str:
            try:
                valor_pago = float(valor_pago_str)
                if valor_pago < 0:
                    flash('Valor Pago não pode ser negativo.', 'error')
                    return render_template('consultas/consulta_form.html', form_action='Adicionar', pacientes=pacientes, medicos=medicos, consulta=request.form)
            except ValueError:
                flash('Valor Pago deve ser um número.', 'error')
                return render_template('consultas/consulta_form.html', form_action='Adicionar', pacientes=pacientes, medicos=medicos, consulta=request.form)


        new_id = db.add_consulta(data_inicio, data_fim, pago, valor_pago, realizada, medico_crm, paciente_cpf)
        if new_id:
            flash('Consulta adicionada com sucesso!', 'success')
            return redirect(url_for('consultas_list'))
        else:
            flash('Erro ao adicionar consulta.', 'error')
            return render_template('consultas/consulta_form.html', 
                                   form_action='Adicionar', 
                                   pacientes=pacientes, 
                                   medicos=medicos,
                                   consulta=request.form)

    return render_template('consultas/consulta_form.html', 
                           form_action='Adicionar', 
                           pacientes=pacientes, 
                           medicos=medicos)

@app.route('/consultas/edit/<int:id_consulta>', methods=['GET', 'POST'])
def consulta_edit(id_consulta):
    """Edita uma consulta existente."""
    consulta = db.get_consulta_by_id(id_consulta)
    if not consulta:
        flash('Consulta não encontrada!', 'error')
        return redirect(url_for('consultas_list'))

    pacientes = db.get_all_pacientes()
    medicos = db.get_all_medicos()

    if request.method == 'POST':
        data_inicio_str = request.form.get('dataInicio')
        data_fim_str = request.form.get('dataFim')
        pago = 'pago' in request.form
        valor_pago_str = request.form.get('valorPago')
        realizada = 'realizada' in request.form
        medico_crm = request.form.get('medico_CRM')
        paciente_cpf = request.form.get('paciente_CPF')

        if not data_inicio_str or not medico_crm or not paciente_cpf:
            flash('Data de Início, Médico e Paciente são obrigatórios!', 'error')
            # Recarregar o formulário com os dados atuais e os dados originais da consulta para referência
            current_form_data = dict(request.form)
            current_form_data['idconsulta'] = id_consulta # Manter o ID
            return render_template('consultas/consulta_form.html', 
                                   form_action='Editar', 
                                   consulta=current_form_data, 
                                   pacientes=pacientes, 
                                   medicos=medicos)
        
        try:
            data_inicio = datetime.datetime.fromisoformat(data_inicio_str)
            data_fim = datetime.datetime.fromisoformat(data_fim_str) if data_fim_str else None
            if data_fim and data_fim < data_inicio:
                flash('Data de Fim não pode ser anterior à Data de Início.', 'error')
                current_form_data = dict(request.form)
                current_form_data['idconsulta'] = id_consulta
                return render_template('consultas/consulta_form.html', form_action='Editar', consulta=current_form_data, pacientes=pacientes, medicos=medicos)
        except ValueError:
            flash('Formato de Data de Início ou Data de Fim inválido.', 'error')
            current_form_data = dict(request.form)
            current_form_data['idconsulta'] = id_consulta
            return render_template('consultas/consulta_form.html', form_action='Editar', consulta=current_form_data, pacientes=pacientes, medicos=medicos)

        valor_pago = None
        if valor_pago_str:
            try:
                valor_pago = float(valor_pago_str)
                if valor_pago < 0:
                    flash('Valor Pago não pode ser negativo.', 'error')
                    current_form_data = dict(request.form)
                    current_form_data['idconsulta'] = id_consulta
                    return render_template('consultas/consulta_form.html', form_action='Editar', consulta=current_form_data, pacientes=pacientes, medicos=medicos)
            except ValueError:
                flash('Valor Pago deve ser um número.', 'error')
                current_form_data = dict(request.form)
                current_form_data['idconsulta'] = id_consulta
                return render_template('consultas/consulta_form.html', form_action='Editar', consulta=current_form_data, pacientes=pacientes, medicos=medicos)

        if db.update_consulta(id_consulta, data_inicio, data_fim, pago, valor_pago, realizada, medico_crm, paciente_cpf) is not None:
            flash('Consulta atualizada com sucesso!', 'success')
            return redirect(url_for('consultas_list'))
        else:
            flash('Erro ao atualizar consulta.', 'error')
            current_form_data = dict(request.form)
            current_form_data['idconsulta'] = id_consulta
            return render_template('consultas/consulta_form.html', 
                                   form_action='Editar', 
                                   consulta=current_form_data, 
                                   pacientes=pacientes, 
                                   medicos=medicos)
    
    # Para o GET request, formatar as datas para o input datetime-local
    if consulta.get('datainicio'):
        consulta['datainicio_form'] = consulta['datainicio'].isoformat(sep='T', timespec='minutes') if isinstance(consulta['datainicio'], datetime.datetime) else consulta['datainicio']
    if consulta.get('datafim'):
        consulta['datafim_form'] = consulta['datafim'].isoformat(sep='T', timespec='minutes') if isinstance(consulta['datafim'], datetime.datetime) else consulta['datafim']


    return render_template('consultas/consulta_form.html', 
                           form_action='Editar', 
                           consulta=consulta, 
                           pacientes=pacientes, 
                           medicos=medicos)

@app.route('/consultas/delete/<int:id_consulta>', methods=['POST'])
def consulta_delete(id_consulta):
    """Deleta uma consulta."""
    consulta = db.get_consulta_by_id(id_consulta)
    if not consulta:
        flash('Consulta não encontrada!', 'error')
        return redirect(url_for('consultas_list'))

    if db.delete_consulta(id_consulta) is not None:
        flash('Consulta removida com sucesso!', 'success')
    else:
        flash('Erro ao remover consulta. Verifique se há diagnósticos associados (ON DELETE RESTRICT).', 'error')
    return redirect(url_for('consultas_list'))


if __name__ == '__main__':
    app.run(debug=True) 
