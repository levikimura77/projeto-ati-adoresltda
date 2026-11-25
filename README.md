# Atiçadores LTDA

A campanha de três capítulos acompanha os Atiçadores na missão de reunir
as turmas no pátio e recuperar a resenha da ETE Advogado José David Gil Rodrigues.

## Jogar no Windows

Abra [AticadoresLTDA-Campanha.exe](release/AticadoresLTDA-Campanha.exe)
ou extraia o [pacote ZIP](release/AticadoresLTDA-Windows.zip) e abra o
executável dentro dele. A versão distribuída já inclui o necessário para jogar.

## Campanha

| Capítulo | Onde acontece | O que fazer |
| --- | --- | --- |
| 1. Um novo integrante | Sala Preta | Conhecer Levi, Reidryan, Bruno, Davi, Jaylson e Jota. |
| 2. Conquistar as salas | Corredores, refeitório e auditório | Vencer três desafios e reunir pistas sobre a troca dos avisos. |
| 3. A Sala Branca | Sala Branca e pátio | Enfrentar quem manipulou as turmas e reunir a escola no epílogo. |

Converse com os personagens que têm **!** animado. Entre na área demarcada para começar
o desafio. Após os diálogos obrigatórios e o combate, quando houver, atravesse a
porta aberta para seguir ao próximo cenário.

## Controles e classes

| Controle | Ação |
| --- | --- |
| WASD ou setas | Andar |
| E | Conversar |
| Espaço, Enter ou E | Avançar o diálogo |
| Espaço ou Z | Soco |
| Botão esquerdo do mouse | Arremessar bolinha de papel |
| C ou Shift | Segurar a defesa até bloquear um golpe |
| Q | Usar a habilidade da classe |
| Esc | Abrir o menu de pausa com a opção **Salvar e sair** |

O Atacante usa **Ruptura** para quebrar a guarda. O Velocista usa **Dash**
para dar uma arrancada na direção do movimento. O Curandeiro usa
**Recuperação** para restaurar até dois corações.

## Executar pelo código-fonte

Na pasta principal, com Python instalado, execute os comandos abaixo.

```powershell
py -m pip install -r requirements.txt
py main.py
```

O jogo usa Python e Pygame CE. `campaign.py` contém o roteiro e as classes,
`school_maps.py` define os cenários, `pixel_people.py` desenha os sprites e
`chip_audio.py` gera as trilhas por capítulo e os sons das falas.

Para gerar a distribuição Windows e atualizar a cópia de download do site,
execute `build_windows.bat`. A estrutura legada de Godot permanece no
repositório como referência.

## Documentação e site

- [Documentação do jogo e do site (PDF)](<Atiçadores LTDA — Documentação do jogo e site.pdf>)
- [Como executar o site localmente](site/README.md)
