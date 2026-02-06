from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import OPENWEATHERMAP_API_KEY, USERS_DATA
from states import ProfileSetupStates
import requests
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

def setup(dispatcher):
    dispatcher.include_router(router)

# Таблица уровней активности
ACTIVITY_LEVELS = {
    "Минимальная активность": 1.2,
    "Слабая активность": 1.375,
    "Средняя активность": 1.55,
    "Высокая активность": 1.725,
    "Экстра-активность": 1.9
}

# Таблица перевода минут активности в коэффициенты активности
MINUTES_TO_ACTIVITY_FACTOR = {
    range(0, 10): 1.2,                 # Минимальная активность
    range(10, 30): 1.375,              # Слабая активность
    range(30, 60): 1.55,               # Средняя активность
    range(60, 90): 1.725,              # Высокая активность
    range(90, 500): 1.9                # Экстра-активность
}

# Таблица тренировок с параметрами
TRAININGS = {
    "Бег": {"kcal_per_minute": 10, "water_per_half_hour": 200},
    "Быстрая ходьба": {"kcal_per_minute": 6, "water_per_half_hour": 150},
    "Езда на велосипеде": {"kcal_per_minute": 8, "water_per_half_hour": 200},
    "Силовая тренировка": {"kcal_per_minute": 12, "water_per_half_hour": 250},
    "Йога": {"kcal_per_minute": 4, "water_per_half_hour": 100},
    "Плавание": {"kcal_per_minute": 10, "water_per_half_hour": 200}
}

# Список продуктов с калорийностью
FOODS = {
      "Яблоко": {"calories_per_100g": 52},
      "Банан": {"calories_per_100g": 89},
      "Куриная грудка": {"calories_per_100g": 165},
      "Говядина": {"calories_per_100g": 250},
      "Рыба треска": {"calories_per_100g": 78},
      "Сыр чеддер": {"calories_per_100g": 400},
      "Морковь": {"calories_per_100g": 41},
      "Огурец": {"calories_per_100g": 15},
      "Капуста белокочанная": {"calories_per_100g": 25},
      "Свёкла варёная": {"calories_per_100g": 49},
      "Картофель отварной": {"calories_per_100g": 87},
      "Хлеб ржаной": {"calories_per_100g": 214},
      "Молоко коровье": {"calories_per_100g": 61},
      "Йогурт натуральный": {"calories_per_100g": 59},
      "Майонез": {"calories_per_100g": 624},
      "Масло сливочное": {"calories_per_100g": 717},
      "Мёд": {"calories_per_100g": 304},
      "Сахар-песок": {"calories_per_100g": 387},
      "Чай чёрный": {"calories_per_100g": 1},
      "Салат латук": {"calories_per_100g": 15},
      "Творог нежирный": {"calories_per_100g": 100},
      "Макароны сухие": {"calories_per_100g": 371},
      "Гречка": {"calories_per_100g": 343},
      "Овсянка": {"calories_per_100g": 366},
      "Перловая крупа": {"calories_per_100g": 324},
      "Виноград": {"calories_per_100g": 69},
      "Арбуз": {"calories_per_100g": 30},
      "Апельсин": {"calories_per_100g": 47},
      "Яйцо варёное": {"calories_per_100g": 155},
      "Кефир жирный": {"calories_per_100g": 61},
      "Шоколад тёмный": {"calories_per_100g": 535},
}

# Функции для определения текущей погоды с помощью OpenWeatherMap API
BASE_GEO_URL = "http://api.openweathermap.org/geo/1.0/direct?"
BASE_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

def fetch_coordinates(city):
    """Получаем координаты города."""
    complete_url = f"{BASE_GEO_URL}q={city}&limit=1&appid={OPENWEATHERMAP_API_KEY}"
    response = requests.get(complete_url)
    data = response.json()
    if len(data) > 0:
        lat = data[0].get('lat')
        lon = data[0].get('lon')
        return lat, lon
    else:
        raise ValueError(f"Город {city} не найден")

def fetch_current_weather(lat, lon):
    """Получаем текущую температуру по координатам."""
    complete_url = f"{BASE_WEATHER_URL}?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHERMAP_API_KEY}"
    response = requests.get(complete_url)
    data = response.json()
    return data["main"]["temp"]

# Формула нормы калорий
def calculate_cal_norm(gender, weight, height, age, activity_factor):
    if gender == "Мужской":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    elif gender == "Женский":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        raise ValueError("Недопустимый пол")
    
    return round(bmr * activity_factor)

def calculate_water_norm(weight, activity_minutes, city):
    base_water_norm = weight * 30
    activity_water_norm = (activity_minutes // 30) * 500
    temperature_bonus = 0
    try:
        lat, lon = fetch_coordinates(city)
        current_temp = fetch_current_weather(lat, lon)
        if current_temp and current_temp > 25:
            temperature_bonus = 500
    except Exception as e:
        print(f"Ошибка при проверке погоды: {e}")

    total_water = base_water_norm + activity_water_norm + temperature_bonus
    return total_water


# Приветствие
@router.message(F.text.lower().startswith('/start'))
async def start_handler(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\n" 
                         "Этот бот поможет вам следить за своим питанием и потреблением воды.\n\n"
                         "/set_profile — настроить профиль,\n"
                         "/log_water — записать потребление воды в мл,\n"
                         "/log_food — добавить съеденный продукт,\n"
                         "/log_workout — зафиксировать тренировку,\n"
                         "/check_progress — проверить прогресс,\n"
                         "/recommended — посмотреть список низкокалорийных продуктов.")

# Настройка профиля пользователя
@router.message(F.text.lower().startswith('/set_profile'))
async def profile_setup_start(message: types.Message, state: FSMContext):
    await state.set_state(ProfileSetupStates.weight)
    await message.answer("Введите ваш вес (в килограммах):")

@router.message(ProfileSetupStates.weight)
async def process_weight(message: types.Message, state: FSMContext):
    weight = float(message.text.strip())
    await state.update_data(weight=weight)
    await state.set_state(ProfileSetupStates.height)
    await message.answer("Введите ваш рост (в сантиметрах):")

@router.message(ProfileSetupStates.height)
async def process_height(message: types.Message, state: FSMContext):
    height = float(message.text.strip())
    await state.update_data(height=height)
    await state.set_state(ProfileSetupStates.age)
    await message.answer("Введите ваш возраст:")

@router.message(ProfileSetupStates.age)
async def process_age(message: types.Message, state: FSMContext):
    age = int(message.text.strip())
    await state.update_data(age=age)
    await state.set_state(ProfileSetupStates.gender)
    await message.answer("Введите ваш пол ('Мужской' или 'Женский'):")

@router.message(ProfileSetupStates.gender)
async def process_gender(message: types.Message, state: FSMContext):
    gender = message.text.strip()
    if gender not in ["Мужской", "Женский"]:
        return await message.answer("Пожалуйста, введите 'Мужской' или 'Женский'.")
    
    await state.update_data(gender=gender)
    await state.set_state(ProfileSetupStates.activity)
    await message.answer("Введите среднее количество минут активности в день:")

@router.message(ProfileSetupStates.activity)
async def process_activity_level(message: types.Message, state: FSMContext):
    activity_minutes = int(message.text.strip())
    activity_factor = None
    for interval, factor in MINUTES_TO_ACTIVITY_FACTOR.items():
        if activity_minutes in interval:
            activity_factor = factor
            break
    
    if activity_factor is None:
        return await message.answer("Некорректное количество минут активности. Попробуйте снова.")
    
    await state.update_data(activity_minutes=activity_minutes, activity=activity_factor)
    await state.set_state(ProfileSetupStates.city)
    await message.answer("Введите название города проживания:")

@router.message(ProfileSetupStates.city)
async def process_city(message: types.Message, state: FSMContext):
    city = message.text.strip()
    data = await state.get_data()
    user_id = str(message.from_user.id)
    activity_minutes = data["activity_minutes"]
    water_goal = calculate_water_norm(data["weight"], activity_minutes, city)
    
    # Добавляем данные пользователя
    USERS_DATA[user_id] = {
        "weight": data["weight"],
        "height": data["height"],
        "age": data["age"],
        "gender": data["gender"],
        "activity_minutes": activity_minutes, 
        "city": city,
        "water_goal": water_goal,
        "calorie_goal": calculate_cal_norm(data["gender"], data["weight"], data["height"], data["age"], data["activity"]),
        "logged_water": 0,
        "logged_calories": 0,
        "burned_calories": 0
    }
    await state.clear()
    
    water_goal = USERS_DATA[user_id]["water_goal"]
    calorie_goal = USERS_DATA[user_id]["calorie_goal"]
    await message.answer(f"Профиль настроен!\n\n"
                         f"Ваш дневная норма воды: {water_goal:.1f} мл.\n"
                         f"Ваша дневная норма калорий: {calorie_goal:.1f} ккал.")

# Логирование воды
@router.message(F.text.lower().startswith('/log_water'))
async def log_water(message: types.Message, state: FSMContext):
    try:
        parts = message.text.split()
        user_id = str(message.from_user.id)
        user_data = USERS_DATA.get(user_id)

        if not user_data:
            await message.answer("Сначала настройте профиль с помощью /set_profile.")
            return

        if len(parts) == 2:
            amount_str = parts[1].strip()
            amount = float(amount_str)
            
            # Обновляем количество выпитой воды
            user_data["logged_water"] += amount
            USERS_DATA[user_id] = user_data 
            water_left = max(0, user_data["water_goal"] - user_data["logged_water"])
            
            await message.answer(f"Вы выпили {amount} мл воды. Осталось выпить {water_left:.1f} мл.")
        else:
            await message.answer("Укажите количество воды после команды, например: /log_water 200.")

    except ValueError as ve:
        await message.answer(str(ve))
        
# Логирование тренировок
@router.message(F.text.lower().startswith('/log_workout'))
async def log_workout(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    row_buttons = []
    buttons_per_row = 2
    for idx, training in enumerate(TRAININGS.keys()):
        button = types.InlineKeyboardButton(text=training, callback_data=f"log_workout:{training}")
        row_buttons.append(button)
        if (idx + 1) % buttons_per_row == 0 or idx == len(TRAININGS) - 1:
            builder.row(*row_buttons)
            row_buttons = []  
    
    await message.answer("Выберите тип тренировки:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith('log_workout:'))
async def select_training_type(callback: types.CallbackQuery, state: FSMContext):
    selected_training = callback.data.split(':')[1]
    await state.update_data(training_type=selected_training)
    await callback.message.answer(f"Вы выбрали {selected_training}. Введите количество минут тренировки:")

@router.message(lambda msg: msg.text.isdigit())
async def finalize_training(message: types.Message, state: FSMContext):
    try:
        training_time = int(message.text)
        data = await state.get_data()
        training_type = data.get("training_type")
        params = TRAININGS.get(training_type)

        burned_calories = training_time * params["kcal_per_minute"]
        recommended_water = ((training_time + 29) // 30) * params["water_per_half_hour"]
        
        # Обновляем общее количество сожженных калорий и воды
        user_id = str(message.from_user.id)
        user_data = USERS_DATA.get(user_id)
        if not user_data:
            return await message.answer("Сначала настройте профиль с помощью /set_profile.")
        user_data["logged_water"] += recommended_water
        remaining_water = user_data["water_goal"] - user_data["logged_water"]
        user_data["burned_calories"] += burned_calories
        remaining_calories = user_data["calorie_goal"] + user_data["burned_calories"]
        
        await state.clear()

        answer_text = (
            f"{training_type} {training_time} минут — {burned_calories} ккал.\n"
            f"Дополнительно: выпейте {recommended_water} мл воды.\n"
            f"Остаток воды за день: {remaining_water:.1f} мл.\n"
            f"Остаток калорий за день: {remaining_calories:.1f} ккал."
        )

        await message.answer(answer_text)

    except Exception as e:
        await message.answer("Что-то пошло не так. Попробуйте снова.")
        

# Проверка прогресса        
@router.message(F.text.lower().startswith('/check_progress'))
async def check_progress(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data = USERS_DATA.get(user_id)

    if not user_data:
        return await message.answer("Сначала настройте профиль с помощью /set_profile.")

    # Информация о воде
    water_consumed = user_data["logged_water"]
    water_goal = user_data["water_goal"]
    water_remaining = water_goal - water_consumed

    # Информация о калориях
    calories_consumed = user_data["logged_calories"]
    calories_burned = user_data["burned_calories"]
    calories_goal = user_data["calorie_goal"]
    calories_balance = calories_goal - calories_consumed + calories_burned

    # Сообщение пользователю
    progress_message = (
        "Ваш прогресс:\n\n"
        f"Вода:\n"
        f"- Выпито: {water_consumed:.1f} мл из {water_goal:.1f} мл.\n"
        f"- Осталось: {water_remaining:.1f} мл.\n\n"
        f"Калории:\n"
        f"- Потреблено: {calories_consumed:.1f} ккал из {calories_goal:.1f} ккал.\n"
        f"- Сожжено: {calories_burned:.1f} ккал.\n"
        f"- Баланс: {calories_balance:.1f} ккал."
    )

    await message.answer(progress_message, parse_mode="HTML")
    
# Логирование еды
@router.message(F.text.lower().startswith('/log_food'))
async def log_food(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    row_buttons = []
    buttons_per_row = 2
    for idx, food in enumerate(FOODS.keys()):
        button = types.InlineKeyboardButton(text=food, callback_data=f"log_food:{food}")
        row_buttons.append(button)
        if (idx + 1) % buttons_per_row == 0 or idx == len(FOODS) - 1:
            builder.row(*row_buttons)
            row_buttons = []  
    
    await message.answer("Выберите продукт:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith('log_food:'))
async def select_food_item(callback: types.CallbackQuery, state: FSMContext):
    selected_food = callback.data.split(':')[1]
    await state.update_data(selected_food=selected_food)
    await callback.message.answer(f"{selected_food} — {FOODS[selected_food]['calories_per_100g']} ккал на 100 г. Сколько грамм вы съели?")

@router.message(lambda msg: msg.text.isdigit())
async def finalize_food_log(message: types.Message, state: FSMContext):
    try:
        grams_eaten = int(message.text)
        data = await state.get_data()
        selected_food = data.get("selected_food")
        calories_per_gram = FOODS[selected_food]['calories_per_100g'] / 100
        consumed_calories = grams_eaten * calories_per_gram
        
        user_id = str(message.from_user.id)
        user_data = USERS_DATA.get(user_id)
        if not user_data:
            return await message.answer("Сначала настройте профиль с помощью /set_profile.")
        
        # Обновляем кол-во потреблённых калорий
        user_data["logged_calories"] += consumed_calories
        USERS_DATA[user_id] = user_data
        await state.clear()
        
        await message.answer(f"Записано: {consumed_calories:.1f} ккал.")

    except Exception as e:
        await message.answer("Что-то пошло не так. Попробуйте снова.")
        
# Обработчик команды /recommended
@router.message(F.text.lower().startswith('/recommended'))
async def show_recommendations(message: types.Message):
    # Отбираем продукты с низкой калорийностью (< 100 ккал на 100 г)
    low_cal_foods = [(food, info['calories_per_100g']) for food, info in FOODS.items() if info['calories_per_100g'] <= 100]
    sorted_low_cal_foods = sorted(low_cal_foods, key=lambda x: x[1])

    # Сообщение с перечнем продуктов
    recommendation_message = "Рекомендуемые низкокалорийные продукты:\n\n"
    for food, calories in sorted_low_cal_foods:
        recommendation_message += f"- {food}: {calories} ккал на 100 г\n"

    await message.answer(recommendation_message)