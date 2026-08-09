import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.interview_engine.comprehension_engine import ComprehensionEngine
from app.services.interview_engine.evaluation_engine import EvaluationEngine
from app.services.interview_engine.prompt_builder import PromptBuilder
from app.services.interview_engine import QuestionMeta

class DummyGroq:
    async def complete(self, messages, *, max_tokens=256, temperature=0.4, json_mode=False):
        print('GROQ called, messages:', messages)
        return '{}'

async def main():
    question = QuestionMeta(
        question_id='tech_medium_03',
        text='Describe how the MongoDB aggregation pipeline works and give a practical example of filtering, grouping, and projecting data.',
        topic='mongodb aggregation',
        expected_concepts=[
            {'name': 'pipeline stages', 'weight': 1.0, 'is_core': True},
            {'name': 'aggregation operators', 'weight': 1.0, 'is_core': True},
        ],
        core_concepts=[
            {'name': '$match', 'weight': 1.0, 'is_core': True},
            {'name': '$group', 'weight': 1.0, 'is_core': True},
        ],
    )
    answer_text = 'The MongoDB Aggregation Pipeline processes data through multiple stages. The $match stage filters documents. The $group stage groups documents and performs calculations. The $project stage selects required fields. For example, it reshapes documents.'
    engine = ComprehensionEngine(DummyGroq(), PromptBuilder())
    answer = await engine.understand_answer(answer_text, question)
    print('mentioned_concepts:', answer.mentioned_concepts)
    print('claims:')
    for claim in answer.claims:
        print(claim.id, claim.text, claim.concepts)
    scores = engine.score_concepts(answer, question)
    print('scores:')
    for name, score in scores.items():
        print(name, score.status, score.score, score.evidence_claim_ids)
    naive = EvaluationEngine(DummyGroq(), PromptBuilder())
    verdict = await naive.evaluate_correctness(scores, question, answer)
    print('verdict', verdict.verdict, verdict.score, verdict.core_coverage)

if __name__ == '__main__':
    asyncio.run(main())
