
from market import app
from flask import render_template,redirect,url_for,flash,get_flashed_messages,request
from market.models import Item,User
from market.forms import RegisterForm,LoginForm,PurchaseItemForm,SellItemForm
from market import db
from flask_login import login_user,logout_user,login_required,current_user

print("routes.py loaded") 
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market',methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form=PurchaseItemForm()
    selling_form=SellItemForm()
    if request.method == 'POST':
        # purchase item logic
        purchased_item=request.form.get('purchased_item')
        p_item_object=Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
              
                flash(f'Congratulations! You purchased {p_item_object.name} for {p_item_object.price} $', 'success')
            else:
                flash(f'Unfortunately, you cannot  buy {p_item_object.name} because it costs {p_item_object.price} $ and your current budget is {current_user.budgets} $', 'danger')

            # sell item logic
        sold_item=request.form.get('sold_item')
        s_item_object=Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f'Congratulations! You sold {s_item_object.name} back to Market for {s_item_object.price} $', 'success')
            else:
                flash(f'Unfortunately, something went wrong with selling {s_item_object.name} ', 'danger')
        return redirect(url_for('market_page'))
    if request.method == "GET":     
         items=Item.query.filter_by(owner=None)
         owned_items=Item.query.filter_by(owner=current_user.id)
    return render_template('market.html',items=items,purchase_form=purchase_form,owned_items=owned_items,selling_form=selling_form)

@app.route('/register',methods=['GET', 'POST'])
def register_page():
    form=RegisterForm()
    if form.validate_on_submit():
        if form.password1.data != form.password2.data:
            flash('Passwords must match', 'danger')
            return redirect(url_for('register_page'))
        user_to_create=User(username=form.username.data,
                            email_address=form.email_address.data)
        user_to_create.password = form.password1.data
                            
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Your account has been created successfully!.You are now logged in as {user_to_create.username}', 'success')
        return redirect(url_for('market_page'))
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"There was error creating the user {error}", category='danger')


    return render_template('register.html', form=form)

@app.route('/login',methods=['GET', 'POST'])
def login_page():
    form=LoginForm()
    if form.validate_on_submit():
        attempted_user=User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Logged In successfully! as {attempted_user.username}','success')
            return redirect(url_for('market_page'))
        else:
            flash('Login unsuccessful. Please check your username and password','danger')
    return render_template('login.html',form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!','info')
    return redirect(url_for('home_page'))

