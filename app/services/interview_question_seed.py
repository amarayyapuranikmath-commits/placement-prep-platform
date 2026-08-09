import logging
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, TEXT

from app.models.interview import InterviewQuestionModel

logger = logging.getLogger(__name__)

INTERVIEW_QUESTION_COLLECTION = "interview_questions"

NOW = datetime.now(timezone.utc)

INTERVIEW_QUESTION_TEMPLATES: list[dict[str, Any]] = [
    {
        "question_id": "tech_easy_01",
        "interview_type": "technical",
        "category": "Programming Fundamentals",
        "topic": "python collections",
        "difficulty": "easy",
        "difficulty_rating": 950.0,
        "role": "Software Engineer",
        "experience_level": "Entry",
        "company_type": "product",
        "question": "Explain the difference between a list and a tuple in Python.",
        "expected_concepts": [
            {"name": "mutability", "weight": 1.0, "is_core": True},
            {"name": "sequence types", "weight": 0.5, "is_core": False},
        ],
        "core_concepts": [
            {"name": "mutability", "weight": 1.0, "is_core": True},
            {"name": "tuple immutability", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "hashability", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "tuple performance", "pattern": "tuple.*faster|tuple.*performance"},
        ],
        "attached_knowledge": {
            "mutability": [
                "Python lists are mutable collections, while tuples are immutable sequences.",
            ]
        },
        "keywords": ["python", "list", "tuple", "mutable", "immutable"],
        "follow_up_questions": [
            "When would you choose a tuple instead of a list in a real application scenario?",
            "How does immutability affect function arguments and caching?",
        ],
        "ideal_answer_summary": "Lists are mutable ordered collections, while tuples are immutable. Use tuples for fixed records, hashable keys, and when immutability improves safety.",
        "evaluation_hints": [
            "Confirm that the candidate understands mutability and sequence behavior.",
            "Listen for use cases where tuple immutability is beneficial.",
        ],
        "estimated_answer_time": 120,
        "estimated_score": 65,
        "tags": ["python", "fundamentals", "collections"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_easy_02",
        "interview_type": "technical",
        "category": "Algorithms",
        "topic": "binary search",
        "difficulty": "easy",
        "difficulty_rating": 1000.0,
        "role": "Software Engineer",
        "experience_level": "Entry",
        "company_type": "startup",
        "question": "Describe how binary search works and why it is more efficient than linear search on a sorted array.",
        "expected_concepts": [
            {"name": "divide and conquer", "weight": 1.0, "is_core": True},
            {"name": "sorted array", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "divide and conquer", "weight": 1.0, "is_core": True},
            {"name": "logarithmic time", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "boundary conditions", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "unsorted input", "pattern": "unsorted|not sorted|random order"},
        ],
        "attached_knowledge": {
            "logarithmic time": [
                "Binary search reduces the search range by half on each comparison, yielding O(log n) performance.",
            ]
        },
        "keywords": ["binary search", "sorted", "efficiency", "algorithm"],
        "follow_up_questions": [
            "What are the stopping conditions for binary search?",
            "How would you adapt binary search to work on a rotated sorted array?",
        ],
        "ideal_answer_summary": "Binary search repeatedly halves a sorted array and compares the middle element with the target, giving O(log n) time compared to O(n) linear search.",
        "evaluation_hints": [
            "Expect the candidate to mention sorted data and halving the search interval.",
            "Watch for clear explanation of time complexity and bounds.",
        ],
        "estimated_answer_time": 140,
        "estimated_score": 70,
        "tags": ["algorithms", "search", "complexity"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_easy_03",
        "interview_type": "technical",
        "category": "Databases",
        "topic": "sql joins",
        "difficulty": "easy",
        "difficulty_rating": 980.0,
        "role": "Backend Engineer",
        "experience_level": "Entry",
        "company_type": "enterprise",
        "question": "Explain the difference between INNER JOIN and LEFT JOIN in SQL with an example use case for each.",
        "expected_concepts": [
            {"name": "join types", "weight": 1.0, "is_core": True},
            {"name": "result set", "weight": 0.5, "is_core": False},
        ],
        "core_concepts": [
            {"name": "inner join", "weight": 1.0, "is_core": True},
            {"name": "left join", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "outer join", "weight": 0.4, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "join order", "pattern": "join order|left.*right|right.*left"},
        ],
        "attached_knowledge": {
            "left join": [
                "A LEFT JOIN returns all rows from the left table and matching rows from the right table, with NULLs when there is no match.",
            ]
        },
        "keywords": ["sql", "inner join", "left join", "relational database"],
        "follow_up_questions": [
            "When would an outer join be a better choice than an inner join?",
            "How can you prevent duplicate rows when joining large tables?",
        ],
        "ideal_answer_summary": "An INNER JOIN returns only rows with matches in both tables, while a LEFT JOIN returns all rows from the left table and matched rows from the right table.",
        "evaluation_hints": [
            "Look for correct descriptions of both joins and a realistic example.",
            "Accept mention of NULL values for unmatched rows in LEFT JOIN.",
        ],
        "estimated_answer_time": 150,
        "estimated_score": 68,
        "tags": ["sql", "joins", "databases"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_easy_04",
        "interview_type": "technical",
        "category": "Operating Systems",
        "topic": "process vs thread",
        "difficulty": "easy",
        "difficulty_rating": 920.0,
        "role": "Software Engineer",
        "experience_level": "Entry",
        "company_type": "product",
        "question": "What is the difference between a process and a thread, and when would you use threads in a server application?",
        "expected_concepts": [
            {"name": "process isolation", "weight": 0.8, "is_core": True},
            {"name": "thread concurrency", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "separate memory space", "weight": 1.0, "is_core": True},
            {"name": "shared memory within threads", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "context switching", "weight": 0.4, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "thread safety", "pattern": "thread safe|thread.*safe|threads.*safe"},
        ],
        "attached_knowledge": {
            "threads in servers": [
                "Threads are useful when tasks share memory and need lightweight concurrency within the same process.",
            ]
        },
        "keywords": ["process", "thread", "os", "concurrency", "server"],
        "follow_up_questions": [
            "How do locks help when multiple threads access shared data?",
            "What are the trade-offs between processes and threads in microservices?",
        ],
        "ideal_answer_summary": "A process has its own memory and resources; a thread shares process memory and is lighter weight. Threads are useful for concurrent I/O or handling multiple connections in the same application.",
        "evaluation_hints": [
            "Accept both OS-level and application-level explanations.",
            "Look for awareness of shared state and potential synchronization issues.",
        ],
        "estimated_answer_time": 130,
        "estimated_score": 66,
        "tags": ["os", "concurrency", "threads"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_easy_05",
        "interview_type": "technical",
        "category": "Web Development",
        "topic": "rest apis",
        "difficulty": "easy",
        "difficulty_rating": 990.0,
        "role": "Full Stack Engineer",
        "experience_level": "Entry",
        "company_type": "startup",
        "question": "Describe the main principles of REST API design and how HTTP methods map to CRUD operations.",
        "expected_concepts": [
            {"name": "idempotence", "weight": 0.8, "is_core": False},
            {"name": "http methods", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "resource orientation", "weight": 1.0, "is_core": True},
            {"name": "GET POST PUT DELETE", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "statelessness", "weight": 0.7, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "REST vs HTTP", "pattern": "rest.*http|http.*rest"},
        ],
        "attached_knowledge": {
            "rest principles": [
                "REST APIs should expose resources through stable URLs and use HTTP verbs for consistent semantics.",
            ]
        },
        "keywords": ["rest", "http", "api design", "crud"],
        "follow_up_questions": [
            "What makes an endpoint idempotent?",
            "How would you version a REST API without breaking existing clients?",
        ],
        "ideal_answer_summary": "REST APIs map resources to URLs and use HTTP verbs like GET, POST, PUT, and DELETE to represent CRUD operations. They should be stateless and predictable.",
        "evaluation_hints": [
            "Accept clear mapping between methods and create/read/update/delete.",
            "Listen for mention of resource-based design and stateless operations.",
        ],
        "estimated_answer_time": 140,
        "estimated_score": 68,
        "tags": ["rest", "api", "web", "http"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_easy_06",
        "interview_type": "technical",
        "category": "DevOps",
        "topic": "git workflows",
        "difficulty": "easy",
        "difficulty_rating": 940.0,
        "role": "Software Engineer",
        "experience_level": "Entry",
        "company_type": "enterprise",
        "question": "Explain the difference between git merge and git rebase, and when you might prefer one workflow over the other.",
        "expected_concepts": [
            {"name": "branch history", "weight": 1.0, "is_core": True},
            {"name": "conflict resolution", "weight": 0.5, "is_core": False},
        ],
        "core_concepts": [
            {"name": "merge history", "weight": 1.0, "is_core": True},
            {"name": "rebase linear history", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "shared branch safety", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "rebase destroys history", "pattern": "destroy.*history|rewrite.*history"},
        ],
        "attached_knowledge": {
            "rebase": [
                "Rebasing rewrites branch commits on top of a new base, while merge preserves branch history with a merge commit.",
            ]
        },
        "keywords": ["git", "merge", "rebase", "version control"],
        "follow_up_questions": [
            "What problems can rebasing shared branches introduce?",
            "How would you resolve a merge conflict when combining two feature branches?",
        ],
        "ideal_answer_summary": "Merge preserves all branch history and creates a merge commit; rebase rewrites commits onto a new base to keep history linear. Use merge for shared branches and rebase for local cleanup.",
        "evaluation_hints": [
            "Check for understanding of history preservation and safe branch usage.",
            "Accept practical workflow examples for feature branches.",
        ],
        "estimated_answer_time": 130,
        "estimated_score": 65,
        "tags": ["git", "devops", "workflow"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_easy_07",
        "interview_type": "technical",
        "category": "Data Structures",
        "topic": "linked lists",
        "difficulty": "easy",
        "difficulty_rating": 900.0,
        "role": "Software Engineer",
        "experience_level": "Entry",
        "company_type": "startup",
        "question": "How would you reverse a singly linked list in place, and what is the time and space complexity of your approach?",
        "expected_concepts": [
            {"name": "pointer manipulation", "weight": 1.0, "is_core": True},
            {"name": "in place reversal", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "iterative reversal", "weight": 1.0, "is_core": True},
            {"name": "O(n) time", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "space complexity", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "recursive overhead", "pattern": "recurs.*stack|recursive.*space"},
        ],
        "attached_knowledge": {
            "linked list reversal": [
                "Reversing a linked list in place requires reassigning next pointers while tracking previous and current nodes.",
            ]
        },
        "keywords": ["linked list", "reverse", "complexity"],
        "follow_up_questions": [
            "How would your approach change if the list were doubly linked?",
            "What edge cases must you handle in your implementation?",
        ],
        "ideal_answer_summary": "Iterate through the list while reassigning each node's pointer to its predecessor, using O(n) time and O(1) additional space.",
        "evaluation_hints": [
            "Ensure the candidate mentions previous node tracking and loop invariants.",
            "Search for clear complexity reasoning.",
        ],
        "estimated_answer_time": 150,
        "estimated_score": 72,
        "tags": ["linked list", "data structures"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_easy_08",
        "interview_type": "technical",
        "category": "Security",
        "topic": "jwt authentication",
        "difficulty": "easy",
        "difficulty_rating": 980.0,
        "role": "Backend Engineer",
        "experience_level": "Entry",
        "company_type": "product",
        "question": "What is JWT-based authentication, and how does a server verify a JWT token sent by a client?",
        "expected_concepts": [
            {"name": "token signing", "weight": 1.0, "is_core": True},
            {"name": "stateless auth", "weight": 0.8, "is_core": True},
        ],
        "core_concepts": [
            {"name": "signature verification", "weight": 1.0, "is_core": True},
            {"name": "token claims", "weight": 0.7, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "expiration handling", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "encryption vs signing", "pattern": "encrypt.*jwt|decrypt.*jwt"},
        ],
        "attached_knowledge": {
            "jwt verification": [
                "The server checks the token signature with a secret or public key, verifies expiry, and reads claims without storing session state.",
            ]
        },
        "keywords": ["jwt", "authentication", "token", "security"],
        "follow_up_questions": [
            "How does JWT differ from traditional session cookies?",
            "What are common risks when using JWT for authentication?",
        ],
        "ideal_answer_summary": "JWT authentication uses signed tokens; the server verifies the signature, expiration, and claims to authenticate requests without server-side session state.",
        "evaluation_hints": [
            "Look for differentiation between signing and encryption.",
            "Accept mention of stateless authentication benefits.",
        ],
        "estimated_answer_time": 140,
        "estimated_score": 70,
        "tags": ["security", "jwt", "auth"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_easy_09",
        "interview_type": "technical",
        "category": "Computer Networks",
        "topic": "tcp handshake",
        "difficulty": "easy",
        "difficulty_rating": 960.0,
        "role": "Software Engineer",
        "experience_level": "Entry",
        "company_type": "enterprise",
        "question": "Briefly describe the TCP three-way handshake and why it is important for reliable connections.",
        "expected_concepts": [
            {"name": "SYN SYN-ACK ACK", "weight": 1.0, "is_core": True},
            {"name": "connection establishment", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "reliability", "weight": 0.8, "is_core": True},
            {"name": "stateful connection", "weight": 0.7, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "sequence numbers", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "http handshake", "pattern": "http handshake|ssl handshake"},
        ],
        "attached_knowledge": {
            "tcp handshake": [
                "TCP creates a reliable, ordered connection by exchanging SYN, SYN-ACK, and ACK packets before data transfer.",
            ]
        },
        "keywords": ["tcp", "handshake", "network", "reliability"],
        "follow_up_questions": [
            "What can happen if one of the handshake packets is lost?",
            "How does TCP differ from UDP in terms of connection setup?",
        ],
        "ideal_answer_summary": "The TCP three-way handshake uses SYN, SYN-ACK, and ACK packets to establish a reliable, ordered connection before data transmission.",
        "evaluation_hints": [
            "Expect the candidate to name the three packets and explain reliable setup.",
            "Accept mention of retransmission after packet loss.",
        ],
        "estimated_answer_time": 130,
        "estimated_score": 64,
        "tags": ["networking", "tcp", "connection"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_easy_10",
        "interview_type": "technical",
        "category": "Problem Solving",
        "topic": "debugging approach",
        "difficulty": "easy",
        "difficulty_rating": 970.0,
        "role": "Software Engineer",
        "experience_level": "Entry",
        "company_type": "product",
        "question": "What steps would you take to debug a production issue in a web application that reproduces intermittently?",
        "expected_concepts": [
            {"name": "isolate root cause", "weight": 1.0, "is_core": True},
            {"name": "logging and monitoring", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "reproduce issue", "weight": 1.0, "is_core": True},
            {"name": "safe rollback or fix", "weight": 0.8, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "communication plan", "weight": 0.4, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "blame the code first", "pattern": "blame.*code|fault.*code"},
        ],
        "attached_knowledge": {
            "incident response": [
                "Good debugging includes collecting logs, reproducing safely, isolating changes, and communicating status with stakeholders.",
            ]
        },
        "keywords": ["debugging", "production", "incident"],
        "follow_up_questions": [
            "How would you use logs and metrics to narrow down the cause?",
            "When is it appropriate to roll back a deployment?",
        ],
        "ideal_answer_summary": "A production debug workflow includes gathering data, reproducing or isolating the issue, checking recent changes, and applying a safe fix or rollback while communicating effectively.",
        "evaluation_hints": [
            "Look for a structured approach rather than guessing.",
            "Accept emphasis on data, monitoring, and safe remediation.",
        ],
        "estimated_answer_time": 150,
        "estimated_score": 67,
        "tags": ["debugging", "production", "troubleshooting"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_medium_01",
        "interview_type": "technical",
        "category": "Algorithms",
        "topic": "dynamic programming",
        "difficulty": "medium",
        "difficulty_rating": 1300.0,
        "role": "Software Engineer",
        "experience_level": "Mid",
        "company_type": "startup",
        "question": "How would you approach solving a problem using dynamic programming, and what differentiates it from a greedy algorithm?",
        "expected_concepts": [
            {"name": "overlapping subproblems", "weight": 1.0, "is_core": True},
            {"name": "optimal substructure", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "memoization", "weight": 1.0, "is_core": True},
            {"name": "greedy tradeoffs", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "bottom-up vs top-down", "weight": 0.6, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "all greedy algorithms fail", "pattern": "greedy.*never|greedy.*always fails"},
        ],
        "attached_knowledge": {
            "dp vs greedy": [
                "Dynamic programming stores results of subproblems, while greedy algorithms make a locally optimal choice without backtracking.",
            ]
        },
        "keywords": ["dynamic programming", "greedy", "memoization"],
        "follow_up_questions": [
            "Can you give an example of a problem where greedy works but dynamic programming is overkill?",
            "How do you decide between top-down and bottom-up dynamic programming?",
        ],
        "ideal_answer_summary": "Dynamic programming uses memoization or tabulation for overlapping subproblems and optimal substructure; greedy algorithms choose the best immediate step but may not always yield a global optimum.",
        "evaluation_hints": [
            "Expect clarity around when dynamic programming is appropriate.",
            "Look for a comparison to greedy strategies and solution correctness.",
        ],
        "estimated_answer_time": 180,
        "estimated_score": 75,
        "tags": ["dp", "algorithms", "optimization"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_medium_02",
        "interview_type": "technical",
        "category": "Web Development",
        "topic": "node express middleware",
        "difficulty": "medium",
        "difficulty_rating": 1320.0,
        "role": "Backend Engineer",
        "experience_level": "Mid",
        "company_type": "product",
        "question": "How does middleware work in Express.js, and how would you structure middleware for authentication, logging, and error handling?",
        "expected_concepts": [
            {"name": "middleware chain", "weight": 1.0, "is_core": True},
            {"name": "error handling middleware", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "request life cycle", "weight": 1.0, "is_core": True},
            {"name": "next() pattern", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "composition order", "weight": 0.6, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "middleware order unimportant", "pattern": "order.*doesn't matter|any order"},
        ],
        "attached_knowledge": {
            "express middleware": [
                "Middleware in Express is a function that receives request, response, and next, and can modify or short-circuit the request flow.",
            ]
        },
        "keywords": ["node", "express", "middleware", "authentication"],
        "follow_up_questions": [
            "How do you make sure authentication runs before route handlers?",
            "What is the benefit of using centralized error-handling middleware?",
        ],
        "ideal_answer_summary": "Express middleware composes functions over the request-response cycle. Authentication should run early, logging can wrap requests, and error-handling middleware should be last to catch thrown errors.",
        "evaluation_hints": [
            "Look for proper ordering of middleware and how next() is used.",
            "Accept examples of authentication and logging middleware placement.",
        ],
        "estimated_answer_time": 170,
        "estimated_score": 76,
        "tags": ["node.js", "express", "backend"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_medium_03",
        "interview_type": "technical",
        "category": "Databases",
        "topic": "mongodb aggregation",
        "difficulty": "medium",
        "difficulty_rating": 1350.0,
        "role": "Backend Engineer",
        "experience_level": "Mid",
        "company_type": "product",
        "question": "Describe how the MongoDB aggregation pipeline works and give a practical example of filtering, grouping, and projecting data.",
        "expected_concepts": [
            {"name": "pipeline stages", "weight": 1.0, "is_core": True},
            {"name": "aggregation operators", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "$match", "weight": 1.0, "is_core": True},
            {"name": "$group", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "$project", "weight": 0.6, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "aggregation vs map reduce", "pattern": "map reduce|mapreduce"},
        ],
        "attached_knowledge": {
            "aggregation pipeline": [
                "MongoDB aggregation pipelines let you transform documents step by step with stages like $match, $group, and $project.",
            ]
        },
        "keywords": ["mongodb", "aggregation", "pipeline"],
        "follow_up_questions": [
            "How would you optimize a pipeline that scans many documents?",
            "What is the difference between $project and $addFields?",
        ],
        "ideal_answer_summary": "MongoDB aggregation pipelines compose stages to filter, group, and reshape documents. A common example is matching records, grouping by a key, and projecting calculated fields.",
        "evaluation_hints": [
            "Look for an end-to-end example and stage ordering.",
            "Accept discussion of performance considerations.",
        ],
        "estimated_answer_time": 180,
        "estimated_score": 78,
        "tags": ["mongodb", "aggregation", "databases"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_medium_04",
        "interview_type": "technical",
        "category": "Operating Systems",
        "topic": "deadlock prevention",
        "difficulty": "medium",
        "difficulty_rating": 1330.0,
        "role": "Backend Engineer",
        "experience_level": "Mid",
        "company_type": "enterprise",
        "question": "What is a deadlock in an operating system, and what strategies can a developer or system architect use to prevent or recover from it?",
        "expected_concepts": [
            {"name": "resource locking", "weight": 1.0, "is_core": True},
            {"name": "deadlock detection", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "circular wait", "weight": 1.0, "is_core": True},
            {"name": "lock ordering", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "transaction rollback", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "deadlock equals performance", "pattern": "performance.*deadlock|deadlock.*slow"},
        ],
        "attached_knowledge": {
            "deadlock handling": [
                "Deadlocks happen when two or more processes wait on each other for resources. Prevention can use lock ordering or timeout-based retries.",
            ]
        },
        "keywords": ["deadlock", "operating systems", "concurrency"],
        "follow_up_questions": [
            "How would you detect a deadlock in a distributed system?",
            "What is the cost of using timeouts to avoid deadlocks?",
        ],
        "ideal_answer_summary": "A deadlock occurs when processes wait on each other in a cycle. Prevention strategies include ordering locks consistently, avoiding hold-and-wait, and using timeouts or deadlock detection algorithms.",
        "evaluation_hints": [
            "Expect mention of the four Coffman conditions and practical prevention techniques.",
            "Accept examples from multi-threaded or database contexts.",
        ],
        "estimated_answer_time": 190,
        "estimated_score": 80,
        "tags": ["os", "deadlock", "concurrency"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_medium_05",
        "interview_type": "technical",
        "category": "Programming Fundamentals",
        "topic": "time complexity",
        "difficulty": "medium",
        "difficulty_rating": 1280.0,
        "role": "Software Engineer",
        "experience_level": "Mid",
        "company_type": "product",
        "question": "Explain why quicksort has average-case complexity O(n log n) and worst-case complexity O(n^2). What can be done to avoid the worst case?",
        "expected_concepts": [
            {"name": "pivot selection", "weight": 1.0, "is_core": True},
            {"name": "divide and conquer", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "average case analysis", "weight": 1.0, "is_core": True},
            {"name": "worst-case partitioning", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "randomized pivot", "weight": 0.6, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "quicksort always O(n log n)", "pattern": "always.*n log n|never.*n\^2"},
        ],
        "attached_knowledge": {
            "quicksort": [
                "Quicksort splits the array around a pivot. Balanced partitions produce O(n log n), while unbalanced partitions can degrade to O(n^2).",
            ]
        },
        "keywords": ["quicksort", "complexity", "algorithms"],
        "follow_up_questions": [
            "What pivot-selection strategy reduces the chance of worst-case behavior?",
            "How does quicksort compare to mergesort in terms of space usage?",
        ],
        "ideal_answer_summary": "Quicksort averages O(n log n) because balanced partitions reduce problem size exponentially. The worst case occurs with badly chosen pivots; randomized or median-of-three pivot selection helps avoid it.",
        "evaluation_hints": [
            "Look for a sound explanation of both average and worst cases.",
            "Accept mention of practical pivot strategies.",
        ],
        "estimated_answer_time": 180,
        "estimated_score": 78,
        "tags": ["sorting", "algorithms", "complexity"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_medium_06",
        "interview_type": "technical",
        "category": "Web Development",
        "topic": "react state",
        "difficulty": "medium",
        "difficulty_rating": 1310.0,
        "role": "Frontend Engineer",
        "experience_level": "Mid",
        "company_type": "startup",
        "question": "How does React state differ from props, and how would you decide whether to lift state up to a parent component?",
        "expected_concepts": [
            {"name": "unidirectional data flow", "weight": 1.0, "is_core": True},
            {"name": "component communication", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "immutable props", "weight": 1.0, "is_core": True},
            {"name": "shared state", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "controlled components", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "props are mutable", "pattern": "props.*mutable|change props"},
        ],
        "attached_knowledge": {
            "react state": [
                "State is local to a component and can change over time; props are read-only inputs passed from a parent.",
            ]
        },
        "keywords": ["react", "state", "props", "components"],
        "follow_up_questions": [
            "When would you move state to a context provider instead of lifting it?",
            "How might you avoid prop drilling in a deep component tree?",
        ],
        "ideal_answer_summary": "State is mutable within a component and drives rendering; props are immutable inputs. Lift state when multiple components need the same data so a parent can manage it centrally.",
        "evaluation_hints": [
            "Expect a clear distinction between state and props.",
            "Accept examples of shared component state.",
        ],
        "estimated_answer_time": 170,
        "estimated_score": 76,
        "tags": ["react", "frontend", "state management"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_medium_07",
        "interview_type": "technical",
        "category": "Databases",
        "topic": "indexing",
        "difficulty": "medium",
        "difficulty_rating": 1290.0,
        "role": "Backend Engineer",
        "experience_level": "Mid",
        "company_type": "enterprise",
        "question": "How do database indexes improve query performance, and what are the trade-offs when adding indexes to a collection?",
        "expected_concepts": [
            {"name": "query execution", "weight": 1.0, "is_core": True},
            {"name": "write amplification", "weight": 0.8, "is_core": True},
        ],
        "core_concepts": [
            {"name": "index scan vs table scan", "weight": 1.0, "is_core": True},
            {"name": "maintenance cost", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "composite indexes", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "more indexes always better", "pattern": "more.*index|all.*indexes"},
        ],
        "attached_knowledge": {
            "database indexes": [
                "Indexes speed up reads by allowing the database to locate rows quickly but add overhead on inserts, updates, and storage.",
            ]
        },
        "keywords": ["indexes", "sql", "performance"],
        "follow_up_questions": [
            "What factors determine whether a composite index is a good fit?",
            "How can an index harm performance for write-heavy workloads?",
        ],
        "ideal_answer_summary": "Indexes reduce query time by avoiding full scans, but they increase storage overhead and slow write operations because each index must be updated.",
        "evaluation_hints": [
            "Look for trade-offs, not just benefits.",
            "Accept mention of index selectivity and coverage.",
        ],
        "estimated_answer_time": 180,
        "estimated_score": 79,
        "tags": ["database", "indexing", "optimization"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_medium_08",
        "interview_type": "technical",
        "category": "Networking",
        "topic": "http caching",
        "difficulty": "medium",
        "difficulty_rating": 1340.0,
        "role": "Backend Engineer",
        "experience_level": "Mid",
        "company_type": "product",
        "question": "Explain how HTTP caching works with cache-control headers and a use case where caching significantly improves performance.",
        "expected_concepts": [
            {"name": "cache-control", "weight": 1.0, "is_core": True},
            {"name": "freshness and validation", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "public vs private cache", "weight": 0.8, "is_core": False},
            {"name": "cache hit ratio", "weight": 0.8, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "ETag and last-modified", "weight": 0.6, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "caching always good", "pattern": "always.*cache|cache.*instead"},
        ],
        "attached_knowledge": {
            "http caching": [
                "Cache-control headers such as max-age and must-revalidate inform clients and intermediaries how long a resource is fresh.",
            ]
        },
        "keywords": ["http", "cache", "performance"],
        "follow_up_questions": [
            "How would you use ETag headers for resource validation?",
            "When should a developer avoid caching a response?",
        ],
        "ideal_answer_summary": "HTTP caching uses metadata like cache-control to tell clients what can be reused. Proper caching can reduce load by serving repeated requests from the cache instead of the origin server.",
        "evaluation_hints": [
            "Expect both header semantics and a realistic performance example.",
            "Accept mention of caching pitfalls for dynamic data.",
        ],
        "estimated_answer_time": 175,
        "estimated_score": 78,
        "tags": ["http", "caching", "networking"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_hard_01",
        "interview_type": "technical",
        "category": "System Design",
        "topic": "api rate limiting",
        "difficulty": "hard",
        "difficulty_rating": 1650.0,
        "role": "Senior Backend Engineer",
        "experience_level": "Senior",
        "company_type": "enterprise",
        "question": "Design a rate limiting strategy for a public API that supports bursts and distinguishes between free-tier and paid customers.",
        "expected_concepts": [
            {"name": "token bucket", "weight": 1.0, "is_core": True},
            {"name": "tiered quotas", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "burst handling", "weight": 1.0, "is_core": True},
            {"name": "state storage", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "distributed coordination", "weight": 0.6, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "rate limit equals security", "pattern": "rate.*limit.*security|security.*rate.*limit"},
        ],
        "attached_knowledge": {
            "rate limiting": [
                "A token bucket algorithm can smooth bursts and enforce different rates for customer tiers while using a centralized or distributed counter store.",
            ]
        },
        "keywords": ["rate limiting", "api", "token bucket", "scalability"],
        "follow_up_questions": [
            "How would you implement rate limiting across multiple service instances?",
            "What metrics would you track to know if the rate limiter is too strict?",
        ],
        "ideal_answer_summary": "Use a token bucket or leaky bucket scheme with separate limits for free and paid customers. Track bursts, enforce quotas in a shared store, and fail gracefully when the limit is exceeded.",
        "evaluation_hints": [
            "Expect architecture-level thinking and trade-offs between accuracy and performance.",
            "Accept mention of distributed coordination or caching.",
        ],
        "estimated_answer_time": 240,
        "estimated_score": 88,
        "tags": ["api", "rate limiting", "system design"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_hard_02",
        "interview_type": "technical",
        "category": "Databases",
        "topic": "cap theorem",
        "difficulty": "hard",
        "difficulty_rating": 1680.0,
        "role": "Senior Backend Engineer",
        "experience_level": "Senior",
        "company_type": "enterprise",
        "question": "Explain the CAP theorem and how a distributed database like MongoDB makes trade-offs across consistency, availability, and partition tolerance.",
        "expected_concepts": [
            {"name": "consistency", "weight": 1.0, "is_core": True},
            {"name": "partition tolerance", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "availability trade-offs", "weight": 1.0, "is_core": True},
            {"name": "MongoDB replica sets", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "read preferences", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "CAP implies only two", "pattern": "only two|exactly two"},
        ],
        "attached_knowledge": {
            "CAP theorem": [
                "CAP says a distributed system can only guarantee two of consistency, availability, and partition tolerance when a partition occurs.",
            ]
        },
        "keywords": ["cap theorem", "distributed systems", "mongodb"],
        "follow_up_questions": [
            "How does MongoDB’s read preference affect consistency?",
            "What would you sacrifice in a system that prioritizes availability?",
        ],
        "ideal_answer_summary": "CAP theorem asserts that during network partitions a distributed system must choose between consistency and availability. MongoDB typically accepts partition tolerance and offers configurable consistency through replica sets and read preferences.",
        "evaluation_hints": [
            "Look for an accurate CAP description and MongoDB-specific examples.",
            "Accept balanced trade-off reasoning.",
        ],
        "estimated_answer_time": 240,
        "estimated_score": 88,
        "tags": ["distributed systems", "mongodb", "cap"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_hard_03",
        "interview_type": "technical",
        "category": "Algorithms",
        "topic": "graph cycle detection",
        "difficulty": "hard",
        "difficulty_rating": 1660.0,
        "role": "Software Engineer",
        "experience_level": "Senior",
        "company_type": "enterprise",
        "question": "How would you detect a cycle in a directed graph, and what algorithmic approach would you use for a large sparse graph?",
        "expected_concepts": [
            {"name": "depth-first search", "weight": 1.0, "is_core": True},
            {"name": "recursion stack", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "topological sort", "weight": 0.8, "is_core": False},
            {"name": "sparse graph efficiency", "weight": 0.6, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "Kahn’s algorithm", "weight": 0.6, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "BFS cycle detection", "pattern": "bfs.*cycle|breadth.*cycle"},
        ],
        "attached_knowledge": {
            "cycle detection": [
                "A DFS with a recursion stack or colored visitation marks can detect cycles in directed graphs efficiently.",
            ]
        },
        "keywords": ["graph", "cycle detection", "dfs"],
        "follow_up_questions": [
            "How does cycle detection differ between directed and undirected graphs?",
            "What memory trade-offs are there for recursive vs iterative DFS?",
        ],
        "ideal_answer_summary": "Detect cycles in a directed graph with DFS while tracking nodes currently on the recursion stack; a large sparse graph benefits from adjacency lists and efficient stack tracking.",
        "evaluation_hints": [
            "Expect algorithmic clarity and appropriate complexity reasoning.",
            "Accept a comparison to Kahn’s algorithm if offered.",
        ],
        "estimated_answer_time": 220,
        "estimated_score": 85,
        "tags": ["graphs", "algorithms", "complexity"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_hard_04",
        "interview_type": "technical",
        "category": "System Design",
        "topic": "caching strategies",
        "difficulty": "hard",
        "difficulty_rating": 1700.0,
        "role": "Senior Backend Engineer",
        "experience_level": "Senior",
        "company_type": "enterprise",
        "question": "Design a caching strategy for a product catalog service where data is updated frequently and reads are much higher than writes.",
        "expected_concepts": [
            {"name": "cache invalidation", "weight": 1.0, "is_core": True},
            {"name": "cache coherence", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "write-through vs write-back", "weight": 0.8, "is_core": False},
            {"name": "time-based expiration", "weight": 0.8, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "cache stampede protection", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "cache as permanent store", "pattern": "cache.*permanent|store.*forever"},
        ],
        "attached_knowledge": {
            "cache strategy": [
                "Frequent updates require a cache invalidation strategy such as TTL, event-driven invalidation, or versioned keys to keep data fresh.",
            ]
        },
        "keywords": ["cache", "performance", "invalidation"],
        "follow_up_questions": [
            "What trade-offs do you see between TTL-based expiration and explicit invalidation?",
            "How would you handle cache consistency when the catalog is updated by multiple services?",
        ],
        "ideal_answer_summary": "Use a cache with short TTL and event-driven invalidation or versioned keys to keep a hot product catalog fast while ensuring updates do not leave stale data for long.",
        "evaluation_hints": [
            "Look for practical invalidation and consistency trade-offs.",
            "Accept mention of caching layers and stale data risks.",
        ],
        "estimated_answer_time": 240,
        "estimated_score": 88,
        "tags": ["cache", "system design", "scalability"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "tech_hard_05",
        "interview_type": "technical",
        "category": "Database Design",
        "topic": "query optimization",
        "difficulty": "hard",
        "difficulty_rating": 1640.0,
        "role": "Senior Backend Engineer",
        "experience_level": "Senior",
        "company_type": "enterprise",
        "question": "A query on a reporting table is too slow. How would you identify the bottleneck and improve performance without changing the query semantics?",
        "expected_concepts": [
            {"name": "execution plan analysis", "weight": 1.0, "is_core": True},
            {"name": "index selection", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "table scans", "weight": 1.0, "is_core": True},
            {"name": "statistics and cardinality", "weight": 0.8, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "materialized views", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "rewrite query only", "pattern": "rewrite.*query|change.*query"},
        ],
        "attached_knowledge": {
            "query optimization": [
                "Improving performance can involve adding indexes, revising join order, or using summary tables while preserving the original query results.",
            ]
        },
        "keywords": ["optimization", "database", "query"],
        "follow_up_questions": [
            "How would you know if an index is being used by the query planner?",
            "When might you choose a materialized view over an additional index?",
        ],
        "ideal_answer_summary": "Identify the slowest operation with an execution plan, then improve indexing or data layout rather than changing the query semantics. Consider summary tables or denormalization for reporting workloads.",
        "evaluation_hints": [
            "Look for strong diagnostic steps and a balanced solution.",
            "Accept talk of execution plans and trade-offs.",
        ],
        "estimated_answer_time": 240,
        "estimated_score": 87,
        "tags": ["sql", "performance", "optimization"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "hr_01",
        "interview_type": "hr",
        "category": "Motivation",
        "topic": "career goals",
        "difficulty": "easy",
        "difficulty_rating": 900.0,
        "role": "Any",
        "experience_level": "Entry",
        "company_type": "any",
        "question": "Tell me about your career goals for the next two to three years and how this role fits into them.",
        "expected_concepts": [
            {"name": "career planning", "weight": 1.0, "is_core": True},
            {"name": "company fit", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "growth objectives", "weight": 1.0, "is_core": True},
            {"name": "role alignment", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "long-term ambition", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "generic goals", "pattern": "generic|vague|not specific"},
        ],
        "attached_knowledge": {
            "career goals": [
                "A strong answer connects personal growth goals with the company's mission and the responsibilities of the role.",
            ]
        },
        "keywords": ["career", "goals", "motivation"],
        "follow_up_questions": [
            "What skills are you most interested in developing in this role?",
            "How would you measure success in the first year?",
        ],
        "ideal_answer_summary": "The candidate should describe realistic growth in skills and responsibilities, and explain how the role supports that development without being overly generic.",
        "evaluation_hints": [
            "Listen for thoughtful alignment with the role and company.",
            "Avoid answers that sound scripted or unrelated.",
        ],
        "estimated_answer_time": 150,
        "estimated_score": 70,
        "tags": ["hr", "growth", "goals"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "hr_02",
        "interview_type": "hr",
        "category": "Strengths",
        "topic": "strengths",
        "difficulty": "easy",
        "difficulty_rating": 920.0,
        "role": "Any",
        "experience_level": "Entry",
        "company_type": "any",
        "question": "What are your top strengths, and how have you leveraged them in a team or work situation?",
        "expected_concepts": [
            {"name": "self-awareness", "weight": 1.0, "is_core": True},
            {"name": "real examples", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "strength description", "weight": 1.0, "is_core": True},
            {"name": "impact example", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "team benefit", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "hype without evidence", "pattern": "I am the best|excellent|perfect"},
        ],
        "attached_knowledge": {
            "strengths": [
                "A strong answer names a strength that matters for the role and backs it up with a concrete example.",
            ]
        },
        "keywords": ["strengths", "self-awareness", "team"],
        "follow_up_questions": [
            "How has this strength helped you overcome a challenge?",
            "How do you balance this strength when working with others?",
        ],
        "ideal_answer_summary": "The candidate identifies one or two strengths and supports them with examples showing tangible impact on a team or project.",
        "evaluation_hints": [
            "Look for sincerity and evidence rather than buzzwords.",
            "Accept honest and role-relevant strengths.",
        ],
        "estimated_answer_time": 140,
        "estimated_score": 72,
        "tags": ["hr", "strengths", "behavior"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "hr_03",
        "interview_type": "hr",
        "category": "Weaknesses",
        "topic": "weaknesses",
        "difficulty": "easy",
        "difficulty_rating": 930.0,
        "role": "Any",
        "experience_level": "Entry",
        "company_type": "any",
        "question": "What is one area you are working to improve, and what steps have you taken to make progress?",
        "expected_concepts": [
            {"name": "self-reflection", "weight": 1.0, "is_core": True},
            {"name": "development plan", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "honesty", "weight": 1.0, "is_core": True},
            {"name": "action steps", "weight": 1.0, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "recent progress", "weight": 0.6, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "clichéd weakness", "pattern": "perfectionism|working too hard|I care too much"},
        ],
        "attached_knowledge": {
            "weakness answer": [
                "A good answer names a real development area and shows concrete improvement steps without undermining the candidate's ability to do the job.",
            ]
        },
        "keywords": ["weaknesses", "improvement", "self-awareness"],
        "follow_up_questions": [
            "How do you monitor your progress on this improvement?",
            "What has been the hardest part of changing this behavior?",
        ],
        "ideal_answer_summary": "The candidate should mention a genuine weakness and the steps they are taking to improve it, demonstrating accountability and growth.",
        "evaluation_hints": [
            "Avoid answers that sound too rehearsed or insincere.",
            "Accept clear improvement actions.",
        ],
        "estimated_answer_time": 150,
        "estimated_score": 70,
        "tags": ["hr", "weakness", "growth"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "hr_04",
        "interview_type": "hr",
        "category": "Teamwork",
        "topic": "teamwork",
        "difficulty": "easy",
        "difficulty_rating": 940.0,
        "role": "Any",
        "experience_level": "Entry",
        "company_type": "any",
        "question": "Describe a time when you contributed to a team effort and how you helped the team succeed.",
        "expected_concepts": [
            {"name": "collaboration", "weight": 1.0, "is_core": True},
            {"name": "role clarity", "weight": 0.8, "is_core": True},
        ],
        "core_concepts": [
            {"name": "communication", "weight": 1.0, "is_core": True},
            {"name": "shared success", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "stakeholder alignment", "weight": 0.4, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "individual credit", "pattern": "I did everything|my idea only"},
        ],
        "attached_knowledge": {
            "teamwork": [
                "Strong answers emphasize the candidate's contribution within a collaborative effort and the value of working well with others.",
            ]
        },
        "keywords": ["teamwork", "collaboration", "success"],
        "follow_up_questions": [
            "What challenge did the team face and how did you address it?",
            "How did you ensure everyone stayed aligned?",
        ],
        "ideal_answer_summary": "The candidate describes a collaborative effort, their role in it, and how the team achieved a positive outcome through cooperation.",
        "evaluation_hints": [
            "Look for team-focused language and concrete contributions.",
            "Accept mention of communication or coordination techniques.",
        ],
        "estimated_answer_time": 150,
        "estimated_score": 72,
        "tags": ["hr", "teamwork", "collaboration"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "hr_05",
        "interview_type": "hr",
        "category": "Communication",
        "topic": "pressure handling",
        "difficulty": "easy",
        "difficulty_rating": 930.0,
        "role": "Any",
        "experience_level": "Mid",
        "company_type": "any",
        "question": "Tell me about a time you had to deliver results under pressure. What was the situation and how did you manage it?",
        "expected_concepts": [
            {"name": "stress management", "weight": 1.0, "is_core": True},
            {"name": "prioritization", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "clear communication", "weight": 0.8, "is_core": True},
            {"name": "stakeholder expectations", "weight": 0.6, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "results delivered", "weight": 0.4, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "pressure is always bad", "pattern": "pressure.*bad|stress.*negative"},
        ],
        "attached_knowledge": {
            "pressure handling": [
                "A strong response includes the situation, the actions taken under pressure, and the result achieved."
            ]
        },
        "keywords": ["pressure", "deadline", "time management"],
        "follow_up_questions": [
            "How did you keep your team focused during that period?",
            "What did you learn from that experience?",
        ],
        "ideal_answer_summary": "The answer should show that the candidate stayed calm, prioritized effectively, and delivered a positive outcome despite the pressure.",
        "evaluation_hints": [
            "Listen for concrete actions and realistic pressure.",
            "Avoid answers that only describe stress without resolution.",
        ],
        "estimated_answer_time": 150,
        "estimated_score": 72,
        "tags": ["hr", "pressure", "delivery"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "hr_06",
        "interview_type": "hr",
        "category": "Culture Fit",
        "topic": "learning ability",
        "difficulty": "easy",
        "difficulty_rating": 920.0,
        "role": "Any",
        "experience_level": "Entry",
        "company_type": "any",
        "question": "Describe a recent skill you learned and how you applied it in your work or studies.",
        "expected_concepts": [
            {"name": "continuous learning", "weight": 1.0, "is_core": True},
            {"name": "application of learning", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "learning process", "weight": 1.0, "is_core": True},
            {"name": "impact", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "self-directed research", "weight": 0.4, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "learning buzzwords", "pattern": "learned.*xyz|took.*course"},
        ],
        "attached_knowledge": {
            "learning ability": [
                "Good responses show how the candidate chose a skill, learned it, and used it to solve a real problem."
            ]
        },
        "keywords": ["learning", "skills", "development"],
        "follow_up_questions": [
            "What resources did you use to learn this skill?",
            "How have you continued to build on that knowledge?",
        ],
        "ideal_answer_summary": "The candidate describes a concrete learning experience, the resources used, and the real-world application of the new skill.",
        "evaluation_hints": [
            "Look for evidence of initiative and practical application.",
            "Accept examples from work, study, or personal projects.",
        ],
        "estimated_answer_time": 150,
        "estimated_score": 70,
        "tags": ["hr", "learning", "growth"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "hr_07",
        "interview_type": "hr",
        "category": "Leadership",
        "topic": "leadership",
        "difficulty": "easy",
        "difficulty_rating": 940.0,
        "role": "Any",
        "experience_level": "Mid",
        "company_type": "any",
        "question": "Tell me about a time when you took the lead on a project or task. What was your approach?",
        "expected_concepts": [
            {"name": "initiative", "weight": 1.0, "is_core": True},
            {"name": "team coordination", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "decision making", "weight": 0.8, "is_core": True},
            {"name": "stakeholder communication", "weight": 0.6, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "outcome focus", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "self-promotion", "pattern": "I did it all|my team.*me"},
        ],
        "attached_knowledge": {
            "leadership": [
                "A good leadership answer balances task ownership with collaboration and support for the team."
            ]
        },
        "keywords": ["leadership", "initiative", "direction"],
        "follow_up_questions": [
            "How did you keep the project on track?",
            "What challenges did the team face and how did you address them?",
        ],
        "ideal_answer_summary": "The candidate should describe taking ownership, coordinating the team, and delivering the project while empowering others.",
        "evaluation_hints": [
            "Listen for leadership style and team impact.",
            "Avoid answers that only focus on personal achievement.",
        ],
        "estimated_answer_time": 150,
        "estimated_score": 72,
        "tags": ["hr", "leadership", "management"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "hr_08",
        "interview_type": "hr",
        "category": "Achievements",
        "topic": "achievements",
        "difficulty": "easy",
        "difficulty_rating": 950.0,
        "role": "Any",
        "experience_level": "Entry",
        "company_type": "any",
        "question": "What is one achievement you are proud of, and why does it matter to you?",
        "expected_concepts": [
            {"name": "personal achievement", "weight": 1.0, "is_core": True},
            {"name": "motivation", "weight": 0.8, "is_core": True},
        ],
        "core_concepts": [
            {"name": "impact", "weight": 1.0, "is_core": True},
            {"name": "values alignment", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "learning outcome", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "non-work achievement", "pattern": "not work|personal.*hobby"},
        ],
        "attached_knowledge": {
            "achievements": [
                "A strong answer links the achievement to skills or values that are relevant to the job."
            ]
        },
        "keywords": ["achievement", "motivation", "impact"],
        "follow_up_questions": [
            "What did this achievement teach you about your strengths?",
            "How would you apply that success in this position?",
        ],
        "ideal_answer_summary": "The candidate shares a concrete achievement and explains why it matters, ideally tying it to qualities beneficial for the role.",
        "evaluation_hints": [
            "Look for relevance to the role and a strong personal takeaway.",
            "Accept examples that demonstrate initiative or impact.",
        ],
        "estimated_answer_time": 150,
        "estimated_score": 73,
        "tags": ["hr", "achievement", "motivation"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "behavioral_01",
        "interview_type": "behavioral",
        "category": "Leadership",
        "topic": "leadership challenge",
        "difficulty": "easy",
        "difficulty_rating": 930.0,
        "role": "Any",
        "experience_level": "Mid",
        "company_type": "any",
        "question": "Tell me about a time when you took a leadership role without a formal title. What was the situation and what actions did you take?",
        "expected_concepts": [
            {"name": "situation", "weight": 0.8, "is_core": True},
            {"name": "actions", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "initiative", "weight": 1.0, "is_core": True},
            {"name": "result", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "reflection", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "vague outcome", "pattern": "some success|it went well"},
        ],
        "attached_knowledge": {
            "leadership story": [
                "Behavioral leadership questions should follow a STAR format: describe the situation, task, action, and result.",
            ]
        },
        "keywords": ["leadership", "STAR", "behavioral"],
        "follow_up_questions": [
            "What did you learn about leading people in that moment?",
            "How did you involve others in the solution?",
        ],
        "ideal_answer_summary": "The candidate shares a STAR story about leading through influence, describing the situation, their actions, and the positive result.",
        "evaluation_hints": [
            "Expect clear STAR structure and reflection.",
            "Avoid answers that are only high-level or self-centered.",
        ],
        "estimated_answer_time": 170,
        "estimated_score": 74,
        "tags": ["behavioral", "leadership"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "behavioral_02",
        "interview_type": "behavioral",
        "category": "Conflict",
        "topic": "conflict resolution",
        "difficulty": "easy",
        "difficulty_rating": 940.0,
        "role": "Any",
        "experience_level": "Mid",
        "company_type": "any",
        "question": "Describe a time when you had a disagreement with a coworker. How did you handle the conflict and what was the outcome?",
        "expected_concepts": [
            {"name": "communication", "weight": 1.0, "is_core": True},
            {"name": "resolution", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "active listening", "weight": 0.8, "is_core": True},
            {"name": "compromise", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "relationship building", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "blaming others", "pattern": "they were wrong|he/she said"},
        ],
        "attached_knowledge": {
            "conflict resolution": [
                "Good answers show respect, a willingness to understand the other side, and a constructive outcome.",
            ]
        },
        "keywords": ["conflict", "team", "communication"],
        "follow_up_questions": [
            "What would you do differently from that experience?",
            "How did you make sure the team moved forward positively?",
        ],
        "ideal_answer_summary": "The candidate should describe a STAR example where they actively listened, addressed the issue constructively, and produced a positive outcome or learning.",
        "evaluation_hints": [
            "Look for empathy and resolution rather than blame.",
            "Accept realistic conflict details with a constructive tone.",
        ],
        "estimated_answer_time": 170,
        "estimated_score": 74,
        "tags": ["behavioral", "conflict"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "behavioral_03",
        "interview_type": "behavioral",
        "category": "Decision Making",
        "topic": "decision making",
        "difficulty": "easy",
        "difficulty_rating": 950.0,
        "role": "Any",
        "experience_level": "Mid",
        "company_type": "any",
        "question": "Tell me about a time when you had to make a difficult decision with incomplete information. What was your process and what did you learn?",
        "expected_concepts": [
            {"name": "judgment", "weight": 1.0, "is_core": True},
            {"name": "risk assessment", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "decision framework", "weight": 1.0, "is_core": True},
            {"name": "learning outcome", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "stakeholder input", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "decision paralysis", "pattern": "unable to decide|paralyzed"},
        ],
        "attached_knowledge": {
            "decision making": [
                "Behavioral decision questions should describe how the candidate weighed options and learned from the outcome.",
            ]
        },
        "keywords": ["decision", "judgment", "learning"],
        "follow_up_questions": [
            "How did you balance speed and accuracy in that decision?",
            "What evidence did you gather before choosing?",
        ],
        "ideal_answer_summary": "The candidate should explain a practical decision process under uncertainty and reflect on what they learned about making trade-offs.",
        "evaluation_hints": [
            "Look for structured reasoning and reflection.",
            "Avoid answers that are too vague or lack result details.",
        ],
        "estimated_answer_time": 170,
        "estimated_score": 74,
        "tags": ["behavioral", "decision"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "behavioral_04",
        "interview_type": "behavioral",
        "category": "Time Management",
        "topic": "time management",
        "difficulty": "easy",
        "difficulty_rating": 940.0,
        "role": "Any",
        "experience_level": "Entry",
        "company_type": "any",
        "question": "Describe a situation where you had competing deadlines. How did you manage your time and priorities?",
        "expected_concepts": [
            {"name": "priority setting", "weight": 1.0, "is_core": True},
            {"name": "planning", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "communication", "weight": 0.8, "is_core": True},
            {"name": "task tracking", "weight": 0.6, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "adjusting scope", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "working longer hours", "pattern": "long hours|overtime"},
        ],
        "attached_knowledge": {
            "time management": [
                "Strong answers describe prioritization, communication, and use of tools or methods to manage workload effectively.",
            ]
        },
        "keywords": ["time management", "priorities", "deadlines"],
        "follow_up_questions": [
            "How did you communicate competing priorities to stakeholders?",
            "What tools or methods helped you stay on track?",
        ],
        "ideal_answer_summary": "The candidate should share a concrete example of prioritizing tasks, communicating clearly, and meeting key deadlines effectively.",
        "evaluation_hints": [
            "Look for a balanced approach rather than just working harder.",
            "Accept mention of collaboration and adjustment.",
        ],
        "estimated_answer_time": 150,
        "estimated_score": 73,
        "tags": ["behavioral", "time management"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "behavioral_05",
        "interview_type": "behavioral",
        "category": "Failures",
        "topic": "failure reflection",
        "difficulty": "easy",
        "difficulty_rating": 950.0,
        "role": "Any",
        "experience_level": "Mid",
        "company_type": "any",
        "question": "Tell me about a failure you experienced, how you responded, and what you learned from it.",
        "expected_concepts": [
            {"name": "ownership", "weight": 1.0, "is_core": True},
            {"name": "learning", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "responsibility", "weight": 0.8, "is_core": True},
            {"name": "improvement", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "process adjustment", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "blaming others", "pattern": "they made me|because of them"},
        ],
        "attached_knowledge": {
            "failure story": [
                "A good failure story describes what happened, the candidate's response, and the lesson learned.",
            ]
        },
        "keywords": ["failure", "learning", "behavioral"],
        "follow_up_questions": [
            "How have you applied that lesson since then?",
            "What would you do differently if a similar situation happened again?",
        ],
        "ideal_answer_summary": "The candidate should describe a past failure honestly, explain how they responded constructively, and highlight the learning that followed.",
        "evaluation_hints": [
            "Look for accountability and improvement rather than excuses.",
            "Accept a realistic example with good reflection.",
        ],
        "estimated_answer_time": 170,
        "estimated_score": 74,
        "tags": ["behavioral", "failure", "reflection"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "behavioral_06",
        "interview_type": "behavioral",
        "category": "Success Stories",
        "topic": "success story",
        "difficulty": "easy",
        "difficulty_rating": 940.0,
        "role": "Any",
        "experience_level": "Entry",
        "company_type": "any",
        "question": "Share a success story where you solved a difficult problem. What was the impact?",
        "expected_concepts": [
            {"name": "problem solving", "weight": 1.0, "is_core": True},
            {"name": "impact", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "actions taken", "weight": 1.0, "is_core": True},
            {"name": "results", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "team collaboration", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "overly broad story", "pattern": "many people|a lot of things"},
        ],
        "attached_knowledge": {
            "success story": [
                "Good responses focus on the specific problem, the candidate's actions, and the meaningful result.",
            ]
        },
        "keywords": ["success", "impact", "problem solving"],
        "follow_up_questions": [
            "What made this solution particularly effective?",
            "How did others react to the result?",
        ],
        "ideal_answer_summary": "The candidate should describe a clear problem, the actions they took, and the positive impact the solution delivered.",
        "evaluation_hints": [
            "Look for concrete evidence of success and value created.",
            "Accept relevant metrics or outcomes.",
        ],
        "estimated_answer_time": 160,
        "estimated_score": 75,
        "tags": ["behavioral", "success", "impact"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "behavioral_07",
        "interview_type": "behavioral",
        "category": "Customer Situations",
        "topic": "customer service",
        "difficulty": "easy",
        "difficulty_rating": 930.0,
        "role": "Any",
        "experience_level": "Entry",
        "company_type": "any",
        "question": "Describe a time when you helped a customer or stakeholder with a difficult request. How did you ensure they were satisfied?",
        "expected_concepts": [
            {"name": "customer focus", "weight": 1.0, "is_core": True},
            {"name": "problem resolution", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "active listening", "weight": 0.8, "is_core": True},
            {"name": "follow-up", "weight": 0.6, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "empathy", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "overpromising", "pattern": "promise.*anything|do.*everything"},
        ],
        "attached_knowledge": {
            "customer situations": [
                "A strong answer balances customer empathy with realistic delivery and follow-through.",
            ]
        },
        "keywords": ["customer", "stakeholder", "service"],
        "follow_up_questions": [
            "How did you keep the customer informed during the process?",
            "What would you do differently next time?",
        ],
        "ideal_answer_summary": "The candidate should show they listened, took ownership, and followed through on a difficult stakeholder request with a good outcome.",
        "evaluation_hints": [
            "Look for empathy and results rather than just pleasing the customer.",
            "Accept mention of clear communication and follow-up.",
        ],
        "estimated_answer_time": 160,
        "estimated_score": 74,
        "tags": ["behavioral", "customer", "service"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "behavioral_08",
        "interview_type": "behavioral",
        "category": "Innovation",
        "topic": "innovation",
        "difficulty": "easy",
        "difficulty_rating": 940.0,
        "role": "Any",
        "experience_level": "Mid",
        "company_type": "any",
        "question": "Describe a time when you suggested an improvement or innovation that made a process better. What was the result?",
        "expected_concepts": [
            {"name": "creative thinking", "weight": 1.0, "is_core": True},
            {"name": "impact", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "initiative", "weight": 0.8, "is_core": True},
            {"name": "measurable result", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "collaboration", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "small change counting as innovation", "pattern": "small.*change|tiny.*improvement"},
        ],
        "attached_knowledge": {
            "innovation": [
                "A good example explains both the idea and the measurable benefit it delivered."
            ]
        },
        "keywords": ["innovation", "improvement", "process"],
        "follow_up_questions": [
            "How did you convince others to adopt the improvement?",
            "What did you measure to know it was successful?",
        ],
        "ideal_answer_summary": "The candidate should describe a practical innovation, the actions taken to implement it, and the impact it had on the process or team.",
        "evaluation_hints": [
            "Look for clear impact and collaborative execution.",
            "Accept quantifiable or qualitative improvements.",
        ],
        "estimated_answer_time": 165,
        "estimated_score": 75,
        "tags": ["behavioral", "innovation"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "system_01",
        "interview_type": "system_design",
        "category": "System Design",
        "topic": "url shortener",
        "difficulty": "easy",
        "difficulty_rating": 1000.0,
        "role": "Software Engineer",
        "experience_level": "Entry",
        "company_type": "startup",
        "question": "Design a simple URL shortener service. What components would you include and how would you generate unique short URLs?",
        "expected_concepts": [
            {"name": "simplified architecture", "weight": 1.0, "is_core": True},
            {"name": "unique key generation", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "storage model", "weight": 1.0, "is_core": True},
            {"name": "redirect flow", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "scalability", "weight": 0.4, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "collision handling absent", "pattern": "no.*collision|ignore.*collision"},
        ],
        "attached_knowledge": {
            "url shortener": [
                "A basic design includes a web front end, a service to create short codes, and a storage layer that maps codes to long URLs.",
            ]
        },
        "keywords": ["url shortener", "system design", "scalability"],
        "follow_up_questions": [
            "How would you handle a very high volume of redirect requests?",
            "What strategy would you use to avoid duplicate short codes?",
        ],
        "ideal_answer_summary": "A URL shortener includes a short code generator, persistent mapping storage, and redirect handling. Uniqueness can be enforced with a counter-based or hash-based approach and collision checks.",
        "evaluation_hints": [
            "Expect a simple architecture and consideration for unique URL generation.",
            "Accept either random codes or sequential generation with collision handling.",
        ],
        "estimated_answer_time": 190,
        "estimated_score": 75,
        "tags": ["system design", "scalability"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "system_02",
        "interview_type": "system_design",
        "category": "System Design",
        "topic": "chat application",
        "difficulty": "medium",
        "difficulty_rating": 1350.0,
        "role": "Software Engineer",
        "experience_level": "Mid",
        "company_type": "startup",
        "question": "Design a chat application for one-to-one messaging. What are the main components, and how would you handle message delivery and persistence?",
        "expected_concepts": [
            {"name": "message routing", "weight": 1.0, "is_core": True},
            {"name": "data persistence", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "real-time delivery", "weight": 1.0, "is_core": True},
            {"name": "message storage", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "presence signaling", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "chat as simple CRUD", "pattern": "simple.*crud|just.*db"},
        ],
        "attached_knowledge": {
            "chat app": [
                "A one-to-one chat service needs a realtime delivery layer, durable message storage, and handling for offline recipients.",
            ]
        },
        "keywords": ["chat", "messaging", "real-time"],
        "follow_up_questions": [
            "How would you ensure message order is preserved?",
            "What would you do for offline message delivery?",
        ],
        "ideal_answer_summary": "A chat app includes a messaging API, realtime delivery system, and persistent storage. Delivery should support online users with retries and store messages for offline users.",
        "evaluation_hints": [
            "Expect mention of delivery guarantees and offline persistence.",
            "Accept a simple but extensible architecture.",
        ],
        "estimated_answer_time": 220,
        "estimated_score": 80,
        "tags": ["system design", "messaging"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "system_03",
        "interview_type": "system_design",
        "category": "System Design",
        "topic": "food delivery",
        "difficulty": "medium",
        "difficulty_rating": 1380.0,
        "role": "Backend Engineer",
        "experience_level": "Mid",
        "company_type": "product",
        "question": "Outline a high-level design for a food delivery app that matches orders, restaurants, and delivery partners. What are the main data stores and services?",
        "expected_concepts": [
            {"name": "matching service", "weight": 1.0, "is_core": True},
            {"name": "scaled data stores", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "service decomposition", "weight": 1.0, "is_core": True},
            {"name": "user flows", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "geo queries", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "everything in one database", "pattern": "single.*db|one.*store"},
        ],
        "attached_knowledge": {
            "food delivery": [
                "A delivery platform typically includes order management, restaurant catalog, delivery tracking, and matching services.",
            ]
        },
        "keywords": ["food delivery", "system design", "matching"],
        "follow_up_questions": [
            "How would you keep driver location updates scalable?",
            "What consistency model is appropriate for order state?",
        ],
        "ideal_answer_summary": "The design should include services for orders, restaurants, delivery partner matching, and tracking, with separate stores for transactional data and geospatial queries.",
        "evaluation_hints": [
            "Look for end-to-end user flows and separation of concerns.",
            "Accept simple data models for MVP scope.",
        ],
        "estimated_answer_time": 230,
        "estimated_score": 82,
        "tags": ["system design", "logistics"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "system_04",
        "interview_type": "system_design",
        "category": "System Design",
        "topic": "ride sharing",
        "difficulty": "medium",
        "difficulty_rating": 1400.0,
        "role": "Senior Backend Engineer",
        "experience_level": "Senior",
        "company_type": "enterprise",
        "question": "Design the core architecture for a ride sharing platform. How would you support matching riders and drivers while minimizing latency?",
        "expected_concepts": [
            {"name": "geo-based matching", "weight": 1.0, "is_core": True},
            {"name": "low latency", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "service boundaries", "weight": 1.0, "is_core": True},
            {"name": "real-time updates", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "failure handling", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "driver location not needed", "pattern": "no.*location|ignore.*location"},
        ],
        "attached_knowledge": {
            "ride sharing": [
                "Ride sharing requires real-time driver location, matching algorithms, and efficient coordination between riders and drivers.",
            ]
        },
        "keywords": ["ride share", "matching", "low latency"],
        "follow_up_questions": [
            "How would you handle driver cancellations after a match is made?",
            "What caching strategy would you use for nearby driver lookups?",
        ],
        "ideal_answer_summary": "A ride sharing design includes driver location ingestion, rider requests, matching service, and short-lived booking state, optimized for low latency and resilience.",
        "evaluation_hints": [
            "Expect consideration of real-time location and matching costs.",
            "Accept a modular architecture with clear services.",
        ],
        "estimated_answer_time": 240,
        "estimated_score": 84,
        "tags": ["system design", "transport"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "system_05",
        "interview_type": "system_design",
        "category": "System Design",
        "topic": "load balancer",
        "difficulty": "medium",
        "difficulty_rating": 1370.0,
        "role": "Senior Backend Engineer",
        "experience_level": "Senior",
        "company_type": "enterprise",
        "question": "Describe how a load balancer distributes traffic across servers and what health checks are important to keep the service reliable.",
        "expected_concepts": [
            {"name": "traffic distribution", "weight": 1.0, "is_core": True},
            {"name": "service health checks", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "sticky sessions", "weight": 0.6, "is_core": False},
            {"name": "load balancing algorithms", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "autoscaling", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "health checks are optional", "pattern": "health.*optional|not.*health"},
        ],
        "attached_knowledge": {
            "load balancer": [
                "Load balancers route requests and use health checks to remove unhealthy instances before routing traffic to them.",
            ]
        },
        "keywords": ["load balancer", "scalability", "reliability"],
        "follow_up_questions": [
            "How would you handle a sudden traffic spike?",
            "What are the pros and cons of session affinity?",
        ],
        "ideal_answer_summary": "A load balancer distributes traffic with algorithms like round robin or least connections and uses health checks to keep unhealthy servers out of rotation.",
        "evaluation_hints": [
            "Expect mention of health checks and traffic distribution policies.",
            "Accept discussion of reliability trade-offs.",
        ],
        "estimated_answer_time": 220,
        "estimated_score": 80,
        "tags": ["system design", "load balancing"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "system_06",
        "interview_type": "system_design",
        "category": "System Design",
        "topic": "news feed caching",
        "difficulty": "medium",
        "difficulty_rating": 1360.0,
        "role": "Senior Backend Engineer",
        "experience_level": "Senior",
        "company_type": "enterprise",
        "question": "Design a caching layer for a social feed where content freshness matters but read volume is very high.",
        "expected_concepts": [
            {"name": "cache freshness", "weight": 1.0, "is_core": True},
            {"name": "read-heavy workloads", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "cache invalidation", "weight": 0.8, "is_core": True},
            {"name": "stale while revalidate", "weight": 0.6, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "fan-out on write", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "caching always reduces latency", "pattern": "always.*reduce|always.*faster"},
        ],
        "attached_knowledge": {
            "feed caching": [
                "Feeds often use time-based expiration or write-side fan-out to keep cached results fresh while still serving high read traffic.",
            ]
        },
        "keywords": ["cache", "feed", "social"],
        "follow_up_questions": [
            "How would you support personalized feeds while caching?",
            "What is the impact of cache misses in this design?",
        ],
        "ideal_answer_summary": "A feed cache balances freshness and volume with strategies like short TTL, stale-while-revalidate, or precomputed feed snapshots for common users.",
        "evaluation_hints": [
            "Look for awareness of personalization and staleness.",
            "Accept sensible caching trade-offs.",
        ],
        "estimated_answer_time": 230,
        "estimated_score": 82,
        "tags": ["system design", "cache", "feed"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "system_07",
        "interview_type": "system_design",
        "category": "System Design",
        "topic": "monitoring alerting",
        "difficulty": "medium",
        "difficulty_rating": 1340.0,
        "role": "Senior SRE Engineer",
        "experience_level": "Senior",
        "company_type": "enterprise",
        "question": "Design a basic monitoring and alerting system for a set of microservices. What metrics would you collect and how would you prioritize alerts?",
        "expected_concepts": [
            {"name": "key metrics", "weight": 1.0, "is_core": True},
            {"name": "alert prioritization", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "health metrics", "weight": 0.8, "is_core": True},
            {"name": "incident severity", "weight": 0.8, "is_core": False},
        ],
        "nice_to_have": [
            {"name": "dashboard design", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "alert every failure", "pattern": "alert.*every|all.*errors"},
        ],
        "attached_knowledge": {
            "monitoring": [
                "Strong monitoring systems collect latency, error rate, and saturation metrics and alert on actionable issues, not noise.",
            ]
        },
        "keywords": ["monitoring", "alerts", "microservices"],
        "follow_up_questions": [
            "How would you avoid alert fatigue for the on-call team?",
            "What’s the difference between a symptom and a root cause alert?",
        ],
        "ideal_answer_summary": "Collect service health metrics like latency, error rate, and saturation. Prioritize alerts for production-impacting issues and use thresholds to reduce noise.",
        "evaluation_hints": [
            "Look for actionable metrics and alert clarity.",
            "Accept practical examples for microservices.",
        ],
        "estimated_answer_time": 230,
        "estimated_score": 82,
        "tags": ["system design", "monitoring"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "question_id": "system_08",
        "interview_type": "system_design",
        "category": "System Design",
        "topic": "scalability",
        "difficulty": "hard",
        "difficulty_rating": 1680.0,
        "role": "Senior Architect",
        "experience_level": "Senior",
        "company_type": "enterprise",
        "question": "How would you scale a legacy monolithic application to handle ten times the traffic? Describe the high-level strategy and key trade-offs.",
        "expected_concepts": [
            {"name": "horizontal scaling", "weight": 1.0, "is_core": True},
            {"name": "service decomposition", "weight": 1.0, "is_core": True},
        ],
        "core_concepts": [
            {"name": "data partitioning", "weight": 0.8, "is_core": True},
            {"name": "operational complexity", "weight": 0.8, "is_core": True},
        ],
        "nice_to_have": [
            {"name": "deployment strategy", "weight": 0.5, "is_core": False},
        ],
        "common_misconceptions": [
            {"name": "scale by throwing hardware", "pattern": "more.*hardware|bigger.*server"},
        ],
        "attached_knowledge": {
            "legacy scaling": [
                "Scaling a monolith often requires sharding, caching, and incremental service extraction while managing operational risk.",
            ]
        },
        "keywords": ["scalability", "monolith", "microservices"],
        "follow_up_questions": [
            "How would you preserve data consistency while scaling?",
            "What is the role of caching in this plan?",
        ],
        "ideal_answer_summary": "A scalable strategy may involve load balancing, caching, and gradually extracting parts of the monolith into services, while balancing operational complexity and consistency.",
        "evaluation_hints": [
            "Expect realistic trade-offs and phased migration thinking.",
            "Accept a mix of short-term and long-term architecture.",
        ],
        "estimated_answer_time": 250,
        "estimated_score": 88,
        "tags": ["system design", "scalability"],
        "active": True,
        "created_at": NOW,
        "updated_at": NOW,
    },
]


def _validate_question_document(document: dict[str, Any]) -> InterviewQuestionModel:
    return InterviewQuestionModel.model_validate(document)


async def ensure_interview_question_indexes(db: AsyncIOMotorDatabase) -> None:
    collection = db[INTERVIEW_QUESTION_COLLECTION]
    indexes = [
        IndexModel([("question_id", ASCENDING)], unique=True),
        IndexModel([("interview_type", ASCENDING)]),
        IndexModel([("category", ASCENDING)]),
        IndexModel([("topic", ASCENDING)]),
        IndexModel([("difficulty", ASCENDING)]),
        IndexModel([("role", ASCENDING)]),
        IndexModel([("experience_level", ASCENDING)]),
        IndexModel([("company_type", ASCENDING)]),
        IndexModel([("active", ASCENDING)]),
        IndexModel([("tags", ASCENDING)]),
        IndexModel([("created_at", ASCENDING)]),
        IndexModel([("question", TEXT), ("keywords", TEXT)]),
    ]
    await collection.create_indexes(indexes)


async def seed_interview_questions(db: AsyncIOMotorDatabase) -> dict[str, int]:
    collection = db[INTERVIEW_QUESTION_COLLECTION]
    await ensure_interview_question_indexes(db)

    inserted = 0
    updated = 0
    skipped = 0

    for template in INTERVIEW_QUESTION_TEMPLATES:
        validated_model = _validate_question_document(template)
        document = validated_model.model_dump(mode="json")
        query = {"question_id": document["question_id"]}
        existing = await collection.find_one(query)
        if existing is None:
            await collection.insert_one(document)
            inserted += 1
            continue

        existing_content = {k: v for k, v in existing.items() if k not in {"_id", "created_at", "updated_at"}}
        new_content = {k: v for k, v in document.items() if k not in {"created_at", "updated_at"}}
        if existing_content != new_content:
            await collection.update_one(
                query,
                {
                    "$set": {**new_content, "updated_at": datetime.now(timezone.utc)},
                    "$setOnInsert": {"created_at": existing.get("created_at", datetime.now(timezone.utc))},
                },
                upsert=True,
            )
            updated += 1
        else:
            skipped += 1

    logger.info(
        "Interview question seed complete: %s inserted, %s updated, %s skipped",
        inserted,
        updated,
        skipped,
    )
    return {"inserted": inserted, "updated": updated, "skipped": skipped}
