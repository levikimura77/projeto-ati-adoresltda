"""Locais, personagens e funções da campanha de Atiçadores LTDA."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Role:
    title: tuple[str, str]
    skill: tuple[str, str]
    description: tuple[str, str]
    color: tuple[int, int, int]
    cooldown: float


ROLES = {
    "attack": Role(("Atacante", "Attacker"), ("Ruptura", "Breakthrough"),
                   ("Golpe próximo que quebra a guarda.", "A close-range strike that breaks guard."), (255, 111, 130), 8),
    "sprinter": Role(("Velocista", "Sprinter"), ("Dash", "Dash"),
                     ("Arrancada rápida na direção do movimento.", "Quick burst in your movement direction."),
                     (125, 220, 255), 3.5),
    "heal": Role(("Curandeiro", "Healer"), ("Recuperação", "Recovery"),
                 ("Recupera até dois corações.", "Restores up to two hearts."), (149, 239, 162), 15),
}


@dataclass(frozen=True)
class Resident:
    name: tuple[str, str]
    position: tuple[int, int]
    outfit: str
    lines: tuple[tuple[str, str], ...]
    required: bool = True


@dataclass(frozen=True)
class Room:
    chapter: int
    name: tuple[str, str]
    color: tuple[int, int, int]
    residents: tuple[Resident, ...]
    boss: tuple[str, str] | None = None


CHAPTERS = (
    ("Um novo integrante", "A new teammate"),
    ("Conquistar as salas", "Win over the rooms"),
    ("A Sala Branca", "The White Room"),
)

ROOMS = (
    Room(1, ("Sala Preta", "Black Room"), (94, 115, 161), (
        Resident(("Levi", "Levi"), (452, 360), "student", (
            ("Bem-vindo, {name}! Somos os Atiçadores LTDA da ETE Advogado José David Gil Rodrigues. Antes, o intervalo juntava as turmas no pátio para jogar dominó, bater papo e dar risada. A gente quer recuperar essa resenha.",
             "Welcome, {name}! We're Atiçadores LTDA from ETE Advogado José David Gil Rodrigues. At break, everyone used to meet in the courtyard to play dominoes, chat and laugh. We want those good times back."),
        )),
        Resident(("Reidryan", "Reidryan"), (642, 346), "student", (
            ("Ontem o horário do pátio sumiu do mural. Agora tem uma hierarquia escondida decidindo quem pode ficar na resenha. Se a gente juntar as turmas de novo, dá para escolher os horários em conjunto.",
             "Yesterday the courtyard schedule disappeared. Now a hidden hierarchy decides who gets to hang out. If we bring the groups together again, we can agree on the schedule together."),
        )),
        Resident(("Bruno", "Bruno"), (846, 342), "student", (
            ("A Sala Vermelha recebeu um bilhete sobre a troca. Rafa levou sua turma para o corredor. Escute o lado deles para descobrir o que separou a galera.",
             "The Red Room got a note about the switch. Rafa took his group into the hall. Hear them out and find out what drove everyone apart."),
        )),
        Resident(("Davi", "Davi"), (448, 485), "student", (
            ("Vou com o Jaylson dar cobertura nos desafios. Deixe a turma chamar a rodada e espere a abertura para agir.",
             "I'll back you up with Jaylson during the challenges. Let the other group call the round and wait for an opening."),
        )),
        Resident(("Jaylson", "Jaylson"), (813, 492), "student", (
            ("Espaço dá soco, o mouse lança papel e C ou Shift defende. Use Q para a sua especialidade. A gente ajuda durante as rodadas.",
             "Space punches, the mouse throws paper, and C or Shift blocks. Use Q for your special move. We'll help during the rounds."),
        )),
        Resident(("Jota", "Jota"), (1006, 420), "student", (
            ("Vou juntar os recados das salas com Reidryan. Se todos vieram da mesma pessoa, a gente consegue provar.",
             "I'll gather the notes with Reidryan. If they all came from the same person, we can prove it."),
        )),
        Resident(("Professora Marta", "Ms. Marta"), (278, 337), "teacher", (
            ("Podem conversar com as outras turmas durante o intervalo. Os desafios recreativos têm regras combinadas e param ao meu sinal.",
             "You can talk to the other groups during break. These games have agreed rules and stop when I signal."),
        ), False),
        Resident(("Seu Damião • inspetor", "Damião • hall monitor"), (1055, 260), "staff", (
            ("Foi depois do sinal que trocaram os avisos. Vou deixar o corredor aberto para vocês compararem os recados.",
             "The notices were swapped after the bell. I'll leave the hall open so you can compare notes."),
        ), False),
    )),
    Room(2, ("Corredores", "Hallways"), (74, 172, 188), (
        Resident(("Rafa • Sala Vermelha", "Rafa • Red Room"), (646, 330), "rival", (
            ("Quer ver o bilhete? Minha turma propõe uma rodada de força. Observe quando eu me preparar e use a defesa.",
             "Want to see the note? My group calls a round of strength. Watch me wind up and block."),
        )),
        Resident(("Davi", "Davi"), (304, 422), "student", (
            ("Tem espaço no meio do corredor. Vou ficar ao lado dos armários e dar cobertura daqui.",
             "There's room in the middle of the hall. I'll cover you from the lockers."),
        ), False),
    ), ("Rafa • Força", "Rafa • Strength")),
    Room(2, ("Refeitório", "Cafeteria"), (245, 182, 89), (
        Resident(("Dona Celina • merendeira", "Celina • cafeteria staff"), (307, 365), "staff", (
            ("Essa marca branca no bilhete também apareceu nos avisos da fila. A Bia viu quem deixou os envelopes.",
             "That white stamp on the note also appeared on the queue notices. Bia saw who dropped the envelopes."),
        )),
        Resident(("Bia • clube de robótica", "Bia • robotics club"), (646, 325), "rival", (
            ("Vamos fazer a rodada de mira que meu clube ensaiou. Eu jogo de longe. Use as mesas para se reposicionar e chegue perto.",
             "Let's play my club's aiming round. I throw from a distance. Move around the tables and close in."),
        )),
    ), ("Bia • Inteligência", "Bia • Strategy")),
    Room(2, ("Auditório", "Auditorium"), (173, 104, 155), (
        Resident(("Jaylson", "Jaylson"), (320, 440), "student", (
            ("O professor André ficou zangado. Recebeu um aviso falso de que a nossa turma ia tomar o palco. O registro verdadeiro está com ele.",
             "Mr. André is upset. A fake notice said our group would take over the stage. He has the original booking record."),
        )),
        Resident(("Prof. André", "Mr. André"), (649, 310), "rival", (
            ("Mudaram as reservas do meu auditório e botaram a culpa em vocês. Façam a prova de resistência do festival comigo e depois vamos conferir o livro.",
             "Someone changed my auditorium bookings and blamed you. Take the festival endurance challenge with me, then we'll check the ledger."),
            ("Minha guarda alterna com uma abertura. Se aprender a esperar o momento certo, você passa na prova.",
             "My guard alternates with an opening. Time it right and you'll pass the challenge."),
        )),
    ), ("Prof. André • Resistência", "Mr. André • Endurance")),
    Room(3, ("Sala Branca", "White Room"), (180, 206, 223), (
        Resident(("Jota", "Jota"), (321, 420), "student", (
            ("Reidryan comparou o mural, Bruno trouxe o bilhete, e eu juntei o registro do professor. Cada grupo recebeu uma mentira diferente. Todas levam à Sala Branca.",
             "Reidryan checked the board, Bruno brought the note, and I added the teacher's ledger. Every group got a different lie. They all lead to the White Room."),
        )),
        Resident(("Alex • Sala Branca", "Alex • White Room"), (646, 325), "rival", (
            ("Eu troquei os avisos. Com as turmas brigadas, a Sala Branca decidia quem entrava no pátio e quem ficava de fora da resenha. Agora que vocês chegaram juntos, proponho uma última rodada.",
             "I swapped the notices. With the groups fighting, the White Room decided who could use the courtyard and who got left out. Now that you've come together, I call one last round."),
        )),
    ), ("Alex • Sala Branca", "Alex • White Room")),
    Room(3, ("Pátio", "Courtyard"), (101, 173, 131), (
        Resident(("Levi", "Levi"), (460, 405), "student", (
            ("Conseguimos, {name}! As turmas voltaram a jogar juntas. Bruno trouxe o dominó e Reidryan já está montando as mesas.",
             "We did it, {name}! The groups are playing together again. Bruno brought dominoes and Reidryan is setting up the tables."),
        )),
        Resident(("Professora Marta", "Ms. Marta"), (782, 320), "teacher", (
            ("As turmas combinaram os novos horários. O pátio voltou a ser de toda a escola, e a resenha voltou com ele.",
             "The groups agreed on new times. The courtyard belongs to the whole school again, and everyone can hang out."),
        )),
        Resident(("Seu Damião • inspetor", "Damião • hall monitor"), (1017, 445), "staff", (
            ("Quadro atualizado e corredor aberto. Avisem lá no refeitório que hoje o dominó é no pátio!",
             "Schedule updated and hall open. Tell the cafeteria crew that dominoes are in the courtyard today!"),
        ), False),
    )),
)

VERDICTS = {
    1: ("A Sala Branca disse que vocês queriam expulsar a nossa turma. Se a ideia é fazer a resenha voltar para todo mundo, contem com a Sala Vermelha. A Bia viu um bilhete com o mesmo selo no refeitório.",
        "The White Room said you wanted our group out. If we're bringing everyone back together, count the Red Room in. Bia saw a note with the same stamp in the cafeteria."),
    2: ("Vi Alex deixando os envelopes. O professor André tem o livro de reservas original no auditório. Dá para comparar.",
        "I saw Alex dropping the envelopes. Mr. André has the original booking ledger in the auditorium. You can compare them."),
    3: ("Eu me precipitei. A assinatura do Alex está nos horários adulterados. Levem o livro e mostrem às outras turmas.",
        "I jumped to conclusions. Alex's signature is on the altered schedule. Take the ledger and show the other groups."),
    4: ("Eu vou devolver o quadro e contar às turmas o que fiz. Vamos combinar os horários juntos. O pátio e a resenha são de todo mundo.",
        "I'll return the board and tell the groups what I did. Let's agree on the schedule together. The courtyard is for everyone."),
}
