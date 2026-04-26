const STORAGE_KEY = 'oliviasPetCadastros';
const CURRENT_KEY = 'oliviasPetCadastroAtual';

function getCadastros() {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
}

function setCadastros(cadastros) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cadastros));
}

function getCadastroAtual() {
    return localStorage.getItem(CURRENT_KEY);
}

function setCadastroAtual(id) {
    localStorage.setItem(CURRENT_KEY, id);
}

function getCadastroPorId(id) {
    return getCadastros().find((cadastro) => cadastro.id === id);
}

function preencherFormularioCadastro() {
    const form = document.querySelector('[data-cadastro-form]');

    if (!form) {
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    const cadastro = id ? getCadastroPorId(id) : null;

    if (!cadastro) {
        return;
    }

    form.elements.id.value = cadastro.id;
    form.elements.nome_pet.value = cadastro.nome_pet;
    form.elements.nascimento.value = cadastro.nascimento;
    form.elements.tutor.value = cadastro.tutor;
    form.elements.email.value = cadastro.email;
    form.elements.contato.value = cadastro.contato;
    form.elements.endereco.value = cadastro.endereco;
    form.elements.bairro.value = cadastro.bairro;

    const titulo = document.querySelector('[data-cadastro-titulo]');
    if (titulo) {
        titulo.textContent = 'Editar Cadastro de Pet';
    }
}

function iniciarCadastro() {
    const form = document.querySelector('[data-cadastro-form]');

    if (!form) {
        return;
    }

    preencherFormularioCadastro();

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        if (!form.reportValidity()) {
            return;
        }

        const formData = new FormData(form);
        const id = formData.get('id') || crypto.randomUUID();
        const cadastros = getCadastros();
        const cadastro = {
            id,
            nome_pet: formData.get('nome_pet').trim(),
            nascimento: formData.get('nascimento'),
            tutor: formData.get('tutor').trim(),
            email: formData.get('email').trim(),
            contato: formData.get('contato').trim(),
            endereco: formData.get('endereco').trim(),
            bairro: formData.get('bairro').trim(),
            servico: formData.get('servico') || '',
        };
        const index = cadastros.findIndex((item) => item.id === id);

        if (index >= 0) {
            cadastro.servico = cadastros[index].servico || '';
            cadastros[index] = cadastro;
        } else {
            cadastros.push(cadastro);
        }

        setCadastros(cadastros);
        setCadastroAtual(id);
        window.location.href = '/servicos';
    });
}

function iniciarLogin() {
    const form = document.querySelector('[data-login-form]');

    if (!form) {
        return;
    }

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        if (!form.reportValidity()) {
            return;
        }

        window.location.href = '/inicial';
    });
}

function iniciarServico() {
    const form = document.querySelector('[data-servico-form]');

    if (!form) {
        return;
    }

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        if (!form.reportValidity()) {
            return;
        }

        const id = getCadastroAtual();
        const cadastros = getCadastros();
        const index = cadastros.findIndex((cadastro) => cadastro.id === id);

        if (index < 0) {
            alert('Cadastre um pet antes de agendar um serviço.');
            window.location.href = '/cadastro';
            return;
        }

        cadastros[index].servico = new FormData(form).get('servico');
        setCadastros(cadastros);
        window.location.href = '/ficha';
    });
}

function criarLinhaFicha(cadastro) {
    const tr = document.createElement('tr');
    const campos = [
        cadastro.nome_pet,
        cadastro.tutor,
        cadastro.email,
        cadastro.contato,
        cadastro.servico || 'Não agendado',
    ];

    campos.forEach((campo) => {
        const td = document.createElement('td');
        td.textContent = campo;
        tr.appendChild(td);
    });

    const acoes = document.createElement('td');
    const editar = document.createElement('a');
    const excluir = document.createElement('button');

    acoes.className = 'acoes';
    editar.href = `/cadastro?id=${cadastro.id}`;
    editar.textContent = 'Editar';
    excluir.type = 'button';
    excluir.dataset.deleteId = cadastro.id;
    excluir.textContent = 'Excluir';

    acoes.append(editar, excluir);
    tr.appendChild(acoes);

    return tr;
}

function iniciarFicha() {
    const tabela = document.querySelector('[data-ficha-lista]');
    const vazio = document.querySelector('[data-ficha-vazio]');

    if (!tabela) {
        return;
    }

    const cadastros = getCadastros();
    tabela.innerHTML = '';

    if (vazio) {
        vazio.hidden = cadastros.length > 0;
    }

    cadastros.forEach((cadastro) => {
        tabela.appendChild(criarLinhaFicha(cadastro));
    });

    tabela.addEventListener('click', (event) => {
        const botao = event.target.closest('[data-delete-id]');

        if (!botao) {
            return;
        }

        const id = botao.dataset.deleteId;
        const cadastrosAtualizados = getCadastros().filter((cadastro) => cadastro.id !== id);
        setCadastros(cadastrosAtualizados);

        if (getCadastroAtual() === id) {
            localStorage.removeItem(CURRENT_KEY);
        }

        window.location.reload();
    });
}

iniciarLogin();
iniciarCadastro();
iniciarServico();
iniciarFicha();
