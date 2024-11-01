from aiogram.fsm.state import StatesGroup, State

# Create questions
class CreatQuestionsRU(StatesGroup):
    create_question_ru = State()
    create_option_a_ru = State()
    create_option_b_ru = State()
    create_option_v_ru = State()
    create_option_g_ru = State()
    chose_correct_ru = State()

class CreatQuestionsKG(StatesGroup):
    create_question_kg = State()
    create_option_a_kg = State()
    create_option_b_kg = State()
    create_option_v_kg = State()
    create_option_g_kg = State()
    chose_correct_kg = State()

class EditAnalogy(StatesGroup):
    finish_editing = State()