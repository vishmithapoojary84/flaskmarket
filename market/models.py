from market import db,login_manager
from market import bcrypt
from flask_login import UserMixin
print("models.py loaded")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email_address = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(60), nullable=False)
    budgets = db.Column(db.Integer, nullable=False, default=1000)
    items = db.relationship('Item', backref='owned_user', lazy=True)

    @property
    def prettier_budgets(self):
        if len(str(self.budgets))>=4:
            return f"{str(self.budgets)[:-3]},{str(self.budgets)[-3:]} $"
        else:
            return f"{self.budgets} $"


    @property
    def password(self):
        raise AttributeError('Password cannot be accessed directly')

    @password.setter
    def password(self, plain_text_password):
        # Hash the password before storing it
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
            
    def can_purchase(self, item_obj):
        return self.budgets >= item_obj.price
    
    def can_sell(self, item_obj):
        return item_obj in self.items
    

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    barcode = db.Column(db.String(12), unique=True, nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(1024), nullable=False,unique=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self):
     return f"Item {self.name}"
    
    def buy(self, user):
        self.owner=user.id
        user.budgets -= self.price
        db.session.commit()

    def sell(self, user):
        self.owner=None
        user.budgets += self.price
        db.session.commit()