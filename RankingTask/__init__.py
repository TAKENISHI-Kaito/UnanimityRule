import itertools

import numpy as np
from otree.api import *

import json
with open('./RankingTask/tasks_info.json') as f:
    tasks_info = json.load(f)

doc = """
Ranking Task: Preliminary Survey
"""
rng = np.random.default_rng()

class C(BaseConstants):
    NAME_IN_URL = 'RankingTask'
    PLAYERS_PER_GROUP = None
    TASKS_INFO = tasks_info 
    NUM_PAIRS = 21
    NUM_ROUNDS = 11 + (2 + NUM_PAIRS) * len(TASKS_INFO) + 2 # instruction + task + result = 151

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    informed_consent = models.CharField(
        initial = None,
        choices = ['私は、以上の説明を理解したうえで、本調査に参加することに同意します。'],
        widget = widgets.RadioSelect()
        )
    id_number = models.IntegerField(
        initial = None,
        verbose_name = 'あなたのID番号を入力してください。'
        )
    gender = models.CharField(
        initial = None,
        choices = ['男性', '女性', '回答しない'],
        verbose_name = 'あなたの性別を教えてください。',
        widget = widgets.RadioSelect()
        )
    age = models.IntegerField(
        initial = None,
        verbose_name = 'あなたの年齢を教えてください。'
        )
    
    ranking_task = models.LongStringField()

# FUNCTION
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        for p in subsession.get_players():
            tasks = [item["task"] for item in tasks_info]
            task_order = tasks.copy()
            rng.shuffle(task_order)
            task_rounds = []
            for i, (task, start) in enumerate(zip(task_order, range(12, C.NUM_ROUNDS - 2, C.NUM_PAIRS + 2))):
                task_rounds.append([task, start])
            print('player', p.id_in_subsession)
            print('task_rounds is', task_rounds)
            p.participant.vars['task_rounds'] = task_rounds


# PAGES
class InformedConsent(Page):
    form_model = 'player'
    form_fields = ['informed_consent']

    def is_displayed(player):
        return player.round_number == 1


class Demographic(Page):
    form_model = 'player'
    form_fields = ['id_number', 'gender', 'age']

    @staticmethod
    def is_displayed(player):
        return player.round_number == 2

class PreInstruction1(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        return player.round_number == 3

class PreInstruction2(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        return player.round_number == 4

class PreInstruction3(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        return 5 <= player.round_number <= 10
    
    @staticmethod
    def vars_for_template(player):
        task_index = player.round_number - 5
        task_info = C.TASKS_INFO[task_index]
        
        return {
            'kind_number': task_index + 1,
            'kind': task_info['kind'],
            'question': task_info['question'],
            'example1': task_info['example'][0],
            'example2': task_info['example'][1],
            'annotations': task_info['annotation'],
            'instruction': task_info['instruction'][0]
        }

class PreInstruction4(Page):
    form_model = 'player'

    def is_displayed(player):
        return player.round_number == 11


class Announce(Page):
    @staticmethod
    def is_displayed(player: Player):
        return len(player.participant.vars['task_rounds']) > 0 and player.round_number == player.participant.vars['task_rounds'][0][1]

    @staticmethod
    def vars_for_template(player):
        current_task = player.participant.vars['task_rounds'][0][0]
        current_task_infomation = next((item for item in C.TASKS_INFO if item['task'] == current_task), None)
        
        return {
            'task_order': len(C.TASKS_INFO) - len(player.participant.vars['task_rounds']) + 1,
            'task_kind': current_task_infomation['kind']
            }


class Instruction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return len(player.participant.vars['task_rounds']) > 0 and player.round_number == player.participant.vars['task_rounds'][0][1] + 1

    @staticmethod
    def vars_for_template(player):
        current_task = player.participant.vars['task_rounds'][0][0]
        current_task_infomation = next((item for item in C.TASKS_INFO if item['task'] == current_task), None)
        
        return {
            'question': current_task_infomation['question'],
            'example1': current_task_infomation['example'][0],
            'example2': current_task_infomation['example'][1],
            'annotations': current_task_infomation['annotation']
            }

class Task(Page):
    form_model = 'player'
    form_fields = ['ranking_task']

    @staticmethod
    def is_displayed(player: Player):
        if len(player.participant.vars['task_rounds']) == 0:
            return False
        start = player.participant.vars['task_rounds'][0][1]
        task_rounds = [round_num for round_num in range(start + 2, start + 2 + C.NUM_PAIRS)]
        return player.round_number in task_rounds

    @staticmethod
    def vars_for_template(player):
        current_task = player.participant.vars['task_rounds'][0][0] 
        current_task_infomation = next((item for item in C.TASKS_INFO if item['task'] == current_task), None) 
        
        if 'random_pairs' not in player.participant.vars or player.round_number == player.participant.vars['task_rounds'][0][1] + 2:
            candidates = current_task_infomation['candidate']
            pairs = np.array(list(itertools.combinations(candidates, 2)))
            [rng.shuffle(li) for li in pairs]
            rng.shuffle(pairs)
            player.participant.vars['random_pairs'] = pairs

        start = player.participant.vars['task_rounds'][0][1]
        task_rounds = [round_num for round_num in range(start + 2, start + C.NUM_PAIRS + 2)]
        question_index = player.round_number - min(task_rounds)
        current_pair = player.participant.vars['random_pairs'][question_index]
        
        if player.round_number == max(task_rounds):
            player.participant.vars['task_rounds'].pop(0)
            del player.participant.vars['random_pairs']
        
        return {
            'pair_num': question_index + 1,
            'question': current_task_infomation['question'],
            'option1': current_pair[0],
            'option2': current_pair[1]
        }
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        if 'random_pairs' not in player.participant.vars:
            return
        
        current_task = player.participant.vars['task_rounds'][0][0]
        task_index = [idx for idx, task in enumerate(C.TASKS_INFO) if task['task'] == current_task][0]

        pairs = player.participant.vars['random_pairs']
        question_index = player.round_number - player.participant.vars['task_rounds'][0][1] - 2
        current_pair = pairs[question_index]

        player.participant.vars[f'task_{task_index}_answer_{question_index}'] = player.ranking_task


class Answer(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS - 1
    
    @staticmethod
    def vars_for_template(player):
        task_answers = []
        for task in C.TASKS_INFO:
            task_answers.append({
                'kind': task['kind'],
                'candidates': task['candidate']
            })
        
        return {
            'task_answers': task_answers
        }


class Results(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [
    InformedConsent, Demographic,
    PreInstruction1, PreInstruction2, PreInstruction3, PreInstruction4,
    Announce, Instruction, Task,
    Answer, Results
]


def custom_export(players):
    yield [
        'ID', 'informed_consent', 'gender', 'age',
        'questionID', 'kind', 'subquestionID', 
        'option1', 'option2', 'rank1', 'rank2',
        'answer', 'TrueFalse'
    ]
    
    for player in players:
        participant = player.participant
        
        informed_consent = player.informed_consent
        id_number = player.id_number
        gender = player.gender
        age = player.age
        
        for idx, task in enumerate(C.TASKS_INFO):
            task_base_id = idx * C.NUM_PAIRS
            for sub_idx, (option1, option2) in enumerate(itertools.combinations(task['candidate'], 2)):
                subquestionID = sub_idx + 1
                questionID = task_base_id + subquestionID
                
                rank1 = task['ranking'][task['candidate'].index(option1)]
                rank2 = task['ranking'][task['candidate'].index(option2)]
                
                answer = participant.vars.get(f'task_{idx}_answer_{sub_idx}', None)
                
                if answer == option1:
                    true_false = 1 if rank1 < rank2 else 0
                elif answer == option2:
                    true_false = 1 if rank2 < rank1 else 0
                else:
                    true_false = None
                
                yield [
                    id_number, informed_consent, gender, age,
                    questionID, task['task'], subquestionID,
                    option1, option2, rank1, rank2,
                    answer, true_false
                ]
