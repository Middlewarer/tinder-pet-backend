import os
import django
from random import choice, randint
from django.contrib.auth.hashers import make_password

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Tag, Preference
from animals.models import Animal, Characteristic
from interactions.models import Interaction, Match
from chats.models import Chat, Message

User = get_user_model()

# ===== ДАННЫЕ ДЛЯ ГЕНЕРАЦИИ =====
FIRST_NAMES = ['Алексей', 'Мария', 'Дмитрий', 'Елена', 'Сергей', 'Анна', 'Владимир', 'Екатерина', 'Андрей', 'Татьяна']
LAST_NAMES = ['Иванов', 'Петрова', 'Сидоров', 'Кузнецова', 'Смирнов', 'Васильева', 'Попов', 'Новикова', 'Федоров', 'Морозова']

ANIMAL_NAMES = {
    'dog': ['Рекс', 'Бим', 'Джек', 'Бобик', 'Тузик', 'Лорд', 'Граф', 'Мухтар', 'Барбос', 'Шарик'],
    'cat': ['Барсик', 'Мурка', 'Васька', 'Рыжик', 'Снежок', 'Пушок', 'Маркиз', 'Барон', 'Тиша', 'Люся']
}

DESCRIPTIONS = {
    'calm': 'Очень спокойный и уравновешенный питомец. Отлично подходит для квартиры.',
    'active': 'Энергичный и жизнерадостный. Требует активных прогулок и игр.',
    'kid_friendly': 'Обожает детей, очень терпеливый и дружелюбный.',
    'guide': 'Имеет навыки поводыря, очень послушный и умный.'
}

PHOTOS = {
    'dog': [
        'https://images.pexels.com/photos/4587956/german-shepherd-dog-outdoors-animal-4587956.jpeg',
        'https://images.pexels.com/photos/58997/pexels-photo-58997.jpeg',
        'https://images.pexels.com/photos/33053/dog-beagle-whistle-animal.jpg',
        'https://images.pexels.com/photos/1851164/pexels-photo-1851164.jpeg',
        'https://images.pexels.com/photos/2089679/pexels-photo-2089679.jpeg',
    ],
    'cat': [
        'https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg',
        'https://images.pexels.com/photos/416160/pexels-photo-416160.jpeg',
        'https://images.pexels.com/photos/127028/pexels-photo-127028.jpeg',
        'https://images.pexels.com/photos/1056251/pexels-photo-1056251.jpeg',
        'https://images.pexels.com/photos/3777622/pexels-photo-3777622.jpeg',
    ]
}

# ===== ФУНКЦИИ =====

def create_tags():
    """Создание базовых тегов"""
    tags_data = [
        ('calm', 'спокойный'),
        ('active', 'активный'),
        ('kid_friendly', 'для детей'),
        ('guide', 'поводырь')
    ]
    
    tags = []
    for tag_name, tag_display in tags_data:
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        tags.append(tag)
        print(f"  ✓ {tag_display}")
    return tags

def create_users(count=20):
    """Создание пользователей (owners и users)"""
    owners_count = count // 3  # 1/3 владельцы
    users_count = count - owners_count
    
    users = []
    
    print(f"\n  👤 Создание владельцев ({owners_count})...")
    for i in range(owners_count):
        first_name = choice(FIRST_NAMES)
        last_name = choice(LAST_NAMES)
        username = f"owner_{first_name.lower()}_{last_name.lower()}_{i}"
        
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="owner123",
            first_name=first_name,
            last_name=last_name,
            role='owner'
        )
        users.append(user)
        if (i + 1) % 5 == 0:
            print(f"    ✓ Создано {i + 1} владельцев...")
    
    print(f"  👤 Создание пользователей ({users_count})...")
    for i in range(users_count):
        first_name = choice(FIRST_NAMES)
        last_name = choice(LAST_NAMES)
        username = f"user_{first_name.lower()}_{last_name.lower()}_{i}"
        
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="user123",
            first_name=first_name,
            last_name=last_name,
            role='user'
        )
        users.append(user)
        if (i + 1) % 5 == 0:
            print(f"    ✓ Создано {i + 1} пользователей...")
    
    print(f"  ✓ Всего создано: {len(users)} пользователей")
    return users

def create_animals(owners, animals_per_owner=3):
    """Создание животных для каждого владельца"""
    animals = []
    tags = list(Tag.objects.all())
    tag_combinations = [
        ['calm'],
        ['active'],
        ['kid_friendly'],
        ['calm', 'kid_friendly'],
        ['active', 'kid_friendly'],
        ['calm', 'guide'],
        ['active', 'guide'],
        ['calm', 'active', 'kid_friendly'],
    ]
    
    print(f"\n  🐾 Создание животных (по {animals_per_owner} на владельца)...")
    
    for owner in owners:
        for i in range(animals_per_owner):
            # Выбираем тип животного
            pet_type = choice(['dog', 'cat'])
            name = choice(ANIMAL_NAMES[pet_type])
            age = randint(1, 12)  # от 1 до 12 лет
            photo = choice(PHOTOS[pet_type])
            
            # Выбираем случайные теги
            selected_tags = choice(tag_combinations)
            tags_for_animal = [t for t in tags if t.name in selected_tags]
            
            # Создаём животное
            animal = Animal.objects.create(
                owner=owner,
                name=f"{name}_{i+1}",
                years_of_age=age,
                description=f"{DESCRIPTIONS.get(selected_tags[0], 'Замечательный питомец')} "
                           f"Возраст: {age} лет. Привит, стерилизован.",
                photo=photo
            )
            
            # Добавляем характеристики
            for tag in tags_for_animal:
                Characteristic.objects.create(
                    pet=animal,
                    character=tag.name
                )
            
            animals.append(animal)
        
        print(f"    ✓ {owner.first_name} {owner.last_name}: создано {animals_per_owner} животных")
    
    print(f"  ✓ Всего создано: {len(animals)} животных")
    return animals

def create_preferences(users, tags):
    """Создание предпочтений для обычных пользователей"""
    users_list = [u for u in users if u.role == 'user']
    preferences_count = 0
    
    print(f"\n  ⚙️ Создание предпочтений для {len(users_list)} пользователей...")
    
    for user in users_list:
        # Случайный набор тегов (1-3 тега)
        num_tags = randint(1, 3)
        selected_tags = choice([
            ['calm'],
            ['active'],
            ['kid_friendly'],
            ['guide'],
            ['calm', 'kid_friendly'],
            ['active', 'kid_friendly'],
            ['calm', 'active'],
            ['calm', 'kid_friendly', 'active'],
        ][:num_tags])
        
        pref = Preference.objects.create(user=user)
        for tag_name in selected_tags:
            tag = Tag.objects.filter(name=tag_name).first()
            if tag:
                pref.preferred_tags.add(tag)
                preferences_count += 1
    
    print(f"  ✓ Создано предпочтений: {preferences_count}")
    return preferences_count

def create_likes_and_matches(users, animals):
    """Создание лайков и мэтчей"""
    users_list = [u for u in users if u.role == 'user']
    likes_created = 0
    matches_created = 0
    
    print(f"\n  💕 Создание лайков и мэтчей...")
    
    for user in users_list:
        # Каждый пользователь лайкает 30-70% животных
        animals_to_like = animals[:randint(len(animals) // 3, len(animals) // 2)]
        
        for animal in animals_to_like:
            # Проверяем, не лайкал ли уже
            if Interaction.objects.filter(user=user, animal=animal).exists():
                continue
            
            # Создаём лайк
            Interaction.objects.create(
                user=user,
                animal=animal,
                type='like'
            )
            likes_created += 1
            
            # Создаём мэтч (30% лайков превращаются в мэтчи)
            if randint(1, 100) <= 30:
                match = Match.objects.create(
                    user=user,
                    owner=animal.owner,
                    animal=animal,
                    status='pending'
                )
                matches_created += 1
        
        print(f"    ✓ {user.first_name} {user.last_name}: "
              f"лайкнул {len(animals_to_like)} животных")
    
    # Подтверждаем 50% мэтчей
    pending_matches = list(Match.objects.filter(status='pending'))
    matches_to_accept = pending_matches[:len(pending_matches) // 2]
    
    print(f"\n  💑 Подтверждение мэтчей...")
    for match in matches_to_accept:
        match.status = 'matched'
        match.save()
    
    print(f"  ✓ Создано лайков: {likes_created}")
    print(f"  ✓ Создано мэтчей: {matches_created} (подтверждено: {len(matches_to_accept)})")
    return likes_created, matches_created

def create_chats_and_messages():
    """Создание чатов и сообщений для подтверждённых мэтчей"""
    from chats.models import Chat, Message
    
    matched_matches = list(Match.objects.filter(status='matched'))
    messages_created = 0
    
    print(f"\n  💬 Создание чатов и сообщений...")
    
    for match in matched_matches:
        # Создаём чат
        chat = Chat.objects.create(match=match)
        
        # Создаём несколько сообщений
        num_messages = randint(3, 10)
        senders = [match.user, match.owner]
        
        messages_sample = [
            "Здравствуйте! Мне очень понравилось животное.",
            "Добрый день! Расскажите подробнее о нём?",
            "Да, конечно! Это очень ласковый и умный питомец.",
            "А сколько ему лет?",
            f"Уже {match.animal.years_of_age} года/лет.",
            "Прививки сделаны?",
            "Да, все прививки по возрасту.",
            "Отлично! Можно приехать посмотреть?",
            "Конечно, приезжайте в любое удобное время.",
            "Спасибо, договорились!"
        ]
        
        for i in range(num_messages):
            sender = choice(senders)
            text = choice(messages_sample)
            
            Message.objects.create(
                chat=chat,
                sender=sender,
                text=f"{text} (сообщение {i+1})"
            )
            messages_created += 1
        
        print(f"    ✓ Чат #{chat.id}: {match.animal.name} ({num_messages} сообщений)")
    
    print(f"  ✓ Создано чатов: {len(matched_matches)}")
    print(f"  ✓ Создано сообщений: {messages_created}")

def print_statistics():
    """Вывод статистики"""
    print("\n" + "=" * 60)
    print("📊 СТАТИСТИКА БАЗЫ ДАННЫХ")
    print("=" * 60)
    print(f"  • Теги: {Tag.objects.count()}")
    print(f"  • Пользователи: {User.objects.count()} "
          f"(владельцев: {User.objects.filter(role='owner').count()}, "
          f"ищущих: {User.objects.filter(role='user').count()})")
    print(f"  • Животные: {Animal.objects.count()}")
    print(f"  • Характеристики: {Characteristic.objects.count()}")
    print(f"  • Предпочтения: {Preference.objects.count()}")
    print(f"  • Лайки: {Interaction.objects.count()}")
    print(f"  • Мэтчи: {Match.objects.count()} "
          f"(подтверждено: {Match.objects.filter(status='matched').count()}, "
          f"ожидают: {Match.objects.filter(status='pending').count()}, "
          f"отклонено: {Match.objects.filter(status='rejected').count()})")
    
    from chats.models import Chat, Message
    print(f"  • Чаты: {Chat.objects.count()}")
    print(f"  • Сообщения: {Message.objects.count()}")
    print("=" * 60)

def print_test_accounts():
    """Вывод тестовых аккаунтов"""
    print("\n🔐 ТЕСТОВЫЕ АККАУНТЫ")
    print("-" * 40)
    
    owners = User.objects.filter(role='owner')[:3]
    print("Владельцы (пароль: owner123):")
    for owner in owners:
        print(f"  • {owner.username} - {owner.first_name} {owner.last_name}")
    
    users = User.objects.filter(role='user')[:3]
    print("\nПользователи (пароль: user123):")
    for user in users:
        print(f"  • {user.username} - {user.first_name} {user.last_name}")
    
    if len(owners) > 3 or len(users) > 3:
        print(f"\n  ... и ещё {User.objects.count() - 6} аккаунтов")

def main():
    print("\n" + "🌱" * 30)
    print("ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ ТЕСТОВЫМИ ДАННЫМИ")
    print("🌱" * 30)
    
    # Очистка БД
    print("\n🧹 Очистка базы данных...")
    Message.objects.all().delete()
    Chat.objects.all().delete()
    Match.objects.all().delete()
    Interaction.objects.all().delete()
    Preference.objects.all().delete()
    Characteristic.objects.all().delete()
    Animal.objects.all().delete()
    User.objects.all().delete()
    print("  ✓ База очищена")
    
    # Заполнение
    print("\n1️⃣ Создание тегов...")
    tags = create_tags()
    
    print("\n2️⃣ Создание пользователей...")
    users = create_users(count=30)  # 30 пользователей (10 владельцев, 20 ищущих)
    
    print("\n3️⃣ Создание животных...")
    owners = [u for u in users if u.role == 'owner']
    animals = create_animals(owners, animals_per_owner=4)  # 40 животных
    
    print("\n4️⃣ Создание предпочтений...")
    create_preferences(users, tags)
    
    print("\n5️⃣ Создание лайков и мэтчей...")
    create_likes_and_matches(users, animals)
    
    print("\n6️⃣ Создание чатов и сообщений...")
    create_chats_and_messages()
    
    print_statistics()
    print_test_accounts()
    
    print("\n" + "✅" * 30)
    print("ГОТОВО! БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА")
    print("✅" * 30)

if __name__ == '__main__':
    main()