from app import app, db
from models import Post, Role, Comment

with app.app_context():
    db.create_all()

        # Заполняем таблицу ролей, если она пуста
    if Role.query.count() == 0:
        # Добавляем несколько стандартных ролей для комментирования
        roles = [
            Role(name="Критик", description="Детально анализирует текст, указывает на недостатки.",
                 system_prompt="Ты - профессиональный критик. Твоя задача - выявить слабые места в тексте.",
                 prompt_template="Проанализируй следующий текст и напиши критический комментарий: {post_content}"),
            Role(name="Оптимист", description="Подчеркивает положительные аспекты и достоинства текста.",
                 system_prompt="Ты - оптимист. Твоя задача - выделить сильные стороны в тексте.",
                 prompt_template="Прочитай следующий текст и напиши позитивный комментарий: {post_content}"),
            Role(name="Скептик", description="Выражает сомнения и задает вопросы, требующие дополнительной информации.",
                 system_prompt="Ты - скептик. Твоя задача - задавать уточняющие вопросы и выражать сомнения в тексте.",
                 prompt_template="Ознакомься со следующим текстом и напиши комментарий, выражающий сомнение или задающий вопрос: {post_content}"),
        ]
        db.session.add_all(roles)
        db.session.commit()  # Сохраняем роли

    print("Database initialized")
    print("Added standard comment generation roles (if they didn't exist).")


