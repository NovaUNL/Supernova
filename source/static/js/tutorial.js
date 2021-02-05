(function () {
    const path = window.location.pathname;
    let panes = document.querySelectorAll('.pane');
    const ijs = introJs().setOptions({
        prevLabel: 'Voltar',
        nextLabel: 'Seguinte',
        doneLabel: 'Prosseguir'
    });
    switch (path) {
        case '/':
            ijs.setOptions({
                steps: [
                    {
                        title: 'Bem vindo',
                        intro: '<p style="min-width: min(750px, 90vw)">' +
                            '<img width="300px" src="/static/img/logo-alt.svg"><br>' +
                            'O Supernova é uma plataforma académica que visa melhorar a vida académica na FCT NOVA.<br>' +
                            'Este guia faz uma introdução à plataforma. (A tecla ➡ avança)</p>'
                    },
                    {
                        element: document.querySelector('.news-list-item'),
                        intro: 'O Supernova recolhe a informação disponível nos canais oficiais da FCT.',
                        position: 'top'
                    },
                    {
                        element: document.querySelector('#transportation-widget').parentNode,
                        intro: 'Agrega serviços externos de especial interesse.',
                        position: 'left'
                    },
                    {
                        element: document.querySelector('.question-list'),
                        intro: 'E promove a participação da comunidade.<br>' +
                            'Questões, resoluções ou partilha de conteúdos, tudo é bem vindo<br>' +
                            '<small>(admitindo o respeito pelos direitos autorais e docentes)</small>',
                        position: 'top'
                    },
                    {
                        element: document.querySelector('.user'),
                        intro: 'Existem contas no Supernova para limitar acesso a informações académicas privadas.<br>' +
                            'Para fazer uma conta é necessário um convite bem como um email da FCT.',
                        position: 'left'
                    },
                    {
                        intro: '<p style="min-width: min(700px, 90vw)">Este guia introduziu o conceito; ' +
                            'Uma segunda parte demonstra algumas funcionalidades.<br>' +
                            '<a href="/faculdade/cursos/?tutorial">Carregue aqui para continuar</a> ou proceda para ' +
                            '<b>fechar</b> o guia.<br>' +
                            'Para voltar a ver este guia poderá abrir o Supernova em navegação privada.</p>'
                    }
                ],
                doneLabel: 'Fechar'
            }).onexit(() => {
                localStorage.setItem("skipTutorial", "true");
            }).start();
            break;
        case '/faculdade/cursos/':
            ijs.setOptions({
                steps: [
                    {
                        element: document.querySelector("#nav-column li.active").parentNode.parentNode,
                        intro: 'O menu permite alcançar muita da informação',
                        position: 'right'
                    },
                    {
                        element: panes[0],
                        intro: 'Sendo que as páginas raiz listam as principais entidades.',
                        position: 'right'
                    },
                    {
                        element: document.querySelector('#search'),
                        intro: 'Todavia é possível pesquisar pelo desejado.',
                        position: 'bottom'
                    },
                    {
                        intro: 'As pesquisas podem ser globais ou aplicadas a uma categoria especifica.<br>' +
                            'Algumas das entidades requerem autenticação e cada pesquisa retorna ' +
                            'no máximo 10 resultados por entidade.',
                    }
                ],
                doneLabel: 'Prosseguir'
            }).onbeforechange(() => {
                if (ijs._currentStep === 3) {
                    showSearch();
                } else {
                    $('.pane-title .close').click();
                }
            }).oncomplete(() => {
                window.location.href = '/faculdade/departamento/5/?tutorial';
            }).start();
            break
        case '/faculdade/departamento/5/':
            ijs.setOptions({
                steps: [
                    {
                        element: panes[0],
                        intro: 'Nos departamentos estão as respetivas unidades curriculares.',
                        position: 'right',
                        scrollTo: "tooltip"
                    },
                    {
                        element: document.querySelector('sup'),
                        intro: 'O identificador que sucede cada UC. é o identificador do CLIP.<br>' +
                            'O CLIP oferece uma pesquisa por este identificador dentro do perfil em "Informação Geral".',
                        position: 'bottom'
                    },
                    {
                        element: panes[2],
                        intro: 'É ainda possível ver os cursos que <b>atualmente</b> são geridos por este departamento.<br>' +
                            'Esta atribuição é manual pelo que poderá estar incompleta.',
                        position: 'bottom'
                    },
                    {
                        element: panes[3],
                        intro: 'São ainda apresentados os docentes que historicamente já trabalharam para o departamento.<br>' +
                            'A listagem não é exaustiva, excluindo docentes com anos de inatividade.',
                        position: 'left'
                    }],
                doneLabel: 'Prosseguir'
            }).start().oncomplete(() => {
                window.location.href = '/servicos/?tutorial';
            });
            break
        case '/servicos/':
            ijs.setOptions({
                steps: [
                    {
                        title: 'Serviços',
                        intro: 'É possível visualizar informações a respeito dos serviços presentes no campus.<br>' +
                            'Para já, <b>nenhum dos serviços tem presença oficial no Supernova</b> e como tal as informações ' +
                            'não devem de ser consideradas representativas.'
                    }],
                doneLabel: 'Prosseguir'
            }).start().oncomplete(() => {
                window.location.href = '/servicos/cantina/?tutorial';
            });
            break
        case '/servicos/cantina/':
            ijs.setOptions({
                steps: [
                    {
                        element: panes[0].querySelector('.meal-list'),
                        intro: 'Nos locais de refeição constam ementas.',
                    },
                    {
                        element: panes[2],
                        intro: 'Em todos os serviços constam informações a respeito do serviço como horários e localização.',
                        position: 'left'
                    },
                    {
                        element: panes[1],
                        intro: 'Bem como preçários.',
                        position: 'top'
                    },
                ],
                doneLabel: 'Prosseguir'
            }).start().oncomplete(() => {
                window.location.href = '/faculdade/campus/edificio/2/?tutorial';
            });
            break
        case '/faculdade/campus/edificio/2/':
            ijs.setOptions({
                steps: [
                    {
                        element: panes[0].parentNode,
                        title: 'Edifícios.',
                        intro: 'Nos edifícios apresenta-se a informação relativa aos espaços, como a localização ' +
                            'geográfica e (eventualmente) informações de navegação interior.<br>' +
                            'Quem nunca se perdeu no departamental? :)',
                        position: 'bottom'
                    },
                    {
                        element: panes[2],
                        intro: 'São ainda enumeradas as diversas divisões do edifício.',
                        position: 'top'
                    },
                    {
                        element: panes[panes.length - 1],
                        intro: 'Os departamentos aqui sediados.',
                        position: 'left'
                    },
                    {
                        element: panes[panes.length - 2],
                        intro: 'E é possível observar a informação ocupacional, permitindo retirar conclusões como ' +
                            'salas potencialmente vazias (e portanto utilizáveis p.ex. para estudo).',
                        position: 'top',
                        scrollTo: "tooltip"
                    },
                ],
            }).start().oncomplete(() => {
                window.location.href = '/noticias/?tutorial';
            });
            break
        case '/noticias/':
            ijs.setOptions({
                steps: [
                    {
                        element: panes[0].querySelector('.news-list-item'),
                        title: 'Notícias',
                        intro: 'No portal das notícias são agregadas noticias que constam nos diversos portais da FCT.',
                        position: 'bottom'
                    },
                ],
                doneLabel: 'Prosseguir'
            }).start().oncomplete(() => {
                window.location.href = '/feedback/sugestoes?tutorial';
            });
            break
        case '/feedback/sugestoes':
            ijs.setOptions({
                steps: [
                    {
                        intro: 'Já no portal das sugestões transmitem-se opiniões com o intuito de ajudar as ' +
                            'entidades associadas à FCT a saber quais as melhorias desejadas.',
                        position: 'left'
                    },
                ],
            }).start().oncomplete(() => {
                window.location.href = '/grupos/?tutorial';
            });
            break
        case '/grupos/':
            ijs.setOptions({
                steps: [
                    {
                        title: 'Grupos',
                        intro: 'São listadas as entidades públicas coletivas da FCT, repartidas por quatro categorias:'
                    },
                    {
                        element: document.querySelector('[href="/grupos/AEFCT"]'),
                        title: 'Institucionais',
                        intro: 'Estipulou-se que as entidades institucionais são entidades geridas ou ' +
                            'fortemente acopladas à FCT.',
                        position: 'bottom'
                    },
                    {
                        element: document.querySelector('[href="/grupos/NEEC"]'),
                        title: 'Núcleos',
                        intro: 'Os núcleos são grupos de estudantes que são registados pela associação de estudantes ' +
                            'para realização de atividades no Campus.',
                        position: 'bottom'
                    },
                    {
                        element: document.querySelector('[href="/grupos/CPInformática"]'),
                        title: 'Pedagógicos',
                        intro: 'A categoria de pedagógicos isola os grupos cujo propósito é debater a pedagogia ' +
                            'dos cursos.',
                        position: 'bottom'
                    },
                    {
                        element: document.querySelector('[href="/grupos/SN"]'),
                        title: 'Comunidades',
                        intro: 'E por fim as comunidades identificam grupos não oficiais dentro da FCT.',
                        position: 'bottom'
                    },
                    {
                        element: document.querySelector("#m5").parentNode,
                        intro: 'Estes grupos são consultáveis por categoria no menu.',
                        position: 'right'
                    },
                ],
            }).start().oncomplete(() => {
                window.location.href = '/grupos/SN?tutorial';
            });
            break
        case '/grupos/SN':
            ijs.setOptions({
                scrollTo: "tooltip",
                steps: [
                    {
                        element: panes[0],
                        intro: 'Cada entidade pode descrever-se livremente.',
                        position: 'bottom'
                    },
                    {
                        element: panes[1],
                        intro: 'Os utilizadores tem acesso ao histórico de atividades...',
                        position: 'top'
                    },
                    {
                        element: panes[2],
                        intro: '...e à calendarização da entidade.',
                        position: 'top'
                    }
                ],
            }).start().oncomplete(() => {
                window.location.href = '/estudo/?tutorial';
            });
            break
        case '/estudo/':
            ijs.setOptions({
                steps: [
                    {
                        title: 'Sínteses',
                        intro: 'Acreditamos que existe um vasto catalogo de sínteses que todos os anos cai ' +
                            'no esquecimento, e que partilhar conhecimento é uma boa forma não só de o aprender como ' +
                            'de evoluirmos.',
                        position: 'bottom'
                    },
                    {
                        element: panes[1].querySelector('.class-synopsis'),
                        intro: 'Incentivamos assim que o conhecimento seja catalogado não só por unidade curricular.',
                        position: 'top'
                    },
                    {
                        element: panes[0].querySelector('.flex-grid-item'),
                        intro: 'Como também por área de estudo.',
                        position: 'bottom'
                    },
                ],
            }).start().oncomplete(() => {
                window.location.href = '/estudo/seccao/224/?tutorial';
            });
            break
        case '/estudo/seccao/224/':
            ijs.setOptions({
                steps: [
                    {
                        title: 'Secções',
                        intro: 'É estabelecido um grafo de conhecimento que segue a estrutura ' +
                            'area-subarea-secção-subsecções<br>' +
                            'As secções detém o conteúdo...',
                        position: 'right'
                    },
                    {
                        element: panes[1],
                        intro: '... bem como meta-dados, recursos externos, dúvidas e exercícios associados',
                        position: 'left'
                    },
                ],
            }).start().oncomplete(() => {
                window.location.href = '/estudo/seccao/224/exercicios/?tutorial';
            });
            break
        case '/estudo/seccao/224/exercicios/':
            ijs.setOptions({
                steps: [
                    {
                        title: 'Exercícios',
                        intro: 'Os utilizadores podem submeter exercícios, idealmente com as respetivas soluções.'
                    },
                    {
                        intro: 'São suportados três tipos de exercício:<br>' +
                            '<ul style="min-width: 300px"><li>Pares questão-resposta,</li>' +
                            '<li>Escolhas-múltiplas e</li>' +
                            '<li>Grupos com sub-exercícios.</li></ul>'

                    },
                    {
                        intro: 'Tenciona-se vir a tornar o processo de estudo mais dinâmico, ' +
                            'com avaliações automáticas e propostas de exercícios por utilizador.',
                    },
                ],
            }).start().oncomplete(() => {
                window.location.href = '/estudo/duvida/28/?tutorial';
            });
            break
        case '/estudo/duvida/28/':
            ijs.setOptions({
                steps: [
                    {
                        element: panes[0],
                        title: 'Questões',
                        intro: 'Os utilizadores podem colocar questões a respeito de qualquer temática; ' +
                            'tipicamente associadas a conteúdos, exercícios ou unidades curriculares.',
                        position: 'bottom'
                    },
                    {
                        element: panes[1],
                        title: 'Respostas',
                        intro: 'E qualquer um pode responder às questões colocadas.',
                        position: 'bottom'
                    },
                    {
                        element: panes[0].querySelector('.user'),
                        title: 'Reputação',
                        intro: 'A reputação é um mecanismo para prevenir o abuso da plataforma.' +
                            'Ações benéficas, como responder a dúvidas dos outros utilizadores aumentam a reputação. ' +
                            'Existem mínimos de reputação para publicar ou editar conteúdos no Supernova.',
                        position: 'left'
                    },
                ],
            }).start().oncomplete(() => {
                window.location.href = '/faq/?tutorial';
            });
            break
        case '/faq/':
            ijs.setOptions({
                steps: [
                    {
                        title: 'Fim da visita.',
                        intro: 'Esperamos que tenha gostado do conceito que apresentamos.<br>' +
                            'Existe muito mais para ver, todavia, por questões de privacidade terá que se autenticar ' +
                            'para aceder aos restantes conteúdos.<br>' +
                            'Perante o fecho desta mensagem terá a resposta a algumas questões comuns.',
                        position: 'bottom'
                    },
                ],
            }).start();
            break
    }
})();