import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from streamlit.components.v2 import component

# Arquivos de armazenamento
ARQUIVO_USUARIOS = 'usuarios.txt'
ARQUIVO_PONTUACAO = 'pontuacao.txt'

def salvar_recorde(email, pontos, arquivo):
    if type(pontos) is not int or pontos < 0:
        raise ValueError('Pontuação inválida')
    with open(arquivo, 'r', encoding='utf-8') as origem:
        linhas = origem.read().splitlines()
    indice = next(i for i in range(0, len(linhas), 2) if linhas[i] == email)
    recorde = int(linhas[indice + 1])
    if pontos <= recorde:
        return recorde
    linhas[indice + 1] = str(pontos)
    with open(arquivo, 'w', encoding='utf-8') as destino:
        destino.write('\n'.join(linhas) + '\n')
    return pontos


with open(Path(__file__).with_name('pong.html'), 'r', encoding='utf-8') as arquivo_html:
    conteudo = arquivo_html.read()

html_jogo, _, script_jogo = conteudo.partition('<script type="module">')
js_jogo = script_jogo.rsplit('</script>', 1)[0]
pong = component('pong', html=html_jogo, js=js_jogo)


def ler_usuarios(arquivo=ARQUIVO_USUARIOS):
    with open(ARQUIVO_USUARIOS, 'r', encoding='utf-8') as arquivo:
        return [usuario.strip() for usuario in arquivo.readlines()]

def ler_pontuacao(arquivo=ARQUIVO_PONTUACAO):
    with open(ARQUIVO_PONTUACAO, 'r', encoding='utf-8') as pontuacao:
        return [pontos.strip() for pontos in pontuacao.readlines()]

st.set_page_config(page_title='Pong Rankeado', layout='centered')

if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'dados_usuario' not in st.session_state:
    st.session_state.dados_usuario = {}

if not st.session_state.logado:

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
                        pontuacao = ler_pontuacao()
                        pontos = 0
                        for i in range(0, len(pontuacao), 2):
                            if i + 1 < len(pontuacao) and pontuacao[i] == email:
                                pontos = int(pontuacao[i + 1])
                                break
                        else:
                            pontuacao.extend([email, '0'])
                            with open(ARQUIVO_PONTUACAO, 'w', encoding='utf-8') as arquivo:
                                arquivo.writelines([f'{linha}\n' for linha in pontuacao])

                        st.session_state.dados_usuario = {
                            'email': usuarios[indice],
                            'senha': usuarios[indice + 1],
                            'nome': usuarios[indice + 2],
                            'pontos': pontos
                        }
                        st.session_state.logado = True
                        st.rerun()
                    else:
                        st.error('Senha errada')

                else:
                    st.error('Usuário não cadastrado!')

else:
    aba_jogo, aba_estatisticas, aba_competidores, aba_perfil = st.tabs(['Jogo','Estatisticas', 'Competidores','Perfil'])

    with aba_perfil:
        st.subheader('Perfil de Usuário')

        email_atual = st.session_state.dados_usuario['email']
        pontuacao = ler_pontuacao()
        pontos = 0
        for i in range(0, len(pontuacao), 2):
            if i + 1 < len(pontuacao) and pontuacao[i] == email_atual:
                pontos = int(pontuacao[i + 1])
                break
        else:
            pontuacao.extend([email_atual, '0'])
            with open(ARQUIVO_PONTUACAO, 'w', encoding='utf-8') as arquivo:
                arquivo.writelines([f'{linha}\n' for linha in pontuacao])
        st.session_state.dados_usuario['pontos'] = pontos

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

                    email_anterior = st.session_state.dados_usuario['email']
                    pontuacao_atual = st.session_state.dados_usuario['pontos']
                    st.session_state.dados_usuario = {
                        'email': email,
                        'senha': senha,
                        'nome': nome,
                        'pontos': pontuacao_atual
                    }

                    with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as arquivo:
                        arquivo.writelines([f'{linha}\n' for linha in usuarios])

                    if email != email_anterior:
                        pontuacao = ler_pontuacao()
                        for i in range(0, len(pontuacao), 2):
                            if i < len(pontuacao) and pontuacao[i] == email_anterior:
                                pontuacao[i] = email
                                with open(ARQUIVO_PONTUACAO, 'w', encoding='utf-8') as arquivo:
                                    arquivo.writelines([f'{linha}\n' for linha in pontuacao])
                                break

                    st.rerun()

        if st.button('Excluir Conta', use_container_width=True, type='primary'):
            usuarios = ler_usuarios()
            indice = usuarios.index(st.session_state.dados_usuario['email'])
            del usuarios[indice:indice+3]

            with open(ARQUIVO_USUARIOS, 'w', encoding='utf-8') as arquivo:
                arquivo.writelines([f'{linha}\n' for linha in usuarios])

            pontuacao = ler_pontuacao()
            indice_pontuacao = next((i for i in range(0, len(pontuacao), 2) if pontuacao[i] == st.session_state.dados_usuario['email']), None)
            if indice_pontuacao is not None:
                del pontuacao[indice_pontuacao:indice_pontuacao+2]
                with open(ARQUIVO_PONTUACAO, 'w', encoding='utf-8') as arquivo:
                    arquivo.writelines([f'{linha}\n' for linha in pontuacao])

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

        usuarios = ler_usuarios()

        pontuacao = ler_pontuacao()

        nomes = usuarios[2::3]
        pontos = pontuacao[1::2]
        
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
        st.subheader('Estatísticas')

        usuarios = ler_usuarios()
        nomes = usuarios[2::3]
        pontuacao = ler_pontuacao()
        dados = pd.DataFrame({
            'Email': pontuacao[0::2],
            'Pontos': [int(valor) for valor in pontuacao[1::2]]
        })
        jogadores = pd.DataFrame({'Email': usuarios[0::3], 'Nome': usuarios[2::3]})
        dados = jogadores.merge(dados, on='Email', how='left')
        dados['Pontos'] = dados['Pontos'].fillna(0).astype(int)

        if not dados.empty:
            media_pontos = dados['Pontos'].mean()
            maior_pontuacao = dados['Pontos'].max()

            coluna_jogadores, coluna_maximo, coluna_media, coluna_total, btn = st.columns(5)
            coluna_jogadores.metric('Jogadores', len(nomes))
            coluna_maximo.metric('Maior recorde', int(maior_pontuacao))
            coluna_media.metric('Média dos recordes', f'{media_pontos:.1f}')
            coluna_total.metric('Com pontuação', int((dados['Pontos'] > 0).sum()))
            with btn:
                if st.button('Atualizar'):
                    st.rerun()
            
            #grafico1
            st.subheader('Top 10 recordes')
            ranking = dados.sort_values('Pontos', ascending=False).head(10)
            email_atual = st.session_state.dados_usuario['email']
            # A posição no rótulo diferencia jogadores com o mesmo nome.
            rotulos = []
            for posicao, nome in enumerate(ranking['Nome'], start=1):
                rotulos.append(f'{posicao}. {nome}')

            fig, ax = plt.subplots()
            ax.barh(rotulos, ranking['Pontos'])
            ax.invert_yaxis()
            ax.set_xlabel('Recorde (pontos)')
            st.pyplot(fig)
            plt.close(fig)

            #grafico2
            st.subheader('Distribuição dos recordes')
            pontos = dados['Pontos']
            faixas = ['0', '1 a 9', '10 a 19', '20 ou mais']
            quantidades = [
                (pontos == 0).sum(),
                ((pontos >= 1) & (pontos <= 9)).sum(),
                ((pontos >= 10) & (pontos <= 19)).sum(),
                (pontos >= 20).sum()
            ]
            fig, ax = plt.subplots()
            ax.bar(faixas, quantidades)
            ax.set_xlabel('Recorde (pontos)')
            ax.set_ylabel('Jogadores')
            st.pyplot(fig)
            plt.close(fig)

            #grafico3
            st.subheader('Seu recorde entre os jogadores')
            recorde_atual = int(dados.loc[dados['Email'] == email_atual, 'Pontos'].iloc[0])
            adversarios = dados.loc[dados['Email'] != email_atual, 'Pontos']
            if not adversarios.empty:
                categorias = ['Abaixo do seu', 'Igual ao seu', 'Acima do seu']
                quantidades = [
                    (adversarios < recorde_atual).sum(),
                    (adversarios == recorde_atual).sum(),
                    (adversarios > recorde_atual).sum()
                ]
                fig, ax = plt.subplots()
                ax.bar(categorias, quantidades)
                ax.set_title(f'Seu recorde: {recorde_atual} pontos')
                ax.set_ylabel('Outros jogadores')
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info('Cadastre outros jogadores para comparar os recordes.')

            #grafico4
            st.subheader('Jogadores que alcançaram cada meta')
            metas = [1, 5, 10, 20, 50]
            quantidades = []
            for meta in metas:
                quantidades.append((dados['Pontos'] >= meta).sum())

            fig, ax = plt.subplots()
            ax.scatter(metas, quantidades)
            ax.grid()
            ax.set_xticks(metas)
            # ax.fill_between(metas, quantidades, alpha=0.3)
            ax.set_xlabel('Meta de pontos')
            ax.set_ylabel('Jogadores que alcançaram a meta')
            st.pyplot(fig)
            plt.close(fig)
            
            #grafico5
            st.subheader('Concentração de pontos (Top 1)')
            total_pontos = dados['Pontos'].sum()
            if total_pontos > 0:
                top_1 = dados.sort_values('Pontos', ascending=False).iloc[0]
                pontos_top1 = top_1['Pontos']
                nome_top1 = top_1['Nome']
                pontos_restante = total_pontos - pontos_top1
                
                fig, ax = plt.subplots()
                ax.pie(
                    [pontos_top1, pontos_restante],
                    labels=[f'Top 1 ({nome_top1})', 'Restante'],
                    autopct="%1.1f%%",
                    startangle=90,
                    wedgeprops=dict(width=0.4)
                )
                ax.axis('equal')
                st.pyplot(fig)
                plt.close(fig)
            
            #grafico6
            st.subheader('Resumo estatístico da base')
            menor_pontuacao = dados['Pontos'].min()
            mediana_pontos = dados['Pontos'].median()
            
            metricas = ['Mínimo', 'Mediana', 'Média', 'Máximo']
            valores = [menor_pontuacao, mediana_pontos, media_pontos, maior_pontuacao]
            
            fig, ax = plt.subplots()
            barras = ax.bar(metricas, valores)
            ax.set_ylabel('Pontos')
            for bar in barras:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{height:.1f}', ha='center', va='bottom')
            st.pyplot(fig)
            plt.close(fig)
            
        else:
            st.info('Ainda não há pontuações para exibir.')


    with aba_jogo:
        st.subheader('Pong Rankeado')
        jogador = st.session_state.dados_usuario
            
        resultado = pong(data={'email': jogador['email'], 'recorde': int(jogador['pontos'])}, key=f"pong_{jogador['email']}", on_resultado_change=lambda: None).resultado
        if isinstance(resultado, dict) and resultado.get('email') == jogador['email']:
            pontos = resultado.get('pontos')
            if type(pontos) is int and pontos > int(jogador['pontos']):
                try:
                    recorde = salvar_recorde(jogador['email'], pontos, ARQUIVO_PONTUACAO)
                except (OSError, ValueError, StopIteration, IndexError):
                    st.error('Não foi possível salvar o recorde. Tente novamente.')
                    if st.button('Tentar salvar novamente'):
                        st.rerun()
                else:
                    jogador['pontos'] = str(recorde)
                    st.rerun()
