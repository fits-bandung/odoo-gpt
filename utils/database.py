from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import inspect

app = Flask(__name__)
db_sqlalchemy = SQLAlchemy()
date_format = '%d/%m/%Y %H:%M'

class User(db_sqlalchemy.Model):
    __tablename__ = 'user'

    id = db_sqlalchemy.Column(db_sqlalchemy.Integer, primary_key=True)
    username = db_sqlalchemy.Column(db_sqlalchemy.String(64), unique=True)
    url = db_sqlalchemy.Column(db_sqlalchemy.String(64), unique=True)   
    db = db_sqlalchemy.Column(db_sqlalchemy.String(64), unique=True)
    password = db_sqlalchemy.Column(db_sqlalchemy.String(64) )
    nick_name = db_sqlalchemy.Column(db_sqlalchemy.String(64))
    phone_number  = db_sqlalchemy.Column(db_sqlalchemy.String(20), nullable=False)
    messages = db_sqlalchemy.relationship('Message', backref='user', lazy=True)
    entity_memory = db_sqlalchemy.Column(db_sqlalchemy.PickleType, nullable=True)
    token = db_sqlalchemy.Column(db_sqlalchemy.String(64))
    created_at = db_sqlalchemy.Column(db_sqlalchemy.DateTime, default=datetime.utcnow, nullable=False, unique=True)

    def __repr__(self):
        # return f'<User {self.id}: phone_number={self.phone_number}, entity_memory={self.entity_memory}>'
        return f'<user_id {self.id}: username={self.username}, url={self.url}, db={self.db}, nick_name={self.nick_name}, phone_number={self.phone_number}, entity_memory={self.entity_memory} ,  created_at={self.created_at.strftime(date_format)}>'
        #return f'<user_id {self.id}: username={self.username}, url={self.url}, db={self.db}, nick_name={self.nick_name}, phone_number={self.phone_number}, created_at={self.created_at.strftime(date_format)}>'
    
    
class Message(db_sqlalchemy.Model):
    __tablename__ = 'message'
    id = db_sqlalchemy.Column(db_sqlalchemy.Integer, primary_key=True)
    user_id = db_sqlalchemy.Column(db_sqlalchemy.Integer, db_sqlalchemy.ForeignKey('user.id'), nullable=False)
    user_name = db_sqlalchemy.Column(db_sqlalchemy.String(80), nullable=True)
    sender = db_sqlalchemy.Column(db_sqlalchemy.String(80), nullable=False)  
    recipient = db_sqlalchemy.Column(db_sqlalchemy.String(80), nullable=False) #sama dengan mobile_phone
    past = db_sqlalchemy.Column(db_sqlalchemy.Text, nullable=False)
    generated = db_sqlalchemy.Column(db_sqlalchemy.Text, nullable=False)
    timestamp = db_sqlalchemy.Column(db_sqlalchemy.DateTime, default=datetime.utcnow, nullable=False)
    total_cost = db_sqlalchemy.Column(db_sqlalchemy.Float, nullable=False)

    def __repr__(self):
        return f'<message_id {self.id}: timestamp={self.timestamp.strftime(date_format)}, recipient={self.recipient}, past={self.past}, sender={self.sender}, generated={self.generated}, total_cost=Rp. {round(self.total_cost,2)}>'


class Document(db_sqlalchemy.Model):
    __tablename__ = 'document'

    id = db_sqlalchemy.Column(db_sqlalchemy.Integer, primary_key=True)
    title = db_sqlalchemy.Column(db_sqlalchemy.String(128), nullable=False)
    pkl_data = db_sqlalchemy.Column(db_sqlalchemy.LargeBinary, nullable=False)  # Menyimpan data pickle
    uploaded_at = db_sqlalchemy.Column(db_sqlalchemy.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db_sqlalchemy.Column(db_sqlalchemy.Integer, db_sqlalchemy.ForeignKey('user.id'), nullable=False)  # ID pengguna yang mengunggah dokumen

    def __repr__(self):
        return f'<document_id {self.id}: title={self.title}, uploaded_at={self.uploaded_at.strftime(date_format)}, user_id={self.user_id}>'





def inspect_db():
    # Create a context for the current app


    with app.app_context():
        
        # Ketika mau drop di un-comment dulu (PENTING SAAT akan REINSTAL)
        #db_sqlalchemy.drop_all()
        # user.__table__.drop(db_sqlalchemy.engine)


        # Get table names
        engine = db_sqlalchemy.engine
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f'Total Tables: {len(tables)}. [database.py]')
        for i, table in enumerate(tables):
            a = i+1
            columns = inspector.get_columns(table)
            table_columns = [column['name'] for column in columns]
    
            #Cek apakah field dalam tabel sudah sesuai dengan objectnya? kalau berbeda lakukan drop table dan create kembali.
            model = globals()[table.capitalize()]
            model_columns = [column.name for column in model.__table__.columns]


            while set(model_columns) != set(table_columns):
                print(f'Column names for model of {table.capitalize()} is NOT OK')
                print(f'Dropping table "{table}"...')
                model.__table__.drop(db_sqlalchemy.engine)
                print(f'Initialize table "{table}"...')
                # db_sqlalchemy.create_all()
                table_to_create = model.__table__
                table_to_create.create(bind=engine, checkfirst=True)


                inspector = inspect(engine)
                tables = inspector.get_table_names()
                columns = inspector.get_columns(table)
                table_columns = [column['name'] for column in columns]
                #Cek apakah field dalam tabel sudah sesuai dengan objectnya? kalau berbeda lakukan drop table dan create kembali.
                model = globals()[table.capitalize()]
                model_columns = [column.name for column in model.__table__.columns]
                

            print(f"Table [{a}]: {table.capitalize()} ({', '.join(table_columns)}) --> OK")







    return tables

        


def init_app(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_data.db'
    db_sqlalchemy.init_app(app)
    
    with app.app_context():
        db_sqlalchemy.create_all()


#   return f'<message_id {self.id}: timestamp={self.timestamp.strftime(date_format)}, recipient={self.recipient}, past={self.past}, sender={self.sender}, generated={self.generated}>'


#Fungsi untuk tulis record chat ke database
def write_chat_to_db(user_name, recipient, past, sender ,generated, total_cost):
 
    msg = Message(
                user_id=1,
                user_name=user_name,
                recipient=recipient,
                past=past,
                sender=sender,
                generated=generated,
                timestamp=datetime.now(),
                total_cost=total_cost
                )

    with app.app_context():
        db_sqlalchemy.session.add(msg)  # Menambahkan objek pesan masuk ke database
        db_sqlalchemy.session.commit()  # Menyimpan perubahan ke database

    print(f"Message from {recipient} added to database")
    return msg

def reset_memory(phone):
    with app.app_context():
        user_query = User.query.filter_by(phone_number=phone).first() 

        print('\n\nMelakukan reset memori...\n\n')
        user_query.entity_memory = None
        db_sqlalchemy.session.commit()  
        incoming_message = "Katakan 'Memori percakapan sebelumnya sudah saya hapus.'"

    return incoming_message

def call_memory(phone):
    with app.app_context():
        user_query = User.query.filter_by(phone_number=phone).first() 
        memory = user_query.entity_memory

    return memory



init_app(app)
inspect_db()



