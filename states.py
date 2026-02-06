from aiogram.fsm.state import StatesGroup, State

class ProfileSetupStates(StatesGroup):
    weight = State()
    height = State()
    age = State()
    gender = State()       
    activity = State()
    city = State()