from flask import Flask,render_template,redirect,request,flash,url_for,session,jsonify,json
from datetime import datetime,timedelta
import time
from time import sleep
import requests
import traceback
import pytz
import threading
import os,random,string
import spacy
from functools import wraps
from sqlalchemy import text,and_,func
from flask_wtf.csrf import CSRFError,validate_csrf
from werkzeug.security import generate_password_hash,check_password_hash
from pkg import app,csrf
from pkg.forms import RegistrationForm
from pkg.models import db,User,Questions,Difficulty,CorrectAnswer,Categories,Answer,Plan,QuizResult,Transaction,Payment,Banks
from random import  shuffle, sample
from urllib.parse import unquote
from sqlalchemy import desc
from operator import attrgetter
from jinja2 import Environment




def login_required(f):
    @wraps(f)
    def check_login(*args,**kwargs):
        if session.get('useronline') !=None:
          return  f(*args,**kwargs)

        else:
            flash('You must be logged in to access this page', category='error')
            return redirect('/login')
    return check_login

def filter_max_round(values):
    non_none_values = [v for v in values if v is not None]
    return max(non_none_values, default=None)

# Add the custom filter to Jinja environment
app.jinja_env.filters['max_round'] = filter_max_round

# @app.route('/user_profile', methods=['GET'])
# @login_required
# def user_profile():
#     id = session.get('useronline')
#     user = User.query.filter_by(id).first()

#     if user:
#         return render_template('user_profile.html', user=user)
#     else:
#         flash('User not found', 'error')
#         return redirect(url_for('dashboard'))  # Redirect to the dashboard or another route if the user is not found

@app.route('/', methods=['GET', 'POST'])
def home():
    form = RegistrationForm()
    
    
    return render_template('mainindex.html',form=form)

@app.route('/aboutus')
def aboutus():
    
    
    return render_template('aboutus.html')
    

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='GET':
        return render_template('loginpage.html')
    else:
        email=request.form.get('email')
        password=request.form.get('password')
        record = db.session.query(User).filter(User.email ==email).first()
        if record:
         hashed_pwd = record.password
         rsp = check_password_hash(hashed_pwd,password)
         if rsp:
            id = record.id
            session['useronline']=id
            return redirect(url_for('custhome'))
         else:
            flash('Incorrect Credentials',category='error')
            return redirect('/login')
        else:
            flash('Incorrect Invalid Credentials',category='error')
            return redirect('/login')
        
@app.route('/logout')
def logout():
    if session.get('useronline') !=None:
        session.pop('useronline',None)
   
    return redirect('/')
@app.route('/info', methods=['GET'])
def info():
   
    return render_template('info.html')
@app.route('/user_ranks', methods=['GET'])
def user_ranks():
    # Query the QuizResult table and join with the User table to get user information
    results = db.session.query(QuizResult, User)\
        .join(User, QuizResult.user_id == User.id)\
        .order_by(QuizResult.score.desc(), QuizResult.time_finished.asc())\
        .all()

    return render_template('user_ranks.html', results=results)

@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    id = session.get('useronline')

    if request.method == 'GET':
            deets = User.query.get(id)
            return render_template('profile.html', deets=deets)
    else:
            user = User.query.get(id)
            if user:
                user.first_name = request.form.get('fname')
                user.last_name = request.form.get('lname')
                user.phone = request.form.get('phone')
                user.bank_account= request.form.get('bank_account')
                user.bank_account_name= request.form.get('bank_account_name')

                # Commit the changes
                db.session.commit()

                flash('Updated successfully',category='success')
                return redirect(url_for('custhome'))
            else:
                  flash('Update unsuccessful',category='error')
@app.route('/confirm')
@login_required
def confirm():
    id=session.get('useronline')
    deets = User.query.get(id)
    ref = session.get('ref')
    if ref:
        payment_deets =Payment.query.filter(Payment.payment_ref==ref).first()
        return render_template('confirm.html',deets=deets, payment_deets=payment_deets)
    else:
        flash('please start the transaction again')
        return render_template('confirm.html')
    


@app.route("/paylanding")
@login_required
def paylanding():
    id = session.get('useronline')
    trxref = request.args.get('trxref')

    if (session.get('ref') is not None) and (str(trxref) == str(session.get('ref'))):
        url = 'https://api.paystack.co/transaction/verify/' + (str(session.get('ref')))
        headers = {"content_type": "application/json", "authorization": "Bearer sk_test_e7a7d9967a35c1887e79446f21f25b3362f7e793"}

        response = requests.get(url, headers=headers)
        rsp = response.json()

        if rsp and rsp.get('status') == True:
            # Payment is successful, update user balance in the database
            payment_deets = Payment.query.filter(Payment.payment_ref == session.get('ref')).first()
            user = User.query.get(id)

            if payment_deets and user:
                # Update user's balance
                user.balance += payment_deets.payment_amt
                db.session.commit()

                # Flash a message for demonstration purposes (optional)
                flash('Payment successful! Balance updated.')

                # Redirect to custhome page with updated balance
                return redirect(url_for('custhome', balance=user.balance))
            else:
                flash('Error updating user balance. Please contact support.')
                return redirect('/custhome')
        else:
            time.sleep(1)
            flash('Payment verification failed. Please try again.')
            return redirect('/custhome')
    else:
        flash('Start again')
        return redirect('/custhome')
    
@app.route('/paystack', methods=['POST'])
@login_required
def paystack():
    user_id = session.get('useronline')
    ref = session.get('ref')

    if ref:
        # Retrieve payment details from the database
        transaction_deets = Payment.query.filter(Payment.payment_ref == ref).first()

        if not transaction_deets:
            flash('Transaction details not found. Start the payment process again.', category='error')
            return redirect('/custhome')

        # Construct the data payload for initializing the transaction
        data = {
            "email": transaction_deets.payment_email,
            "amount": transaction_deets.payment_amt * 100,
            "reference": ref,
            "callback_url": "http://127.0.0.1:5000/paylanding",
        }

        # Determine whether it's a deposit or withdrawal
        if transaction_deets.payment_type == 'deposit':
            # For deposit, call the Paystack API to initialize the transaction
            url = "https://api.paystack.co/transaction/initialize"
        elif transaction_deets.payment_type == 'withdrawal':
            # For withdrawal, call the Paystack API to initialize the transfer
            url = "https://api.paystack.co/transfer/finalize_transfer"
            data["recipient_code"] = transaction_deets.recipient_code  # Include recipient code for withdrawal
        else:
            flash('Invalid transaction type', category='error')
            return redirect('/custhome')

        try:
            # Send the request to Paystack API
            response = send_request(url, data)
            rspjson = response.json()

            if rspjson and rspjson.get('status') == True:
                auth_url = rspjson['data']['authorization_url']
                return redirect(auth_url)
            else:
                flash('Start the payment process again', category='error')
                return redirect('/custhome')

        except Exception as e:
            traceback.print_exc()
            print(f"Error calling Paystack API: {str(e)}")
            flash(f'Start the payment process again. Error: {str(e)}', category='error')
            return redirect('/custhome')
    else:
        flash('Start the payment process again', category='error')
        return 'done'

def send_request(url, data):
    headers = {"content_type": "application/json", "authorization": "Bearer sk_test_e7a7d9967a35c1887e79446f21f25b3362f7e793"}
    return requests.post(url, headers=headers, data=json.dumps(data))

# Separate route for withdrawal
@app.route('/withdrawal', methods=['GET', 'POST'])
@login_required
def withdrawal():
    id = session.get('useronline')
    user = User.query.get(id)
    type = 'withdrawal'

    if request.method == 'POST':
        withdrawal_amount = float(request.form.get('withdrawal_amount', 0.0))
        ref = int(random.random() * 10000000000)
        email = request.form.get('email')

        if withdrawal_amount > 0 and user.balance >= withdrawal_amount:
            try:
                # Process the withdrawal
                user.balance -= withdrawal_amount

                # Record the transaction in the Payment table
                transaction = Payment(payment_amt=withdrawal_amount, payment_email=email, payment_ref=ref,
                                      payment_status='pending', payment_userid=id, payment_type=type)
                db.session.add(transaction)
                db.session.commit()

                # Call Paystack API to initialize the transfer
                url = "https://api.paystack.co/transfer/finalize_transfer"
                headers = {
                    "content_type": "application/json",
                    "authorization": "Bearer sk_test_e7a7d9967a35c1887e79446f21f25b3362f7e793"
                }
                data = {
                    "source": "balance",
                    "reason": "Withdrawal",
                    "amount": withdrawal_amount * 100,  # Paystack expects amount in kobo
                }

                response = requests.post(url, headers=headers, json=data)
                rspjson = response.json()

                print("Paystack API Response:", rspjson)  # Add this line for debugging

                if response.status_code == 200 and rspjson.get('status') == True:
                    # If the withdrawal is successful, update the payment status to completed
                    transaction.payment_status = 'completed'
                    db.session.commit()
                    flash('Withdrawal successful!', category='success')
                    return redirect(url_for('withdrawal'))
                else:
                    # If the withdrawal fails, update the payment status to failed
                    transaction.payment_status = 'failed'
                    db.session.commit()
                    flash(f'Withdrawal failed. Paystack API error: {rspjson}', category='error')

            except Exception as e:
                traceback.print_exc()
                print(f"Error calling Paystack API: {str(e)}")
                flash(f'Withdrawal failed. Unexpected error: {str(e)}. Please try again.', category='error')

        else:
            flash('Insufficient balance or invalid withdrawal amount.', category='error')

    return render_template('withdrawal.html', user=user)

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    id = session.get('useronline')
    if request.method == 'GET':
        deets = User.query.get(id)
        return render_template('deposit.html', deets=deets)
    else:
        email = request.form.get('email')
        amt = request.form.get('amt')
        ref = int(random.random() * 10000000000)
        type = 'deposit'
        session['ref'] = ref

        if email != '' and amt != '':
            # Create a Payment record
            payment = Payment(payment_amt=amt, payment_email=email, payment_ref=ref,
                              payment_status='pending', payment_userid=id, payment_type=type)
            db.session.add(payment)
            db.session.commit()
            transaction = Transaction(user_id=id, payment_id=payment.payment_id)
            db.session.add(transaction)
            db.session.commit()
            if payment.payment_id:
                return redirect('/confirm')
            else:
                flash('Please complete the form')
                return redirect('/custhome')
        else:
            flash('Please complete the form')
            return redirect('/custhome')

@app.route('/transaction_history')
@login_required
def transaction_history():
    id = session.get('useronline')
    user = User.query.get(id)
    user_transactions = Transaction.query.filter_by(user_id=id).all()


    return render_template('transaction.html', user=user,transactions=user_transactions)

@app.route('/changedp', methods=['POST', 'GET'])
@login_required
def change_dp():
    id = session.get('useronline')
    deets = User.query.get(id)
    oldpix = deets.user_pix
    if request.method == 'GET':

        return render_template('changedp.html',deets=deets)
    else:
          dp= request.files.get('dp')
          filename = dp.filename
          if filename =='':
            flash('please select a file',category='error')
            return redirect('/changedp')
          else:
            name,ext = os.path.splitext(filename)
            allowed=['.jpg','.png','.jpeg']
            if ext.lower() in allowed:
                # final_name=random.sample(string.ascii_lowercase,10)
                final_name = int(random.random()*1000000)
                final_name = str(final_name) + ext
                dp.save(f'pkg/static/profile/{final_name}')
                user = db.session.query(User).get(id)
                user.user_pix =final_name
                db.session.commit()
                try:
                    os.remove(f'pkg/static/profile/{oldpix}')
                except:
                    pass
                flash('profile picture added',category='success')
                return redirect('/dashboard')
    
            else:
                flash('extension not allowed',category='error')
                return redirect('/changedp')

@app.route('/custhome')
@login_required
def custhome():
    user_id = session.get('useronline')

    # Query the database to get the user's balance
    user = User.query.get(user_id)
    
    # Check if the user object and balance attribute exist before accessing them
    balance = user.balance if user and hasattr(user, 'balance') else 0.0

    current_round = session.get('current_round', 1)

    quiz_results = QuizResult.query.filter_by(
        user_id=user_id, 
        round_number=current_round
    ).all()

    highest_rounds = db.session.query(QuizResult.plan_id, func.max(QuizResult.round_number).label('highest_round')) \
                                .group_by(QuizResult.plan_id) \
                                .all()

    # Fetch top 100 results for the highest round and each plan based on score (descending) and time_finished (ascending)
    rankings_all_plans = []

    for plan_id, highest_round in highest_rounds:
        rankings_plan = QuizResult.query.filter_by(round_number=highest_round, plan_id=plan_id) \
                                        .order_by(desc('score'), 'time_finished') \
                                        .limit(100) \
                                        .all()

        rankings_all_plans.extend(rankings_plan)

    # Custom function to handle sorting by score (descending) and time_finished (ascending) with tiebreaker
    def sort_key(result):
        return (result.score, result.time_finished if result.time_finished else datetime.max)

    # Sort rankings based on score (descending) and time_finished (ascending)
    rankings_all_plans = sorted(rankings_all_plans, key=sort_key, reverse=True)

    # Handle tiebreaker condition
    sorted_rankings_all_plans = []
    prev_score = None
    same_score_results_all_plans = []

    for result in rankings_all_plans:
        if result.score == prev_score:
            same_score_results_all_plans.append(result)
        else:
            # Sort same-score results by time_finished (ascending)
            same_score_results_all_plans.sort(key=lambda x: x.time_finished if x.time_finished else datetime.max)
            sorted_rankings_all_plans.extend(same_score_results_all_plans)
            same_score_results_all_plans = [result]
            prev_score = result.score

    # Append any remaining same-score results
    same_score_results_all_plans.sort(key=lambda x: x.time_finished if x.time_finished else datetime.max)
    sorted_rankings_all_plans.extend(same_score_results_all_plans)

    # Create a list of dictionaries with position, user_id, score, and time_finished for all plans
    positions_all_plans = [{'position': i + 1, 'user_id': result.user_id, 'plan_id': result.plan_id,'email':result.user.email,'round_number': result.round_number, 'score': result.score, 'time_finished': result.time_finished} for i, result in enumerate(sorted_rankings_all_plans)]

    # Add more logic for fetching additional data or performing calculations

    return render_template('custhome.html', user=user, balance=balance, quiz_results=quiz_results, round_number=current_round, positions_all_plans=positions_all_plans)
def calculate_current_position(user_id, round_number, plan_id):
    # Fetch all results for the current round and plan
    results = QuizResult.query.filter_by(
        round_number=round_number,
        plan_id=plan_id
    ).order_by(QuizResult.score.desc()).all()

    # Calculate the current position based on ranking
    for index, result in enumerate(results):
        if result.user_id == user_id:
            return index + 1

    return None
@app.route('/contactus', methods=['GET', 'POST'])
def contactus():

    return render_template('contact.html')


@app.route('/dashboard')
@login_required
def dashboard():
    id = session.get('useronline')

    deets = User.query.get(id)
    return render_template('cust_dash.html',deets=deets)
@app.route('/dash')
@login_required
def dash():
    user_id = session.get('useronline')

    # Fetch the latest quiz result for the user
    latest_result = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.id.desc()).first()

    # Calculate the percentage change for scores
    current_score = latest_result.score if latest_result else 0
    previous_score = session.get('previous_score', current_score)
    percentage_change_scores = ((current_score - previous_score) / abs(previous_score)) * 100 if previous_score != 0 else 0
    session['previous_score'] = current_score

    # Calculate the number of plans
    quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
    user_plans = [result.plan for result in quiz_results]
    current_plans = len(user_plans)

    # Calculate the percentage change for plans
    previous_plans = session.get('previous_plans', current_plans)
    percentage_change_plans = ((current_plans - previous_plans) / abs(previous_plans)) * 100 if previous_plans != 0 else 0
    session['previous_plans'] = current_plans

    # Fetch user transactions with related plan and user details
    user_transactions = Transaction.query.filter_by(user_id=user_id).all()

    # Calculate the number of transactions
    current_transactions = len(user_transactions)

    # Calculate the percentage change for transactions
    previous_transactions = session.get('previous_transactions', current_transactions)
    percentage_change_transactions = ((current_transactions - previous_transactions) / abs(previous_transactions)) * 100 if previous_transactions != 0 else 0
    session['previous_transactions'] = current_transactions

    return render_template('dash.html', 
                           deets = latest_result.user if latest_result else None,
                           percentage_change=percentage_change_scores,
                           current_plans=current_plans,
                           percentage_change_plans=percentage_change_plans,
                           current_transactions=current_transactions,
                           percentage_change_transactions=percentage_change_transactions,
                           transactions=user_transactions,user_id=user_id)


@app.route('/prizes')
def prizes():
    return render_template('prizes.html')
@app.route('/rules')
def rules():
    return render_template('rules.html')
@app.route('/eligibility')
def eligibility():
    return render_template('eligibility.html')

@app.route('/categories')
def categories():
    return render_template('categories.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegistrationForm()
    form.set_bank_choices()
    if request.method=='GET':
        return render_template('reg.html',form=form)
    else:
        bank_id = form.bank_account_name.data
        firstname = request.form.get('first_name')
        lastname = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        dob = request.form.get('Date of Birth')
        hashed_pwd=generate_password_hash(password)  
        next_of_kin = request.form.get('next_of_kin')
        address = request.form.get('address')
        bank_account = request.form.get('bank_account')
        bank = Banks.query.get(bank_id)
        bank_name = bank.bank_name if bank else None
        dob = request.form.get('date_of_birth')
    

        # Check if the username or email already exists
        existing_user = User.query.filter((User.email == email)).first()

        if existing_user:
            flash('Username or email already exists', category='error')
            return redirect(url_for('your_register_route'))  

        new_user = User(
            first_name=firstname,
            last_name=lastname,
            email=email,
            gender=gender,
            phone=phone,
            password=hashed_pwd, 
            user_nok=next_of_kin,
            user_address=address,
            bank_account=bank_account,
            bank_account_name=bank_name,
            bank_id = bank_id,
            dob=dob
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', category='success')
        return redirect(url_for('home')) 



@app.route('/get_questions', methods=['GET'])
def get_questions():
    # Ensure that selected_category is in the session
    selected_category = session.get('selected_category')
    
    # Debug print statement
    print(f"DEBUG: Category ID in get_questions: {selected_category}")

    # Check if selected_category is not None and retrieve questions based on category
    if selected_category:
        questions = Questions.query.filter_by(category_id=selected_category).options(db.joinedload(Questions.correct_answer)).order_by(func.rand()).limit(15).all()

        if questions:
            questions_data = [
                {
                    'question_text': question.question_text,
                    'correct_answer': question.correct_answer.correct_answer_text if question.correct_answer else None,
                    'option1': question.answers[0].option1,
                    'option2': question.answers[0].option2,
                    'option3': question.answers[0].option3,
                    'option4': question.correct_answer.correct_answer_text
                }
                for question in questions
            ]
            return jsonify({'data': questions_data})
        else:
            return jsonify({'error': 'No questions available'})

    else:
        return jsonify({'error': 'Category ID is missing'})

@app.route('/choose_category', methods=['GET', 'POST'])
@login_required
def choose_category():
    def get_dashboard_data(user_id):
        latest_result = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.id.desc()).first()

        if latest_result:
            current_score = latest_result.score
        else:
            current_score = 0

        previous_score = session.get('previous_score', current_score)
        percentage_change_scores = ((current_score - previous_score) / abs(previous_score)) * 100 if previous_score != 0 else 0
        session['previous_score'] = current_score

        quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
        user_plans = [result.plan for result in quiz_results]
        current_plans = len(user_plans)

        previous_plans = session.get('previous_plans', current_plans)
        percentage_change_plans = ((current_plans - previous_plans) / abs(previous_plans)) * 100 if previous_plans != 0 else 0
        session['previous_plans'] = current_plans

        user_transactions = Transaction.query.filter_by(user_id=user_id).all()

        current_transactions = len(user_transactions)

        previous_transactions = session.get('previous_transactions', current_transactions)
        percentage_change_transactions = ((current_transactions - previous_transactions) / abs(previous_transactions)) * 100 if previous_transactions != 0 else 0
        session['previous_transactions'] = current_transactions

        return {
            'deets': latest_result.user if latest_result else None,
            'percentage_change': percentage_change_scores,
            'current_plans': current_plans,
            'percentage_change_plans': percentage_change_plans,
            'current_transactions': current_transactions,
            'percentage_change_transactions': percentage_change_transactions,
            'transactions': user_transactions
        }

    user_id = session.get('useronline')
    dashboard_data = get_dashboard_data(user_id)

    categories = Categories.query.all()

    if request.method == 'GET':
        return render_template('choose_category.html', categories=categories, **dashboard_data)

    if request.method == 'POST':
        selected_category_id = request.form.get('category')
        if not selected_category_id:
            flash('You need to choose a category.', 'error')
            return redirect(url_for('choose_category'))
        session['selected_category'] = selected_category_id
        return redirect(url_for('choose_plan', category_id=selected_category_id))

    return render_template('choose_category.html', categories=categories, **dashboard_data)



@app.route('/start_quiz', methods=['GET'])
@login_required
def start_quiz():
    # Get the timer data from the request
    timer_data = request.args.to_dict()

    # Store the start time in the session when the quiz begins
    session['quiz_start_time'] = datetime.now()

    # Access timer data like timer_data['duration'] if needed
    duration_seconds = int(timer_data.get('duration', 300))  # Default to 5 minutes if not provided

    # Calculate the end time based on the duration
    end_time = session['quiz_start_time'] + timedelta(seconds=duration_seconds)

    # Store the end time in the session for later reference
    session['quiz_end_time'] = end_time

    # Initialize quiz state
    session['quiz_state'] = 'started'

    # Retrieve and prepare questions (you need to implement this logic)
    questions = get_questions()

    # Send relevant data back to the client
    response_data = {
        'quiz_state': session['quiz_state'],
        'quiz_start_time': session['quiz_start_time'].strftime('%Y-%m-%d %H:%M:%S'),
        'quiz_end_time': session['quiz_end_time'].strftime('%Y-%m-%d %H:%M:%S'),
        'questions': questions,
    }

    return jsonify(response_data)


    


# @app.route('/choose_plan/<category_id>', methods=['GET', 'POST'])
# @login_required
# def choose_plan(category_id):
#     deets = User.query.get(id)
#     plans = Plan.query.all()
#     category = Categories.query.get(category_id)

#     if request.method == 'GET':
#         return render_template('choose_plan.html', category=category, plans=plans)

#     if request.method == 'POST':
#         selected_plan_id = request.form.get('plan')

#         if not selected_plan_id:
#             flash('You need to choose a plan.', 'error')
#             return redirect(url_for('choose_plan', category_id=category_id))
#         session['selected_category'] = category_id
#         session['selected_plan'] = selected_plan_id

#         # Get the current user
#         user_id = session.get('useronline')
#         user = User.query.get(user_id)

#         # Get the selected plan
#         selected_plan = Plan.query.get(selected_plan_id)

#         # Check if the user has sufficient balance
#         if user.balance < selected_plan.price:
#             return render_template('insufficient_balance.html', category=category, plans=plans,deets=deets)

#         # Deduct the amount from the user's balance
#         user.balance -= selected_plan.price
#         db.session.commit()

#         # Create a Transaction record
#         transaction = Transaction(user_id=user_id, plan_id=selected_plan_id)
#         db.session.add(transaction)
#         db.session.commit()

#         return redirect(url_for('quiz_intermediate'))

#     return render_template('choose_plan.html', category=category, plans=plans)



# @app.route('/start_quiz', methods=['GET'])
# @login_required
# def start_quiz():
#     # Get the timer data from the request
#     timer_data = request.args.to_dict()

#     # Store the start time in the session when the quiz begins
#     session['quiz_start_time'] = datetime.now()

#     # Access timer data like timer_data['duration'] if needed
#     duration_seconds = int(timer_data.get('duration', 300))  # Default to 5 minutes if not provided

#     # Calculate the end time based on the duration
#     end_time = session['quiz_start_time'] + timedelta(seconds=duration_seconds)

#     # Store the end time in the session for later reference
#     session['quiz_end_time'] = end_time

#     # Initialize quiz state
#     session['quiz_state'] = 'started'

#     # Retrieve and prepare questions (you need to implement this logic)
#     questions = get_questions()

#     # Send relevant data back to the client
#     response_data = {
#         'quiz_state': session['quiz_state'],
#         'quiz_start_time': session['quiz_start_time'].strftime('%Y-%m-%d %H:%M:%S'),
#         'quiz_end_time': session['quiz_end_time'].strftime('%Y-%m-%d %H:%M:%S'),
#         'questions': questions,
#     }

#     return jsonify(response_data)


    


@app.route('/choose_plan/<category_id>', methods=['GET', 'POST'])
@login_required
def choose_plan(category_id):
    user_id = session.get('useronline')
    deets = User.query.get(user_id)
    
    # Fetch plans and categories (you may need to adjust this based on your models)
    plans = Plan.query.all()
    category = Categories.query.get(category_id)
    print(f"DEBUG: Category ID in choose_plan: {category_id}")

    # Fetch the latest quiz result for the user
    latest_result = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.id.desc()).first()

    # Calculate the percentage change for scores
    current_score = latest_result.score if latest_result else 0
    previous_score = session.get('previous_score', current_score)
    percentage_change_scores = ((current_score - previous_score) / abs(previous_score)) * 100 if previous_score != 0 else 0
    session['previous_score'] = current_score

    # Calculate the number of plans
    quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
    user_plans = [result.plan for result in quiz_results]
    current_plans = len(user_plans)

    # Calculate the percentage change for plans
    previous_plans = session.get('previous_plans', current_plans)
    percentage_change_plans = ((current_plans - previous_plans) / abs(previous_plans)) * 100 if previous_plans != 0 else 0
    session['previous_plans'] = current_plans

    # Fetch user transactions with related plan and user details
    user_transactions = Transaction.query.filter_by(user_id=user_id).all()

    # Calculate the number of transactions
    current_transactions = len(user_transactions)

    # Calculate the percentage change for transactions
    previous_transactions = session.get('previous_transactions', current_transactions)
    percentage_change_transactions = ((current_transactions - previous_transactions) / abs(previous_transactions)) * 100 if previous_transactions != 0 else 0
    session['previous_transactions'] = current_transactions
    if request.method == 'POST':
        selected_plan_id = request.form.get('plan')

        if not selected_plan_id:
            flash('You need to choose a plan.', 'error')
            return redirect(url_for('choose_plan', category_id=category_id))

        session['selected_category'] = category_id
        session['selected_plan'] = selected_plan_id

        # Get the selected plan
        selected_plan = Plan.query.get(selected_plan_id)

        # Check if the user has sufficient balance
        if deets.balance < selected_plan.price:
            flash('Insufficient balance. Please choose a different plan or recharge your account.', 'error')
            return redirect(url_for('choose_plan', category_id=category_id))

        # Deduct the amount from the user's balance
        deets.balance -= selected_plan.price
        db.session.commit()

        # Create a Transaction record
        transaction = Transaction(user_id=user_id, plan_id=selected_plan_id)
        db.session.add(transaction)
        db.session.commit()

        # Flash success message
        flash(f'Successfully selected plan: {selected_plan.name}. Amount deducted: {selected_plan.price}', 'success')

        # Redirect to quiz_intermediate
        return redirect(url_for('quiz_intermediate', deets=deets))

    # ...

    # Flash error message in case of insufficient balance
    return render_template('choose_plan.html', category=category, plans=plans, deets=deets,
                        percentage_change=percentage_change_scores,
                        current_plans=current_plans,
                        percentage_change_plans=percentage_change_plans,
                        current_transactions=current_transactions,
                        percentage_change_transactions=percentage_change_transactions,
                        transactions=user_transactions)
def get_dashboard_data(user_id):
    latest_result = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.id.desc()).first()

    current_score = latest_result.score if latest_result else 0
    previous_score = session.get('previous_score', current_score)
    percentage_change_scores = ((current_score - previous_score) / abs(previous_score)) * 100 if previous_score != 0 else 0
    session['previous_score'] = current_score

    quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
    user_plans = [result.plan for result in quiz_results]
    current_plans = len(user_plans)

    previous_plans = session.get('previous_plans', current_plans)
    percentage_change_plans = ((current_plans - previous_plans) / abs(previous_plans)) * 100 if previous_plans != 0 else 0
    session['previous_plans'] = current_plans

    user_transactions = Transaction.query.filter_by(user_id=user_id).all()

    current_transactions = len(user_transactions)

    previous_transactions = session.get('previous_transactions', current_transactions)
    percentage_change_transactions = ((current_transactions - previous_transactions) / abs(previous_transactions)) * 100 if previous_transactions != 0 else 0
    session['previous_transactions'] = current_transactions

    return {
        'deets': latest_result.user if latest_result else None,
        'percentage_change': percentage_change_scores,
        'current_plans': current_plans,
        'percentage_change_plans': percentage_change_plans,
        'current_transactions': current_transactions,
        'percentage_change_transactions': percentage_change_transactions,
        'transactions': user_transactions
    }

@app.route('/quiz_intermediate', methods=['GET', 'POST'])
@login_required
def quiz_intermediate():
    user_id = session.get('useronline')
    deets = User.query.get(user_id)
    selected_category_id = session.get('selected_category')
    selected_plan_id = session.get('selected_plan')

    if selected_category_id is None or selected_plan_id is None:
        return redirect(url_for('choose_category'))

    selected_category = Categories.query.get(selected_category_id)
    selected_plan = Plan.query.get(selected_plan_id)

    # Check if the user has already completed the game for this plan
    if session.get(f'game_completed_{selected_plan_id}'):
        # Clear the session variable
        session.pop(f'game_completed_{selected_plan_id}', None)
        # Redirect to the plan page
        return redirect(url_for('choose_plan', category_id=selected_category_id,deets=deets))

    user_id = session.get('useronline')
    user = User.query.get(user_id)

    # Get the selected plan
    selected_plan = Plan.query.get(selected_plan_id)

    # Check if the user has sufficient balance
    if user.balance < selected_plan.price:
        flash("Insufficient balance for the selected plan.", 'error')
        return redirect(url_for('choose_plan', category_id=selected_category_id,deets=deets))

    # Deduct the amount from the user's balance
    user.balance -= selected_plan.price
    db.session.commit()

    # Increment the played_games counter in the session for this plan
    played_games_key = f'played_games_{selected_plan_id}'
    played_games = session.get(played_games_key, 0)
    played_games += 1
    session[played_games_key] = played_games  # Set the played_games counter in the session

    games_per_round = 100
    current_round = (played_games - 1) // games_per_round + 1
    games_played_in_current_round = played_games % games_per_round if played_games % games_per_round != 0 else games_per_round
    round_info = {
        'round_number': current_round,
        'plan_name': selected_plan.name,
        'games_played_in_current_round': games_played_in_current_round
    }

    # Print statements for troubleshooting
    print(f"Round {current_round} started for Plan {selected_plan.name}")
    print(f"Games played in Round {current_round}: {games_played_in_current_round}")
    print(f"User {user_id}'s balance after deduction: {user.balance}")

    # Check if the current game is the last game in the round
    if games_played_in_current_round == games_per_round:
        winners, user_position = get_winners(selected_plan, current_round, user_id)
        print(f"Winners for Round {current_round}: {winners}")

        credit_winners(QuizResult, winners)
        print(f"User {user_id}'s balance after crediting winners: {user.balance}")

        # Retrieve quiz results again after crediting winners
        results = QuizResult.query.filter(QuizResult.plan_id == selected_plan_id,
                                          QuizResult.status == 'finished',
                                          QuizResult.round_number == int(current_round)) \
                                .order_by(desc(QuizResult.score), QuizResult.time_finished) \
                                .all()

        # Check if the user is in the winners list and print the position and score
        if user_position is not None:
            print(f"You are currently in position {user_position} with a score of {results[user_position - 1].score}")
    dashboard_data = get_dashboard_data(user_id)
    return render_template('game.html', 
                       category=selected_category, 
                       plan=selected_plan, 
                       round_info=round_info, 
                       current_round=current_round,**dashboard_data)
def get_user_position(selected_plan, current_round, user_id):
    selected_plan_id = selected_plan.id
    results = QuizResult.query.filter(QuizResult.plan_id == selected_plan_id,
                                       QuizResult.status == 'finished',
                                       QuizResult.round_number == int(current_round)) \
                             .order_by(desc(QuizResult.score), QuizResult.time_finished) \
                             .all()

    user_position = {'position': None, 'score': None}
    
    print("Results for Round", current_round)
    for i, result in enumerate(results):
        print(f"User {result.user_id} - Score: {result.score}, Time: {result.time_finished}")

        if result.user_id == user_id:
            user_position['position'] = i + 1
            user_position['score'] = result.score
            break

    return user_position


@app.route('/game')
@login_required
def game():
    id = session.get('useronline')

    dashboard_data = get_dashboard_data(id)
    return render_template('game.html', **dashboard_data)


def get_starter_prize(position):
    print('Calculating Starter prize for position:', position)
    if position == 1:
        return 5000
    elif position == 2:
        return 2000
    elif position == 3:
        return 1000
    elif 4 <= position <= 13:
        return 100  # Refund for 4th to 13th position
    else:
        return 0

def get_basic_prize(position):
    print('Calculating Basic prize for position:', position)
    if position == 1:
        return 10000
    elif position == 2:
        return 4000
    elif position == 3:
        return 2000
    elif 4 <= position <= 13:
        return 200  # Refund for 4th to 13th position
    else:
        return 0

def get_pro_prize(position):
    print('Calculating Pro prize for position:', position)
    if position == 1:
        return 25000
    elif position == 2:
        return 10000
    elif position == 3:
        return 5000
    elif 4 <= position <= 13:
        return 500  # Refund for 4th to 13th position
    else:
        return 0

def get_gold_prize(position):
    print('Calculating Gold prize for position:', position)
    if position == 1:
        return 50000
    elif position == 2:
        return 20000
    elif position == 3:
        return 10000
    elif 4 <= position <= 13:
        return 1000  # Refund for 4th to 13th position
    else:
        return 0

def get_gold_winner_takes_it_all_prize(position):
    print('Calculating Gold Winner Takes It All prize for position:', position)
    if position == 1:
        return 90000
    else:
        return 0

def get_premium_prize(position):
    print('Calculating Premium prize for position:', position)
    if position == 1:
        return 250000
    elif position == 2:
        return 100000
    elif position == 3:
        return 50000
    elif 4 <= position <= 13:
        return 5000  # Refund for 4th to 13th position
    else:
        return 0

def get_premium_winner_takes_it_all_prize(position):
    print('Calculating Premium Winner Takes It All prize for position:', position)
    if position == 1:
        return 400000
    else:
        return 0

def get_prize_amount(selected_plan_id, position):
    print(f"Calculating prize for Plan {selected_plan_id} at position {position}")

    if selected_plan_id == 1:
        return float(get_starter_prize(position))
    elif selected_plan_id == 2:
        return float(get_basic_prize(position))
    elif selected_plan_id == 3:
        return float(get_pro_prize(position))
    elif selected_plan_id == 4:
        return float(get_gold_prize(position))
    elif selected_plan_id == 5:
        return float(get_gold_winner_takes_it_all_prize(position))
    elif selected_plan_id == 6:
        return float(get_premium_prize(position))
    elif selected_plan_id == 7:
        return float(get_premium_winner_takes_it_all_prize(position))
    else:
        return 0.0  # Handle the case for an unknown pla

def get_winners(selected_plan, current_round, user_id):
    selected_plan_id = selected_plan.id
    results = QuizResult.query.filter(QuizResult.plan_id == selected_plan_id,
                                       QuizResult.status == 'finished',
                                       QuizResult.round_number == int(current_round)) \
                             .order_by(desc(QuizResult.score), QuizResult.time_finished) \
                             .all()

    winners = []

    for i, result in enumerate(results):
        position = i + 1  # Positions start from 1
        prize_amount = get_prize_amount(selected_plan_id, position)
        winners.append({'user_id': result.user_id, 'prize': prize_amount, 'position': position})

    print("Winners list:", winners)

    # Calculate the user's position based on user_id
    user_position = None
    for i, winner in enumerate(winners):
        if winner['user_id'] == user_id:
            user_position = winner['position']
            break

    return winners, user_position

def credit_winners(cls, winners):
    users_to_update = [User.query.get(winner['user_id']) for winner in winners]
    total_prize_amount = sum([winner['prize'] for winner in winners])

    print(f"Crediting {len(winners)} winners with a total prize amount of: {total_prize_amount}")

    if not winners:
        print("No winners to credit.")
        return

    for user, winner in zip(users_to_update, winners):
        prize_amount = winner['prize']
        print(f"Crediting user {user.id} with prize amount: {prize_amount}")

        # Get the current balance
        current_balance = user.balance

        user.balance += prize_amount

        # Print the balance
        print(f"User {user.id}'s balance after credit: {user.balance}")

    db.session.commit()
@app.route('/get_user_balance/<int:user_id>', methods=['GET'])
def get_user_balance(user_id):
    print(f"Received request for user ID: {user_id}")
    user = User.query.get(user_id)

    if user:
        print(f"Returning balance for user {user_id}: {user.balance}")
        return jsonify({'balance': user.balance})
    else:
        print(f"User {user_id} not found.")
        return jsonify({'error': 'User not found'}), 404

@app.route('/submit_score', methods=['GET'])
@login_required
def submit_score():
    selected_category_id = session.get('selected_category')
    selected_plan_id = session.get('selected_plan')

    user_id = session.get('useronline')
    score_str = request.args.get('score')
    time_completed_str = request.args.get('time_completed')
    game_status = request.args.get('gameStatus')

    if score_str is not None and time_completed_str is not None and game_status is not None:
        try:
            score = float(score_str)

            # Duration of the quiz in seconds (5 minutes)
            duration_seconds = 300

            # Calculate time_completed
            time_completed = datetime.strptime(time_completed_str, "%M:%S")
            time_completed_seconds = time_completed.minute * 60 + time_completed.second

            # Calculate remaining time as the difference between allotted time and time completed
            remaining_time_seconds = max(0, duration_seconds - time_completed_seconds)
            remaining_time_str = str(timedelta(seconds=remaining_time_seconds))

            # Get the round number from the session
            played_games_key = f'played_games_{selected_plan_id}'
            played_games = session.get(played_games_key, 0)
            current_round = (played_games - 1) // 15 + 1

        except ValueError:
            return jsonify({"error": "Invalid score, time completed, or game status format"}), 400
    else:
        return jsonify({"error": "Score, time completed, or game status is None"}), 400

    quiz = QuizResult(
        user_id=user_id,
        category_id=selected_category_id,
        plan_id=selected_plan_id,
        score=score,
        time_finished=remaining_time_str,  # Storing the remaining time
        status=game_status,
        round_number=current_round  # Set the round number
    )

    try:
        db.session.add(quiz)
        db.session.commit()

        print(f"User {user_id} submitted a score of {score} for Plan {selected_plan_id} in Round {current_round}")

        return jsonify({"message": "Submitted Successfully", "remaining_time": remaining_time_str})
    except Exception as e:
        print(f"Error committing to the database: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error committing to the database"}), 500

def shuffle(choices):
    random.shuffle(choices)

@app.route('/apply_lifeline', methods=['GET'])
@login_required
def apply_lifeline():
    # Get the selected_friend from the request
    selected_friend = request.args.get('selected_friend')
    selected_friend_index = request.args.get('selected_friend_index')

    # Get the choices, correct_answer, accuracy, and correct_answer_index from the request
    options = request.args.getlist('choices')
    correct_answer = request.args.get('correct_answer')
    accuracy = float(request.args.get('accuracy')) if request.args.get('accuracy') is not None else 0.0
    correct_answer_index = int(request.args.get('correct_answer_index')) if request.args.get('correct_answer_index') is not None else -1

    if correct_answer is not None:
        lifeline = request.args.getlist('lifelines') or []
        choices = options
        shuffle(choices)

        if 'fifty_fifty' in lifeline:
          original_choices = 'correct_option,option1,option2,option3'
          choices = original_choices.split(',')

# Shuffle the incorrect answers in place
          shuffle(choices)

# Print the shuffled incorrect answers
          print("Shuffled Choices:", choices)

# Keep only the first half of the shuffled list (i.e., remove the last two)
          hidden_answers = choices[:len(choices)//2]

# Update the UI or perform any necessary actions based on hidden_answers
          print("Hidden Answers:", hidden_answers)

          for hidden_answer in hidden_answers:
                # Find the index of the hidden answer in choices
                if hidden_answer in choices:
                    index = choices.index(hidden_answer)
                    
                    # Replace the hidden answer with None in choices
                    choices[index] = None

            # Return the response
          return jsonify({'hidden_options': hidden_answers, 'lifeline_conversation': 'You used the 50:50 lifeline.'})

        if 'phone_a_friend' in lifeline:
            print('Accuracy:', accuracy)

            # Generate the conversation for the "phone_a_friend" lifeline
            lifeline_conversation = generate_phone_a_friend_conversation(selected_friend,selected_friend_index,accuracy,correct_answer,choices)

            # Simulate a delayed conversation
            # delayed_conversation = simulate_delayed_response(lifeline_conversation)

            return jsonify({'lifeline_conversation': lifeline_conversation, 'correct_answer_index': correct_answer_index})

        # Return a response even when 'phone_a_friend' is not in lifelines
        return jsonify({'lifeline_conversation': None, 'correct_answer_index': correct_answer_index})
    else:
        return jsonify({'error': 'Correct answer is None'})
    
def generate_phone_a_friend_conversation(selected_friend_index, selected_friend, accuracy, correct_answer, choices):
    # Get the chosen option based on the logic and accuracy
    chosen_option = get_chosen_option(choices, selected_friend_index, accuracy, correct_answer)

    # Define image path based on accuracy
    if accuracy == 1:
        image_path = '/static/images/bard1.jpeg'
        friend_style = "color: pink; font-weight: bold; font-style: italic;"
        user_style = "color: blue; font-weight: bold;"
    elif accuracy == 0.75:
        image_path = '/static/images/bard4.jpeg'
        friend_style = "color: orange; font-weight: bold; font-style: italic;"
        user_style = "color: blue; font-weight: bold;"
    else:
        image_path = '/static/images/bard5.jpeg'
        friend_style = "color: red; font-weight: bold; font-style: italic;"
        user_style = "color: blue; font-weight: bold;"

    # Construct HTML with inline styles and image tag
    result = (
        f'<div style="margin-bottom: 10px; {friend_style}">'
        f'<span style="font-weight: bold;">Friend:</span> The answer is {chosen_option}'
        f'</div>'
        f'<div style="margin-bottom: 10px; {user_style}">'
        f'<span style="font-weight: bold;">User:</span> How confident are you?'
        f'</div>'
        f'<div>'
        f'<span style="font-weight: bold; {friend_style}">Friend:</span> '
        f'''{"I'm confident! The answer is definitely correct." if accuracy == 1 else
        ("I think the answer is probably correct." if accuracy == 0.75 else "I'm not sure, but I guess it might be correct.")}'''

        f'</div>'
        f'<img src="{image_path}" alt="Friend Image" style="max-width: 100px; max-height: 100px; margin-top: 10px; margin-left: 10px; float: left;">'
        f'<div style="clear: both;"></div>'
    )

    return result











def generate_html_string():
    # Replace this with your actual logic to generate HTML string
    # For example:
    html_string = '<p>This is an example HTML string.</p>'
    return html_string


def generate_combined_conversation(selected_friend_index, selected_friend, accuracy, correct_answer, choices):
    lifeline_conversation = generate_phone_a_friend_conversation(selected_friend_index, selected_friend, accuracy, correct_answer, choices)
    additional_html = generate_html_string()  # Modify this based on your needs

    # Combine the two HTML strings
    combined_conversation = f"{lifeline_conversation}\n{additional_html}"

    return combined_conversation






def get_chosen_option(choices,selected_friend_index,accuracy,correct_answer):
    choices = [correct_answer, 'B', 'C', 'D']
    
    # Assuming 'accuracy' is a float between 0 and 1
    if accuracy == 1:
        # If accuracy is perfect, choose the correct answer
        return choices[0]
    elif accuracy==0.75:
        # If accuracy is high, choose the correct answer or another random option
        return choices[0] if random.random() < 0.5 else random.choice(choices[1:])
    else:
        # If accuracy is low, choose a random incorrect answer
        return random.choice(choices[1:])


def simulate_delayed_response(conversation):
    # Split the conversation into lines
    lines = conversation.split('\n')

    # Simulate a delayed conversation
    delayed_lines = []
    delay = 3  # Adjust the delay time in seconds as needed

    for line in lines:
        if line.startswith("Friend:"):
            accuracy = float(line.split(':')[-1].strip()) if ':' in line else None

            if accuracy == 1.0:
                image_url = '/static/images/bard1.jpeg'
            elif accuracy == 0.75:
                image_url = '/static/images/bard4.jpeg'
            else:
                image_url = '/static/images/bard5.jpeg'

            delayed_lines.append(f"Friend: {line}\n<img src='{image_url}' alt='Friend's Image'>")
            delayed_lines.append("User: How confident are you?")
            time.sleep(delay)  # Add a delay between Friend's response and User's question
        else:
            delayed_lines.append(f"User: {line}\n<img src='/static/images/bard3.jpeg' alt='User's Image'>")
            time.sleep(delay)  # Add a delay after User's question

    delayed_conversation = '\n'.join(delayed_lines)
    return delayed_conversation

