from aiogram.fsm.state import StatesGroup, State

# Create questions
class CreatAnalogyQuestionsRU(StatesGroup):
    create_question_ru = State()
    create_option_a_ru = State()
    create_option_b_ru = State()
    create_option_v_ru = State()
    create_option_g_ru = State()
    chose_correct_ru = State()

class CreatAnalogyQuestionsKG(StatesGroup):
    create_question_kg = State()
    create_option_a_kg = State()
    create_option_b_kg = State()
    create_option_v_kg = State()
    create_option_g_kg = State()
    chose_correct_kg = State()

class CreatGrammarQuestionsKG(StatesGroup):
    create_question_kg = State()
    create_option_a_kg = State()
    create_option_b_kg = State()
    create_option_v_kg = State()
    create_option_g_kg = State()
    chose_correct_kg = State()

class CreatGrammarQuestionsRU(StatesGroup):
    create_question_ru = State()
    create_option_a_ru = State()
    create_option_b_ru = State()
    create_option_v_ru = State()
    create_option_g_ru = State()
    chose_correct_ru = State()

class ChangeLanguageKG(StatesGroup):
    write_ru = State()

class ChangeLanguageRU(StatesGroup):
    write_kg = State()

class ChangePhoneNumberRU(StatesGroup):
    enter_phone_ru = State()

class ChangePhoneNumberKG(StatesGroup):
    enter_phone_kg = State()