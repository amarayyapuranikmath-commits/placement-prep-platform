import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.interview_service import QuestionBankRepository
from app.services.interview_engine.comprehension_engine import ComprehensionEngine
from app.services.interview_engine.evaluation_engine import EvaluationEngine
from app.services.interview_engine import GroqClientProtocol
from app.services.interview_engine.prompt_builder import PromptBuilder
from app.core.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient

class DummyGroq(GroqClientProtocol):
    async def complete(self, messages, *, max_tokens=256, temperature=0.4, json_mode=False):
        print('--- GROQ called ---')
        print(messages)
        return '{}'

async def main():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB]
    repo = QuestionBankRepository(db)
    q = await repo.get_question('tech_medium_03')
    print('Question ID:', q.question_id)
    print('Topic:', q.topic)
    print('Expected concepts:', [c['name'] for c in q.expected_concepts])
    print('Core concepts:', [c['name'] for c in q.core_concepts])

    answer_text = (
        'The MongoDB Aggregation Pipeline processes data through multiple stages. '
        'The $match stage filters documents. The $group stage groups documents and performs calculations. '
        'The $project stage selects required fields. For example, pipeline output can reshape documents with computed totals.'
    )
    comp = ComprehensionEngine(DummyGroq(), PromptBuilder())
    ao = await comp.understand_answer(answer_text, q)
    print('Mentioned concepts:', ao.mentioned_concepts)
    print('Claims:')
    for claim in ao.claims:
        print('-', claim.text, '=>', claim.concepts)
    sc = comp.score_concepts(ao, q, {})
    print('Score map:')
    for name, cs in sc.items():
        print(name, cs.status, cs.score, cs.evidence_claim_ids)

    eval_engine = EvaluationEngine(DummyGroq(), PromptBuilder())
    verdict = await eval_engine.evaluate_correctness(sc, q, ao)
    print('Core coverage', verdict.core_coverage, 'Score', verdict.score, 'Verdict', verdict.verdict)
    gaps = eval_engine.detect_gaps(sc, q)
    print('Gaps:', [(g.concept, g.gap_type) for g in gaps])
    client.close()

if __name__ == '__main__':
    asyncio.run(main())
