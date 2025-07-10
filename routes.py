from flask import render_template, request, redirect, url_for, flash, send_file
from app import app, db
from models import Post, Role, Comment
from config import Config
import time
import json
import os


@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title or not content:
            flash('Заголовок и содержание не могут быть пустыми!', 'danger')
        else:
            post = Post(title=title, content=content)
            db.session.add(post)
            db.session.commit()
            flash('Пост успешно создан!', 'success')
            return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
def view_post(post_id):
    """Отображает детальную страницу поста с комментариями."""
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.generated_at.desc()).all()
    # Получаем только активные роли для отображения в выпадающем списке
    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()

    return render_template('post_detail.html', post=post, comments=comments, roles=roles)



@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title or not content:
            flash('Заголовок и содержание не могут быть пустыми!', 'danger')
        else:
            post.title = title
            post.content = content
            db.session.commit()
            flash('Пост успешно обновлен!', 'success')
            return redirect(url_for('view_post', post_id=post.id))
    return render_template('post_form.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Пост успешно удален!', 'success')
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/generate_comments', methods=['POST'])
def generate_comments_for_post(post_id):
    """Генерирует комментарии для поста, опционально для конкретной роли."""
    post = Post.query.get_or_404(post_id)
    selected_role_id = request.form.get('role_id')
    
    # Переписываем логику выбора ролей, чтобы избежать дублирования
    roles_to_process = []
    if selected_role_id and selected_role_id != 'all':
        # Ищем одну конкретную роль, но убеждаемся, что она активна
        role = Role.query.filter_by(id=selected_role_id, is_active=True).first()
        if role:
            roles_to_process = [role] # Результат - список с одним элементом
        else:
            flash(f"Активная роль с ID {selected_role_id} не найдена.", 'danger')
    else:
        # Иначе, берем все активные роли
        roles_to_process = Role.query.filter_by(is_active=True).all()

    if not roles_to_process:
        flash('Не выбрано ни одной роли для генерации комментариев.', 'warning')
        return redirect(url_for('view_post', post_id=post.id))

    generated_count = 0
    for i, role in enumerate(roles_to_process):
        if i > 0:
            time.sleep(5)

        user_prompt = role.prompt_template.format(post_content=post.content)

        # Определяем, какой сервис использовать для генерации комментария
        if Config.GEMINI_API_KEY:
            from llm_service import generate_comment  # Импортируем здесь, чтобы избежать ошибки циклического импорта
        elif Config.OPENAI_API_KEY:
            from llm_openai_service import generate_comment
        else:
            flash('Не найден API ключ ни для Gemini, ни для OpenAI.', 'danger')
            return redirect(url_for('view_post', post_id=post.id))
        comment_text = generate_comment(role.system_prompt, user_prompt)

        if "Ошибка при генерации комментария" in comment_text:
            flash(f"Ошибка генерации комментария для роли {role.name}: {comment_text}", 'warning')
        else:
            generated_count += 1
            db.session.add(Comment(post_id=post.id, role_id=role.id, comment_text=comment_text))
            
    if generated_count > 0:
        db.session.commit()
        flash(f'Успешно сгенерировано {generated_count} комментариев!', 'success')
    return redirect(url_for('view_post', post_id=post.id))

@app.route('/roles')
def roles_index():
    """Отображает список всех ролей."""
    roles = Role.query.order_by(Role.name).all()
    return render_template('roles_index.html', roles=roles)

@app.route('/role/new', methods=['GET', 'POST'])
def new_role():
    """Обрабатывает создание новой роли."""
    if request.method == 'POST':
        form_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'system_prompt': request.form.get('system_prompt'),
            'prompt_template': request.form.get('prompt_template')
        }

        if not form_data['name'] or not form_data['prompt_template']:
            flash('Название роли и шаблон промпта обязательны для заполнения.', 'danger')
            return render_template('role_form.html', role=form_data, title="Создать роль")

        if Role.query.filter_by(name=form_data['name']).first():
            flash('Роль с таким названием уже существует.', 'danger')
            return render_template('role_form.html', role=form_data, title="Создать роль")

        new_role = Role(**form_data)
        db.session.add(new_role)
        db.session.commit()
        flash('Роль успешно создана!', 'success')
        return redirect(url_for('roles_index'))

    return render_template('role_form.html', role=None, title="Создать роль")

@app.route('/role/<int:role_id>/edit', methods=['GET', 'POST'])
def edit_role(role_id):
    """Обрабатывает редактирование существующей роли."""
    role = Role.query.get_or_404(role_id)
    if request.method == 'POST':
        new_name = request.form.get('name')
        if not new_name or not request.form.get('prompt_template'):
            flash('Название роли и шаблон промпта обязательны для заполнения.', 'danger')
            return render_template('role_form.html', role=role, title=f"Редактировать роль: {role.name}")

        existing_role = Role.query.filter(Role.name == new_name, Role.id != role_id).first()
        if existing_role:
            flash('Роль с таким названием уже существует.', 'danger')            
            return render_template('role_form.html', role=role, title=f"Редактировать роль: {role.name}")

        role.name = new_name
        role.description = request.form.get('description')
        role.system_prompt = request.form.get('system_prompt')
        role.prompt_template = request.form.get('prompt_template')
        db.session.commit()
        flash('Роль успешно обновлена!', 'success')
        return redirect(url_for('roles_index'))

    return render_template('role_form.html', role=role, title=f"Редактировать роль: {role.name}")

@app.route('/role/<int:role_id>/delete', methods=['POST'])
def delete_role(role_id):
    """Обрабатывает удаление роли."""
    role = Role.query.get_or_404(role_id)
    if role.comments:
        flash('Нельзя удалить роль, так как она уже используется в комментариях. Сначала удалите связанные комментарии.', 'danger')
    else:
        db.session.delete(role)
        db.session.commit()
        flash('Роль успешно удалена!', 'success')
    return redirect(url_for('roles_index'))

@app.route('/role/<int:role_id>/toggle_active', methods=['POST'])
def toggle_role_active(role_id):
    """Переключает статус активности роли."""
    role = Role.query.get_or_404(role_id)
    role.is_active = not role.is_active
    db.session.commit()
    status = "активирована" if role.is_active else "деактивирована"
    flash(f'Роль "{role.name}" была успешно {status}.', 'success')
    return redirect(url_for('roles_index'))



@app.route('/roles/export')
def export_roles():
    """Экспортирует все роли в JSON файл."""
    roles = Role.query.all()
    roles_data = [{'name': role.name, 
                   'description': role.description,
                   'system_prompt': role.system_prompt,
                   'prompt_template': role.prompt_template,
                   'is_active': role.is_active}  # Добавляем is_active
                  for role in roles]
    
    # Формируем имя файла с временной меткой
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"roles_export_{timestamp}.json"
    
    # Указываем путь для сохранения файла во временной папке экземпляра Flask
    filepath = os.path.join(app.instance_path, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(roles_data, f, ensure_ascii=False, indent=4)  # Включаем indent для читаемости

    # Возвращаем файл пользователю для скачивания
    return send_file(filepath, 
                     as_attachment=True, 
                     download_name=filename,  # Имя файла для скачивания
                     mimetype='application/json')

from flask import request

@app.route('/roles/import', methods=['POST'])
def import_roles():
    """Импортирует роли из JSON файла."""
    if 'file' not in request.files:
        flash('Не выбрано ни одного файла.', 'danger')
        return redirect(url_for('roles_index'))

    file = request.files['file']
    if file.filename == '':
        flash('Не выбран файл для импорта.', 'danger')
        return redirect(url_for('roles_index'))

    if file and file.filename.endswith('.json'):
        try:
            roles_data = json.load(file)
            imported_count = 0
            updated_count = 0
            for role_data in roles_data:
                # Проверяем наличие обязательных полей
                if not all(key in role_data for key in ['name', 'prompt_template']):
                    flash(f"Ошибка: В данных отсутствует обязательное поле (name, prompt_template). Пропущена запись: {role_data.get('name', 'N/A')}", 'danger')
                    continue

                role = Role.query.filter_by(name=role_data['name']).first()
                if role:
                    # Роль с таким именем уже существует, обновляем данные
                    role.description = role_data.get('description', '')
                    role.system_prompt = role_data.get('system_prompt', "Ты - полезный AI-ассистент, комментирующий текст.")
                    role.prompt_template = role_data['prompt_template']
                    role.is_active = role_data.get('is_active', True)
                    updated_count += 1
                else:
                    # Создаем новую роль
                    new_role = Role(**role_data)
                    db.session.add(new_role)
                    imported_count += 1

            db.session.commit()
            if imported_count > 0:
                flash(f'Успешно импортировано {imported_count} ролей.', 'success')
            if updated_count > 0:
                flash(f'Успешно обновлено {updated_count} ролей.', 'info')
        except json.JSONDecodeError:
            flash('Ошибка: Некорректный JSON файл.', 'danger')
        except Exception as e:
            flash(f'Произошла ошибка при импорте ролей: {e}', 'danger')
    else:
        flash('Ошибка: Допустим только импорт JSON файлов.', 'danger')
    return redirect(url_for('roles_index'))