class Period:
    ANNUAL = 1
    FIRST_SEMESTER = 2
    SECOND_SEMESTER = 3
    FIRST_TRIMESTER = 4
    SECOND_TRIMESTER = 5
    THIRD_TRIMESTER = 6
    FOURTH_TRIMESTER = 7

    CHOICES = (
        (ANNUAL, 'Anual'),
        (FIRST_SEMESTER, '1º semestre'),
        (SECOND_SEMESTER, '2º semestre'),
        (FIRST_TRIMESTER, '1º trimestre'),
        (SECOND_TRIMESTER, '2º trimestre'),
        (THIRD_TRIMESTER, '3º trimestre'),
        (FOURTH_TRIMESTER, '4º trimestre'),
    )

    SHORT_CHOICES = ('', 'S1', 'S2', 'T1', 'T2', 'T3', 'T4')


class ShiftType:
    THEORETICAL = 1
    PRACTICAL = 2
    PRACTICAL_THEORETICAL = 3
    SEMINAR = 4
    TUTORIAL_ORIENTATION = 5
    FIELD_WORK = 6
    THEORETICAL_ONLINE = 7
    PRACTICAL_ONLINE = 8
    PRACTICAL_THEORETICAL_ONLINE = 9
    CHOICES = (
        (THEORETICAL, 'Teórico'),
        (PRACTICAL, 'Prático'),
        (PRACTICAL_THEORETICAL, 'Teórico-pratico'),
        (SEMINAR, 'Seminário'),
        (TUTORIAL_ORIENTATION, 'Orientação tutorial'),
        (FIELD_WORK, 'Trabalho de campo'),
        (THEORETICAL_ONLINE, 'Teórico Online'),
        (PRACTICAL_ONLINE, 'Prático Online'),
        (PRACTICAL_THEORETICAL_ONLINE, 'Teórico-Pratico Online'),
    )
    ABBREVIATIONS = {
        THEORETICAL: 'T',
        PRACTICAL: 'P',
        PRACTICAL_THEORETICAL: 'TP',
        SEMINAR: 'S',
        TUTORIAL_ORIENTATION: 'OT',
        FIELD_WORK: 'TC',
        THEORETICAL_ONLINE: 'TO',
        PRACTICAL_ONLINE: 'PO',
        PRACTICAL_THEORETICAL_ONLINE: 'OP'
    }

    @staticmethod
    def abbreviation(shift_type):
        if shift_type in ShiftType.ABBREVIATIONS:
            return ShiftType.ABBREVIATIONS[shift_type]
        return ""

    @staticmethod
    def min():
        return ShiftType.THEORETICAL

    @staticmethod
    def max():
        return ShiftType.PRACTICAL_THEORETICAL_ONLINE


class RoomType:
    GENERIC = 1
    CLASSROOM = 2
    AUDITORIUM = 3
    LABORATORY = 4
    COMPUTER = 5
    MEETING = 6
    MASTERS = 7
    CABINET = 8

    CHOICES = (
        (GENERIC, 'Genérico'),
        (CLASSROOM, 'Sala de aula'),
        (AUDITORIUM, 'Auditório'),
        (LABORATORY, 'Laboratório'),
        (COMPUTER, 'Sala de computadores'),
        (MEETING, 'Sala de reuniões'),
        (MASTERS, 'Sala de mestrados'),
        (CABINET, 'Gabinete'),
    )
    ABBREVIATIONS = {
        GENERIC: 'Sala',
        CLASSROOM: 'Sala',
        AUDITORIUM: 'Aud.',
        LABORATORY: 'Lab.',
        COMPUTER: 'Comp.',
        MEETING: 'Sala',
        MASTERS: 'Sala',
        CABINET: 'Gabin.',
    }

    @staticmethod
    def plural(room_type):
        plurals = {1: 'Salas',
                   2: 'Salas de aula',
                   3: 'Auditórios',
                   4: 'Laboratórios',
                   5: 'Salas de computadores',
                   6: 'Salas de reuniões',
                   7: 'Salas de mestrados',
                   8: 'Gabinetes'}
        if room_type not in plurals:
            return None
        return plurals[room_type]


class EventSeason:
    NORMAL = 1
    EXAM = 2
    SPECIAL = 3

    CHOICES = (
        (NORMAL, 'Epoca normal'),
        (EXAM, 'Epoca de exame'),
        (SPECIAL, 'Epoca especial'),
    )


class EventType:
    TEST = 1
    EXAM = 2
    DISCUSSION = 3
    FIELD_TRIP = 4
    PROJECT_ANNOUNCEMENT = 5
    PROJECT_DELIVERY = 6
    ADDITIONAL_CLASS = 7
    PRESENTATION = 8
    SEMINAR = 9
    TALK = 10

    CHOICES = (
        (TEST, 'Teste'),
        (EXAM, 'Exame'),
        (DISCUSSION, 'Discussão'),
        (FIELD_TRIP, 'Viagem'),
        (PROJECT_ANNOUNCEMENT, 'Enúnciação'),
        (PROJECT_DELIVERY, 'Entrega'),
        (ADDITIONAL_CLASS, 'Aula'),
        (PRESENTATION, 'Apresentação'),
        (SEMINAR, 'Seminário'),
        (TALK, 'Palestra'),
    )


class FileType:
    IMAGE = 1
    SLIDES = 2
    PROBLEMS = 3
    PROTOCOL = 4
    SEMINAR = 5
    EXAM = 6
    TEST = 7
    SUPPORT = 8
    OTHERS = 9

    CHOICES = (
        (IMAGE, 'Imagem'),
        (SLIDES, 'Slides'),
        (PROBLEMS, 'Problemas'),
        (PROTOCOL, 'Protolos'),
        (SEMINAR, 'Seminário'),
        (EXAM, 'Exame'),
        (TEST, 'Teste'),
        (SUPPORT, 'Suporte'),
        (OTHERS, 'Outros'),
    )


class FileLicense:
    RIGHTS_RESERVED = 0
    PUBLIC_DOMAIN = 1
    GPL = 2
    MIT = 3
    BSD = 4
    CC_BY = 5
    CC_BY_SA = 6
    CC_BY_NC = 7
    CC_BY_SA_NC = 8
    GENERIC_PERMISSIVE = 100

    CHOICES = (
        (RIGHTS_RESERVED, 'Todos os direitos reservados'),
        (PUBLIC_DOMAIN, 'Domínio Público'),
        (GPL, 'GPLv3'),
        (MIT, 'MIT'),
        (BSD, 'BSD'),
        (CC_BY, 'Creative Commons BY'),
        (CC_BY_SA, 'Creative Commons BY-SA'),
        (CC_BY_NC, 'Creative Commons BY-NC'),
        (CC_BY_SA_NC, 'Creative Commons BY-SA-NC'),
        (GENERIC_PERMISSIVE, 'Permissiva genérica'),
    )


class FileVisibility:
    PUBLIC = 0
    STUDENTS = 1
    ENROLLED = 2
    NOBODY = 3

    CHOICES = (
        (PUBLIC, 'Todos'),
        (STUDENTS, 'Estudantes'),
        (ENROLLED, 'Inscritos'),
        (NOBODY, 'Ninguém'),
    )


WEEKDAY_CHOICES = (
    (0, 'Segunda-feira'),
    (1, 'Terça-feira'),
    (2, 'Quarta-feira'),
    (3, 'Quinta-feira'),
    (4, 'Sexta-feira'),
    (5, 'Sábado'),
    (6, 'Domingo')
)


class Degree:
    BACHELORS = 1
    MASTERS = 2
    PHD = 3
    INTEGRATED_MASTERS = 4
    POST_GRADUATION = 5
    ADVANCED_STUDIES = 6
    PRE_GRADUATION = 7

    CHOICES = (
        (BACHELORS, 'Licenciatura'),
        (MASTERS, 'Mestrado'),
        (PHD, 'Doutoramento'),
        (INTEGRATED_MASTERS, 'Mestrado Integrado'),
        (POST_GRADUATION, 'Pos-Graduação'),
        (ADVANCED_STUDIES, 'Estudos Avançados'),
        (PRE_GRADUATION, 'Pré-Graduação'),
    )
    ABBREVIATIONS = {
        BACHELORS: 'L',
        MASTERS: 'M',
        PHD: 'D',
        INTEGRATED_MASTERS: 'Mi',
        POST_GRADUATION: 'Pg',
        ADVANCED_STUDIES: 'EA',
        PRE_GRADUATION: 'pG'
    }

    @staticmethod
    def abbreviation(degree: int):
        if degree in range(0, 7):
            return Degree.ABBREVIATIONS[degree]
        return ""

    @staticmethod
    def name(degree: int):
        if degree in range(1, 8):
            return Degree.CHOICES[degree - 1][1]
        return "Estágio"  # AKA, Nothing, Nilch, Nada
