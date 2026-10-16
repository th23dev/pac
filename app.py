import streamlit as st

# Arquivos de armazenamento
ARQUIVO_USUARIOS = 'usuarios.txt'
ARQUIVO_PONTUACAO = 'pontuacao.txt'

def ler_usuarios(arquivo=ARQUIVO_USUARIOS):
    with open(ARQUIVO_USUARIOS, 'r', encoding='utf-8') as arquivo:
        return [usuario.strip() for usuario in arquivo.readlines()]

def ler_pontuacao(arquivo=ARQUIVO_PONTUACAO):
    with open(ARQUIVO_PONTUACAO, 'r', encoding='utf-8') as pontuacao:
        return [pontos.strip() for pontos in pontuacao.readlines()]

st.set_page_config(page_title='Login simples', layout='centered')

if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'dados_usuario' not in st.session_state:
    st.session_state.dados_usuario = {}

if not st.session_state.logado:

    st.title('Controle de Pontuação')

    aba_login, aba_cadastro = st.tabs(['Login', 'Cadastro'])

    with aba_cadastro:
        st.subheader('Cadastre-se aqui')

        with st.form('form_cadastro'):
            nome = st.text_input('Nome', placeholder='Seu nome aqui')
            email = st.text_input('Email', type='email')
            senha = st.text_input('Senha', type='password')
            cadastrar = st.form_submit_button('Cadastrar', use_container_width=True)

        if cadastrar:
            if not nome.split() or not email or not senha.split():
                st.error('Preencha todos os campos!')

            else:
                usuarios = ler_usuarios()

                if email in usuarios:
                    st.error('Email já cadastrado no sistema!')
                else:
                    with open(ARQUIVO_USUARIOS, 'a', encoding='utf-8') as arquivo:
                        arquivo.write(f'{email}\n{senha}\n{nome}\n')
                    with open(ARQUIVO_PONTUACAO, 'a', encoding='utf-8') as pontuacao:
                        pontuacao.write(f'{email}\n{0}\n')
                    st.success('Usuário cadastrado com sucesso!')

    with aba_login:
        st.subheader('Login de usuário')

        with st.form('form_login'):
            email = st.text_input('Email', type='email')
            senha = st.text_input('Senha', type='password')
            entrar = st.form_submit_button('Entrar', use_container_width=True)

        if entrar:
            if not email.split() or not senha.split():
                st.error('Preencha todos os campos!')
            else:
                usuarios = ler_usuarios()
                pontuacao = ler_pontuacao()

                if email in usuarios:
                    indice = usuarios.index(email)

                    if senha == usuarios[indice + 1]:
                        st.session_state.dados_usuario = {
                            'email': usuarios[indice],
                            'senha': usuarios[indice + 1],
                            'nome': usuarios[indice + 2],
                            'pontos': pontuacao[pontuacao.index(email) + 1]
                        }
                        st.session_state.logado = True
                        st.rerun()
                    else:
                        st.error('Senha errada')

                else:
                    st.error('Usuário não cadastrado!')

else:
    aba_estatisticas, aba_competidores, aba_perfil = st.tabs(['Estatisticas', 'Competidores','Perfil'])

    with aba_perfil:
        st.subheader('Perfil de Usuário')

        pontuacao = ler_pontuacao()
        indice_pontuacao = pontuacao.index(st.session_state.dados_usuario['email'])
        st.session_state.dados_usuario['pontos'] = pontuacao[indice_pontuacao + 1]

        with st.container(border=True):
            st.write(f"Nome: {st.session_state.dados_usuario['nome']}")
            st.write(f"Email: {st.session_state.dados_usuario['email']}")
            st.write(f"Senha: {st.session_state.dados_usuario['senha']}")
            st.write(f"Pontos: {st.session_state.dados_usuario['pontos']}")

            if st.button('Sair'):
                st.session_state.logado = False
                st.session_state.dados_usuario = {}
                st.rerun()

        st.subheader('Atualizar dados')

        with st.form('atualizar_dados'):
            nome = st.text_input('Novo nome', placeholder='Seu nome aqui', value=st.session_state.dados_usuario['nome'])
            email = st.text_input('Novo email', type='email', value=st.session_state.dados_usuario['email'])
            senha = st.text_input('Nova senha', type='password', value=st.session_state.dados_usuario['senha'])
            atualizar = st.form_submit_button('Atualizar', use_container_width=True)

        if atualizar:
            if not nome.split() or not email or not senha.split():
                st.error('Preencha todos os campos!')

            else:
                usuarios = ler_usuarios()
                if email in usuarios and email != st.session_state.dados_usuario['email']:
                    st.error('Email já cadastrado no sistema!')
                else:
                    indice = usuarios.index(st.session_state.dados_usuario['email'])        
                    usuarios[indice] = email
                    usuarios[indice + 1] = senha
                    usuarios[indice + 2] = nome

                    st.session_state.dados_usuario = {
                        'email': email,
                        'senha': senha,
                        'nome': nome,
                        'pontos': st.session_state.dados_usuario['pontos']
                    }

                    with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as arquivo:
                        arquivo.writelines([f'{linha}\n' for linha in usuarios])
                    st.rerun()

        if st.button('Excluir Conta', use_container_width=True, type='primary'):
            usuarios = ler_usuarios()
            indice = usuarios.index(st.session_state.dados_usuario['email'])
            del usuarios[indice:indice+3]

            with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as arquivo:
                arquivo.writelines([f'{linha}\n' for linha in usuarios])

            st.session_state.logado = False
            st.session_state.dados_usuario = {}
            st.rerun()

    with aba_competidores:
        with st.form('form_pesquisar', border=False):
            colunas = st.columns([8, 2])

            with colunas[0]:
                pesquisa = st.text_input('Buscar competidores', placeholder='competidor123', label_visibility="collapsed")

            with colunas[1]:
                buscar = st.form_submit_button('Buscar', use_container_width=True)

        # O arquivo usuarios.txt segue esta ordem repetida:
        # [email, senha, nome, email, senha, nome, ...].
        usuarios = ler_usuarios()

        # O recorte [2::3] começa no índice 2 e pega um item a cada 3 posições:
        # índices 2, 5, 8... Assim, cria uma lista só com os nomes.
        nomes = usuarios[2::3]

        # O arquivo pontuacao.txt guarda pares [email, pontos, email, pontos, ...].
        pontuacao = ler_pontuacao()

        # O recorte [1::2] pega os índices 1, 3, 5... e cria a lista de pontos.
        pontos = pontuacao[1::2]

        # A senha fica no arquivo de usuários, mas não é selecionada para a lista
        # nem exibida aqui. zip associa cada nome à pontuação da mesma posição.
        # A classificação é ordenada pela pontuação, da maior para a menor.
        classificacao = sorted(zip(nomes, pontos),key=lambda competidor: int(competidor[1]),reverse=True)

        if buscar and pesquisa.strip():
            # Procura parte do nome sem diferenciar letras maiúsculas e minúsculas.
            termo = pesquisa.strip().casefold()
            classificacao = [
                (nome, pontos) for nome, pontos in classificacao
                if termo in nome.casefold()
            ]

        st.subheader('Classificação')
        if classificacao:
            st.table([
                {'Posição': posicao, 'Competidor': nome, 'Pontos': pontos}
                for posicao, (nome, pontos) in enumerate(classificacao, start=1)
            ])
        elif buscar and pesquisa.strip():
            # Informa quando a busca não encontra nenhum competidor.
            st.info('Nenhum competidor encontrado.')


    with aba_estatisticas:
        st.title('Estatísticas')

        usuarios = ler_usuarios()
        nomes = usuarios[2::3]
        pontuacao = ler_pontuacao()
        pontos = [int(valor) for valor in pontuacao[1::2]]

        if pontos:
            media_pontos = sum(pontos) / len(pontos)
            maior_pontuacao = max(pontos)

            coluna_jogadores, coluna_maximo, coluna_media, coluna_total, btn = st.columns(5)
            coluna_jogadores.metric('Jogadores', len(nomes))
            coluna_maximo.metric('Maior pontuação', maior_pontuacao)
            coluna_media.metric('Média de pontos', f'{media_pontos:.1f}')
            coluna_total.metric('Total de pontos', sum(pontos))
            with btn:
                if st.button('Atualizar'):
                    st.rerun()

            st.subheader('Média e maior pontuação')
            st.bar_chart({'Indicador': ['Média', 'Maior pontuação'],'Pontos': [media_pontos, maior_pontuacao]}, x='Indicador', y='Pontos')

            faixas = {
                '1 a 9': sum(1 for valor in pontos if 1 <= valor < 10),
                '10 a 19': sum(1 for valor in pontos if 10 <= valor < 20),
                '20 ou mais': sum(1 for valor in pontos if valor >= 20)
            }
            st.subheader('Competidores por faixa de pontos')
            st.vega_lite_chart({
                'data': {
                    'values': [
                        {'Faixa': faixa, 'Competidores': quantidade}
                        for faixa, quantidade in faixas.items()
                    ]
                },
                'transform': [
                    {
                        'joinaggregate': [
                            {'op': 'sum', 'field': 'Competidores', 'as': 'Total'}
                        ]
                    },
                    {
                        'calculate': 'datum.Competidores / datum.Total',
                        'as': 'Percentual'
                    }
                ],
                'layer': [
                    {
                        'mark': {'type': 'arc', 'tooltip': True},
                        'encoding': {
                            'theta': {
                                'field': 'Competidores',
                                'type': 'quantitative',
                                'stack': 'normalize'
                            },
                            'color': {'field': 'Faixa', 'type': 'nominal'},
                            'order': {
                                'field': 'Faixa',
                                'type': 'nominal',
                                'sort': ['1 a 9', '10 a 19', '20 ou mais']
                            },
                            'tooltip': [
                                {'field': 'Faixa', 'type': 'nominal'},
                                {'field': 'Competidores', 'type': 'quantitative'},
                                {
                                    'field': 'Percentual',
                                    'type': 'quantitative',
                                    'format': '.1%'
                                }
                            ]
                        }
                    },
                    {
                        'mark': {'type': 'text', 'radius': 100, 'color': 'white'},
                        'encoding': {
                            'theta': {
                                'field': 'Competidores',
                                'type': 'quantitative',
                                'stack': 'normalize'
                            },
                            'detail': {'field': 'Faixa', 'type': 'nominal'},
                            'order': {
                                'field': 'Faixa',
                                'type': 'nominal',
                                'sort': ['0 a 9', '10 a 19', '20 ou mais']
                            },
                            'text': {
                                'field': 'Percentual',
                                'type': 'quantitative',
                                'format': '.1%'
                            }
                        }
                    }
                ],
                'view': {'stroke': None}
            }, use_container_width=True)
        else:
            st.info('Ainda não há pontuações para exibir.')