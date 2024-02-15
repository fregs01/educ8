from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):  
    id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    first_name = db.Column(db.String(100),nullable=False)
    last_name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(120),nullable=False) 
    password=db.Column(db.String(250),nullable=True)
    gender=db.Column(db.Enum('male','female'),nullable=False)
    balance = db.Column(db.Float, default=0.0, nullable=False)
    phone=db.Column(db.String(120),nullable=True) 
    bank_account=db.Column(db.String(120),nullable=False) 
    bank_account_name=db.Column(db.String(120),nullable=False) 
    user_nok=db.Column(db.String(120),nullable=False) 
    user_address=db.Column(db.String(200),nullable=False) 
    user_pix=db.Column(db.String(120),nullable=True) 
    dob = db.Column(db.DateTime(), nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.bank_id'))
    date_registered=db.Column(db.DateTime(), default=datetime.utcnow)#default date
    quiz_results = db.relationship("QuizResult", backref="user")
    payments = db.relationship("Payment", backref="payment_deets")
    transactions = db.relationship("Transaction", backref="transaction_deets")
    

class Banks(db.Model):
    __tablename__ = 'bank'
    bank_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    bank_name = db.Column(db.Text, nullable=False)
    cbn_code = db.Column(db.Integer, nullable=False)
    users = db.relationship("User", backref="user_bank")



class Questions(db.Model):
    __tablename__ = 'question_bank'
    qb_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    question_text = db.Column(db.Text, nullable=True)
    difficulty_level_id = db.Column(db.Integer, db.ForeignKey('difficulty_level.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('quiz_categories.category_id'))
    answers = db.relationship("Answer", backref="question", lazy='joined')
    correct_answer = db.relationship("CorrectAnswer", back_populates="question", uselist=False)

class Answer(db.Model):
    __tablename__ = 'question_answer'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question_bank.qb_id'))
    correct_answer_id = db.Column(db.Integer, db.ForeignKey('correct_answer.correct_answer_id'))
    category_id = db.Column(db.Integer, db.ForeignKey('quiz_categories.category_id'))

class CorrectAnswer(db.Model):
    __tablename__ = 'correct_answer'
    correct_answer_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    correct_answer_text = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question_bank.qb_id'))
    question = db.relationship("Questions", back_populates="correct_answer", uselist=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('quiz_categories.category_id'))


class Difficulty(db.Model):
    __tablename__='difficulty_level'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    level_name = db.Column(db.String(100), nullable=False)
    questions = db.relationship("Questions", backref="difficulty")
    quiz_results = db.relationship("QuizResult", backref="difficulty") 

class Categories(db.Model):
    __tablename__='quiz_categories'
    category_id  = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    questions = db.relationship("Questions", backref="category")
    quiz_results = db.relationship("QuizResult", backref="category")
    answer = db.relationship("Answer", backref="answer") 
    correct_ans = db.relationship("CorrectAnswer", backref="ca")

class QuizResult(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    time_finished = db.Column(db.Time, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('quiz_categories.category_id'), nullable=True)
    difficulty_level_id = db.Column(db.Integer, db.ForeignKey('difficulty_level.id'), nullable=True)
    status = db.Column(db.Enum('in progress','finished'), nullable=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=True)
    round_number = db.Column(db.Integer, nullable=True)
   

class Plan(db.Model):
    __tablename__ = 'plans'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quiz_results = db.relationship("QuizResult", backref="plan")
    transact_deeds = db.relationship("Transaction", back_populates="planner")


class Transaction(db.Model): 
    __tablename__ = 'transaction'  
    transaction_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'))
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.payment_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_date = db.Column(db.DateTime(), default=datetime.utcnow) 
    pay_deets = db.relationship("Payment",back_populates='transact')
    planner = db.relationship("Plan", back_populates="transact_deeds")
    
    


class Payment(db.Model):  
    payment_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    payment_amt= db.Column(db.Float,nullable=False)
    payment_userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    payment_date = db.Column(db.DateTime(), default=datetime.utcnow) 
    payment_status=db.Column(db.Enum('pending','paid','failed'),nullable=False)
    payment_type=db.Column(db.Enum('deposit','withdrawal'),nullable=False)
    payment_ref=db.Column(db.String(500),nullable=True)
    payment_email=db.Column(db.String(250),nullable=True) 
    payment_paygate=db.Column(db.String(500),nullable=True) 
    transact = db.relationship("Transaction",back_populates='pay_deets')


class Admin(db.Model):
    id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    first_name = db.Column(db.String(100),nullable=False)
    last_name = db.Column(db.String(100),nullable=False)
    username= db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(120),nullable=False) 
    password=db.Column(db.String(250),nullable=True)
    gender=db.Column(db.Enum('male','female'),nullable=False)
    phone=db.Column(db.String(120),nullable=True) 

