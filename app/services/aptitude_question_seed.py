import logging
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, TEXT

from app.models.aptitude import APTITUDE_QUESTION_COLLECTION, AptitudeQuestionModel

logger = logging.getLogger(__name__)
NOW = datetime.now(timezone.utc)

COMPANY_TAG_SETS = {
    'Quantitative Aptitude': ['TCS', 'Infosys', 'Wipro', 'Accenture', 'Capgemini'],
    'Logical Reasoning': ['Cognizant', 'IBM', 'Deloitte', 'EY', 'PwC'],
    'Verbal Ability': ['Accenture', 'EY', 'PwC', 'IBM', 'Adobe'],
    'Data Interpretation': ['Amazon', 'Microsoft', 'Google', 'Adobe', 'Oracle', 'Qualcomm'],
    'Mixed Aptitude': ['TCS', 'Amazon', 'Microsoft', 'Google', 'Infosys', 'Cognizant'],
}

DIFFICULTY_VALUES = {'easy': 60, 'medium': 90, 'hard': 120}
MARKS_VALUES = {'easy': 1, 'medium': 2, 'hard': 3}


def _make_company_tags(category: str, index: int) -> list[str]:
    pool = COMPANY_TAG_SETS.get(category, ['TCS', 'Amazon', 'Microsoft'])
    first = pool[index % len(pool)]
    second = pool[(index + 1) % len(pool)]
    return [first, second]


def _build_options_from_numbers(correct: float, offsets: list[float], suffix: str = '', precision: int = 0) -> list[str]:
    values = [correct] + [correct + offset for offset in offsets]
    formatted = []
    for value in values:
        if precision > 0:
            formatted.append(f"{value:.{precision}f}{suffix}")
        else:
            if float(value).is_integer():
                formatted.append(f"{int(value)}{suffix}")
            else:
                formatted.append(f"{value:.2f}{suffix}")
    return list(dict.fromkeys(formatted))


def _question_document(
    question_id: str,
    category: str,
    topic: str,
    difficulty: str,
    question: str,
    options: list[str],
    correct_answer: str,
    explanation: str,
    company_tags: list[str],
    estimated_time: int,
    marks: int,
) -> dict[str, Any]:
    return {
        'question_id': question_id,
        'category': category,
        'topic': topic,
        'difficulty': difficulty,
        'question': question,
        'options': options,
        'correct_answer': correct_answer,
        'explanation': explanation,
        'company_tags': company_tags,
        'estimated_time': estimated_time,
        'marks': marks,
        'active': True,
        'created_at': NOW,
        'updated_at': NOW,
    }


def _build_quantitative_questions() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    category = 'Quantitative Aptitude'

    templates = [
        ('Number System', 'easy', 'What is {a} × {b}?', lambda a, b: a * b, '{:,}', [1, -2, 3, -5]),
        ('Percentage', 'easy', 'A product priced at {price} is discounted by {discount}%. What is the sale price?', lambda price, discount: price * (100 - discount) / 100, '${:.2f}', [-5, 5, 10, -8]),
        ('Profit & Loss', 'easy', 'A retailer buys an item for ${cost} and sells it for ${sell}. What is the profit percentage?', lambda cost, sell: round((sell - cost) / cost * 100, 2), '{:.2f}%', [2, -3, 5, -7]),
        ('Ratio & Proportion', 'easy', 'The ratio of A to B is {a}:{b}. If A is {value}, what is B?', lambda a, b, value: int(value * b / a), '{:,}', [1, -2, 3, -4]),
        ('Simple Interest', 'medium', 'If ${principal} is invested at {rate}% simple interest for {years} years, what is the interest earned?', lambda principal, rate, years: principal * rate * years / 100, '${:.2f}', [10, -15, 20, -25]),
        ('Compound Interest', 'medium', 'A deposit of ${principal} grows at {rate}% compounded annually for {years} years. What is the amount rounded to the nearest dollar?', lambda principal, rate, years: round(principal * ((1 + rate / 100) ** years)), '${:,}', [25, -30, 45, -60]),
        ('Average', 'medium', 'The average of five numbers is {avg}. If four of them are {n1}, {n2}, {n3}, and {n4}, what is the fifth number?', lambda avg, n1, n2, n3, n4: int(avg * 5 - (n1 + n2 + n3 + n4)), '{:,}', [3, -5, 7, -9]),
        ('Time & Work', 'medium', '{person1} can complete a job in {h1} hours and {person2} can complete it in {h2} hours. How many hours will they take together?', lambda h1, h2: round((h1 * h2) / (h1 + h2), 2), '{:.2f}', [0.5, -0.75, 1.25, -1.5]),
        ('Time Speed Distance', 'medium', 'A vehicle travels {distance} km in {time} hours. What is its average speed in km/h?', lambda distance, time: round(distance / time, 2), '{:.2f}', [3, -4, 5, -6]),
        ('Probability', 'medium', 'A bag contains {red} red and {blue} blue balls. What is the probability of drawing a red ball?', lambda red, blue: f"{red}/{red + blue}", '{0}', []),
    ]

    number_system = [
        (6, 12), (8, 15), (9, 14), (11, 13), (7, 16), (18, 5), (24, 9), (27, 4),
    ]
    for idx, (a, b) in enumerate(number_system, start=1):
        correct = a * b
        question = f'What is {a} × {b} in the standard number system?'
        options = _build_options_from_numbers(correct, [correct + 5, correct - 7, correct + 11])
        explanation = f'Use multiplication: {a} × {b} = {correct}.'
        questions.append(_question_document(
            f'qa_ns_easy_{idx:03}', category, 'Number System', 'easy', question, options, str(correct), explanation,
            _make_company_tags(category, idx), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Percentage
    percent_data = [(120, 15), (250, 12), (80, 25), (450, 20), (600, 18), (150, 10), (420, 8), (980, 22)]
    for idx, (price, discount) in enumerate(percent_data, start=1):
        correct = round(price * (100 - discount) / 100, 2)
        question = f'A product priced at ${price} is discounted by {discount}%. What is the sale price?'
        options = _build_options_from_numbers(correct, [-12, 10, 18, -22], '$', 2)
        explanation = f'Discounted price = ${price} × {100 - discount}% = ${correct:.2f}.'
        questions.append(_question_document(
            f'qa_pct_easy_{idx:03}', category, 'Percentage', 'easy', question, options, f'${correct:.2f}', explanation,
            _make_company_tags(category, idx + 10), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Profit & Loss
    profit_data = [(120, 150), (80, 100), (220, 264), (180, 225), (95, 121), (315, 378), (140, 175), (260, 325)]
    for idx, (cost, sell) in enumerate(profit_data, start=1):
        percent = round((sell - cost) / cost * 100, 2)
        question = f'A retailer buys an item for ${cost} and sells it for ${sell}. What is the profit percentage?'
        options = _build_options_from_numbers(percent, [percent + 5, percent - 3, percent + 8, percent - 6], '%', 2)
        explanation = f'Profit = ${sell - cost}. Profit percentage = {percent}%.'
        questions.append(_question_document(
            f'qa_pl_easy_{idx:03}', category, 'Profit & Loss', 'easy', question, options, f'{percent:.2f}%', explanation,
            _make_company_tags(category, idx + 20), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Ratio & Proportion
    ratio_data = [(3,4,24), (2,5,40), (5,6,50), (7,9,63), (4,7,28), (5,8,35), (6,11,66), (9,10,81)]
    for idx, (a, b, value) in enumerate(ratio_data, start=1):
        correct = int(value * b / a)
        question = f'The ratio of A to B is {a}:{b}. If A is {value}, what is B?'
        options = _build_options_from_numbers(correct, [correct + 2, correct - 4, correct + 5, correct - 3])
        explanation = f'If A:B = {a}:{b} and A={value}, then B={value}×{b}/{a} = {correct}.'
        questions.append(_question_document(
            f'qa_rp_easy_{idx:03}', category, 'Ratio & Proportion', 'easy', question, options, str(correct), explanation,
            _make_company_tags(category, idx + 30), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Simple Interest
    interest_data = [(1200, 5, 2), (1500, 6, 3), (1800, 4, 4), (2500, 8, 2), (3200, 7, 3), (2800, 9, 5), (2100, 11, 2), (1750, 6, 6)]
    for idx, (principal, rate, years) in enumerate(interest_data, start=1):
        correct = round(principal * rate * years / 100, 2)
        question = f'If ${principal} is invested at {rate}% simple interest for {years} years, what is the interest earned?'
        options = _build_options_from_numbers(correct, [correct + 12, correct - 15, correct + 20, correct - 18], '$', 2)
        explanation = f'Simple interest = {principal} × {rate}% × {years} = ${correct:.2f}.'
        questions.append(_question_document(
            f'qa_si_medium_{idx:03}', category, 'Simple Interest', 'medium', question, options, f'${correct:.2f}', explanation,
            _make_company_tags(category, idx + 40), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Compound Interest
    compound_data = [(1000, 5, 2), (1500, 6, 3), (1200, 8, 2), (1800, 7, 4), (2500, 6, 3), (3200, 5, 5), (2100, 9, 2), (2000, 4, 6)]
    for idx, (principal, rate, years) in enumerate(compound_data, start=1):
        amount = round(principal * ((1 + rate / 100) ** years))
        question = f'A deposit of ${principal} grows at {rate}% compounded annually for {years} years. What is the amount rounded to the nearest dollar?'
        options = _build_options_from_numbers(amount, [amount + 22, amount - 18, amount + 35, amount - 27], '$', 0)
        explanation = f'Amount = {principal} × (1 + {rate}/100)^{years} ≈ ${amount}.'
        questions.append(_question_document(
            f'qa_ci_medium_{idx:03}', category, 'Compound Interest', 'medium', question, options, f'${amount}', explanation,
            _make_company_tags(category, idx + 50), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Average
    average_data = [(18, [16,20,22,14]), (22, [19,24,18,25]), (20, [16,21,23,20]), (14, [12,15,18,17]), (24, [22,26,20,18]), (19, [17,21,16,22]), (23, [20,24,18,20]), (21, [19,23,18,20])]
    for idx, (avg, nums) in enumerate(average_data, start=1):
        total = avg * 5
        correct = total - sum(nums)
        question = f'The average of five numbers is {avg}. If four of them are {nums[0]}, {nums[1]}, {nums[2]}, and {nums[3]}, what is the fifth number?'
        options = _build_options_from_numbers(correct, [correct + 2, correct - 3, correct + 4, correct - 5])
        explanation = f'Total = {avg}×5 = {total}. Missing number = {total} - {sum(nums)} = {correct}.'
        questions.append(_question_document(
            f'qa_avg_medium_{idx:03}', category, 'Average', 'medium', question, options, str(correct), explanation,
            _make_company_tags(category, idx + 60), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Time & Work
    work_data = [(8, 12), (10, 15), (6, 9), (14, 21), (7, 11), (12, 18), (5, 8), (9, 12)]
    for idx, (h1, h2) in enumerate(work_data, start=1):
        correct = round((h1 * h2) / (h1 + h2), 2)
        question = f'Person A can complete a job in {h1} hours and person B can complete it in {h2} hours. How many hours will they take working together?'
        options = _build_options_from_numbers(correct, [correct + 0.5, correct - 0.75, correct + 1.2, correct - 1.5], '', 2)
        explanation = f'Combined rate = 1/{h1} + 1/{h2}. Time = 1 / combined rate ≈ {correct} hours.'
        questions.append(_question_document(
            f'qa_tw_medium_{idx:03}', category, 'Time & Work', 'medium', question, options, f'{correct:.2f}', explanation,
            _make_company_tags(category, idx + 70), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Time Speed Distance
    tsd_data = [(120, 2), (180, 3), (150, 2.5), (210, 3.5), (90, 1.5), (175, 2.5), (144, 3), (260, 4)]
    for idx, (distance, time) in enumerate(tsd_data, start=1):
        correct = round(distance / time, 2)
        question = f'A vehicle travels {distance} km in {time} hours. What is its average speed in km/h?'
        options = _build_options_from_numbers(correct, [correct + 3, correct - 4, correct + 5, correct - 2], '', 2)
        explanation = f'Average speed = {distance} / {time} = {correct} km/h.'
        questions.append(_question_document(
            f'qa_tsd_medium_{idx:03}', category, 'Time Speed Distance', 'medium', question, options, f'{correct:.2f}', explanation,
            _make_company_tags(category, idx + 80), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Probability
    probability_data = [(3, 5), (4, 7), (2, 6), (5, 9), (4, 8), (6, 10), (1, 4), (7, 13)]
    for idx, (red, blue) in enumerate(probability_data, start=1):
        correct = f'{red}/{red + blue}'
        question = f'A bag contains {red} red and {blue} blue balls. What is the probability of drawing a red ball?'
        options = [correct, f'{blue}/{red + blue}', f'{red}/{blue}', f'{red + blue}/{red}']
        explanation = f'The probability is red balls over total balls = {red}/{red + blue}.'
        questions.append(_question_document(
            f'qa_prob_medium_{idx:03}', category, 'Probability', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 90), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Permutation & Combination
    pc_data = [(5, 2), (6, 2), (7, 3), (8, 2), (9, 4), (10, 2), (11, 3), (12, 2)]
    for idx, (n, r) in enumerate(pc_data, start=1):
        correct = int(__import__('math').comb(n, r))
        question = f'How many ways can {n} people be selected for a team of {r} members?'
        options = _build_options_from_numbers(correct, [correct + 5, correct - 4, correct + 10, correct - 7])
        explanation = f'Combination formula nCr = {n}C{r} = {correct}.'
        questions.append(_question_document(
            f'qa_pc_hard_{idx:03}', category, 'Permutation & Combination', 'hard', question, options, str(correct), explanation,
            _make_company_tags(category, idx + 100), DIFFICULTY_VALUES['hard'], MARKS_VALUES['hard'],
        ))

    # Ages
    ages_data = [(24, 32, 8), (18, 24, 6), (30, 42, 12), (15, 20, 5), (40, 52, 12), (22, 30, 8), (28, 36, 8), (35, 45, 10)]
    for idx, (a_age, b_age, diff) in enumerate(ages_data, start=1):
        correct = f'{diff} years' if diff > 0 else '0 years'
        question = f'A is {a_age} years old and B is {b_age} years old. What is the age difference?'
        options = [correct, f'{diff + 2} years', f'{abs(diff - 2)} years', f'{diff + 4} years']
        explanation = f'Age difference = |{a_age} - {b_age}| = {abs(diff)} years.'
        questions.append(_question_document(
            f'qa_ages_easy_{idx:03}', category, 'Ages', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx + 110), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Mixtures
    mix_data = [(3, 4, 5, 10), (2, 5, 3, 15), (4, 1, 6, 24), (5, 6, 4, 20), (3, 7, 2, 14), (2, 9, 7, 18), (4, 5, 3, 12), (6, 7, 5, 22)]
    for idx, (a, b, c, total) in enumerate(mix_data, start=1):
        correct = round((a * c + b * c) / (a + b), 2)
        question = f'A mixture of {a} liters and {b} liters has concentration {c}%. What is the resultant concentration?'
        options = _build_options_from_numbers(correct, [correct + 2, correct - 1.5, correct + 3, correct - 2], '%', 2)
        explanation = f'Result concentration = {correct}% using weighted average of quantities.'
        questions.append(_question_document(
            f'qa_mix_hard_{idx:03}', category, 'Mixtures', 'hard', question, options, f'{correct:.2f}%', explanation,
            _make_company_tags(category, idx + 120), DIFFICULTY_VALUES['hard'], MARKS_VALUES['hard'],
        ))

    # Pipes & Cisterns
    cistern_data = [(6, 9), (5, 8), (4, 12), (7, 14), (3, 10), (6, 15), (8, 16), (9, 18)]
    for idx, (fill, drain) in enumerate(cistern_data, start=1):
        rate = round(1 / fill - 1 / drain, 4)
        time = round(1 / rate, 2)
        question = f'A pipe fills a cistern in {fill} hours and a drain empties it in {drain} hours. If both are open, how long to fill the cistern?' 
        options = _build_options_from_numbers(time, [time + 1.5, time - 1.2, time + 2, time - 0.8], ' hours', 2)
        explanation = f'Net fill rate = 1/{fill} - 1/{drain}. Time = 1 / rate ≈ {time} hours.'
        questions.append(_question_document(
            f'qa_pcis_hard_{idx:03}', category, 'Pipes & Cisterns', 'hard', question, options, f'{time:.2f} hours', explanation,
            _make_company_tags(category, idx + 130), DIFFICULTY_VALUES['hard'], MARKS_VALUES['hard'],
        ))

    # Boats & Streams
    boats_data = [(12, 3), (14, 4), (10, 2), (15, 5), (9, 3), (18, 6), (11, 2), (16, 4)]
    for idx, (still, stream) in enumerate(boats_data, start=1):
        downstream = still + stream
        question = f'A boat travels at {still} km/h in still water and the stream speed is {stream} km/h. What is its downstream speed?'
        options = [f'{downstream} km/h', f'{still - stream} km/h', f'{still + stream * 2} km/h', f'{still + stream // 2} km/h']
        explanation = f'Downstream speed = still water speed + stream speed = {still} + {stream} = {downstream} km/h.'
        questions.append(_question_document(
            f'qa_bs_easy_{idx:03}', category, 'Boats & Streams', 'easy', question, options, f'{downstream} km/h', explanation,
            _make_company_tags(category, idx + 140), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    return questions


def _build_logical_questions() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    category = 'Logical Reasoning'

    # Coding Decoding
    code_templates = [
        ('Coding Decoding', 'easy', 'If STRING is coded as {code}, what is the code for {word}?',),
    ]
    encodings = [
        ('LOUD', 'NPVE', 'WORD'),
        ('CODE', 'EQFG', 'TEST'),
        ('MIND', 'OKPF', 'TIME'),
        ('PLAY', 'QMBZ', 'SAFE'),
        ('EASY', 'GBUZ', 'HARD'),
    ]
    for idx, (word, code, query) in enumerate(encodings, start=1):
        shift = 1
        question = f'If {word} is coded as {code}, what is the code for {query} under the same pattern?'
        options = [f'{chr(ord(c)+shift)}{chr(ord(c)+shift)}' for c in query]  # placeholder
        options = [''.join([chr(ord(char) + shift) for char in query]), ''.join([chr(ord(char) + 2) for char in query]), ''.join([chr(ord(char) - 1) for char in query]), ''.join([chr(ord(char) + 3) for char in query])]
        correct = options[0]
        explanation = 'The code shifts each letter by one position in the alphabet using the same pattern.'
        questions.append(_question_document(
            f'lr_cd_easy_{idx:03}', category, 'Coding Decoding', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Blood Relations
    relations = [
        ('His father is the only son of my grandfather. How is the man related to me?', 'My son', ['My brother', 'My cousin', 'My nephew', 'My son']),
        ('She is the daughter of the father of my brother. How is she related to me?', 'My sister', ['My aunt', 'My sister', 'My niece', 'My cousin']),
        ('X is the son of Y who is the only daughter of Z. How is Z related to X?', 'Grandfather', ['Uncle', 'Grandfather', 'Father', 'Grandmother']),
        ('A is the sister of B. C is the son of B. How is A related to C?', 'Aunt', ['Mother', 'Aunt', 'Sister', 'Cousin']),
    ]
    for idx, (question, correct, options) in enumerate(relations, start=1):
        explanation = f'Trace family relationships to determine that {correct} is the correct relation.'
        questions.append(_question_document(
            f'lr_br_easy_{idx:03}', category, 'Blood Relations', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx + 10), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Directions
    directions = [
        ('If you walk 3 km east, then 4 km north, where are you relative to your starting point?', 'North-east', ['North', 'East', 'North-east', 'South-east']),
        ('From the school you go west 5 km and then south 2 km. In which direction is the school from your final position?', 'North-east', ['North-east', 'South-west', 'North-west', 'South-east']),
        ('A person walks 6 km north and then 8 km west. What is the direction from the starting point to the final point?', 'North-west', ['North-west', 'South-west', 'North-east', 'South-east']),
    ]
    for idx, (question, correct, options) in enumerate(directions, start=1):
        explanation = f'Use the relative motion to determine the final direction: the answer is {correct}.'
        questions.append(_question_document(
            f'lr_dir_easy_{idx:03}', category, 'Directions', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx + 20), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Seating Arrangement
    seating = [
        ('Five friends A, B, C, D and E sit in a row. A is left of C, B is right of D, and E is at one end. Who is between D and C?', 'A', ['B', 'A', 'E', 'C']),
        ('Six colleagues sit around a table. R sits opposite V and to the left of W. Who sits between V and W?', 'T', ['S', 'T', 'R', 'V']),
    ]
    for idx, (question, correct, options) in enumerate(seating, start=1):
        explanation = f'Analyze the seating order from the clues to find that {correct} sits between the named people.'
        questions.append(_question_document(
            f'lr_seat_medium_{idx:03}', category, 'Seating Arrangement', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 30), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Puzzles
    puzzle_data = [
        ('A train leaves station A at 9:00 and arrives at station B at 12:00. Another train leaves at 10:00 and arrives at 12:00 from the opposite direction. Who travels faster?', 'Second train', ['First train', 'Second train', 'Both same', 'Cannot determine']),
        ('A clock is set correctly at 6 a.m. The clock loses 10 minutes every hour. What will the clock show at 9 a.m. real time?', '8:30', ['8:30', '8:20', '8:50', '9:00']),
    ]
    for idx, (question, correct, options) in enumerate(puzzle_data, start=1):
        explanation = f'Work through the timeline or distance relationships to confirm the correct answer: {correct}.'
        questions.append(_question_document(
            f'lr_puz_hard_{idx:03}', category, 'Puzzles', 'hard', question, options, correct, explanation,
            _make_company_tags(category, idx + 40), DIFFICULTY_VALUES['hard'], MARKS_VALUES['hard'],
        ))

    # Analogy
    analogy = [
        ('Bird is to Feathers as Dog is to?', 'Fur', ['Teeth', 'Claws', 'Fur', 'Tail']),
        ('Pen is to Write as Knife is to?', 'Cut', ['Hold', 'Cut', 'Sharpen', 'Carry']),
    ]
    for idx, (question, correct, options) in enumerate(analogy, start=1):
        explanation = f'Choose the relationship that best matches the analogy: {correct}.'
        questions.append(_question_document(
            f'lr_ana_easy_{idx:03}', category, 'Analogy', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx + 50), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Series
    series = [
        ('What is the next number in the series 2, 5, 10, 17, ?', '26', ['24', '26', '28', '30']),
        ('Find the next term: 3, 9, 27, ?', '81', ['54', '72', '81', '90']),
    ]
    for idx, (question, correct, options) in enumerate(series, start=1):
        explanation = f'This sequence follows a consistent multiplier or additive pattern, producing {correct} as the next term.'
        questions.append(_question_document(
            f'lr_ser_medium_{idx:03}', category, 'Series', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 60), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Syllogism
    syllogism = [
        ('All roses are flowers. Some flowers fade quickly. Can we conclude that some roses fade quickly?', 'Cannot be determined', ['Yes', 'No', 'Cannot be determined', 'Only sometimes']),
        ('All cars are vehicles. Some vehicles are red. Can we conclude that some cars are red?', 'Cannot be determined', ['Yes', 'No', 'Cannot be determined', 'Sometimes']),
    ]
    for idx, (question, correct, options) in enumerate(syllogism, start=1):
        explanation = 'The syllogism does not provide enough information to confirm the conclusion about the specific subset.'
        questions.append(_question_document(
            f'lr_syl_hard_{idx:03}', category, 'Syllogism', 'hard', question, options, correct, explanation,
            _make_company_tags(category, idx + 70), DIFFICULTY_VALUES['hard'], MARKS_VALUES['hard'],
        ))

    # Statement & Conclusion
    statements = [
        ('Statement: All managers are leaders. Conclusion I: Some leaders are managers. Conclusion II: All leaders are managers.', 'Only conclusion I follows', ['Only conclusion I follows', 'Only conclusion II follows', 'Both follow', 'Neither follows']),
    ]
    for idx, (question, correct, options) in enumerate(statements, start=1):
        explanation = 'Use standard logic rules for statements and conclusions to determine that only the first conclusion follows.'
        questions.append(_question_document(
            f'lr_sc_hard_{idx:03}', category, 'Statement & Conclusion', 'hard', question, options, correct, explanation,
            _make_company_tags(category, idx + 80), DIFFICULTY_VALUES['hard'], MARKS_VALUES['hard'],
        ))

    # Statement & Assumption
    assumptions = [
        ('Statement: The company will offer bonuses if profits improve. Assumption: Employees will work harder if profits improve.', 'Implicit assumption', ['Explicit assumption', 'Implicit assumption', 'Not a valid assumption', 'Contradictory assumption']),
    ]
    for idx, (question, correct, options) in enumerate(assumptions, start=1):
        explanation = 'The assumption follows logically from the statement about rewards and motivation.'
        questions.append(_question_document(
            f'lr_sa_hard_{idx:03}', category, 'Statement & Assumption', 'hard', question, options, correct, explanation,
            _make_company_tags(category, idx + 90), DIFFICULTY_VALUES['hard'], MARKS_VALUES['hard'],
        ))

    # Logical Sequence
    sequences = [
        ('Find the next item: ABC, BCD, CDE, ?', 'DEF', ['CDE', 'DEF', 'EFG', 'FGH']),
    ]
    for idx, (question, correct, options) in enumerate(sequences, start=1):
        explanation = 'Each term shifts every letter one place forward in the alphabet.'
        questions.append(_question_document(
            f'lr_ls_medium_{idx:03}', category, 'Logical Sequence', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 100), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Calendar and Clock
    clock = [
        ('A clock gains 5 minutes every hour. How many minutes will it gain in 8 hours?', '40 minutes', ['35 minutes', '40 minutes', '45 minutes', '50 minutes']),
        ('If today is Wednesday, what day will it be after 11 days?', 'Sunday', ['Saturday', 'Sunday', 'Monday', 'Tuesday']),
    ]
    for idx, (question, correct, options) in enumerate(clock, start=1):
        explanation = f'Compute the daily shift or clock gain to arrive at {correct}.'
        questions.append(_question_document(
            f'lr_cc_medium_{idx:03}', category, idx < 2 and 'Clock' or 'Calendar', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 110), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Venn Diagrams
    venn_diagrams = [
        ('In a survey of 60 students, 25 like cricket, 20 like football, and 8 like both. How many like neither?', '23', ['23', '15', '30', '7'], '23', 'Neither = 60 - (25 + 20 - 8) = 23.'),
        ('Out of 72 people, 28 like tea, 32 like coffee, and 10 like both. How many like neither?', '22', ['22', '18', '20', '24'], '22', 'Neither = 72 - (28 + 32 - 10) = 22.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(venn_diagrams, start=1):
        questions.append(_question_document(
            f'lr_ven_easy_{idx:03}', category, 'Venn Diagrams', 'easy', question, options, answer, explanation,
            _make_company_tags(category, idx + 120), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Input-Output
    io_data = [
        ('Input: 2468 Output: 7531. If Input: 1357, what is the Output?', '8642', ['8642', '9753', '7531', '6428'], '8642', 'The output is produced by subtracting each digit from 9 and reversing the order.'),
        ('Input: ABCD Output: ZYXC. What is the output for INPUT?', 'RMKFG', ['RMKOG', 'RMKFG', 'SNJQF', 'RVLNH'], 'RMKFG', 'Each letter is replaced by its alphabetic reverse: A→Z, B→Y, C→X, D→W, so INPUT becomes RMKFG.'),
        ('Input: 3142 Output: 6857. If Input: 5291, what is the Output?', '4708', ['4708', '4678', '4857', '4938'], '4708', 'Each digit is replaced by its complement to 9 and then reversed.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(io_data, start=1):
        questions.append(_question_document(
            f'lr_io_easy_{idx:03}', category, 'Input-Output', 'easy', question, options, answer, explanation,
            _make_company_tags(category, idx + 130), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Statement & Argument
    argument_data = [
        ('Statement: All books in the library are novels. Argument I: Some novels are books. Argument II: All novels are in the library. Which follows?', 'Only argument I follows', ['Only argument I follows', 'Only argument II follows', 'Both follow', 'Neither follows'], 'Only argument I follows', 'Argument I is valid because books are a broader category; argument II is not guaranteed.'),
        ('Statement: No vehicle is a bicycle. Argument I: Some bicycles are vehicles. Argument II: No vehicle is a bicycle. Which follows?', 'Only argument II follows', ['Only argument I follows', 'Only argument II follows', 'Both follow', 'Neither follows'], 'Only argument II follows', 'Statement II restates the given information exactly.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(argument_data, start=1):
        questions.append(_question_document(
            f'lr_arg_medium_{idx:03}', category, 'Statement & Argument', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx + 140), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Data Sufficiency
    data_sufficiency = [
        ('Is x greater than y? I. x = 8, y = 5. II. x + y = 13.', 'Statement I alone is sufficient', ['Statement I alone is sufficient', 'Statement II alone is sufficient', 'Both together are sufficient', 'Cannot determine'], 'Statement I alone is sufficient', 'Statement I gives exact values for x and y; statement II alone does not.'),
        ('Is number n prime? I. n = 17. II. n is odd and greater than 1.', 'Statement I alone is sufficient', ['Statement I alone is sufficient', 'Statement II alone is sufficient', 'Both together are sufficient', 'Cannot determine'], 'Statement I alone is sufficient', '17 is prime; the second statement is not enough on its own.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(data_sufficiency, start=1):
        questions.append(_question_document(
            f'lr_ds_medium_{idx:03}', category, 'Data Sufficiency', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx + 150), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Tournament Ranking
    ranking_data = [
        ('In a competition, A finished before B but after C. D finished after B. Who finished second?', 'A', ['A', 'B', 'C', 'D'], 'A', 'Order C, A, B, D places A in second.'),
        ('Five students rank 1 to 5. E is ahead of F, and G is last. Who can be third?', 'E', ['E', 'F', 'G', 'H'], 'E', 'E is positioned ahead of F while G is last, making E a valid third place.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(ranking_data, start=1):
        questions.append(_question_document(
            f'lr_tr_medium_{idx:03}', category, 'Tournament Ranking', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx + 160), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Additional Logical Sequence
    sequences_extra = [
        ('Find the next item in the sequence: 5, 11, 23, 47, ?', '95', ['90', '92', '95', '98'], '95', 'Each term doubles and adds 1: 47 × 2 + 1 = 95.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(sequences_extra, start=1):
        questions.append(_question_document(
            f'lr_ls2_medium_{idx:03}', category, 'Logical Sequence', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx + 170), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Additional Logical Reasoning
    extra_logical = [
        ('In a coding system, if CAT is 3120 and DOG is 4157, what is the code for BAT?', '2120', ['2120', '3120', '2130', '2140'], '2120', 'The pattern uses letters positions with digits in a fixed positional scheme.'),
        ('Two trains are 100 km apart and move towards each other at 40 km/h and 30 km/h. How long until they meet?', '2 hours', ['1.5 hours', '2 hours', '2.5 hours', '3 hours'], '2 hours', 'Time = distance / relative speed = 100 / 70 = 2 hours.'),
        ('A family has a father, mother, son, and daughter. The father is older than the mother. The son is younger than the daughter. Who is the oldest?', 'Father', ['Mother', 'Father', 'Daughter', 'Son'], 'Father', 'The father is older than the mother and no other older relationship is given.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(extra_logical, start=1):
        questions.append(_question_document(
            f'lr_extra_medium_{idx:03}', category, 'Logical Reasoning', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx + 180), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    return questions


def _build_verbal_questions() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    category = 'Verbal Ability'

    synonyms = [
        ('The manager was very meticulous in reviewing the report.', 'Meticulous means?', ['Careless', 'Thorough', 'Fast', 'Critical'], 'Thorough', 'The word meticulous means careful and precise.'),
        ('She was elated after winning the award.', 'Elated means?', ['Sad', 'Angry', 'Thrilled', 'Bored'], 'Thrilled', 'Elated means extremely happy or thrilled.'),
    ]
    for idx, (sentence, prompt, options, correct, explanation) in enumerate(synonyms, start=1):
        question = f'{sentence} {prompt}'
        questions.append(_question_document(
            f'va_syn_{idx:03}', category, 'Synonyms', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    antonyms = [
        ('The verdict was unanimous.', 'Unanimous opposite?', ['Agreed', 'Divided', 'Resolved', 'Supported'], 'Divided', 'Unanimous means in complete agreement; its opposite is divided.'),
        ('Her explanation was vague.', 'Vague opposite?', ['Clear', 'Ambiguous', 'General', 'Simple'], 'Clear', 'The opposite of vague is clear.'),
    ]
    for idx, (sentence, prompt, options, correct, explanation) in enumerate(antonyms, start=1):
        question = f'{sentence} {prompt}'
        questions.append(_question_document(
            f'va_ant_{idx:03}', category, 'Antonyms', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx + 10), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    fill_blanks = [
        ('The team worked ____ through the night to meet the deadline.', ['hard', 'well', 'quickly', 'careful'], 'hard', 'Worked hard is the correct collocation for effort.'),
        ('The project manager will ____ the final report tomorrow.', ['submits', 'submit', 'submitted', 'submitting'], 'submit', 'Future tense after will uses the base form submit.'),
    ]
    for idx, (sentence, options, correct, explanation) in enumerate(fill_blanks, start=1):
        question = f'{sentence.replace("____", "____")}'
        questions.append(_question_document(
            f'va_fill_{idx:03}', category, 'Fill in the Blanks', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx + 20), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    sentence_correction = [
        ('She don’t like the proposal.', ['doesn’t like', 'don’t like', 'didn’t liked', 'not likes'], 'doesn’t like', 'The subject she requires does not: doesn’t.'),
        ('He finished his work, didn’t he?', ['did he', 'does he', 'didn’t he', 'doesn’t he'], 'did he', 'The auxiliary should match finished in past tense.'),
    ]
    for idx, (sentence, options, correct, explanation) in enumerate(sentence_correction, start=1):
        question = f'Select the grammatically correct revision: {sentence}'
        questions.append(_question_document(
            f'va_sc_{idx:03}', category, 'Sentence Correction', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 30), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    grammar_data = [
        ('Neither of the options ____ acceptable.', ['is', 'are', 'were', 'be'], 'is', 'Neither is singular and requires is.'),
        ('She has been working here ____ 2019.', ['since', 'for', 'from', 'during'], 'since', 'Since refers to the start point in time.'),
    ]
    for idx, (sentence, options, correct, explanation) in enumerate(grammar_data, start=1):
        question = f'{sentence}'
        questions.append(_question_document(
            f'va_gram_{idx:03}', category, 'Grammar', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 40), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    sentence_rearrangement = [
        ('the / completed / project / team / the / successfully', ['The team successfully completed the project.', 'Successfully the team project completed the.', 'The project successfully the team completed.', 'Completed the project the team successfully.'], 'The team successfully completed the project.', 'Arrange the segments into a grammatically correct sentence.'),
    ]
    for idx, (segments, options, correct, explanation) in enumerate(sentence_rearrangement, start=1):
        question = f'Arrange the following segments into a correct sentence: {segments}'
        questions.append(_question_document(
            f'va_sr_hard_{idx:03}', category, 'Sentence Rearrangement', 'hard', question, options, correct, explanation,
            _make_company_tags(category, idx + 50), DIFFICULTY_VALUES['hard'], MARKS_VALUES['hard'],
        ))

    error_detection = [
        ('He has gone to the market, and will return soon.', ['gone to the market', 'will return soon', 'and will return', 'no error'], 'no error', 'The sentence is grammatically correct as written.'),
    ]
    for idx, (sentence, options, correct, explanation) in enumerate(error_detection, start=1):
        question = f'Choose the part with an error: {sentence}'
        questions.append(_question_document(
            f'va_ed_medium_{idx:03}', category, 'Error Detection', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 60), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    para_jumbles = [
        ('A. final review B. submit C. complete D. draft the report', ['A B C D', 'C A D B', 'D C A B', 'B D A C'], 'C A D B', 'This order creates the logical process of drafting, completing, reviewing, and submitting.'),
    ]
    for idx, (segments, options, correct, explanation) in enumerate(para_jumbles, start=1):
        question = f'Rearrange the segments into a coherent paragraph: {segments}'
        questions.append(_question_document(
            f'va_pj_hard_{idx:03}', category, 'Para Jumbles', 'hard', question, options, correct, explanation,
            _make_company_tags(category, idx + 70), DIFFICULTY_VALUES['hard'], MARKS_VALUES['hard'],
        ))

    reading_comprehension = [
        ('A brief passage about sustainability and planning is followed by a question on the main idea.', ['The passage focuses on financial returns.', 'The passage focuses on sustainable planning.', 'The passage focuses on market demand.', 'The passage focuses on technology trends.'], 'The passage focuses on sustainable planning.', 'The main idea centers on long-term environmental and operational planning.'),
    ]
    for idx, (context, options, answer, explanation) in enumerate(reading_comprehension, start=1):
        question = f'{context}'
        questions.append(_question_document(
            f'va_rc_medium_{idx:03}', category, 'Reading Comprehension', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx + 80), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    vocabulary = [
        ('Choose the word that best fits: The engineer proposed a very ____ solution.', ['practical', 'abstract', 'confusing', 'lazy'], 'practical', 'A practical solution is realistic and effective.'),
    ]
    for idx, (question, options, correct, explanation) in enumerate(vocabulary, start=1):
        questions.append(_question_document(
            f'va_vocab_medium_{idx:03}', category, 'Vocabulary', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 90), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # One-Word Substitution
    substitutions = [
        ('A person who studies the past is called?', ['Historian', 'Psychologist', 'Biologist', 'Geologist'], 'Historian', 'A historian studies the past.'),
        ('A speech delivered without preparation is called?', ['Extempore', 'Manuscript', 'Impromptu', 'Formal'], 'Impromptu', 'An impromptu speech is delivered without preparation.'),
    ]
    for idx, (question, options, correct, explanation) in enumerate(substitutions, start=1):
        questions.append(_question_document(
            f'va_ows_easy_{idx:03}', category, 'One-Word Substitution', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx + 100), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Additional One-Word Substitution
    substitutions_extra = [
        ('A person who writes computer programs is called?', ['Programmer', 'Teacher', 'Artist', 'Doctor'], 'Programmer', 'A person who writes computer programs is called a programmer.'),
        ('A person who restores old buildings is called?', ['Architect', 'Conservator', 'Engineer', 'Mechanic'], 'Conservator', 'A conservator restores or preserves old artifacts and buildings.'),
    ]
    for idx, (question, options, correct, explanation) in enumerate(substitutions_extra, start=3):
        questions.append(_question_document(
            f'va_ows_easy_{idx:03}', category, 'One-Word Substitution', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx + 110), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Idioms and Phrases
    idioms = [
        ('He decided to bite the bullet and finish the task. What does bite the bullet mean?', ['Avoid the task', 'Face the hardship', 'Delay the task', 'Delegate the task'], 'Face the hardship', 'To bite the bullet means to face a difficult situation with courage.'),
        ('She is on cloud nine after her promotion. What does on cloud nine mean?', ['Very happy', 'Very tired', 'Very busy', 'Very surprised'], 'Very happy', 'Being on cloud nine means being extremely happy.'),
    ]
    for idx, (question, options, correct, explanation) in enumerate(idioms, start=1):
        questions.append(_question_document(
            f'va_idi_easy_{idx:03}', category, 'Idioms & Phrases', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx + 110), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    idioms_extra = [
        ('She decided to let the cat out of the bag. What does it mean?', ['Reveal a secret', 'Feed the cat', 'Lose a bag', 'Buy a cat'], 'Reveal a secret', 'To let the cat out of the bag means to reveal a secret.'),
        ('He is on thin ice after the mistake. What does on thin ice mean?', ['In a risky situation', 'Doing well', 'Feeling cold', 'Playing safely'], 'In a risky situation', 'Being on thin ice means being in a risky or uncertain situation.'),
    ]
    for idx, (question, options, correct, explanation) in enumerate(idioms_extra, start=3):
        questions.append(_question_document(
            f'va_idi_easy_{idx:03}', category, 'Idioms & Phrases', 'easy', question, options, correct, explanation,
            _make_company_tags(category, idx + 120), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Active and Passive Voice
    active_passive = [
        ('The committee will approve the plan.', ['The plan will be approved by the committee.', 'The plan is approved by the committee.', 'The plan was approved by the committee.', 'The plan has been approved by the committee.'], 'The plan will be approved by the committee.', 'Convert the active sentence into passive using future tense.'),
        ('The chef prepared the meal.', ['The meal was prepared by the chef.', 'The meal is prepared by the chef.', 'The meal had been prepared by the chef.', 'The meal has been prepared by the chef.'], 'The meal was prepared by the chef.', 'Convert the active sentence into passive using past tense.'),
    ]
    for idx, (question, options, correct, explanation) in enumerate(active_passive, start=1):
        questions.append(_question_document(
            f'va_ap_medium_{idx:03}', category, 'Active voice / Passive voice', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 120), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    active_passive_extra = [
        ('The manager will announce the results. What is the passive version?', ['The results will be announced by the manager.', 'The results are announced by the manager.', 'The results were announced by the manager.', 'The results will announce by the manager.'], 'The results will be announced by the manager.', 'Convert the future tense active sentence to passive voice.'),
    ]
    for idx, (question, options, correct, explanation) in enumerate(active_passive_extra, start=3):
        questions.append(_question_document(
            f'va_ap_medium_{idx:03}', category, 'Active voice / Passive voice', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 130), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Direct and Indirect Speech
    direct_indirect = [
        ('She said, "I am leaving now." What is the indirect speech?', ['She said that she was leaving then.', 'She said that she is leaving now.', 'She said that she had left then.', 'She said that she will leave now.'], 'She said that she was leaving then.', 'Convert from direct to indirect speech with tense adjustment.'),
        ('He said, "We will arrive at five." What is the indirect speech?', ['He said that they would arrive at five.', 'He said that they will arrive at five.', 'He said they arrive at five.', 'He said they had arrived at five.'], 'He said that they would arrive at five.', 'Future tense in direct speech changes to would in reported speech.'),
    ]
    for idx, (question, options, correct, explanation) in enumerate(direct_indirect, start=1):
        questions.append(_question_document(
            f'va_dis_medium_{idx:03}', category, 'Direct & Indirect Speech', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 130), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Cloze Test
    cloze_tests = [
        ('The manager expects everyone to ____ the deadline without fail.', ['meet', 'meets', 'meeting', 'met'], 'meet', 'The infinitive form is required after expects.'),
        ('She decided to ____ the project personally.', ['supervise', 'supervises', 'supervising', 'supervised'], 'supervise', 'The base verb follows decided to.'),
    ]
    for idx, (question, options, correct, explanation) in enumerate(cloze_tests, start=1):
        questions.append(_question_document(
            f'va_cloze_medium_{idx:03}', category, 'Cloze Test', 'medium', question, options, correct, explanation,
            _make_company_tags(category, idx + 140), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Reading Comprehension
    reading_comprehension_extra = [
        ('A note explains why teamwork matters in project success. What is the main idea?', ['Teamwork improves project outcomes.', 'Teamwork slows down decision-making.', 'Teamwork leads to conflict.', 'Teamwork reduces accountability.'], 'Teamwork improves project outcomes.', 'The passage emphasizes collaboration as a key factor in successful projects.'),
        ('A paragraph describes the weather turning stormy before the event. What does this imply?', ['The event may be postponed.', 'The weather is perfect.', 'The event is canceled.', 'The event is indoors only.'], 'The event may be postponed.', 'Stormy weather suggests potential delay, not certainty of cancellation.'),
    ]
    for idx, (question, options, answer, explanation) in enumerate(reading_comprehension_extra, start=1):
        questions.append(_question_document(
            f'va_rc2_medium_{idx:03}', category, 'Reading Comprehension', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx + 150), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    return questions


def _build_data_interpretation_questions() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    category = 'Data Interpretation'

    # Table interpretation
    table_data = [
        ('A table shows quarterly revenue of $120k, $130k, $140k and $150k. What is the average quarterly revenue?', '$135000', ['135000', '137500', '132000', '140000'], '135000', 'Average revenue = (120+130+140+150)/4 = 135.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(table_data, start=1):
        questions.append(_question_document(
            f'di_table_{idx:03}', category, 'Tables', 'easy', question, options, answer, explanation,
            _make_company_tags(category, idx), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Pie chart
    pie_data = [
        ('A pie chart shows 40%, 30%, 20%, and 10% market share. What percentage is the second segment?', '30%', ['25%', '30%', '35%', '40%'], '30%', 'Identify the segment share directly from the pie chart values.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(pie_data, start=1):
        questions.append(_question_document(
            f'di_pie_{idx:03}', category, 'Pie Charts', 'easy', question, options, answer, explanation,
            _make_company_tags(category, idx + 10), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Line graph
    line_data = [
        ('A line graph shows sales rising from 80 to 120 units over four months. What is the total increase?', '40 units', ['30 units', '40 units', '50 units', '60 units'], '40 units', 'Calculate the difference between the final and initial values.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(line_data, start=1):
        questions.append(_question_document(
            f'di_line_{idx:03}', category, 'Line Graphs', 'easy', question, options, answer, explanation,
            _make_company_tags(category, idx + 20), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Bar chart
    bar_data = [
        ('A bar chart compares costs of $40k, $55k, $65k, and $80k. What is the difference between the highest and lowest values?', '$40k', ['$40k', '$30k', '$20k', '$25k'], '$40k', 'Subtract lowest cost from highest cost: 80k - 40k = 40k.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(bar_data, start=1):
        questions.append(_question_document(
            f'di_bar_{idx:03}', category, 'Bar Charts', 'easy', question, options, answer, explanation,
            _make_company_tags(category, idx + 30), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Mixed graphs
    mixed_data = [
        ('A chart shows sales and growth rates. If sales rise 15% from $200k, what is the new sales value?', '$230k', ['$215k', '$230k', '$240k', '$225k'], '$230k', 'Increase $200k by 15%: $200k × 1.15 = $230k.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(mixed_data, start=1):
        questions.append(_question_document(
            f'di_mixed_{idx:03}', category, 'Mixed Graphs', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx + 40), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Caselets
    caselets = [
        ('A caselet describes a team handling 120 tasks in 6 days. If the team completes 20 tasks per day, how many tasks remain after 5 days?', '20 tasks', ['10 tasks', '15 tasks', '20 tasks', '25 tasks'], '20 tasks', '20 tasks per day × 5 days = 100 tasks completed; 20 remain.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(caselets, start=1):
        questions.append(_question_document(
            f'di_case_{idx:03}', category, 'Caselets', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx + 50), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Additional Table Interpretation
    table_data_extra = [
        ('A table lists 5 products with quantities 10, 12, 15, 8, and 5. What is the total quantity?', '50', ['45', '50', '55', '60'], '50', 'Add all quantities: 10 + 12 + 15 + 8 + 5 = 50.'),
        ('A table shows sales of 15, 20, 25, and 30 units. What is the average sales?', '22.5', ['20', '22.5', '25', '27.5'], '22.5', 'Average = (15 + 20 + 25 + 30) / 4 = 22.5.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(table_data_extra, start=2):
        questions.append(_question_document(
            f'di_table_{idx:03}', category, 'Tables', 'easy', question, options, answer, explanation,
            _make_company_tags(category, idx + 60), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Additional Pie Chart
    pie_data_extra = [
        ('A pie chart allocates 25%, 35%, 20%, and 20% to four categories. What percentage is the third category?', '20%', ['20%', '25%', '35%', '40%'], '20%', 'The third slice is directly stated as 20%.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(pie_data_extra, start=2):
        questions.append(_question_document(
            f'di_pie_{idx:03}', category, 'Pie Charts', 'easy', question, options, answer, explanation,
            _make_company_tags(category, idx + 70), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Additional Line Graph
    line_data_extra = [
        ('A line graph shows production increasing from 50 to 90 units. What is the increase?', '40 units', ['30 units', '35 units', '40 units', '45 units'], '40 units', 'Subtract the initial value from the final value: 90 - 50 = 40.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(line_data_extra, start=2):
        questions.append(_question_document(
            f'di_line_{idx:03}', category, 'Line Graphs', 'easy', question, options, answer, explanation,
            _make_company_tags(category, idx + 80), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Additional Bar Chart
    bar_data_extra = [
        ('A bar chart shows expenses of $30k, $45k, $55k, and $60k. What is the difference between the highest and lowest costs?', '$30k', ['$30k', '$40k', '$45k', '$50k'], '$30k', 'Subtract the minimum from the maximum: 60k - 30k = 30k.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(bar_data_extra, start=2):
        questions.append(_question_document(
            f'di_bar_{idx:03}', category, 'Bar Charts', 'easy', question, options, answer, explanation,
            _make_company_tags(category, idx + 90), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    # Additional Mixed Graphs
    mixed_data_extra = [
        ('A chart shows revenue and profit margins. If revenue is $120k and margin is 20%, what is the profit?', '$24k', ['$22k', '$24k', '$26k', '$28k'], '$24k', 'Profit = $120k × 20% = $24k.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(mixed_data_extra, start=2):
        questions.append(_question_document(
            f'di_mixed_{idx:03}', category, 'Mixed Graphs', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx + 100), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Additional Caselets
    caselets_extra = [
        ('A team of 4 completes 48 tasks in 6 days. If the team doubles its size, how many days will it take to complete 48 similar tasks?', '3 days', ['2 days', '3 days', '4 days', '5 days'], '3 days', 'Doubling the team halves the time: 6 / 2 = 3 days.'),
        ('A project requires 90 person-hours. If 5 people work 6 hours per day, how many days will it take?', '3 days', ['2 days', '3 days', '4 days', '5 days'], '3 days', 'Total hours per day = 5 × 6 = 30; days = 90 / 30 = 3.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(caselets_extra, start=2):
        questions.append(_question_document(
            f'di_case_{idx:03}', category, 'Caselets', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx + 110), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    # Data Comparison
    comparison_data = [
        ('Product X sold 120 units and product Y sold 90 units. What is the ratio of X to Y?', '4:3', ['3:4', '4:3', '5:4', '6:5'], '4:3', '120:90 simplifies to 4:3.'),
        ('Team A completed 24 tasks and Team B completed 18 tasks. What is the ratio of A to B?', '4:3', ['3:4', '4:3', '5:4', '6:5'], '4:3', '24:18 simplifies to 4:3.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(comparison_data, start=1):
        questions.append(_question_document(
            f'di_comp_{idx:03}', category, 'Data Comparison', 'easy', question, options, answer, explanation,
            _make_company_tags(category, idx + 120), DIFFICULTY_VALUES['easy'], MARKS_VALUES['easy'],
        ))

    return questions


def _build_mixed_questions() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    category = 'Mixed Aptitude'

    mixed_cases = [
        ('A candidate solves 20 questions in 30 minutes. If each correct answer earns 1 mark and each incorrect answer loses 0.25 mark, what is the maximum score if all are answered correctly?', '20', ['18', '19', '20', '21'], '20', 'With all correct answers, the total score equals the number of questions.'),
        ('A table shows product sales: 40%, 30%, 20%, 10%. If total revenue is $250k, what is the amount represented by 30%?', '$75k', ['$60k', '$75k', '$90k', '$100k'], '$75k', '30% of $250k = $75k.'),
        ('Choose the sentence with the correct grammar: The team have finished their presentation.', 'The team have finished their presentation.', ['The team has finished their presentation.', 'The team have finished their presentation.', 'The team is finished their presentation.', 'The team are finished their presentation.'], 'The team has finished their presentation.', 'Collective nouns in American English typically take has.'),
    ]
    for idx, (question, correct, options, answer, explanation) in enumerate(mixed_cases, start=1):
        questions.append(_question_document(
            f'mx_gen_medium_{idx:03}', category, 'Integrated Reasoning', 'medium', question, options, answer, explanation,
            _make_company_tags(category, idx), DIFFICULTY_VALUES['medium'], MARKS_VALUES['medium'],
        ))

    return questions


def _build_aptitude_questions() -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    questions.extend(_build_quantitative_questions())
    questions.extend(_build_logical_questions())
    questions.extend(_build_verbal_questions())
    questions.extend(_build_data_interpretation_questions())
    questions.extend(_build_mixed_questions())
    return questions


def _validate_question_document(document: dict[str, Any]) -> AptitudeQuestionModel:
    return AptitudeQuestionModel.model_validate(document)


async def ensure_aptitude_question_indexes(db: AsyncIOMotorDatabase) -> None:
    collection = db[APTITUDE_QUESTION_COLLECTION]
    indexes = [
        IndexModel([('question_id', ASCENDING)], unique=True),
        IndexModel([('category', ASCENDING)]),
        IndexModel([('topic', ASCENDING)]),
        IndexModel([('difficulty', ASCENDING)]),
        IndexModel([('active', ASCENDING)]),
        IndexModel([('company_tags', ASCENDING)]),
        IndexModel([('question', TEXT), ('explanation', TEXT)]),
    ]
    await collection.create_indexes(indexes)


async def _validate_collection(collection) -> dict[str, Any]:
    total = await collection.count_documents({})
    category_distribution = {}
    difficulty_distribution = {}
    topic_distribution = {}

    async for doc in collection.aggregate([
        {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
    ]):
        category_distribution[doc['_id']] = doc['count']

    async for doc in collection.aggregate([
        {'$group': {'_id': '$difficulty', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
    ]):
        difficulty_distribution[doc['_id']] = doc['count']

    async for doc in collection.aggregate([
        {'$group': {'_id': '$topic', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
    ]):
        topic_distribution[doc['_id']] = doc['count']

    duplicates = await collection.aggregate([
        {'$group': {'_id': '$question_id', 'count': {'$sum': 1}}},
        {'$match': {'count': {'$gt': 1}}},
        {'$count': 'duplicate_count'},
    ]).to_list(length=1)
    duplicate_count = duplicates[0]['duplicate_count'] if duplicates else 0

    missing_explanation = await collection.count_documents({'$or': [{'explanation': {'$exists': False}}, {'explanation': ''}]})
    missing_options = await collection.count_documents({'$or': [{'options': {'$exists': False}}, {'options': {'$size': 0}}]})
    missing_correct_answer = await collection.count_documents({'$or': [{'correct_answer': {'$exists': False}}, {'correct_answer': ''}]})

    return {
        'total_questions': total,
        'category_distribution': category_distribution,
        'difficulty_distribution': difficulty_distribution,
        'topic_distribution': topic_distribution,
        'duplicate_question_ids': duplicate_count,
        'missing_explanation': missing_explanation,
        'missing_options': missing_options,
        'missing_correct_answer': missing_correct_answer,
    }


async def seed_aptitude_questions(db: AsyncIOMotorDatabase) -> dict[str, Any]:
    collection = db[APTITUDE_QUESTION_COLLECTION]
    await ensure_aptitude_question_indexes(db)

    templates = _build_aptitude_questions()
    question_ids: set[str] = set()
    unique_templates: list[dict[str, Any]] = []
    duplicate_count = 0

    for template in templates:
        if template['question_id'] in question_ids:
            duplicate_count += 1
            continue
        question_ids.add(template['question_id'])
        unique_templates.append(template)

    inserted = 0
    skipped = 0

    for template in unique_templates:
        validated = _validate_question_document(template)
        document = validated.model_dump(mode='json')
        result = await collection.update_one(
            {'question_id': document['question_id']},
            {'$setOnInsert': document},
            upsert=True,
        )
        if result.upserted_id:
            inserted += 1
        else:
            skipped += 1

    report = await _validate_collection(collection)
    logger.info(
        'Aptitude question seed complete: %s inserted, %s skipped, %s duplicates detected',
        inserted,
        skipped,
        duplicate_count,
    )
    logger.info('Validation report: %s', report)
    return {
        'inserted': inserted,
        'updated': 0,
        'skipped': skipped,
        'duplicate_count': duplicate_count,
        **report,
    }
