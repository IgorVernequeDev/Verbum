function confirmarExclusao(element) {
    const idLivro = element.getAttribute('data-id');  // Recupera o idLivro do botão
    const confirmacao = confirm('Deseja excluir esse livro?');
    if (confirmacao) {
        const confirmacao2 = confirm('Tem certeza disso? Você irá perder TODO O REGISTRO FEITO PARA ESSE LIVRO!');
        if (confirmacao2) {
            window.location.href = '/excluir/' + idLivro;
        }
    }
}

function entrar() {
    const email = document.getElementById('email').value
    const senha = document.getElementById('senha').value

    if (email == "" || senha == "") {
        alert('Por favor, preencha todos os campos!')
    }
}