#coding: utf-8

## @file CourseUnit.py
#   Este arquivo é responsável pelo armazenamento de todas as camadas 
# correspondentes ao módulo de curso. 
#   O módulo de curso é responsável por mostrar aos alunos as lições, bem como
# administrar a resolução e correção de exercícios.
#   Para tal, uma única janela é criada, e chamadas assíncronas são realizadas
# para atualizar seu conteúdo, sendo elas chamadas de atualização de slides.
#   Slides podem conter fragmentos de lições ou exercícios, depenendo de que
# ponto da lição o usuário está navegando - ou do próprio módulo.
#   O aluno só deve ser capaz de prosseguir no curso (lê-se ir para a próxima
# lição/módulo) se tiver obtido uma pontuação mínima na lição/módulo anterior.

from abc import*
from random import shuffle

import ELO.locale.index as lang

from ELO.models import (Courses, 
                        Module, 
                        Lesson, 
                        Exercise, 
                        Student, 
                        Messages,
                        Professor)

from Course.macros import ( LESSONS_URL, 
                            GENERAL_URL, 
                            EXERCISES_URL, 
                            CORRECT_URL,
                            WRONG_URL, 
                            ExerciseType
                          )

from Course.forms import (  LessonForm, 
                            ExerciseForm, 
                            MultipleChoiceExercise,
                            FillTheBlankExercise
                         )

from Profile.forms import QuestionForm

from django.middleware import csrf
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.forms import ValidationError
from django import template
import datetime

## Interface da camada de Apresentação do módulo de Curso.
#   É responsável pelo devido processamento do frame de curso; seleção de
# curso, módulo, lição e slide; formatação dos templates de exercícios; 
# bem como o processamento do primeiro nível da administração dos dados
# submetidos em exercícios.
class IfUiCourse:
    __metaclass__ = ABCMeta

    ## Força a criação da camada subjacente.
    def __init__(self, bus):
        try:
            self.bus = bus
        except TypeError as exc:
            del self
            raise exc

    @property
    def bus(self):
        return self.__bus

    @bus.setter
    def bus(self, value):
        if isinstance(value, IfBusCourse):
            self.__bus = value
        else:
            raise TypeError("Expected IfBusCourse instance at UiCourse.__bus. Received " + str(type(value)) + " instead.")

    @bus.deleter
    def bus(self):
        del self.__bus

    ## run() é o principal método de qualquer classe de apresentação.
    #   Este método permite à Factory (ver MainUnit.py) dar controle
    #   do programa para este módulo.
    #
    #   @arg request    Objeto HttpRequest enviado pela requisição do navegador
    #
    #   @arg courseid   Identificador do curso.
    #                       Deve necessariamente ser um inteiro validado
    #                       através do objeto Id (vide BaseUnit.py).
    @abstractmethod
    def run(self, request, courseid=None): pass


## Interface da camada de Negócio do módulo de Curso.
#   É responsável pelo processamento inteligente dos dados, validação
# e recuperação de dados.
#   Esta camada é a interface necessária de comunicação entre a camada
# de apresentação - o usuário - e a camada de persistência - o servidor.
class IfBusCourse:
    __metaclass__ = ABCMeta

    ## Garante a criação da camada subjacente.
    def __init__(self, pers):
        try:
            self.pers = pers
        except TypeError as exc:
            del self
            raise exc

    @property
    def pers(self):
        return self.__pers
    
    @pers.setter
    def pers(self, value):
        if isinstance(value, IfPersCourse):
            self.__pers = value
        else:
            raise TypeError("Expected IfPersCourse instance at BusCourse.__pers. Received " + str(type(value)) + "instead.")

    @pers.deleter
    def pers(self):
        del self.__pers


    ## Método que recupera uma lista dos módulos ou lições.
    #
    #   @arg user       Objeto usuário, como no contido no cookie user.
    #
    #   @arg accesstype String contendo "MODULE", "LOCK" ou "LESSON"
    #
    #   @return         Lista contendo todas os módulos cadastrados,
    #                       lições destravadas ou cadastrados para o
    #                       usuário 'user', variando sob o argumento
    #                       accesstype.
    @abstractmethod
    def getCompleted(self, user, accesstype): pass

    ## Método que recupera um objeto que representa um curso.
    #
    #   @arg user       Objeto usuário, como no contido no cookie user.
    #
    #   @arg courseid   Identificador do curso.
    #                       Deve ser um inteiro de acordo com o padrão de Id().
    #
    #   @return         Retorna um objeto curso com os seguintes atributos:
    #                       - NAME    : Identifica o nome do curso;
    #                       - ID      : Identifica univocamente o curso;
    #                       - STUDENTS: Lista de Ids de alunos cadastrados;
    #                       - MODULES : Lista de dicionários que representam
    #                                       cada um dos módulos.
    @abstractmethod
    def getCourse(self, user, courseid): pass

    ## Método que recupera um objeto que representa uma lição.
    #
    #   @arg lessonid   Identificador do curso.
    #                       Deve ser um inteiro de acordo com o padrão de Id().
    #
    #   @return         Retorna um objeto lição, com os seguintes atributos:
    #                       - url       : Caminho para a lição a partir de
    #                                     ELO/templates/Course/lessons/;
    #                       - name      : Nome da lição;
    #                       - slides    : Número de slides da lição em questão;
    #                       - exercises : Lista de ids de exercícios que a
    #                                       lição possui.
    @abstractmethod
    def getLesson(self, lessonid): pass

    ## Método que cria e formata um objeto que representa um exercício.
    #
    #   @arg ex_url     Objeto Link()-compatível que leva ao exercício.
    #   
    #   @arg request    Objeto request fornecido pelo navegador.
    #
    #   @return         Retorna um objeto exercício.
    @abstractmethod
    def createExercise(self, request, ex_url): pass

    ## Método que corrige um exercício.
    #
    #   @arg ex_url     Objeto Link()-compatível que leva ao exercício.
    #
    #   @arg answer     Resposta fornecida pelo usuário.
    #
    #   @return         Booleano: true significa certo e false, errado.
    @abstractmethod
    def correctExercise(self, ex_url, answer): pass

    @abstractmethod
    def getNewQuestionId(self): pass

    @abstractmethod
    def registerQuestion(self, request, user, time):pass


## Interface da camada de Persistência para o módulo de Curso.
#   Deve ser capaz de acessar de forma transparente o banco de dados.
#   Deve também ser a única forma de acessar tais dados dentro deste módulo.
class IfPersCourse:

    ## Pseudométodo que faz a chamada dos métodos atômicos desta camada.
    #
    #   @arg    s   self
    #
    #   @arg    x   field   Nome do campo a ser filtrado.
    #
    #   @arg    y   value   Valor que deve haver no campo.
    #
    #   @arg    z   dbase   Objeto do modelo a ser utilizado.
    #                           Deve ser importado de ELO.models.
    retrieve=lambda s,x,y,z: s.fetch(s.getid(x, y, z), z)

    ## Método que recupera o Id() de um objeto.
    #
    #   @arg field  Nome do campo a ser filtrado.
    #
    #   @arg value  Valor que deve haver no campo.
    #
    #   @arg db     Objeto do modelo a ser utilizado.
    #                   Deve ser importado de ELO.models.
    @abstractmethod
    def getid(self, field, value, db): pass

    ## Realiza uma pesquisa no banco de dados.
    #
    #   @arg id     Identificador do objeto requisitado.
    #                   Pode ser obtido através do método getid().
    #   
    #   @arg db     Objeto do modelo a ser utilizado.
    #                   Deve ser importado de ELO.models.
    @abstractmethod
    def fetch(self, id, db): pass

    @abstractmethod
    def fetchCourse(self, lid): pass

    @abstractmethod
    def fetchProfessor(self, cid): pass

    @abstractmethod
    def getQuestionId(self): pass

    @abstractmethod
    def questionIn(seld, newid, m_values):pass


class UiCourse(IfUiCourse):

    def run(self, request, courseid=None):
        
        user = request.session['user']

        if request.method == "GET":
            if courseid:
                if courseid in map(lambda x: x["id"], user["courses"]):
                    course = self.bus.getCourse(user, courseid)
                    return render(request, GENERAL_URL("frame.html"), 
                        {'course':course})
                else:
                    ld = lang.DICT
                    raise PermissionDenied(ld["EXCEPTION_403_STD"])
            else:   
                raise PermissionDenied(lang.DICT["EXCEPTION_403_STD"])

        elif request.method == "POST":
            lesson_form = LessonForm(request.POST)
            
            # É importante fazer a cópia, para que seja possível
            # modificá-la na linha abaixo.
            exercise_form = ExerciseForm(request.POST.copy())
            
            # É importante limpar a form, já que a classe mãe não possui
            # opções válidas.
            exercise_form.data['options'] = []
            try:
                if lesson_form.is_valid():
                    lessonid = lesson_form.cleaned_data['lesson_id']
                    lessonid = lessonid.value

                    slidenum = lesson_form.cleaned_data['slide_number']
                    slidenum = slidenum.value

                    lesson = self.bus.getLesson(lessonid)
                    maxslides = lesson['slides']+len(lesson['exercises'])

                    if 'question' in request.POST:
                        sub = False
                        exc = False
                        q_id = None
                        e_id = None
                        q_form = QuestionForm()

                        if not 'question_id' in request.POST:
                            q_id = self.bus.getNewQuestionId() 
                            
                            if slidenum >= lesson['slides']:
                                e_id = slidenum - lesson['slides']     
                        else:
                            try: 
                                q_form = QuestionForm(request.POST)
                                
                                if q_form.is_valid():
                                    time = datetime.datetime.now()
                                    self.bus.registerQuestion(request, user, time)
                                    q_id = q_form.cleaned_data['question_id']
                                    sub = True
                                else: 
                                    # TODO LANG
                                    raise ValueError(q_form.errors)
                            except ValueError as exce:
                                exc = exce      

                        print type(slidenum)
                        print slidenum

                        return render(request, 'Course/quest.html', 
                                {'lesson_id': lessonid, 'slide_number': slidenum,
                                'exercise_id': e_id, 'question_id': q_id, 
                                'form': q_form, 'sub': sub, 'exc': exc}) 
                    else:
                        gc = self.bus.getCompleted

                        if unicode(lessonid) not in gc(user, 'LOCK') and\
                           unicode(lessonid) not in gc(user, 'LESSON'):
                                ld = lang.DICT
                                raise PermissionDenied(ld["EXCEPTION_403_STD"])


                        if slidenum >= maxslides or slidenum < 0:
                            raise PermissionDenied(lang.DICT["EXCEPTION_403_STD"])

                        if slidenum < lesson['slides']:
                            lurl = lesson['url']
                            url = LESSONS_URL(lurl + "/" + str(slidenum) + ".html")

                            return render(request, url, { 'max': maxslides })
                        else:
                            exercise_id = slidenum - lesson['slides']
                            exercise_url = lesson['exercises'][exercise_id]
                            url = EXERCISES_URL(exercise_url + ".html")

                            exercise=self.bus.createExercise(request, exercise_url)

                            return render(request, url, { 'max': maxslides,
                                                          'exercise': exercise })
                elif exercise_form.is_valid():
                    exerciseId = exercise_form.cleaned_data["exercise_id"]

                    if 'question_form' in request.POST:
                        q_id = self.bus.getNewQuestionId() 

                        return render(request, 'Course/quest.html', 
                            {'exercise_id':exerciseId, 'question_id': q_id, 
                            'form' : q_form, 'sub':sub, 'exc': exc})    

                    try:
                        if self.bus.correctExercise(request.POST, exerciseId):
                            return render(request, CORRECT_URL)
                        else:
                            return render(request, WRONG_URL)
                    except ValueError:
                        raise ValueError(lang.DICT['EXCEPTION_INV_ANS'])
                else:
                    print exercise_form.errors
                    raise ValueError(lang.DICT['EXCEPTION_INV_LES'])
            except ValueError as exc:
                return render(request, GENERAL_URL("assync_std.html"),
                        {'error': exc})
            

class BusCourse(IfBusCourse):

    def getCompleted(self, user, accesstype):
        userdata = self.pers.retrieve('NAME', user['name'], Student)

        return userdata.get(accesstype + '_COMPLETED', [])

    def getCourse(self, user, courseid):
        compmlist = self.getCompleted(user, 'MODULE')
        compllist = self.getCompleted(user, 'LESSON')
        ulocklist = self.getCompleted(user, 'LOCK')
        coursedata = self.pers.fetch(courseid, Courses)
        modulelist = []
        
        for moduleid in coursedata['MODULE']:
            sfm = self.pers.fetch(moduleid, Module)
            modulename = sfm['NAME'][0]

            lessonlist = []

            for lessonid in sfm['LESSON']:
                lessoname = self.pers.fetch(lessonid, Lesson)['NAME']
                lessoncomplete = True if lessonid in compllist else False
                lessonunlocked = True if lessonid in ulocklist else False
                lessonlist = lessonlist + [{'id': lessonid,
                                            'name':lessoname[0],
                                            'complete':lessoncomplete,
                                            'unlocked':lessonunlocked }]

            modulelist = modulelist + [{'id':       moduleid,
                                        'name':     modulename,
                                        'lessons':  lessonlist,
                                        'complete':True \
                                            if moduleid in compmlist \
                                            else False
                                      }]
        
        coursedata['MODULE'] = sorted(modulelist, key=lambda x: x['id'])
        return coursedata

    def getLesson(self, lessonid):

        lessondata = self.pers.fetch(lessonid, Lesson)

        lesson = {}
        exercises_url = []
        lesson['url'] = lessondata['LINK'][0]
        lesson['name'] = lessondata['NAME'][0]
        lesson['slides'] = int(lessondata['SLIDES'][0])

        for e_id in lessondata['EXERCISE']:
            e_link = self.pers.fetch(e_id, Exercise)['LINK']
            exercises_url = exercises_url + e_link

        lesson['exercises'] = exercises_url

        return lesson

    def createExercise(self, request, ex_url):

        ex_id = self.pers.getid('LINK', ex_url, Exercise)
        ex_data = self.pers.fetch(ex_id, Exercise)

        exercise = {'url': ex_url, 
                    'type': int(ex_data['TYPE'][0]),
                    'csrf': csrf.get_token(request) if request else None,
                    'id': ex_id}

        exerciseType = int(ex_data['TYPE'][0])

        ## Exercício de Múltipla Escolha.
        #
        #   TYPE: 1
        #   ITEM_k, k natural: nome da k-ésima opção
        #   CORRECT: k | k é a resposta correta
        if exerciseType == ExerciseType.MultipleChoice:
            options = []
            i = "1"
            while "ITEM_" + i in ex_data:
                options.append((int(i),ex_data["ITEM_" + i][0]))
                i = str(int(i)+1)

            exercise['options'] = options

        ## Exercício de preencher o vazio.
        #
        #   TYPE: 2
        #   CORRECT: uma das possíveis soluções
        elif exerciseType == ExerciseType.FillTheBlank:
            pass # nothing to do here

        ## Exercício de desembaralhar.
        #
        #   TYPE: 3
        #   WORD_k, k natural: k-ésima palavra a ser desembaralhada.
        elif exerciseType == ExerciseType.Unscramble:
            words = []
            i = "1"
            while "WORD_" + i in ex_data:
                words.append((int(i), ex_data["WORD_" + i][0]))
                i = str(int(i)+1)

            exercise['words'] = shuffle(words)

        ## Exercício de Palavras-cruzadas.
        #
        #   TYPE: 4
        #   WORD: palavra que pode ser dividida em xydw:
        #       x: coordenada x da primeira letra da palavra dentro da matriz;
        #       y: coordenada y da primeira letra da palavra dentro da matriz;
        #       d: direção em que a palavra cresce ('N', 'S', 'W', 'E');
        #       w: palavra propriamente dita.
        elif exerciseType == ExerciseType.CrossWords:
            wordList = []
            
            for word in ex_data["WORD"]:
                x,y,d,w = word.split()
                wordlist.append({'x':x,
                                 'y':y,
                                 'direction':d,
                                 'size':str(len(w)),})

            exercise['words'] = wordList

        ## Exercício de Arrastar e Soltar.
        #
        #   TYPE: 5
        #   ITEM_k, k natural: k-ésima imagem
        elif exerciseType == ExerciseType.DragAndDrop:
            left = []
            right = []
            i = "1"

            while "ITEM_" + i in ex_data:
                left.append(ex_data["ITEM_" + i][0])
                right.append(ex_data["ITEM_" + i][1])
                
                i = str(int(i)+1)

            shuffle(right)
            shuffle(left)

            exercise['left'] = left
            exercise['right'] = right
            exercise['number'] = len(images)

        return type("Exercise", (), exercise)

    def correctExercise(self, request, exid):

        ex_data = self.pers.fetch(exid.value, Exercise)
        exerciseType = int(ex_data['TYPE'][0])

        if exerciseType == ExerciseType.MultipleChoice:

            dummy = self.createExercise(None, ex_data['LINK'][0])

            answer = MultipleChoiceExercise(dummy.options)(request)

            try:
                if answer.is_valid():
                    answer = answer.cleaned_data['options']
                    return True if answer == ex_data['CORRECT'][0] \
                                else False
                else:
                   raise ValueError()
            except ValueError as exc:
                print exc
                raise ValueError()

        elif exerciseType == ExerciseType.FillTheBlank:
            
            answer = FillTheBlankExercise(request)

            if answer.is_valid():
                answer = answer.cleaned_data['blank']
                return True if answer in ex_data['CORRECT'] \
                            else False
            else:
                raise ValueError()

        elif exerciseType == ExerciseType.Unscramble:

            answer = UnscrambleExercise(request)

            if answer.is_valid():
                answer = answer.cleaned_data['bloat']
                i = "1"
                while "WORD_" + i in ex_data:
                    if answer[i] != ex_data["WORD_" + i][0]:
                        return False
                return True
            else:
                raise ValueError()

        elif exerciseType == ExerciseType.CrossWords:
        
            answer = CrossWordsExercise(request)

            if answer.is_valid():
                answer = answer.cleaned_data['bloat']

                for ans in ex_data["WORD"]:
                    if not (ans in answer):
                        return False
                return True
            else:
                raise ValueError()

        elif exerciseType == ExerciseType.DragAndDrop:

            answer = DragAndDropExercise(request)

            if answer.is_valid():
                answer = answer.cleaned_data['bloat']

                i = "1"
                while "ITEM_" + i in ex_data:
                    if ex_data["ITEM_" + i][0] != answer[i]:
                        return False

                return True
            else:
                raise ValueError()

        else: return False

    def getNewQuestionId(self):
        qid = self.pers.getQuestionId()

        return qid

    def registerQuestion(self, request, user, time):
        lid = request.POST['lesson_id']
        slid = request.POST['slide_number']

        cid = self.pers.fetchCourse(lid)
        pofc = str(self.pers.fetchProfessor(cid))
        sid = str(self.pers.getid("NAME", user['name'], Student))

        m_values = {'SEND': sid+'S', 'RECEV': pofc+'P', 
                'HOUR': str(time.hour)+':'+str(time.minute) ,
                'DATE': str(time.day)+'-'+str(time.month)+'-'+str(time.year),
                'MESS': request.POST['question'], 'LESSON': lid, 
                'SLIDE': slid}

        if request.POST['exercise_id'] != 'None':
            m_values['EXERCISE'] = request.POST['exercise_id']

        self.pers.questionIn(request.POST['question_id'],m_values)

class PersCourse(IfPersCourse):

    def getid(self, field, value, db):
        try:
            model_data = db.objects.get(field=field, value=value)
            return model_data.identity
        except db.DoesNotExist as exc:
            raise ValueError(exc)

    def fetch(self, id, db):
        model_data = db.objects.filter(identity=id)
        format_data = {}

        ## @for
        #   Cria um dicionário de listas, no fomato:
        #
        #   CAMPO_NO_BANCO_DE_DADOS => [ VALOR_1, VALOR_2 ... VALOR_N ]
        for i in model_data.values():
            format_data[i['field']]=format_data.get(i['field'],[])+[i['value']]

        return format_data

    def fetchCourse(self, lid):
        cid = None

        try:
            lesson = Lesson.objects.get(identity=lid, field="COURSE")
            cid = lesson.value

        except (database.DoesNotExist, 
            database.MultipleObjectsReturned) as exc: 
            raise ValueError(exc)

        return cid

    def fetchProfessor(self, cid):
        pid = None

        try:
            prof = Professor.objects.get(field="COURSE")
            pid = prof.identity

        except (Professor.DoesNotExist, 
            Professor.MultipleObjectsReturned) as exc: 
            raise ValueError(exc)

        return pid

    def getQuestionId(self):
        try:
            # Coleta o ultimo ID inserido.
            lastid = Messages.objects.order_by('-identity')[0]
            newid = lastid.identity+1
        except IndexError:
            newid = 1

        return newid
        
    def questionIn(seld, newid, m_values):
        # Percorre o dicionário ligado aos campos a seu valores.
        for fields in m_values:
            # Insere novos dados: identidade, campo e a novo valor.
            data = Messages(identity=newid, field=fields,
                             value=m_values[fields])
            # Salva os novos dados no database.
            data.save()

