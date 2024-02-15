from flask import Flask,render_template,redirect,request,flash,url_for,session
from datetime import datetime
import os,random,string
from functools import wraps
from sqlalchemy import text,and_
from werkzeug.security import generate_password_hash,check_password_hash
from pkg import app,csrf
from pkg.forms import LoginForm,QuestionForm
from pkg.models import db,User,Admin,QuizResult,Payment,Questions,Answer,CorrectAnswer
from werkzeug.utils import secure_filename
import csv




UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'sql', 'dump'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/admin/login/', methods=['POST', 'GET'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin.html')
    else:
        email = request.form.get('email')
        entered_password = request.form.get('pwd')

        admin = db.session.query(Admin).filter(Admin.email == email).first()

        if admin is not None and admin.password == entered_password:
            session['adminonline'] = admin.id
            flash('Welcome!', category='success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Credentials', category='error')
            return redirect(url_for('admin_login'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def process_csv(file_path, admin_id):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Create a new question
            new_question = Questions(
                question_text=row['question_text'],
                difficulty_level_id=row['difficulty_level_id'],
                category_id=row['category_id'],
                admin_id=admin_id
            )
            db.session.add(new_question)
            db.session.commit()

            # Create corresponding answers
            new_answer = Answer(
                option1=row['option1'],
                option2=row['option2'],
                option3=row['option3'],
                question=new_question,
            )
            db.session.add(new_answer)
            db.session.commit()

            # Create corresponding correct answer
            new_correct_answer = CorrectAnswer(
                correct_answer_text=row['correct_answer_text'],
                question=new_question,
            )
            db.session.add(new_correct_answer)
            db.session.commit()

@app.route('/admindashboard', methods=['GET', 'POST'])
def admin_dashboard():
    admin_id = session.get('admin_id')
    deets = Admin.query.get(admin_id)
    total_users = User.query.count()
    total_games_played = QuizResult.query.count()
    total_deposits = db.session.query(db.func.sum(Payment.payment_amt)).filter_by(payment_type='deposit').scalar() or 0
    total_withdrawals = db.session.query(db.func.count()).filter(Payment.payment_type == 'withdrawal').scalar() or 0
    context = {
        'total_users': total_users,
        'total_games_played': total_games_played,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'arrow_icon': 'zmdi zmdi-long-arrow-up',  # Replace with your actual arrow_icon
    }
    
    question_form = QuestionForm()

    if question_form.validate_on_submit():
        if question_form.file.data:
            # Handle file upload
            file = question_form.file.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)

                # Process the uploaded file based on its extension
                if filename.endswith('.csv'):
                    process_csv(file_path, admin_id)

                flash('File uploaded and processed successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
        elif question_form.question_id.data:
            question_id = int(question_form.question_id.data)
            edited_question = Questions.query.get_or_404(question_id)
            
            # Update the question fields
            edited_question.text = question_form.question_text.data
            edited_question.option_a = question_form.option_a.data
            edited_question.option_b = question_form.option_b.data
            edited_question.option_c = question_form.option_c.data
            edited_question.option_d = question_form.option_d.data
            edited_question.correct_option = question_form.correct_option.data

            db.session.commit()

            flash('Question updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:  # If Question ID does not exist, it's an upload
            new_question = Questions(
                text=question_form.question_text.data,
                option_a=question_form.option_a.data,
                option_b=question_form.option_b.data,
                option_c=question_form.option_c.data,
                option_d=question_form.option_d.data,
                correct_option=question_form.correct_option.data,
                admin_id=admin_id
            )

            db.session.add(new_question)
            db.session.commit()

            flash('Question uploaded successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard.html', deets=deets, context=context, question_form=question_form)



