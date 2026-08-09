import logging
import re
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel

from app.models.coding_preference import CODING_PREFERENCES_COLLECTION
from app.models.coding_problem import CODING_PROBLEMS_COLLECTION
from app.models.coding_submission import CODING_SUBMISSIONS_COLLECTION
from app.schemas.coding import (
    PreferenceResponse,
    PreferenceUpdateRequest,
    ProblemCategoriesResponse,
    ProblemDetailResponse,
    ProblemListResponse,
    ProblemNeighborResponse,
    ProblemSummaryResponse,
    SubmissionHistoryItem,
    SubmissionHistoryResponse,
    TestCaseSchema,
)

logger = logging.getLogger(__name__)

PAGE_SIZE_DEFAULT = 20
CATEGORIES = [
    "Arrays",
    "Strings",
    "Linked Lists",
    "Trees",
    "Graphs",
    "Dynamic Programming",
    "Binary Search",
    "Bit Manipulation",
    "Greedy",
    "Heap",
    "Queue",
    "Recursion",
    "Stack",
    "Backtracking",
]


def _normalize_category(category: str | None) -> str | None:
    if not category:
        return None

    normalized = category.strip()
    if not normalized:
        return None

    aliases = {
        "linked list": "Linked Lists",
        "linked lists": "Linked Lists",
    }
    return aliases.get(normalized.lower(), normalized)


DEFAULT_PROBLEMS = [
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "category": "Arrays",
        "difficulty": "easy",
        "statement": "Given an array of integers nums and an integer target, return the indices of the two numbers that add up to the target.",
        "input_format": "The first line contains n, the second line contains n integers, and the third line contains target.",
        "output_format": "Print the indices as a space-separated pair.",
        "constraints": "2 <= n <= 10^4; -10^9 <= nums[i] <= 10^9",
        "examples": [{"input": "4\n2 7 11 15\n9", "expected_output": "0 1"}],
        "visible_test_cases": [{"input": "4\n2 7 11 15\n9", "expected_output": "0 1"}],
        "hidden_test_cases": [{"input": "4\n3 2 4 6\n6", "expected_output": "1 2"}],
        "starter_code": {
            "python": "def two_sum(nums, target):\n    pass\n",
            "java": "class Solution { public int[] twoSum(int[] nums, int target) { return new int[]{}; } }",
            "cpp": "#include <vector>\nusing namespace std;\nvector<int> twoSum(vector<int>& nums, int target) { return {}; }",
            "javascript": "function twoSum(nums, target) {\n  return [];\n}",
        },
        "tags": ["hash-map", "array"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Valid Parentheses",
        "slug": "valid-parentheses",
        "category": "Strings",
        "difficulty": "easy",
        "statement": "Given a string s containing just parentheses, determine if the input string is valid.",
        "input_format": "The first line contains a string s.",
        "output_format": "Print true or false.",
        "constraints": "1 <= s.length <= 10^4",
        "examples": [{"input": "()[]{}", "expected_output": "true"}],
        "visible_test_cases": [{"input": "()[]{}", "expected_output": "true"}],
        "hidden_test_cases": [{"input": "(]", "expected_output": "false"}],
        "starter_code": {
            "python": "def is_valid(s):\n    pass\n",
            "java": "class Solution { public boolean isValid(String s) { return false; } }",
            "cpp": "#include <string>\nusing namespace std;\nbool isValid(string s) { return false; }",
            "javascript": "function isValid(s) {\n  return false;\n}",
        },
        "tags": ["stack", "string"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Merge Intervals",
        "slug": "merge-intervals",
        "category": "Arrays",
        "difficulty": "medium",
        "statement": "Given an array of intervals where intervals[i] = [start, end], merge all overlapping intervals.",
        "input_format": "The first line contains n, followed by n lines each with start and end.",
        "output_format": "Print the merged intervals.",
        "constraints": "1 <= n <= 10^4",
        "examples": [{"input": "4\n1 3\n2 6\n8 10\n15 18", "expected_output": "1 6\n8 10\n15 18"}],
        "visible_test_cases": [{"input": "4\n1 3\n2 6\n8 10\n15 18", "expected_output": "1 6\n8 10\n15 18"}],
        "hidden_test_cases": [{"input": "4\n1 4\n4 5\n5 6\n7 9", "expected_output": "1 6\n7 9"}],
        "starter_code": {
            "python": "def merge_intervals(intervals):\n    pass\n",
            "java": "class Solution { public int[][] merge(int[][] intervals) { return new int[][]{}; } }",
            "cpp": "#include <vector>\nusing namespace std;\nvector<vector<int>> merge(vector<vector<int>>& intervals) { return {}; }",
            "javascript": "function mergeIntervals(intervals) {\n  return [];\n}",
        },
        "tags": ["intervals", "sorting"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Binary Tree Inorder Traversal",
        "slug": "binary-tree-inorder-traversal",
        "category": "Trees",
        "difficulty": "medium",
        "statement": "Return the inorder traversal of a binary tree.",
        "input_format": "The first line contains the tree values.",
        "output_format": "Print the traversal values.",
        "constraints": "The number of nodes is in the range [0, 100].",
        "examples": [{"input": "1 2 3", "expected_output": "2 1 3"}],
        "visible_test_cases": [{"input": "1 2 3", "expected_output": "2 1 3"}],
        "hidden_test_cases": [{"input": "3 1 2", "expected_output": "1 2 3"}],
        "starter_code": {
            "python": "def inorder_traversal(root):\n    pass\n",
            "java": "class Solution { public List<Integer> inorderTraversal(TreeNode root) { return new ArrayList<>(); } }",
            "cpp": "#include <vector>\nusing namespace std;\nvector<int> inorderTraversal(TreeNode* root) { return {}; }",
            "javascript": "function inorderTraversal(root) {\n  return [];\n}",
        },
        "tags": ["tree", "recursion"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Word Ladder",
        "slug": "word-ladder",
        "category": "Graphs",
        "difficulty": "hard",
        "statement": "Find the length of the shortest transformation sequence from beginWord to endWord.",
        "input_format": "The first line contains beginWord, the second line contains endWord, and the third line contains a list of words.",
        "output_format": "Print the length of the shortest transformation sequence.",
        "constraints": "1 <= words.length <= 5000",
        "examples": [{"input": "hit\ncog\n[hot, dot, dog, lot, log, cog]", "expected_output": "5"}],
        "visible_test_cases": [{"input": "hit\ncog\n[hot, dot, dog, lot, log, cog]", "expected_output": "5"}],
        "hidden_test_cases": [{"input": "hit\ncog\n[hot, dot, dog, lot, log]", "expected_output": "0"}],
        "starter_code": {
            "python": "def ladder_length(begin_word, end_word, word_list):\n    pass\n",
            "java": "class Solution { public int ladderLength(String beginWord, String endWord, List<String> wordList) { return 0; } }",
            "cpp": "#include <string>\n#include <vector>\nusing namespace std;\nint ladderLength(string beginWord, string endWord, vector<string> wordList) { return 0; }",
            "javascript": "function ladderLength(beginWord, endWord, wordList) {\n  return 0;\n}",
        },
        "tags": ["graph", "bfs"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "slug": "longest-substring-without-repeating-characters",
        "category": "Strings",
        "difficulty": "medium",
        "statement": "Given a string s, find the length of the longest substring without repeating characters.",
        "input_format": "The first line contains s.",
        "output_format": "Print the length of the longest substring.",
        "constraints": "0 <= s.length <= 5 * 10^4",
        "examples": [{"input": "abcabcbb", "expected_output": "3"}],
        "visible_test_cases": [{"input": "abcabcbb", "expected_output": "3"}],
        "hidden_test_cases": [{"input": "bbbbb", "expected_output": "1"}],
        "starter_code": {
            "python": "def length_of_longest_substring(s):\n    pass\n",
            "java": "class Solution { public int lengthOfLongestSubstring(String s) { return 0; } }",
            "cpp": "#include <string>\nusing namespace std;\nint lengthOfLongestSubstring(string s) { return 0; }",
            "javascript": "function lengthOfLongestSubstring(s) {\n  return 0;\n}",
        },
        "tags": ["sliding-window", "string"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Maximum Subarray",
        "slug": "maximum-subarray",
        "category": "Arrays",
        "difficulty": "easy",
        "statement": "Find the contiguous subarray with the largest sum.",
        "input_format": "The first line contains n and the next line contains n integers.",
        "output_format": "Print the maximum subarray sum.",
        "constraints": "1 <= n <= 10^5",
        "examples": [{"input": "5\n-2 1 -3 4 -1 2 1 -5 4", "expected_output": "6"}],
        "visible_test_cases": [{"input": "5\n-2 1 -3 4 -1 2 1 -5 4", "expected_output": "6"}],
        "hidden_test_cases": [{"input": "3\n-1 -2 -3", "expected_output": "-1"}],
        "starter_code": {
            "python": "def max_subarray(nums):\n    pass\n",
            "java": "class Solution { public int maxSubArray(int[] nums) { return 0; } }",
            "cpp": "#include <vector>\nusing namespace std;\nint maxSubArray(vector<int>& nums) { return 0; }",
            "javascript": "function maxSubArray(nums) {\n  return 0;\n}",
        },
        "tags": ["dp", "array"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Reverse Linked List",
        "slug": "reverse-linked-list",
        "category": "Linked Lists",
        "difficulty": "easy",
        "statement": "Reverse a singly linked list.",
        "input_format": "The first line contains the linked list values.",
        "output_format": "Print the reversed list.",
        "constraints": "The number of nodes is in the range [0, 10^3].",
        "examples": [{"input": "1 2 3 4", "expected_output": "4 3 2 1"}],
        "visible_test_cases": [{"input": "1 2 3 4", "expected_output": "4 3 2 1"}],
        "hidden_test_cases": [{"input": "0", "expected_output": "0"}],
        "starter_code": {
            "python": "def reverse_linked_list(head):\n    pass\n",
            "java": "class Solution { public ListNode reverseList(ListNode head) { return null; } }",
            "cpp": "struct ListNode { int val; ListNode* next; };\nListNode* reverseList(ListNode* head) { return head; }",
            "javascript": "function reverseList(head) {\n  return head;\n}",
        },
        "tags": ["linked-list", "recursion"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Product of Array Except Self",
        "slug": "product-of-array-except-self",
        "category": "Arrays",
        "difficulty": "medium",
        "statement": "Return an array of products of all elements except the current one.",
        "input_format": "The first line contains n and the second line contains n integers.",
        "output_format": "Print the resulting array.",
        "constraints": "1 <= n <= 10^5",
        "examples": [{"input": "5\n1 2 3 4 5", "expected_output": "120 60 40 30 24"}],
        "visible_test_cases": [{"input": "5\n1 2 3 4 5", "expected_output": "120 60 40 30 24"}],
        "hidden_test_cases": [{"input": "1\n-1", "expected_output": "1"}],
        "starter_code": {
            "python": "def product_except_self(nums):\n    pass\n",
            "java": "class Solution { public int[] productExceptSelf(int[] nums) { return new int[]{}; } }",
            "cpp": "#include <vector>\nusing namespace std;\nvector<int> productExceptSelf(vector<int>& nums) { return {}; }",
            "javascript": "function productExceptSelf(nums) {\n  return [];\n}",
        },
        "tags": ["prefix-sum", "array"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Number of Islands",
        "slug": "number-of-islands",
        "category": "Graphs",
        "difficulty": "medium",
        "statement": "Given a grid of '1' and '0', count the number of islands.",
        "input_format": "The first line contains rows and columns, followed by the grid.",
        "output_format": "Print the number of islands.",
        "constraints": "The number of rows and columns is in the range [1, 300].",
        "examples": [{"input": "4 5\n1 1 0 0 0\n0 1 0 0 1\n1 0 0 1 1\n0 0 0 0 0", "expected_output": "3"}],
        "visible_test_cases": [{"input": "4 5\n1 1 0 0 0\n0 1 0 0 1\n1 0 0 1 1\n0 0 0 0 0", "expected_output": "3"}],
        "hidden_test_cases": [{"input": "1 1\n1", "expected_output": "1"}],
        "starter_code": {
            "python": "def num_islands(grid):\n    pass\n",
            "java": "class Solution { public int numIslands(char[][] grid) { return 0; } }",
            "cpp": "#include <vector>\nusing namespace std;\nint numIslands(vector<vector<char>>& grid) { return 0; }",
            "javascript": "function numIslands(grid) {\n  return 0;\n}",
        },
        "tags": ["dfs", "graph"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Container With Most Water",
        "slug": "container-with-most-water",
        "category": "Arrays",
        "difficulty": "medium",
        "statement": "Find two lines that together with the x-axis form a container, such that the container contains the most water.",
        "input_format": "The first line contains n, followed by n space-separated heights.",
        "output_format": "Print the maximum amount of water a container can store.",
        "constraints": "2 <= n <= 10^5",
        "examples": [{"input": "9\n1 8 6 2 5 4 8 3 7", "expected_output": "49"}],
        "visible_test_cases": [{"input": "9\n1 8 6 2 5 4 8 3 7", "expected_output": "49"}],
        "hidden_test_cases": [{"input": "2\n1 1", "expected_output": "1"}],
        "starter_code": {
            "python": "def max_area(height):\n    pass\n",
            "java": "class Solution { public int maxArea(int[] height) { return 0; } }",
            "cpp": "#include <vector>\nusing namespace std;\nint maxArea(vector<int>& height) { return 0; }",
            "javascript": "function maxArea(height) {\n  return 0;\n}",
        },
        "tags": ["two-pointers", "array"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Palindrome Number",
        "slug": "palindrome-number",
        "category": "Strings",
        "difficulty": "easy",
        "statement": "Given an integer x, return true if x is a palindrome, and false otherwise.",
        "input_format": "The input contains an integer x.",
        "output_format": "Print true or false.",
        "constraints": "-2^31 <= x <= 2^31 - 1",
        "examples": [{"input": "121", "expected_output": "true"}],
        "visible_test_cases": [{"input": "121", "expected_output": "true"}],
        "hidden_test_cases": [{"input": "-121", "expected_output": "false"}],
        "starter_code": {
            "python": "def is_palindrome(x):\n    pass\n",
            "java": "class Solution { public boolean isPalindrome(int x) { return false; } }",
            "cpp": "using namespace std;\nbool isPalindrome(int x) { return false; }",
            "javascript": "function isPalindrome(x) {\n  return false;\n}",
        },
        "tags": ["math", "string"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Search in Rotated Sorted Array",
        "slug": "search-in-rotated-sorted-array",
        "category": "Arrays",
        "difficulty": "medium",
        "statement": "Given the array nums after possible rotation and an integer target, return the index of target if it is in nums, or -1 if it is not in nums.",
        "input_format": "The first line contains n, the second line contains nums, and the third line contains target.",
        "output_format": "Print the index of target or -1.",
        "constraints": "1 <= nums.length <= 5000",
        "examples": [{"input": "7\n4 5 6 7 0 1 2\n0", "expected_output": "4"}],
        "visible_test_cases": [{"input": "7\n4 5 6 7 0 1 2\n0", "expected_output": "4"}],
        "hidden_test_cases": [{"input": "7\n4 5 6 7 0 1 2\n3", "expected_output": "-1"}],
        "starter_code": {
            "python": "def search(nums, target):\n    pass\n",
            "java": "class Solution { public int search(int[] nums, int target) { return -1; } }",
            "cpp": "#include <vector>\nusing namespace std;\nint search(vector<int>& nums, int target) { return -1; }",
            "javascript": "function search(nums, target) {\n  return -1;\n}",
        },
        "tags": ["binary-search", "array"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Climbing Stairs",
        "slug": "climbing-stairs",
        "category": "Dynamic Programming",
        "difficulty": "easy",
        "statement": "You are climbing a staircase. It takes n steps to reach the top. Each time you can climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        "input_format": "The first line contains an integer n.",
        "output_format": "Print the total distinct ways.",
        "constraints": "1 <= n <= 45",
        "examples": [{"input": "3", "expected_output": "3"}],
        "visible_test_cases": [{"input": "3", "expected_output": "3"}],
        "hidden_test_cases": [{"input": "5", "expected_output": "8"}],
        "starter_code": {
            "python": "def climb_stairs(n):\n    pass\n",
            "java": "class Solution { public int climbStairs(int n) { return 0; } }",
            "cpp": "using namespace std;\nint climbStairs(int n) { return 0; }",
            "javascript": "function climbStairs(n) {\n  return 0;\n}",
        },
        "tags": ["dp", "memoization"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Coin Change",
        "slug": "coin-change",
        "category": "Dynamic Programming",
        "difficulty": "medium",
        "statement": "Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up, return -1.",
        "input_format": "The first line contains n, the second line contains coin values, and the third line contains target amount.",
        "output_format": "Print the minimum number of coins or -1.",
        "constraints": "1 <= coins.length <= 12; 0 <= amount <= 10^4",
        "examples": [{"input": "3\n1 2 5\n11", "expected_output": "3"}],
        "visible_test_cases": [{"input": "3\n1 2 5\n11", "expected_output": "3"}],
        "hidden_test_cases": [{"input": "3\n1 2 5\n7", "expected_output": "-1"}],
        "starter_code": {
            "python": "def coin_change(coins, amount):\n    pass\n",
            "java": "class Solution { public int coinChange(int[] coins, int amount) { return -1; } }",
            "cpp": "#include <vector>\nusing namespace std;\nint coinChange(vector<int>& coins, int amount) { return -1; }",
            "javascript": "function coinChange(coins, amount) {\n  return -1;\n}",
        },
        "tags": ["dp", "bfs"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Linked List Cycle",
        "slug": "linked-list-cycle",
        "category": "Linked Lists",
        "difficulty": "easy",
        "statement": "Given head, the head of a linked list, determine if the linked list has a cycle in it.",
        "input_format": "The first line contains list node values, and the second line contains cycle connection index.",
        "output_format": "Print true or false.",
        "constraints": "The number of nodes in the list is in the range [0, 10^4].",
        "examples": [{"input": "3 2 0 -4\n1", "expected_output": "true"}],
        "visible_test_cases": [{"input": "3 2 0 -4\n1", "expected_output": "true"}],
        "hidden_test_cases": [{"input": "1\n-1", "expected_output": "false"}],
        "starter_code": {
            "python": "def has_cycle(head):\n    pass\n",
            "java": "class Solution { public boolean hasCycle(ListNode head) { return false; } }",
            "cpp": "struct ListNode { int val; ListNode *next; };\nbool hasCycle(ListNode *head) { return false; }",
            "javascript": "function hasCycle(head) {\n  return false;\n}",
        },
        "tags": ["linked-list", "two-pointers"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Maximum Depth of Binary Tree",
        "slug": "maximum-depth-of-binary-tree",
        "category": "Trees",
        "difficulty": "easy",
        "statement": "Given the root of a binary tree, return its maximum depth.",
        "input_format": "The input contains level-order tree node values.",
        "output_format": "Print the maximum depth integer.",
        "constraints": "The number of nodes in the tree is in the range [0, 10^4].",
        "examples": [{"input": "3 9 20 null null 15 7", "expected_output": "3"}],
        "visible_test_cases": [{"input": "3 9 20 null null 15 7", "expected_output": "3"}],
        "hidden_test_cases": [{"input": "1 null 2", "expected_output": "2"}],
        "starter_code": {
            "python": "def max_depth(root):\n    pass\n",
            "java": "class Solution { public int maxDepth(TreeNode root) { return 0; } }",
            "cpp": "struct TreeNode { int val; TreeNode *left; TreeNode *right; };\nint maxDepth(TreeNode* root) { return 0; }",
            "javascript": "function maxDepth(root) {\n  return 0;\n}",
        },
        "tags": ["tree", "dfs"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Validate Binary Search Tree",
        "slug": "validate-binary-search-tree",
        "category": "Trees",
        "difficulty": "medium",
        "statement": "Given the root of a binary tree, determine if it is a valid binary search tree (BST).",
        "input_format": "The first line contains tree node values.",
        "output_format": "Print true or false.",
        "constraints": "The number of nodes in the tree is in the range [1, 10^4].",
        "examples": [{"input": "2 1 3", "expected_output": "true"}],
        "visible_test_cases": [{"input": "2 1 3", "expected_output": "true"}],
        "hidden_test_cases": [{"input": "5 1 4 null null 3 6", "expected_output": "false"}],
        "starter_code": {
            "python": "def is_valid_bst(root):\n    pass\n",
            "java": "class Solution { public boolean isValidBST(TreeNode root) { return false; } }",
            "cpp": "struct TreeNode { int val; TreeNode *left; TreeNode *right; };\nbool isValidBST(TreeNode* root) { return false; }",
            "javascript": "function isValidBST(root) {\n  return false;\n}",
        },
        "tags": ["tree", "bst"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Course Schedule",
        "slug": "course-schedule",
        "category": "Graphs",
        "difficulty": "medium",
        "statement": "Return true if you can finish all courses given prerequisite pairs, otherwise return false.",
        "input_format": "The first line contains numCourses, followed by prerequisite pairs.",
        "output_format": "Print true or false.",
        "constraints": "1 <= numCourses <= 2000",
        "examples": [{"input": "2\n1 0", "expected_output": "true"}],
        "visible_test_cases": [{"input": "2\n1 0", "expected_output": "true"}],
        "hidden_test_cases": [{"input": "2\n1 0\n0 1", "expected_output": "false"}],
        "starter_code": {
            "python": "def can_finish(num_courses, prerequisites):\n    pass\n",
            "java": "class Solution { public boolean canFinish(int numCourses, int[][] prerequisites) { return false; } }",
            "cpp": "#include <vector>\nusing namespace std;\nbool canFinish(int numCourses, vector<vector<int>>& prerequisites) { return false; }",
            "javascript": "function canFinish(numCourses, prerequisites) {\n  return false;\n}",
        },
        "tags": ["graph", "topological-sort"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Longest Palindromic Substring",
        "slug": "longest-palindromic-substring",
        "category": "Strings",
        "difficulty": "medium",
        "statement": "Given a string s, return the longest palindromic substring in s.",
        "input_format": "The input contains a single string s.",
        "output_format": "Print the longest palindromic substring.",
        "constraints": "1 <= s.length <= 1000",
        "examples": [{"input": "babad", "expected_output": "bab"}],
        "visible_test_cases": [{"input": "babad", "expected_output": "bab"}],
        "hidden_test_cases": [{"input": "cbbd", "expected_output": "bb"}],
        "starter_code": {
            "python": "def longest_palindrome(s):\n    pass\n",
            "java": "class Solution { public String longestPalindrome(String s) { return \"\"; } }",
            "cpp": "#include <string>\nusing namespace std;\nstring longestPalindrome(string s) { return \"\"; }",
            "javascript": "function longestPalindrome(s) {\n  return \"\";\n}",
        },
        "tags": ["string", "dp"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "Trapping Rain Water",
        "slug": "trapping-rain-water",
        "category": "Arrays",
        "difficulty": "hard",
        "statement": "Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
        "input_format": "The first line contains n, followed by n elevation heights.",
        "output_format": "Print the total trapped water amount.",
        "constraints": "n == height.length; 1 <= n <= 2 * 10^4",
        "examples": [{"input": "12\n0 1 0 2 1 0 1 3 2 1 2 1", "expected_output": "6"}],
        "visible_test_cases": [{"input": "12\n0 1 0 2 1 0 1 3 2 1 2 1", "expected_output": "6"}],
        "hidden_test_cases": [{"input": "6\n4 2 0 3 2 5", "expected_output": "9"}],
        "starter_code": {
            "python": "def trap(height):\n    pass\n",
            "java": "class Solution { public int trap(int[] height) { return 0; } }",
            "cpp": "#include <vector>\nusing namespace std;\nint trap(vector<int>& height) { return 0; }",
            "javascript": "function trap(height) {\n  return 0;\n}",
        },
        "tags": ["two-pointers", "stack"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
    {
        "title": "House Robber",
        "slug": "house-robber",
        "category": "Dynamic Programming",
        "difficulty": "medium",
        "statement": "Determine the maximum amount of money you can rob tonight without alerting the police by robbing adjacent houses.",
        "input_format": "The first line contains n, followed by house values.",
        "output_format": "Print the maximum storable money amount.",
        "constraints": "1 <= nums.length <= 100",
        "examples": [{"input": "4\n1 2 3 1", "expected_output": "4"}],
        "visible_test_cases": [{"input": "4\n1 2 3 1", "expected_output": "4"}],
        "hidden_test_cases": [{"input": "5\n2 7 9 3 1", "expected_output": "12"}],
        "starter_code": {
            "python": "def rob(nums):\n    pass\n",
            "java": "class Solution { public int rob(int[] nums) { return 0; } }",
            "cpp": "#include <vector>\nusing namespace std;\nint rob(vector<int>& nums) { return 0; }",
            "javascript": "function rob(nums) {\n  return 0;\n}",
        },
        "tags": ["dp", "array"],
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    },
]


async def get_preferences(db: AsyncIOMotorDatabase, user_id: str) -> PreferenceResponse:
    collection = db[CODING_PREFERENCES_COLLECTION]
    document = await collection.find_one({"user_id": user_id})
    return PreferenceResponse(preferred_language=document.get("preferred_language") if document else None)


async def update_preferences(
    db: AsyncIOMotorDatabase, user_id: str, payload: PreferenceUpdateRequest
) -> PreferenceResponse:
    collection = db[CODING_PREFERENCES_COLLECTION]
    await collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "preferred_language": payload.preferred_language,
                "updated_at": datetime.now(timezone.utc),
            },
            "$setOnInsert": {"user_id": user_id},
        },
        upsert=True,
    )
    logger.info("Coding language preference set for user %s: %s", user_id, payload.preferred_language)
    return PreferenceResponse(preferred_language=payload.preferred_language)


async def _ensure_problems_seeded(db: AsyncIOMotorDatabase) -> None:
    """Seed a default catalog of coding problems when the collection has fewer than 20 problems."""
    collection = db[CODING_PROBLEMS_COLLECTION]

    for template in DEFAULT_PROBLEMS:
        existing = await collection.find_one({"slug": template["slug"]})
        if not existing:
            document = {
                "title": template["title"],
                "slug": template["slug"],
                "category": template["category"],
                "difficulty": template["difficulty"],
                "statement": template["statement"],
                "input_format": template["input_format"],
                "output_format": template["output_format"],
                "constraints": template["constraints"],
                "examples": template.get("examples", []),
                "visible_test_cases": template.get("visible_test_cases", []),
                "hidden_test_cases": template.get("hidden_test_cases", []),
                "starter_code": template.get("starter_code", {}),
                "tags": template.get("tags", []),
                "time_limit_ms": template.get("time_limit_ms", 1000),
                "memory_limit_mb": template.get("memory_limit_mb", 128),
                "total_submissions": 0,
                "total_accepted": 0,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            await collection.insert_one(document)

    logger.info("Seeded default coding problems catalog into MongoDB")


async def _ensure_coding_problem_indexes(db: AsyncIOMotorDatabase) -> None:
    collection = db[CODING_PROBLEMS_COLLECTION]
    await collection.create_indexes([
        IndexModel([("category", 1)]),
        IndexModel([("difficulty", 1)]),
        IndexModel([("created_at", 1)]),
        IndexModel([("title", 1)]),
        IndexModel([("tags", 1)]),
        IndexModel([("starter_code.python", 1)]),
        IndexModel([("starter_code.javascript", 1)]),
        IndexModel([("starter_code.java", 1)]),
        IndexModel([("starter_code.cpp", 1)]),
    ])


def _build_problem_query(
    search: str | None,
    category: str | None,
    difficulty: str | None,
    language: str | None,
) -> dict:
    query: dict = {}
    normalized_category = _normalize_category(category)

    if search:
        trimmed_search = search.strip()
        if trimmed_search:
            escaped_search = re.escape(trimmed_search)
            query["$or"] = [
                {"title": {"$regex": escaped_search, "$options": "i"}},
                {"category": {"$regex": escaped_search, "$options": "i"}},
                {"tags": {"$elemMatch": {"$regex": escaped_search, "$options": "i"}}},
            ]

    if normalized_category:
        query["category"] = {"$regex": f"^{re.escape(normalized_category)}$", "$options": "i"}

    normalized_difficulty = difficulty.strip().lower() if difficulty else None
    if normalized_difficulty in {"easy", "medium", "hard"}:
        query["difficulty"] = normalized_difficulty

    normalized_language = language.strip().lower() if language else None
    if normalized_language in {"python", "java", "cpp", "javascript"}:
        query[f"starter_code.{normalized_language}"] = {"$exists": True}

    return query


def _resolve_sort(sort: str) -> tuple[str, int]:
    sort_map = {
        "problem_number": ("created_at", 1),
        "title": ("title", 1),
        "difficulty": ("difficulty", 1),
        "category": ("category", 1),
    }
    return sort_map.get(sort, ("created_at", 1))


async def get_problem_categories(db: AsyncIOMotorDatabase) -> ProblemCategoriesResponse:
    await _ensure_problems_seeded(db)
    collection = db[CODING_PROBLEMS_COLLECTION]
    categories = await collection.distinct("category")

    normalized_categories = sorted(
        { _normalize_category(category) for category in categories if _normalize_category(category) }
    )

    return ProblemCategoriesResponse(categories=normalized_categories)


async def list_problems(
    db: AsyncIOMotorDatabase,
    user_id: str,
    search: str | None,
    category: str | None,
    difficulty: str | None,
    language: str | None,
    page: int,
    page_size: int = PAGE_SIZE_DEFAULT,
    sort: str = "problem_number",
) -> ProblemListResponse:
    await _ensure_problems_seeded(db)

    problems_collection = db[CODING_PROBLEMS_COLLECTION]
    query = _build_problem_query(search, category, difficulty, language)

    total = await problems_collection.count_documents(query)
    skip = max(page - 1, 0) * page_size

    sort_field, sort_order = _resolve_sort(sort)

    cursor = (
        problems_collection.find(query)
        .sort(sort_field, sort_order)
        .skip(skip)
        .limit(page_size)
    )
    documents = await cursor.to_list(length=page_size)

    solved_ids = await _get_solved_problem_ids(db, user_id)

    problems = [
        ProblemSummaryResponse(
            id=str(doc["_id"]),
            title=doc["title"],
            category=doc["category"],
            difficulty=doc["difficulty"],
            tags=doc.get("tags", []),
            is_solved=str(doc["_id"]) in solved_ids,
            acceptance_rate=(
                (doc.get("total_accepted", 0) / doc.get("total_submissions", 1))
                if doc.get("total_submissions", 0) > 0
                else 0.0
            ),
        )
        for doc in documents
    ]

    return ProblemListResponse(problems=problems, total=total, page=page, page_size=page_size)


async def get_problem_neighbors(
    db: AsyncIOMotorDatabase,
    user_id: str,
    problem_id: str,
    search: str | None,
    category: str | None,
    difficulty: str | None,
    language: str | None,
    sort: str = "problem_number",
) -> ProblemNeighborResponse:
    await _ensure_problems_seeded(db)

    if not ObjectId.is_valid(problem_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid problem identity")

    problems_collection = db[CODING_PROBLEMS_COLLECTION]
    query = _build_problem_query(search, category, difficulty, language)

    sort_field, sort_order = _resolve_sort(sort)
    total = await problems_collection.count_documents(query)

    cursor = problems_collection.find(query, {"_id": 1}).sort(sort_field, sort_order)
    ids = [str(doc["_id"]) for doc in await cursor.to_list(length=total)]

    if not ids:
        return ProblemNeighborResponse(position=0, total=0)

    try:
        current_index = ids.index(problem_id)
    except ValueError:
        return ProblemNeighborResponse(position=0, total=total)

    previous_problem_id = ids[current_index - 1] if current_index > 0 else None
    next_problem_id = ids[current_index + 1] if current_index < total - 1 else None

    return ProblemNeighborResponse(
        previous_problem_id=previous_problem_id,
        next_problem_id=next_problem_id,
        position=current_index + 1,
        total=total,
    )


async def _get_solved_problem_ids(db: AsyncIOMotorDatabase, user_id: str) -> set[str]:
    from app.models.coding_progress import CODING_PROGRESS_COLLECTION

    progress_collection = db[CODING_PROGRESS_COLLECTION]
    document = await progress_collection.find_one({"user_id": user_id})
    if not document:
        return set()
    return set(document.get("solved_problem_ids", []))


async def get_problem_detail(
    db: AsyncIOMotorDatabase, user_id: str, problem_id: str
) -> ProblemDetailResponse:
    if not ObjectId.is_valid(problem_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid problem identity")

    collection = db[CODING_PROBLEMS_COLLECTION]
    document = await collection.find_one({"_id": ObjectId(problem_id)})

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    solved_ids = await _get_solved_problem_ids(db, user_id)

    raw_examples = []
    for item in document.get("examples", []):
        raw_examples.append(
            TestCaseSchema(
                input=item.get("input", ""),
                expected_output=item.get("expected_output") or item.get("output", ""),
            )
        )

    def normalize_test_cases(test_cases):
        normalized = []
        for item in test_cases:
            normalized.append(
                TestCaseSchema(
                    input=item.get("input", ""),
                    expected_output=item.get("expected_output") or item.get("output", ""),
                )
            )
        return normalized

    constraints = document.get("constraints", "")
    if isinstance(constraints, list):
        constraints = "\n".join(str(item) for item in constraints)

    return ProblemDetailResponse(
        id=str(document["_id"]),
        title=document["title"],
        category=document["category"],
        difficulty=document["difficulty"],
        tags=document.get("tags", []),
        statement=document.get("statement") or document.get("problem_statement", ""),
        input_format=document.get("input_format", ""),
        output_format=document.get("output_format", ""),
        constraints=constraints,
        examples=raw_examples,
        visible_test_cases=normalize_test_cases(document.get("visible_test_cases", [])),
        starter_code=document.get("starter_code", {}),
        time_limit_ms=document.get("time_limit_ms", 1000),
        memory_limit_mb=document.get("memory_limit_mb", 128),
        is_solved=problem_id in solved_ids,
    )


async def get_submission_history(
    db: AsyncIOMotorDatabase, user_id: str, problem_id: str | None = None
) -> SubmissionHistoryResponse:
    collection = db[CODING_SUBMISSIONS_COLLECTION]

    query: dict = {"user_id": user_id}
    if problem_id:
        query["problem_id"] = problem_id

    cursor = collection.find(query).sort("submitted_at", -1).limit(50)
    documents = await cursor.to_list(length=50)

    submissions = [
        SubmissionHistoryItem(
            id=str(doc["_id"]),
            problem_id=doc["problem_id"],
            language=doc["language"],
            status=doc["status"],
            runtime_ms=doc.get("runtime_ms"),
            memory_kb=doc.get("memory_kb"),
            submitted_at=doc["submitted_at"],
        )
        for doc in documents
    ]

    return SubmissionHistoryResponse(submissions=submissions)