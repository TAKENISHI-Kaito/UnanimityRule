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
            task_data = []
            question_id = 1
            for task in C.TASKS_INFO:
                task_kind = task['task']
                question = task['question']
                candidates = task['candidate']
                rankings = task['ranking']
                for subquestion_id, (option1, option2) in enumerate(itertools.combinations(candidates, 2), start=1):
                    rank1 = rankings[candidates.index(option1)]
                    rank2 = rankings[candidates.index(option2)]
                    task_data.append({
                        'question_id': question_id,
                        'kind': task_kind,
                        'question': question,
                        'subquestion_id': subquestion_id,
                        'option1': option1,
                        'option2': option2,
                        'rank1': rank1,
                        'rank2': rank2
                    })
                    question_id += 1  
            p.participant.vars['all_tasks'] = task_data

            task_order = list(set([item['kind'] for item in task_data]))
            rng.shuffle(task_order)
            
            randomized_task_data = []
            for kind in task_order:
                task_questions = [q for q in task_data if q['kind'] == kind]
                rng.shuffle(task_questions)
                for question in task_questions:
                    if rng.random() < 0.5:
                        question['option1'], question['option2'] = question['option2'], question['option1']
                        question['rank1'], question['rank2'] = question['rank2'], question['rank1']
                randomized_task_data.extend(task_questions)
            p.participant.vars['randomized_tasks'] = randomized_task_data
            print(task_order)
            print(len(randomized_task_data))


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
        return player.round_number == 12 or (player.round_number - 12) % (C.NUM_PAIRS + 2) == 0

    @staticmethod
    def vars_for_template(player):
        task_index = (player.round_number - 12) // (C.NUM_PAIRS + 2)
        current_task = player.participant.vars['randomized_tasks'][task_index * C.NUM_PAIRS]['kind']
        current_task_info = next(task for task in C.TASKS_INFO if task['kind'] == current_task)

        return {
            'task_order': task_index + 1,
            'task_kind': current_task_info['kind'],
        }


class Instruction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 13 or (player.round_number - 11) % (C.NUM_PAIRS + 2) == 1

    @staticmethod
    def vars_for_template(player):
        task_index = (player.round_number - 12) // (C.NUM_PAIRS + 2)
        current_task = player.participant.vars['randomized_tasks'][task_index * C.NUM_PAIRS]['kind']
        current_task_info = next(task for task in C.TASKS_INFO if task['kind'] == current_task)

        return {
            'question': current_task_info['question'],
            'example1': current_task_info['example'][0],
            'example2': current_task_info['example'][1],
            'annotations': current_task_info['annotation']
        }


class Task(Page):
    form_model = 'player'
    form_fields = ['ranking_task']

    @staticmethod
    def is_displayed(player: Player):
        return 14 <= player.round_number <= (11 + len(player.participant.vars['randomized_tasks']))

    @staticmethod
    def vars_for_template(player):
        current_question_index = player.round_number - 12
        current_question = player.participant.vars['randomized_tasks'][current_question_index]
        
        current_kind = current_question['kind']
        pair_num = sum(1 for q in player.participant.vars['randomized_tasks'][:current_question_index] if q['kind'] == current_kind) + 1
        
        return {
            'pair_num': pair_num,
            'question_id': current_question['question_id'],
            'kind': current_question['kind'],
            'question': current_question['question'],
            'subquestion_id': current_question['subquestion_id'],
            'option1': current_question['option1'],
            'option2': current_question['option2']
        }
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        current_question_index = player.round_number - 12
        current_question = player.participant.vars['randomized_tasks'][current_question_index]
        answer = player.ranking_task
        true_false = None

        if answer == current_question['option1']:
            true_false = 1 if current_question['rank1'] < current_question['rank2'] else 0
        elif answer == current_question['option2']:
            true_false = 1 if current_question['rank2'] < current_question['rank1'] else 0
        
        player.participant.vars[f'answer_{current_question_index}'] = {
            'question_id': current_question['question_id'],
            'answer': answer,
            'true_false': true_false
        }


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
        'answer', 'true_false'
    ]
    for player in players:
        for idx, task in enumerate(player.participant.vars['randomized_tasks']):
            answer_data = player.participant.vars.get(f'answer_{idx}', {})
            yield [
                player.id_number,
                player.informed_consent,
                player.gender,
                player.age,
                task['question_id'],
                task['kind'],
                task['subquestion_id'],
                task['option1'],
                task['option2'],
                task['rank1'],
                task['rank2'],
                answer_data.get('answer'),
                answer_data.get('true_false')
            ]