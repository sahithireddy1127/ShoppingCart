from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy import Table
import json
from random import randint
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] ='super-secret-key'
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = '12345'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bks.db'
db=SQLAlchemy(app)
with open("data\sjson.json") as data_file:
    data = json.loads(data_file.read())

class Currentcart(db.Model):
    # __tablename__ = 'users'
    serial = db.Column(db.Integer, primary_key=True)  
    bookid =db.Column(db.Integer)
    isbn=db.Column(db.String(20))
    quantity=db.Column(db.Integer)
    price=db.Column(db.Integer)

    def __init__(self,bookid,isbn, quantity, price):
        self.bookid=bookid
        self.isbn = isbn
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return '<Entry %r %r %r %r >' % (self.isbn, self.quantity, self.price)

class Customerorder(db.Model):
    # __tablename__ = 'users'
    serial = db.Column(db.Integer,primary_key=True)  
    
    bookid=db.Column(db.Integer)
    isbn=db.Column(db.String(20))
    quantity=db.Column(db.Integer)
    price=db.Column(db.Integer)
    orderid=db.Column(db.Integer,db.ForeignKey('customerdetails.orderid'))

    def __init__(self,bookid, isbn, quantity, price,orderid):
        
        self.bookid=bookid
        self.isbn = isbn
        self.quantity = quantity
        self.price = price
        self.orderid=orderid

    def __repr__(self):
    	return '<Entry %r %r %r >' % (self.bookid, self.quantity, self.price)
class Customerdetails(db.Model):
    """docstring for ClassName"""
    name = db.Column(db.String(20))
    phonenumber=db.Column(db.Integer)
    address = db.Column(db.String(20))
    orderid = db.Column(db.Integer,primary_key=True)
    def __init__(self, name,phonenumber,address,orderid):
        self.name=name
        self.phonenumber=phonenumber
        self.address=address
        self.orderid=orderid
    def __repr__(self):
    	return '<Entry %r %r %r >' % (self.name, self.phonenumber, self.orderid)

        
        
        

db.create_all()               
@app.route("/")
def index():
	return redirect("/book/0/")


@app.route('/cart',methods=['GET','POST'])
def cart():
    orders = Currentcart.query.all()


    
    return render_template('cart.html',orders=orders,data=data,count=len(orders))


@app.route('/checkout',methods=['GET','POST'])
def checkout():

    

    if request.method=='POST':
        orders = Currentcart.query.all()
        name = request.form.get('username')
        phonenumber=int(request.form.get('phone'))
        add = request.form.get('address')

        flag=1
        final = Customerdetails(name=name,phonenumber=phonenumber,address=add,orderid=randint(0,10000))
        db.session.add(final)
        db.session.commit()
        d = Currentcart.query.all()

        for x in d:
           
            bookid=  x.bookid
            isbn =  x.isbn
            quantity= x.quantity
            price = x.price
            border= final.orderid
           
            cust = Customerorder(bookid=bookid,isbn=isbn,quantity=quantity,price=price,orderid=border)
            db.session.add(cust)
            db.session.commit()

        olditems=Currentcart.query.all()
        b=final.orderid
        for i in olditems:
            db.session.delete(i)
            db.session.commit()

        nameofcust= final.name
        ordersofcust = Customerorder.query.filter_by(orderid=b).all()

        return render_template('checkout.html',flag=flag,orders = ordersofcust,name=nameofcust)
    return render_template('checkout.html')




@app.route('/book/<int:id>/', methods=['GET','POST'])
def book(id):
    total=Currentcart.query.all()
    m = 0
    for f in total:
        m+=f.quantity

    flag=0
    if request.method == 'GET':
        return render_template('home.html', id = id, data=data, flag=flag,size=len(data['items']),x=m)
    else:
       

        quantity=request.form.get('comp_select')
        isbn = 'ISBN' + str(data['items'][id]["volumeInfo"]["industryIdentifiers"][0]["identifier"])
        cart=Currentcart(bookid = id,isbn=isbn , quantity=quantity, price=data['items'][id]["saleInfo"]["listPrice"]["amount"])
        m+= int(quantity)
        detail = Currentcart.query.filter_by(isbn=isbn).all()
        sum=0
        for d in detail:
            sum+=(d.__dict__["quantity"])
        if sum+int(quantity)<=3:
            db.session.add(cart)
            db.session.commit()
            flag = 1
        else:
            flag = 2

        return render_template('home.html', id=id, data=data, flag=flag, size=len(data['items']),x=m)

@app.route('/vieworders',methods=['GET','POST'])
def vieworders():

	if request.method=='POST':
		name = request.form.get('username')
		phonenumber= request.form.get('phone')
		detail = Customerdetails.query.filter_by(name=name).filter_by(phonenumber=phonenumber).all()
		if len(detail)==1:
			s=0.0
			m=0.0
			print("hey")
			print (detail)
			print(detail[0].orderid)
			m = detail[0].orderid
			order = Customerorder.query.filter_by(orderid=m).all()
			for i in order:
				s=s+(i.price*i.quantity)
			m=s*0.1
			s=s+m



			
			return render_template('vieworders.html',order=order,price=s)
		else:
			print("hh")
			print(detail)
			return render_template('vieworders.html')

	else:
		return render_template('vieworders.html')




if __name__ =='__main__':
	app.run(debug=True)





