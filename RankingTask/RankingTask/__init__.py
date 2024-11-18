from otree.api import *
import random
from random import randint

doc = """
Ranking Task: Preliminary Survey
"""


class C(BaseConstants):
    NAME_IN_URL = 'RankingTask'
    PLAYERS_PER_GROUP = None
    NUM_PAIRS = 21
    TASKS = ['homocide', 'research', 'trust', 'movie', 'area', 'gasoline']
    NUM_ROUNDS = len(TASKS) * NUM_PAIRS + len(TASKS) * 2
    COUNTRIES = ['カナダ', 'フランス', 'ドイツ', 'イタリア', '日本', 'イギリス', 'アメリカ']
    MOVIES = ['THE FIRST SLAM DUNK', '名探偵コナン 黒鉄の魚影', '君たちはどう生きるか', 'キングダム 運命の炎', 'ゴジラ-1.0', 'ミステリと言う勿れ', '劇場版『TOKYO MER〜走る緊急救命室〜』']
    AREA = ['北海道', '岩手県', '福島県', '長野県', '秋田県', '新潟県', '岐阜県']
    GASOLINE = ['愛知県', '東京都', '北海道', '埼玉県', '神奈川県', '千葉県', '大阪府', '福岡県']

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    informed_consent = models.CharField(initial = None,
                                        choices = ['私は、以上の説明を理解したうえで、本調査に参加することに同意します。'],
                                        widget = widgets.RadioSelect()
                                        )
    id_number = models.IntegerField(initial = None,
                                    verbose_name = 'あなたのID番号を入力してください。'
                                    )
    gender = models.CharField(initial = None,
                              choices = ['男性', '女性', '回答しない'],
                              verbose_name = 'あなたの性別を教えてください。',
                              widget = widgets.RadioSelect()
                              )
    age = models.IntegerField(initial = None,
                              verbose_name = 'あなたの年齢を教えてください。'
                              )
    ranking_task = models.LongStringField()

# FUNCTION
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        for p in subsession.get_players():
            task_order = C.TASKS.copy()
            random.shuffle(task_order)
            task_rounds = {
                task: (order + 1, start, start + 1, range(start + 2, start + 23)) # order number, announce page, instruction page, task_page
                # for order, (task, start) in enumerate(zip(task_order, range(1, C.NUM_ROUNDS + 1, 22)))
                for order, (task, start) in enumerate(zip(task_order, range(1, C.NUM_ROUNDS + 1, 23)))
                }
            print('player', p.id_in_subsession)
            print('task_rounds is', task_rounds)
            p.participant.task_rounds = task_rounds

# PAGES
class InformedConsent(Page):
    form_model = 'player'
    form_fields = ['informed_consent']
    
    def is_displayed(player):
        return player.round_number == 1


class Demographic(Page):
    form_model = 'player'
    form_fields = ['id_number', 'gender', 'age']
    
    def is_displayed(player):
        return player.round_number == 2

class Instruction1(Page):
    form_model = 'player'
    
    def is_displayed(player):
        return player.round_number == 3
    
class Instruction2(Page):
    form_model = 'player'
    
    def is_displayed(player):
        return player.round_number == 4

class Instruction3(Page):
    form_model = 'player'
    
    def is_displayed(player):
        return player.round_number == 5

class Instruction4(Page):
    form_model = 'player'
    
    def is_displayed(player):
        return player.round_number == 6

class Instruction5(Page):
    form_model = 'player'
    
    def is_displayed(player):
        return player.round_number == 7

class Instruction6(Page):
    form_model = 'player'
    
    def is_displayed(player):
        return player.round_number == 8

class Instruction7(Page):
    form_model = 'player'
    
    def is_displayed(player):
        return player.round_number == 9

class Instruction8(Page):
    form_model = 'player'
    
    def is_displayed(player):
        return player.round_number == 10

class Instruction9(Page):
    form_model = 'player'
    
    def is_displayed(player):
        return player.round_number == 11

class HomocideAnnounce(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['homocide'][1] + 11
    
    @staticmethod
    def vars_for_template(player):
        task_order = player.participant.vars['task_rounds']['homocide'][0]
        return {'task_order': task_order}

class HomocideInstruction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['homocide'][2] + 11

class HomocideTask(Page):
    form_model = 'player'
    form_fields = ['ranking_task']
    
    @staticmethod
    def is_displayed(player: Player):
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['homocide'][3]] 
        return player.round_number in task_rounds
    
    @staticmethod
    def vars_for_template(player):
        if 'random_pairs_homocide' not in player.session.vars:
            countries = C.COUNTRIES.copy()
            random.shuffle(countries)
            pairs = [(countries[i], countries[j]) for i in range(len(countries)) for j in range(i + 1, len(countries))]
            random_pairs_homocide = random.sample(pairs, C.NUM_PAIRS)
            random_pairs_homocide = [(pair[1], pair[0]) if randint(0, 1) == 1 else pair for pair in random_pairs_homocide]
            player.session.vars['random_pairs_homocide'] = random_pairs_homocide
        
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['homocide'][3]]
        question_index = player.round_number - min(task_rounds)
        current_pair = player.session.vars['random_pairs_homocide'][question_index]
        
        return {
            'pair_num': question_index + 1,
            'country1': current_pair[0],
            'country2': current_pair[1]
        }

class ResearchAnnounce(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['research'][1] + 11
    
    @staticmethod
    def vars_for_template(player):
        task_order = player.participant.vars['task_rounds']['research'][0]
        return {'task_order': task_order}

class ResearchInstruction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['research'][2] + 11

class ResearchTask(Page):
    form_model = 'player'
    form_fields = ['ranking_task']
    
    @staticmethod
    def is_displayed(player: Player):
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['research'][3]]
        return player.round_number in task_rounds
    
    @staticmethod
    def vars_for_template(player):
        if 'random_pairs_research' not in player.session.vars:
            countries = C.COUNTRIES.copy()
            random.shuffle(countries)
            pairs = [(countries[i], countries[j]) for i in range(len(countries)) for j in range(i + 1, len(countries))]
            random_pairs_research = random.sample(pairs, C.NUM_PAIRS)
            random_pairs_research = [(pair[1], pair[0]) if randint(0, 1) == 1 else pair for pair in random_pairs_research]
            player.session.vars['random_pairs_research'] = random_pairs_research
        
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['research'][3]]
        question_index = player.round_number - min(task_rounds)
        current_pair = player.session.vars['random_pairs_research'][question_index]
        
        return {
            'pair_num': question_index + 1,
            'country1': current_pair[0],
            'country2': current_pair[1]
        }

class TrustAnnounce(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['trust'][1] + 11
    
    @staticmethod
    def vars_for_template(player):
        task_order = player.participant.vars['task_rounds']['trust'][0]
        return {'task_order': task_order}

class TrustInstruction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['trust'][2] + 11

class TrustTask(Page):
    form_model = 'player'
    form_fields = ['ranking_task']
    
    @staticmethod
    def is_displayed(player: Player):
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['trust'][3]]
        return player.round_number in task_rounds
    
    @staticmethod
    def vars_for_template(player):
        if 'random_pairs_trust' not in player.session.vars:
            countries = C.COUNTRIES.copy()
            random.shuffle(countries)
            pairs = [(countries[i], countries[j]) for i in range(len(countries)) for j in range(i + 1, len(countries))]
            random_pairs_trust = random.sample(pairs, C.NUM_PAIRS)
            random_pairs_trust = [(pair[1], pair[0]) if randint(0, 1) == 1 else pair for pair in random_pairs_trust]
            player.session.vars['random_pairs_trust'] = random_pairs_trust
        
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['trust'][3]]
        question_index = player.round_number - min(task_rounds)
        current_pair = player.session.vars['random_pairs_trust'][question_index]
        
        return {
            'pair_num': question_index + 1,
            'country1': current_pair[0],
            'country2': current_pair[1]
        }

class MovieAnnounce(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['movie'][1] + 11
    
    @staticmethod
    def vars_for_template(player):
        task_order = player.participant.vars['task_rounds']['movie'][0]
        return {'task_order': task_order}

class MovieInstruction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['movie'][2] + 11

class MovieTask(Page):
    form_model = 'player'
    form_fields = ['ranking_task']
    
    @staticmethod
    def is_displayed(player: Player):
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['movie'][3]]
        return player.round_number in task_rounds
    
    @staticmethod
    def vars_for_template(player):
        if 'random_pairs_movie' not in player.session.vars:
            movies = C.MOVIES.copy()
            random.shuffle(movies)
            pairs = [(movies[i], movies[j]) for i in range(len(movies)) for j in range(i + 1, len(movies))]
            random_pairs_movie = random.sample(pairs, C.NUM_PAIRS)
            random_pairs_movie = [(pair[1], pair[0]) if randint(0, 1) == 1 else pair for pair in random_pairs_movie]
            player.session.vars['random_pairs_movie'] = random_pairs_movie
        
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['movie'][3]]
        question_index = player.round_number - min(task_rounds)
        current_pair = player.session.vars['random_pairs_movie'][question_index]
        
        return {
            'pair_num': question_index + 1,
            'movie1': current_pair[0],
            'movie2': current_pair[1]
        }

class AreaAnnounce(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['area'][1] + 11
    
    @staticmethod
    def vars_for_template(player):
        task_order = player.participant.vars['task_rounds']['area'][0]
        return {'task_order': task_order}

class AreaInstruction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['area'][2] + 11

class AreaTask(Page):
    form_model = 'player'
    form_fields = ['ranking_task']
    
    @staticmethod
    def is_displayed(player: Player):
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['area'][3]]
        return player.round_number in task_rounds
    
    @staticmethod
    def vars_for_template(player):
        if 'random_pairs_area' not in player.session.vars:
            area = C.AREA.copy()
            random.shuffle(area)
            pairs = [(area[i], area[j]) for i in range(len(area)) for j in range(i + 1, len(area))]
            random_pairs_area = random.sample(pairs, C.NUM_PAIRS)
            random_pairs_area = [(pair[1], pair[0]) if randint(0, 1) == 1 else pair for pair in random_pairs_area]
            player.session.vars['random_pairs_area'] = random_pairs_area
        
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['area'][3]]
        question_index = player.round_number - min(task_rounds)
        current_pair = player.session.vars['random_pairs_area'][question_index]
        
        return {
            'pair_num': question_index + 1,
            'area1': current_pair[0],
            'area2': current_pair[1]
        }

class GasolineAnnounce(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['gasoline'][1] + 11
    
    @staticmethod
    def vars_for_template(player):
        task_order = player.participant.vars['task_rounds']['gasoline'][0]
        return {'task_order': task_order}

class GasolineInstruction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.vars['task_rounds']['gasoline'][2] + 11

class GasolineTask(Page):
    form_model = 'player'
    form_fields = ['ranking_task']
    
    @staticmethod
    def is_displayed(player: Player):
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['gasoline'][3]]
        return player.round_number in task_rounds
    
    @staticmethod
    def vars_for_template(player):
        if 'random_pairs_gasoline' not in player.session.vars:
            gasoline = C.GASOLINE.copy()
            random.shuffle(gasoline)
            pairs = [(gasoline[i], gasoline[j]) for i in range(len(gasoline)) for j in range(i + 1, len(gasoline))]
            random_pairs_gasoline = random.sample(pairs, C.NUM_PAIRS)
            random_pairs_gasoline = [(pair[1], pair[0]) if randint(0, 1) == 1 else pair for pair in random_pairs_gasoline]
            player.session.vars['random_pairs_gasoline'] = random_pairs_gasoline
        
        task_rounds = [round_num + 11 for round_num in player.participant.task_rounds['gasoline'][3]]
        question_index = player.round_number - min(task_rounds)
        current_pair = player.session.vars['random_pairs_gasoline'][question_index]
        
        return {
            'pair_num': question_index + 1,
            'gasoline1': current_pair[0],
            'gasoline2': current_pair[1]
        }

class Answer(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    InformedConsent, Demographic, Instruction1, Instruction2, Instruction3, Instruction4, Instruction5, Instruction6, Instruction7, Instruction8, Instruction9,
    HomocideAnnounce, HomocideInstruction, HomocideTask,
    ResearchAnnounce, ResearchInstruction, ResearchTask,
    TrustAnnounce, TrustInstruction, TrustTask,
    MovieAnnounce, MovieInstruction, MovieTask,
    AreaAnnounce, AreaInstruction, AreaTask,
    GasolineAnnounce, GasolineInstruction, GasolineTask,
    Answer, Results
]