import streamlit as st
import mysql.connector

# Connect to the MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="books"
)

#st.set_page_config(background_color="#00ff00")


# In the global scope, initialize the flag using st.session_state
if 'flag' not in st.session_state:
    st.session_state.flag = 0

mycursor = mydb.cursor()

# User registration function
def register_user(name, email, password):
    sql = "INSERT INTO user (username, email, password) VALUES (%s, %s, %s)"
    val = (name, email, password)
    mycursor.execute(sql, val)
    mydb.commit()

# User login function
def login_user(email, password):
    sql = "SELECT * FROM user WHERE email = %s AND password = %s"
    val = (email, password)
    mycursor.execute(sql, val)
    user = mycursor.fetchone()
    print(user)
    if user is not None:
        st.session_state.flag = 1  # Update flag in st.session_state
    print("Flag is now:", st.session_state.flag)
    return user

# User logout function
def logout_user():
    st.session_state.flag = 0  # Reset flag in st.session_state

st.title("Library Management System")
options = st.sidebar.selectbox("Select an Operation", ("Register", "Login", "Search Book", "Rent", "WishList", "Logout"))

if options == "Register":
    st.subheader("User Registration")
    name = st.text_input("Enter UserName")
    email = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")
    if st.button("Register"):
        register_user(name, email, password)
        st.write("Registration successful!")
        st.write("Now you can log in with Email Id")

if options == "Login":
    st.subheader("User Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.write(f"Welcome, {user[1]}!")
        else:
            st.write("Login failed. Please check your credentials")

if options == "Search Book":
    print("Flag inside search book is:", st.session_state.flag)
    print('---')
    st.subheader("Search a Book")
    bookName = st.text_input("Enter the book name: ")
    if st.button("Search Book"):
        sql = "SELECT name FROM book WHERE name = %s"
        val = (bookName,)
        mycursor.execute(sql, val)
        result = mycursor.fetchall()    
        if result and st.session_state.flag == 1:
            st.subheader("Book Found")
            st.subheader("Go to the rent page to borrow the book!")
            for row in result:
                st.write(row[0])
        else:
            if st.session_state.flag == 0:
                st.write("Please Login First")
            else:
                st.write("Book Not Found!!")

if options == "WishList":
    option = st.selectbox("Choose an action:", ("View", "Add"))

    if option == "View":
        st.subheader("Wishlist")
        user_name = st.text_input("Enter User Name:")
        view = st.button("View Wishlist")

        if view:
            if user_name:
                mycursor.execute("SELECT bookname FROM wishlist WHERE username = %s", (user_name,))
                wishlist_items = mycursor.fetchall()

                if wishlist_items and st.session_state.flag == 1:
                    st.write(f"Wishlist items for User ID {user_name}:")
                    for item in wishlist_items:
                        st.write(f"- {item[0]}")
                else:
                    if(st.session_state!=1):
                        st.write("Please Login First!!")
                    else:
                        st.write("No items found for the given User ID.")
            else:
                st.write("Please enter a User ID.")

    elif option == "Add":
        st.subheader("Add to Wishlist")
        u_name = st.text_input("Enter User Name:")
        bn = st.text_input("Enter Book Name:")
        add = st.button("Add to Wishlist")

        if add:
            if u_name and bn and st.session_state.flag == 1:
                try:
                    query = "INSERT INTO wishlist (username, bookname) SELECT %s, %s FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM wishlist WHERE bookname = %s)"
                    mycursor.execute(query, (u_name, bn, bn))
                    mydb.commit()
                except Exception as e:
                    st.write(f"An error occurred: {e}")
            else:
                if(st.session_state!=1):
                    st.write("Please Login First!!")
                else:
                    st.write("Please enter User ID and Book Name.")


if options == "Rent":
    st.subheader("Dashboard")
    bookName = st.text_input("Enter the book name: ")
    rentName = st.text_input("Enter your name: ")

    if st.button("Rent"):
        sql = "INSERT INTO rent (book_name, user_name) VALUES (%s, %s)"
        val = (bookName, rentName)
        mycursor.execute(sql, val)
        mydb.commit()
        st.write("Book rented successfully!")

if options == "Logout":
    logout_user()
    st.write("You have been logged out")

mydb.close()