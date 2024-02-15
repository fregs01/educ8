   
# @app.route('/category',methods=['GET'])
# def cat():
#     categories = Categories.query.all()
#     category_list =[{'CategoryID':category.category_id, 'CategoryName':category.name} for category in categories]
#     return jsonify({'categories':category_list})
# def extract_question_and_answer(lines):
#     # Extract question and answer from the provided lines
#     question_line = lines[0].strip()
#     answer_line = lines[1].strip()

#     # Check if the answer_line contains a completion
#     if answer_line.startswith("Completion:"):
#         # Extract the completion part and use it as the answer
#         answer = answer_line.split("Completion:")[1].strip()
#         return question_line, answer
#     else:
#         # If there is no explicit completion, use the whole answer_line
#         return question_line, answer_line


# def generate_options(correct_answer, all_sentences):
#     # Ensure there are enough sentences to generate incorrect options
#     if len(all_sentences) < 3:
#         return None  # Skip this question if there are not enough sentences

#     # Shuffle all sentences, excluding the correct answer
#     all_sentences = [sentence for sentence in all_sentences if sentence != correct_answer]
#     random.shuffle(all_sentences)

#     # Select the first three sentences as incorrect options
#     incorrect_options = all_sentences[:3]

#     # Add the correct answer to the list of options
#     options = [correct_answer] + incorrect_options

#     # If there are fewer than 4 options, pad with empty strings
#     options += [''] * (4 - len(options))

#     # Shuffle the options to avoid bias
#     random.shuffle(options)

#     return {
#         'A': options[0],
#         'B': options[1],
#         'C': options[2],
#         'D': options[3]
#     }

# def question_cat(filename, category):
#     global generated_question_count
#     desired_question_count = 15  # Set the desired number of questions
    
#     with open(filename, 'r') as file:
#         text = file.read()

#     lines = [line.strip() for line in text.split('\n') if line.strip()]
    
#     # Randomize the order of lines
#     random.shuffle(lines)

#     # Iterate over the lines to extract questions and answers
#     i = 0
#     while i < len(lines) and generated_question_count < desired_question_count:
#         # Extract question and answer
#         question, correct_answer = extract_question_and_answer(lines[i:i+2])
                
#         # Check if there are enough lines to extract options
#         if i + 3 < len(lines):
#             options = generate_options(correct_answer, lines[i+1:i+4])
#         else:
#             options = None

#         if options is not None:
#             print(f"What is the meaning of '{question}'?")
#             print(f"A. {options['A']}")
#             print(f"B. {options['B']}")
#             print(f"C. {options['C']}")
#             print(f"D. {options['D']}")
#             print()

#             generated_question_count += 1

#         i += 1

# # Reset the generated question count
# generated_question_count = 0

# # Call the function for "idioms.txt"
# question_cat('idioms.txt', 'idioms')

# # Reset the generated question count
# generated_question_count = 0

# # Call the function for "english.txt"
# question_cat('english.txt', 'english')
# # question_cat('uoe.txt', 'uoe')
# # nlp = spacy.load("en_core_web_sm")

# # # Function to extract nouns from a given text
# # def extract_nouns(text):
# #     doc = nlp(text)
# #     return [token.text for token in doc if token.pos_ == "NOUN"]

# # # Function to generate questions and options
# # def generate_questions(questions_file, options_file, num_questions):
# #     with open(questions_file, "r", encoding="utf-8") as q_file, open(options_file, "r", encoding="utf-8") as o_file:
# #         questions = q_file.readlines()
# #         options = o_file.readlines()

# #         # Shuffle questions and options
# #         random.shuffle(questions)
# #         random.shuffle(options)

# #         for i in range(num_questions):
# #             # Extract the noun from the completion side
# #             noun = extract_nouns(options[i])[0]

# #             # Generate options from other texts
# #             other_options = random.sample(options, 3)
# #             other_options.append(options[i])

# #             # Shuffle options
# #             random.shuffle(other_options)

#             print(f"{i + 1}. What is the meaning of \"{noun.capitalize()}\"?")
#             print("Options:")
#             for j, option in enumerate(other_options, start=1):
#                 print(f"   {j}. {option.strip()}")
