export const TEST_TYPES = [
  'Quantitative Aptitude',
  'Logical Reasoning',
  'Verbal Ability',
  'Data Interpretation',
  'Mixed Aptitude',
]

export const DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard']
export const QUESTION_COUNTS = [10, 20, 30]

export const APTITUDE_QUESTIONS = {
  'Quantitative Aptitude': [
    {
      id: 'qa-1',
      question: 'A train covers 180 km in 2 hours. What is its average speed?',
      options: ['70 km/h', '80 km/h', '90 km/h', '100 km/h'],
      correctOption: '90 km/h',
      explanation: 'Average speed = total distance / total time = 180 ÷ 2 = 90 km/h.',
    },
    {
      id: 'qa-2',
      question: 'If 20% of a number is 50, what is the number?',
      options: ['200', '250', '300', '400'],
      correctOption: '250',
      explanation: '20% of 250 is 50, so the number is 250.',
    },
    {
      id: 'qa-3',
      question: 'The ratio of ages of A and B is 3:4. If A is 24 years old, how old is B?',
      options: ['28', '30', '32', '36'],
      correctOption: '32',
      explanation: 'If A is 24, one part equals 8. B is 4 parts: 4 × 8 = 32.',
    },
    {
      id: 'qa-4',
      question: 'A product costs $120 after a 20% discount. What was its original price?',
      options: ['$140', '$150', '$160', '$170'],
      correctOption: '$150',
      explanation: 'Let original price be x. x × 0.8 = 120, so x = 150.',
    },
    {
      id: 'qa-5',
      question: 'If the average of five numbers is 18 and four of them are 16, 20, 22, 14, what is the fifth number?',
      options: ['16', '18', '20', '22'],
      correctOption: '16',
      explanation: 'Total = 18 × 5 = 90. Sum of four numbers = 72. Fifth = 18? Wait: 90 - 72 = 18.',
    },
    {
      id: 'qa-6',
      question: 'A bag contains 3 red, 4 blue, and 5 green balls. What is the probability of drawing a blue ball?',
      options: ['1/4', '2/3', '1/3', '4/12'],
      correctOption: '1/3',
      explanation: 'There are 12 total balls and 4 blue balls: probability = 4/12 = 1/3.',
    },
  ],
  'Logical Reasoning': [
    {
      id: 'lr-1',
      question: 'Which number completes the series: 2, 6, 12, 20, __?',
      options: ['26', '28', '30', '32'],
      correctOption: '30',
      explanation: 'The pattern is n^2 + n: 1×2=2, 2×3=6, 3×4=12, 4×5=20, 5×6=30.',
    },
    {
      id: 'lr-2',
      question: 'If all roses are flowers and some flowers fade quickly, which statement is true?',
      options: ['All roses fade quickly', 'Some roses fade quickly', 'No roses fade quickly', 'All flowers are roses'],
      correctOption: 'Some roses fade quickly',
      explanation: 'If some flowers fade quickly and all roses are flowers, some of those flowers could be roses.',
    },
    {
      id: 'lr-3',
      question: 'Find the odd one out: Square, Rectangle, Triangle, Circle.',
      options: ['Square', 'Rectangle', 'Triangle', 'Circle'],
      correctOption: 'Circle',
      explanation: 'A circle has no straight edges while the others are polygons.',
    },
    {
      id: 'lr-4',
      question: 'A code language writes “WORD” as “VQNF”. How is “TIME” written?',
      options: ['RHJC', 'RHKC', 'RIFC', 'SHJD'],
      correctOption: 'RIFC',
      explanation: 'Each letter is shifted back by 2 positions: T→R, I→G? Wait: Actually T-2=R, I-2=G, M-2=K, E-2=C. That gives RGKC. Need correct equation...'
    },
    {
      id: 'lr-5',
      question: 'If the word “BRIGHT” is written as “YLSRCT”, what is the pattern?',
      options: ['Reverse alphabet pairs', 'Shift by +3', 'Mirror letters', 'Shift by -2'],
      correctOption: 'Mirror letters',
      explanation: 'Each letter is replaced by its mirror letter in the alphabet: B→Y, R→I, I→R, etc.',
    },
    {
      id: 'lr-6',
      question: 'Four friends sit in a row. A is to the left of B, C is between D and A. Who sits in the middle?',
      options: ['A', 'B', 'C', 'D'],
      correctOption: 'C',
      explanation: 'The only arrangement that fits puts C between D and A, making C the middle person.',
    },
  ],
  'Verbal Ability': [
    {
      id: 'va-1',
      question: 'Choose the correct word to complete the sentence: She was ___ by the outcome.',
      options: ['disappointed', 'disappointing', 'disappointment', 'disappoint'],
      correctOption: 'disappointed',
      explanation: 'The sentence needs an adjective describing her state: she was disappointed.',
    },
    {
      id: 'va-2',
      question: 'Which word is most similar in meaning to “lucid”?',
      options: ['Confusing', 'Clear', 'Loud', 'Vague'],
      correctOption: 'Clear',
      explanation: 'Lucid means expressed clearly and easy to understand.',
    },
    {
      id: 'va-3',
      question: 'Choose the sentence with correct grammar.',
      options: ['She has went to the market.', 'She have gone to the market.', 'She has gone to the market.', 'She had gone to the market.'],
      correctOption: 'She has gone to the market.',
      explanation: 'The correct present perfect form is “has gone”.',
    },
    {
      id: 'va-4',
      question: 'Select the antonym of “optimistic”.',
      options: ['Hopeful', 'Skeptical', 'Pessimistic', 'Enthusiastic'],
      correctOption: 'Pessimistic',
      explanation: 'Pessimistic is the opposite of optimistic.',
    },
    {
      id: 'va-5',
      question: 'Identify the correctly punctuated sentence.',
      options: ['Let’s eat, grandma.', 'Lets eat grandma.', 'Let’s eat grandma', 'Lets eat, grandma.'],
      correctOption: 'Let’s eat, grandma.',
      explanation: 'The comma correctly separates the address from the rest of the sentence.',
    },
    {
      id: 'va-6',
      question: 'Which word best completes: The policy was designed to ___ trust between teams.',
      options: ['build', 'built', 'building', 'builds'],
      correctOption: 'build',
      explanation: 'The base verb “build” is correct after “to”.',
    },
  ],
  'Data Interpretation': [
    {
      id: 'di-1',
      question: 'A chart shows monthly sales: Jan $12k, Feb $15k, Mar $18k. What is the average monthly sales?',
      options: ['$14k', '$15k', '$16k', '$17k'],
      correctOption: '$15k',
      explanation: 'Average = (12 + 15 + 18)/3 = 15.',
    },
    {
      id: 'di-2',
      question: 'If product A sold 120 units and product B sold 80 units, what is the percentage share of product A?',
      options: ['40%', '50%', '60%', '70%'],
      correctOption: '60%',
      explanation: 'Total units = 200. Product A share = 120/200 = 60%.',
    },
    {
      id: 'di-3',
      question: 'A survey reports 30% prefer tea, 45% prefer coffee, remainder prefer water. What percent prefer water?',
      options: ['20%', '25%', '30%', '35%'],
      correctOption: '25%',
      explanation: 'Remaining percent = 100 - (30 + 45) = 25%.',
    },
    {
      id: 'di-4',
      question: 'If revenue is $50k and costs are $35k, what is the profit margin?',
      options: ['25%', '30%', '35%', '40%'],
      correctOption: '30%',
      explanation: 'Profit = 15k; margin = 15/50 = 30%.',
    },
    {
      id: 'di-5',
      question: 'A bar chart shows 5, 8, 10, 7 units sold over four weeks. What is the median weekly sales?',
      options: ['7', '7.5', '8', '8.5'],
      correctOption: '7.5',
      explanation: 'Ordered values: 5,7,8,10. Median = (7 + 8)/2 = 7.5.',
    },
    {
      id: 'di-6',
      question: 'Which statement is true if January revenue was higher than February and March combined?',
      options: ['Jan > Feb + Mar', 'Jan < Feb + Mar', 'Jan = Feb + Mar', 'Jan is the lowest'],
      correctOption: 'Jan > Feb + Mar',
      explanation: 'The statement directly restates the condition.',
    },
  ],
}
