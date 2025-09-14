import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from tools import run_excel_formula

load_dotenv()

llm = ChatOpenAI(model='gpt-4o', temperature = 0.7)

with open('questions.json', 'r') as f:
    questions = f.read()


# --- 2. STREAMLIT SESSION STATE ---

if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
    st.session_state.user_answers = []
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your AI-powered Excel mock interviewer. I'll ask you a few questions to assess your skills. Let's start with the first one. Good luck!"}]

# --- 3. HELPER FUNCTIONS ---

def current_question():
    """Returns the current question dictionary."""
    index = st.session_state.current_question_index
    if index < len(questions):
        return questions[index]
    return None

def evaluate_answer(question, user_answer):
    """Uses the LLM to evaluate a conceptual answer."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Excel interview evaluator. Your task is to evaluate a candidate's answer to a conceptual question. The evaluation criteria is: '{criteria}'. Based on this, score the candidate's answer from 1 (poor) to 5 (excellent) and provide a brief justification for your score."),
        ("user", "Here is the candidate answer, '{answer} evaluate it now")
    ])

    chain = prompt | llm | StrOutputParser()

    evaluation = chain.invoke({
        "criteria": question['evaluation_criteria'],
        "answer": user_answer
    })

    return evaluation

def handle_answer(user_answer):
    """Handles the user's answer, evaluates it, and moves to the next question."""

    st.session_state.user_answers.append(user_answer)

    question = current_question()

    if question['answer_type'] == 'formula':
        result = run_excel_formula(user_answer, question['test_case'])
        evaluation = result['output']
        st.session_state.scores.append(1 if result['correct'] else 0)
    
    elif question['answer_type'] == 'textual_explaination':
        evaluation = evaluate_answer(question, user_answer)
        st.session_state.scores.append(evaluation)
    
    st.session_state.messages.append({'role': 'assistant', 'contest':evaluation})

    st.session_state.current_question_index += 1

# --- 4. MAIN APP LOGIC ---

st.title('AI Excel Mock Interviewer')
st.write("Welcome! Please answer the questions to the best of your ability.")

for messages in st.session_state.messages:
    with st.chat_message(messages['role']):
        st.markdown(messages['content'])

current_question = current_question()

if current_question:
    question_text = current_question['question_text']
    if 'assistant' not in st.session_state.messages[-1]['content']:
        st.session_state.messages.append({'role':'assistant', 'content':question_text})
        with st.chat_message('assistant'):
            st.markdown(question_text)
    
    if user_input := st.chat_input("Your answer:"):
        handle_answer(user_input)
        # Rerun the script to display the new messages and next question
        st.rerun()
else:
    # End of the interview
    st.write("Thank you for completing the interview! The final report will be generated below.")
    # We will add the final report generation in the next step.
