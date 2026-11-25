"""Gera apresentação editável sem dependências além do Pygame do projeto."""
import os, sys, zipfile, html, struct
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(os.environ.get('ATICADORES_SLIDES_OUTPUT', str(Path(__file__).resolve().parent)))
HERE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT))
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
from main import Game

pygame.mouse.set_cursor = lambda *a, **k: None
original_read = Game.read_settings
Game.read_settings = lambda self: None  # Capturas não usam nem alteram preferências pessoais.
g = Game()
g.settings['brightness'] = 1
g.settings_draft = g.settings.copy()
g.name = 'Jogador'
for state, filename in [('menu','menu'), ('select','selecao'), ('settings','opcoes')]:
    g.state = state
    g.render()
    with (HERE / (filename + '.png')).open('wb') as f:
        pygame.image.save(g.canvas, f, 'capture.png')
g.difficulty = 'hard'
g.start_game()
g.render()
with (HERE/'dialogo.png').open('wb') as f:
    pygame.image.save(g.canvas, f, 'capture.png')
g.phase = 'combat'
g.player.update(520, 420)
g.boss.update(760, 310)
g.render()
with (HERE/'batalha.png').open('wb') as f:
    pygame.image.save(g.canvas, f, 'capture.png')
pygame.quit()

slides = [
dict(title='ATIÇADORES\nLTDA.', tag='PROJETO DE JOGO • ETE', body=['A resenha da escola está em jogo.', 'Python + Pygame • Site com Flask e SQLite'], image='menu.png', notes='Apresente o nome da equipe e a proposta: transformar o ambiente escolar em uma experiência interativa. Esta apresentação foi baseada nos arquivos atuais da pasta, especialmente main.py e o backend do site.'),
dict(title='Da escola\npara o jogo', tag='01 • PROPOSTA', body=['Ação 2D em pixel art com ambientação escolar.', 'Escolha de personagem, diálogos e combate contra um chefão.', 'Projeto que conecta programação, arte e desenvolvimento web.'], image='selecao.png', notes='Explique que o jogador entra na equipe Atiçadores e precisa enfrentar o desafio da Sala da Batalha. O objetivo pedagógico é aplicar lógica, interfaces, persistência e integração entre navegador e servidor.'),
dict(title='Uma hierarquia\nescondida', tag='02 • HISTÓRIA E ESCOPO', body=['O professor apresenta os Atiçadores e a influência da Sala Branca.', 'A demonstração atual oferece uma sala de batalha e um chefão.', 'O site apresenta uma narrativa maior; várias salas e funções de equipe fazem parte dessa proposta.'], image='dialogo.png', notes='Diferencie a narrativa do site do que está efetivamente implementado: o HTML descreve várias salas e funções de ataque, suporte e cura, mas main.py entrega o confronto de uma sala. Não apresente esses sistemas narrativos como recursos já jogáveis.'),
dict(title='O caminho\nda partida', tag='03 • NAVEGAÇÃO', body=['Carregamento → menu → seleção → introdução → combate.', 'Na seleção: nome, dois personagens e quatro dificuldades.', 'Esc abre a pausa; ela permite configurar ou salvar e sair.', 'O confronto termina com vitória ou uma tela de derrota.'], image='menu.png', notes='O carregamento representa o progresso da abertura. Créditos são um painel no menu. A derrota é uma fase da partida, e a vitória possui uma tela própria. Uma partida salva pode ser retomada a partir do menu.'),
dict(title='Movimento, ataque\ne defesa', tag='04 • COMO JOGAR', body=['WASD / setas: movimentar. Espaço / Z: socar.', 'Clique esquerdo: bolinha de papel, 40 de dano e recarga de 5 s.', 'Soco: 20 de dano e intervalo de 0,5 s.', 'C / Shift: bloquear no Difícil e Impossível. Esc: pausar.'], image='batalha.png', notes='A bolinha é lançada na direção do cursor. O bloqueio segura até um ataque por acionamento: é preciso soltar e pressionar a tecla novamente. Na introdução, Espaço ou Enter avançam os diálogos. A movimentação fica mais lenta enquanto o jogador bloqueia.'),
dict(title='Quatro níveis\nde desafio', tag='05 • DIFICULDADES', table=[['Modo','Corações','Vida do chefe','Velocidade*','Bloqueio'],['Fácil','5','200','65','Não'],['Médio','5','230','78','Não'],['Difícil','3','260','92','Sim'],['Impossível','3','400','180','Sim']], body=['Nos dois modos mais difíceis, o chefe também lança projéteis.', '*Velocidade do chefe em unidades do jogo por segundo.'], notes='Os dados vêm de DIFFICULTIES e player_hearts_for_difficulty. Um acerto recebido retira um coração em todos os modos: damage_player não usa o valor numérico de damage do perfil para reduzir a vida. A dificuldade também altera o intervalo de ataque e, nos níveis superiores, os projéteis de pedra, papel e tesoura.'),
dict(title='A sala também\nfaz parte da estratégia', tag='06 • ARTE E MECÂNICAS', body=['Carteiras e limites da sala têm colisão.', 'O chefe persegue o jogador e ataca por proximidade.', 'Corações mostram a vida do jogador; barra mostra a do chefe.', 'Sprites, animações e trilhas chiptune dão identidade à experiência.'], image='batalha.png', notes='O movimento usa vetores e o tempo entre quadros. A classe também desenha sprites por código e gera áudio com ondas e sequências musicais, além de usar imagens de assets/ui. O alvo é 60 quadros por segundo e a resolução lógica é 1280 por 720, com redimensionamento da janela.'),
dict(title='Como o código\norganiza tudo', tag='07 • ESTRUTURA TÉCNICA', body=['main.py / classe Game: entradas, estados, regras, desenho e áudio.', 'Pygame: janela, teclado, mouse, superfícies e som.', 'Ciclo principal: eventos → atualização → renderização.', 'assets/: recursos visuais. build_windows.bat: empacotamento.'], image='selecao.png', notes='A implementação atual concentra responsabilidades na classe Game. A pasta também contém project.godot, scenes e scripts da versão anterior; o ponto de entrada do jogo Python é main.py. Os métodos handle_click, update_game e render ajudam a explicar a divisão lógica mesmo dentro do mesmo arquivo.'),
dict(title='Continuar de onde\nparou', tag='08 • CONFIGURAÇÕES E SAVE', body=['Ajustes de brilho, tela cheia, volumes e idioma PT / EN.', 'Salvar e sair preserva personagem, dificuldade, vidas e posições.', 'A partida também guarda fase e etapa do diálogo.', 'Preferências e progresso ficam em arquivos JSON locais.'], image='opcoes.png', notes='As preferências são gravadas em .aticadores_settings.json, e a partida em .aticadores_save.json, na pasta do usuário. Não são tabelas do banco SQLite. A vitória remove o save da partida. A tela de pausa permite abrir as configurações e voltar ao jogo.'),
dict(title='Um site para\napresentar e ouvir', tag='09 • FRONTEND E API', body=['HTML + CSS + JavaScript: história, jogo, download e sugestões.', 'Flask serve a página e recebe POST /api/suggestions.', 'Nome, e-mail e sugestão são enviados em JSON.', 'O servidor valida, grava no SQLite e confirma o resultado.'], notes='Explique o fluxo navegador → servidor Flask → SQLite → resposta ao navegador. O endpoint retorna 201 quando salva, 400 quando os dados são inválidos e 500 se houver erro de banco. O endpoint GET /api/health permite verificar se o servidor responde. Abrir apenas o HTML não executa essa API.'),
dict(title='Sugestões que\nficam registradas', tag='10 • SQLITE', table=[['Campo','Finalidade'],['id','Identificador automático'],['name','Nome: de 2 a 80 caracteres'],['email','E-mail validado; até 254 caracteres'],['suggestion','Mensagem: de 10 a 2.000 caracteres'],['created_at','Data e hora com CURRENT_TIMESTAMP']], body=['Tabela suggestions • site/backend/database/suggestions.sqlite3', 'O INSERT usa parâmetros; o banco é criado na inicialização.'], notes='A aplicação cria a pasta e a tabela quando o servidor inicia. O schema usa NOT NULL e restrições CHECK. O arquivo SQLite guarda sugestões do site, enquanto o progresso do jogo usa JSON. Não exiba dados reais de visitantes na apresentação.'),
dict(title='Do código\nao executável', tag='11 • EXECUÇÃO E ENTREGA', body=['Desenvolvimento: instalar requirements.txt e executar main.py.', 'Windows: build_windows.bat empacota com PyInstaller.', 'O .exe inclui os recursos e dispensa Python para o jogador.', 'Site local: executar site/backend/app.py e abrir 127.0.0.1:5000.'], notes='O script gera dist/AticadoresLTDA.exe e uma distribuição ZIP em release. O frontend possui um link para downloads/AticadoresLTDA.exe. Para atualizar a versão oferecida no site, substitui-se esse arquivo pelo executável novo. O servidor local usa Flask, não Java, nesta pasta.'),
dict(title='O que aprendemos\nconstruindo', tag='12 • FECHAMENTO', body=['Regras e estados transformam uma ideia em uma partida jogável.', 'Arte, áudio e interface ajudam a comunicar as ações.', 'Frontend, API e banco completam o projeto fora do jogo.', 'Próximos passos: ampliar cenários e dividir o código em módulos.'], image='menu.png', notes='Conclua destacando a integração das áreas e convide a turma a testar o jogo e enviar uma sugestão. A ampliação das salas e a modularização são possibilidades de evolução, não funcionalidades já presentes. Fontes: main.py; site/frontend/index.html e js/main.js; site/backend/app.py; database/schema.sql; build_windows.bat; LEIA-ME-DISTRIBUICAO.txt. Código analisado em 25/11/2026.')
]

# PowerPoint nativo: textos, tabelas e imagens permanecem editáveis.
def esc(s): return html.escape(str(s), quote=True)
def emu(v): return int(v*914400)
P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def xml(s): return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+s
def rels(items): return xml('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="{i}" Type="{R}/{t}" Target="{esc(dest)}"/>' for i,t,dest in items)+'</Relationships>')
def tree(): return '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
def textshape(id,x,y,w,h,text,size=22,color='F3F5FA',bold=False):
    pars=''.join('<a:p><a:pPr marL="0" indent="0"><a:spcAft><a:spcPts val="1100"/></a:spcAft></a:pPr><a:r><a:rPr lang="pt-BR" sz="'+str(int(size*100))+'" b="'+('1' if bold else '0')+'"><a:solidFill><a:srgbClr val="'+color+'"/></a:solidFill><a:latin typeface="Aptos"/></a:rPr><a:t>'+esc(line)+'</a:t></a:r><a:endParaRPr lang="pt-BR"/></a:p>' for line in text.split('\n'))
    return f'<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="Texto {id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"/><a:lstStyle/>{pars}</p:txBody></p:sp>'
def picture(id,x,y,w,h):
    return f'<p:pic><p:nvPicPr><p:cNvPr id="{id}" name="Captura do jogo"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="rIdImage"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
def table(rows):
    cols=len(rows[0]); width=11.9; rowh=.48
    grid=''.join(f'<a:gridCol w="{emu(width/cols)}"/>' for _ in range(cols))
    trs=''
    for n,row in enumerate(rows):
        cells=''
        for cell in row:
            bg='244456' if n==0 else ('172336' if n%2 else '1D2B42')
            cells+=f'<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="pt-BR" sz="1700" b="{1 if n==0 else 0}"><a:solidFill><a:srgbClr val="F3F5FA"/></a:solidFill></a:rPr><a:t>{esc(cell)}</a:t></a:r></a:p></a:txBody><a:tcPr marL="100000" marR="80000" marT="60000" marB="40000"><a:solidFill><a:srgbClr val="{bg}"/></a:solidFill></a:tcPr></a:tc>'
        trs+=f'<a:tr h="{emu(rowh)}">{cells}</a:tr>'
    return f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="7" name="Tabela"/><p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr><p:xfrm><a:off x="{emu(.7)}" y="{emu(2.6)}"/><a:ext cx="{emu(width)}" cy="{emu(rowh*len(rows))}"/></p:xfrm><a:graphic><a:graphicData uri="{A}/table"><a:tbl><a:tblPr/><a:tblGrid>{grid}</a:tblGrid>{trs}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>'

out=HERE/'Aticadores_LTDA_Apresentacao.pptx'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    def put(p,s): z.writestr(p, s.encode('utf-8'))
    overrides=[('/ppt/presentation.xml','application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'),('/ppt/slideMasters/slideMaster1.xml','application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml'),('/ppt/slideLayouts/slideLayout1.xml','application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml')]
    for i in range(1,len(slides)+1):
        overrides.extend([(f'/ppt/slides/slide{i}.xml','application/vnd.openxmlformats-officedocument.presentationml.slide+xml'),(f'/ppt/notesSlides/notesSlide{i}.xml','application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml')])
    put('[Content_Types].xml',xml('<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/>'+''.join(f'<Override PartName="{p}" ContentType="{c}"/>' for p,c in overrides)+'</Types>'))
    put('_rels/.rels',rels([('rId1','officeDocument','ppt/presentation.xml')]))
    put('ppt/presentation.xml',xml(f'<p:presentation xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rIdMaster"/></p:sldMasterIdLst><p:sldIdLst>'+''.join(f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1,len(slides)+1))+f'</p:sldIdLst><p:sldSz cx="{emu(13.333333)}" cy="{emu(7.5)}" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>'))
    put('ppt/_rels/presentation.xml.rels',rels([('rIdMaster','slideMaster','slideMasters/slideMaster1.xml')]+[(f'rId{i}','slide',f'slides/slide{i}.xml') for i in range(1,len(slides)+1)]))
    colors=''.join(f'<a:{name}><a:srgbClr val="{val}"/></a:{name}>' for name,val in [('dk1','101729'),('lt1','FFFFFF'),('dk2','172336'),('lt2','F3F5FA'),('accent1','7DDCFF'),('accent2','FFE14C'),('accent3','7DD3A7'),('accent4','B3A1F8'),('accent5','FF967D'),('accent6','8FB3D9'),('hlink','7DDCFF'),('folHlink','B3A1F8')])
    put('ppt/slideMasters/slideMaster1.xml',xml(f'<p:sldMaster xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:cSld><p:spTree>{tree()}</p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'))
    put('ppt/slideMasters/_rels/slideMaster1.xml.rels',rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml')]))
    put('ppt/slideLayouts/slideLayout1.xml',xml(f'<p:sldLayout xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}" type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{tree()}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'))
    put('ppt/slideLayouts/_rels/slideLayout1.xml.rels',rels([('rId1','slideMaster','../slideMasters/slideMaster1.xml')]))
    for i,s in enumerate(slides,1):
        shapes=tree()+textshape(2,.7,.45,11.9,.35,s['tag'],13,'7DDCFF',True)
        hasimg='image' in s
        shapes+=textshape(3,.7,1.05,6.1 if hasimg else 12,1.4,s['title'],36,'FFE14C',True)
        if 'table' in s:
            shapes+=table(s['table'])+textshape(4,.7,5.8,11.9,.9,'\n'.join(s['body']),17)
        else:
            shapes+=textshape(4,.7,2.9,5.25 if hasimg else 11.5,3.65,'\n'.join(s['body']),20 if hasimg else 25)
        relations=[('rIdLayout','slideLayout','../slideLayouts/slideLayout1.xml'),('rIdNotes','notesSlide',f'../notesSlides/notesSlide{i}.xml')]
        if hasimg:
            shapes+=picture(5,6.35,2.0,6.3,3.54375)
            relations.append(('rIdImage','image',f'../media/image{i}.png'))
            z.write(HERE/s['image'],f'ppt/media/image{i}.png')
            shapes+=textshape(6,6.35,5.7,6.3,.5,'TELA GERADA PELO CÓDIGO DO JOGO',10,'A2B4CA')
        shapes+=textshape(9,.7,7,11.8,.25,f'ATIÇADORES LTDA  /  ETE                                                {i:02d} / {len(slides):02d}',10,'A2B4CA')
        put(f'ppt/slides/slide{i}.xml',xml(f'<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="101729"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>{shapes}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'))
        put(f'ppt/slides/_rels/slide{i}.xml.rels',rels(relations))
        note=textshape(2,.5,1,6.5,8,s['notes'],16)
        note=note.replace('<p:nvPr/>','<p:nvPr><p:ph type="body" idx="1"/></p:nvPr>')
        put(f'ppt/notesSlides/notesSlide{i}.xml',xml(f'<p:notes xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:cSld><p:spTree>{tree()}{note}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>'))
        put(f'ppt/notesSlides/_rels/notesSlide{i}.xml.rels',rels([('rId1','slide',f'../slides/slide{i}.xml')]))

# Cópia HTML para visualização e impressão em PDF.
css='''@page{size:13.333in 7.5in;margin:0}*{box-sizing:border-box}body{margin:0;background:#101729;color:#f3f5fa;font-family:Arial,sans-serif}.slide{width:1280px;height:720px;padding:45px 65px;position:relative;break-after:page;overflow:hidden}.tag{font-size:16px;letter-spacing:2px;color:#7ddcff;font-weight:bold}h1{font-size:48px;color:#ffe14c;line-height:1.08;margin:26px 0 28px;white-space:pre-line}.content{font-size:25px;line-height:1.35;max-width:1130px}.with-image .content{width:505px;font-size:22px}.content p{margin:0 0 21px}.shot{position:absolute;left:610px;top:195px;width:605px;border:1px solid #31435c}.caption{position:absolute;left:610px;top:550px;color:#a2b4ca;font-size:12px;letter-spacing:1px}footer{position:absolute;bottom:28px;left:65px;right:65px;color:#a2b4ca;font-size:12px;display:flex;justify-content:space-between}table{border-collapse:collapse;width:100%;margin-top:10px;font-size:22px}th,td{text-align:left;padding:14px 18px;background:#172336;border-bottom:2px solid #101729}th{background:#244456}tr:nth-child(even) td{background:#1d2b42}.table-note{font-size:18px;margin-top:16px}@media print{.slide{width:13.333in;height:7.5in}body{-webkit-print-color-adjust:exact;print-color-adjust:exact}}'''
parts=[]
for i,s in enumerate(slides,1):
    t=''
    if 'table' in s:
        t='<table>'+''.join('<tr>'+''.join(f'<{"th" if n==0 else "td"}>{esc(c)}</{"th" if n==0 else "td"}>' for c in row)+'</tr>' for n,row in enumerate(s['table']))+'</table><div class="table-note">'+''.join('<p>'+esc(p)+'</p>' for p in s['body'])+'</div>'
    else: t='<div class="content">'+''.join('<p>'+esc(p)+'</p>' for p in s['body'])+'</div>'
    image=f'<img class="shot" src="{s["image"]}"><div class="caption">TELA GERADA PELO CÓDIGO DO JOGO</div>' if 'image' in s else ''
    parts.append(f'<section class="slide {"with-image" if image else ""}"><div class="tag">{esc(s["tag"])}</div><h1>{esc(s["title"])}</h1>{t}{image}<footer><span>ATIÇADORES LTDA / ETE</span><span>{i:02d} / {len(slides):02d}</span></footer></section>')
(HERE/'Apresentacao.html').write_text('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Atiçadores LTDA</title><style>'+css+'</style>'+''.join(parts)+'</html>',encoding='utf-8')
(HERE/'Notas_do_apresentador.md').write_text('# Atiçadores LTDA — notas para apresentação\n\n'+ '\n\n'.join(f'## Slide {i} — {s["title"].replace(chr(10)," ")}\n\n{s["notes"]}' for i,s in enumerate(slides,1)),encoding='utf-8')
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for n in z.namelist():
        if n.endswith(('.xml','.rels')): ET.fromstring(z.read(n))
print(f'Gerados {len(slides)} slides editáveis com notas: {out}')

# PDF de apresentação, com as mesmas cores e conteúdo, sem automação do Office.
import io
pygame.font.init()
def font(n,b=False): return pygame.font.SysFont('Arial',n,bold=b)
def draw_lines(surface,text,pos,width,size=24,color='#F3F5FA',bold=False):
    f=font(size,bold); x,y=pos
    for para in text.split('\n'):
        words=para.split(); line=''
        for word in words:
            candidate=(line+' '+word).strip()
            if line and f.size(candidate)[0]>width:
                surface.blit(f.render(line,True,color),(x,y)); y+=int(size*1.3); line=word
            else: line=candidate
        if line: surface.blit(f.render(line,True,color),(x,y)); y+=int(size*1.3)
        y+=8
    return y
jpgs=[]
for i,s in enumerate(slides,1):
    surface=pygame.Surface((1280,720)); surface.fill('#101729')
    draw_lines(surface,s['tag'],(67,44),1140,16,'#7DDCFF',True)
    draw_lines(surface,s['title'],(67,102),1150,46,'#FFE14C',True)
    if 'table' in s:
        rows=s['table']; cols=len(rows[0]); cw=1140/cols
        for ri,row in enumerate(rows):
            for ci,value in enumerate(row):
                x=67+int(ci*cw); y=249+ri*47
                pygame.draw.rect(surface,'#244456' if ri==0 else '#172336',(x,y,int(cw)-2,45))
                draw_lines(surface,value,(x+11,y+10),cw-18,20 if cols<3 else 18,bold=ri==0)
        draw_lines(surface,'\n'.join(s['body']),(67,249+47*len(rows)+20),1140,20)
    else:
        image='image' in s
        end=draw_lines(surface,'\n'.join(s['body']),(67,278),505 if image else 1120,25 if image else 30)
        assert end<670, (i,end)
        if image:
            shot=pygame.image.load(str(HERE/s['image']))
            surface.blit(pygame.transform.smoothscale(shot,(605,340)),(610,192))
            draw_lines(surface,'TELA GERADA PELO CÓDIGO DO JOGO',(610,548),610,12,'#A2B4CA')
    draw_lines(surface,'ATIÇADORES LTDA / ETE',(67,676),1000,12,'#A2B4CA')
    draw_lines(surface,f'{i:02d} / {len(slides):02d}',(1150,676),100,12,'#A2B4CA')
    if i in (1,5,6,11):
        with (HERE/f'preview_{i:02d}.png').open('wb') as f: pygame.image.save(surface,f,'preview.png')
    f=io.BytesIO(); pygame.image.save(surface,f,'slide.jpg'); jpgs.append(f.getvalue())

objects=[]
def obj(data):
    objects.append(data if isinstance(data,bytes) else data.encode()); return len(objects)
def stream(data,attrs=''):
    return f'<< /Length {len(data)} {attrs} >>\nstream\n'.encode()+data+b'\nendstream'
obj('<< /Type /Catalog /Pages 2 0 R >>'); obj('')
pages=[]
for jpg in jpgs:
    image_id=obj(stream(jpg,'/Type /XObject /Subtype /Image /Width 1280 /Height 720 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode'))
    cmd=b'q 960 0 0 540 0 0 cm /Im0 Do Q'
    content_id=obj(stream(cmd))
    page_id=obj(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 960 540] /Resources << /XObject << /Im0 {image_id} 0 R >> >> /Contents {content_id} 0 R >>')
    pages.append(page_id)
objects[1]=('<< /Type /Pages /Count '+str(len(pages))+' /Kids ['+' '.join(f'{n} 0 R' for n in pages)+'] >>').encode()
buf=io.BytesIO(); buf.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'); offsets=[0]
for n,data in enumerate(objects,1):
    offsets.append(buf.tell()); buf.write(f'{n} 0 obj\n'.encode()+data+b'\nendobj\n')
start=buf.tell(); buf.write(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
for offset in offsets[1:]: buf.write(f'{offset:010d} 00000 n \n'.encode())
buf.write(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF'.encode())
(HERE/'Aticadores_LTDA_Apresentacao.pdf').write_bytes(buf.getvalue())
print('PDF e prévias gerados com sucesso.')
