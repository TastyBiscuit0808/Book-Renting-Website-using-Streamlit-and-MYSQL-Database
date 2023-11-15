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

# Lend Feature
def lend_book(book_name, owner_username, author, genre, book_info):
    try:
        # Get the owner_id based on the provided username
        mycursor.execute("SELECT id FROM user WHERE username = %s", (owner_username,))
        owner_id_result = mycursor.fetchone()

        if owner_id_result:
            owner_id = owner_id_result[0]

            # Insert into the book table
            mycursor.execute("INSERT INTO book (name, owner_id, author, genre, book_info, available, times_rented) VALUES (%s, %s, %s, %s, %s, 1, 0)",
                             (book_name, owner_id, author, genre, book_info))


            # Get the last inserted book_id
            mycursor.execute("SELECT LAST_INSERT_ID()")
            book_id_result = mycursor.fetchone()
            book_id = book_id_result[0] if book_id_result else None

            if book_id:
                # Set a sentinel value for rentee_id
                rentee_id = -1  # You can use any sentinel value you prefer

                # Insert into the rent table
                sql = "INSERT INTO rent (rent_date, book_id, rentee_id, renter_id, status) VALUES (NOW(), %s, %s, %s, 'A')"
                ### status when book when owner places it on the site is A, when 
                ### someone rents it is B, and when they give the book back back to A
                val = (book_id, rentee_id, owner_id)
                mycursor.execute(sql, val)

                mydb.commit()
                st.write("Book lent successfully!")
            else:
                st.write("Failed to get book_id.")
        else:
            st.write("Owner not found.")
    except Exception as e:
        st.write(f"An error occurred: {e}")

# Rent Feature
def rent_book(book_name, rentee_name):
    try:
        # Check if the book is available for rent
        mycursor.execute("SELECT id, available FROM book WHERE name = %s", (book_name,))
        book_info = mycursor.fetchone()

        if book_info and book_info[1] == 1:
            # Set the book as unavailable
            mycursor.execute("UPDATE book SET available = 0 WHERE id = %s", (book_info[0],))

            # Update the rentee's information
            mycursor.execute("UPDATE user SET books_rented = books_rented + 1 WHERE username = %s", (rentee_name,))

            # Update the existing rent record
            sql = "UPDATE rent SET rent_date = NOW(), status = 'rented' WHERE book_id = %s AND rentee_id IS NULL"
            val = (book_info[0],)
            mycursor.execute(sql, val)

            mydb.commit()
            st.write("Book rented successfully!")
        else:
            st.write("Book is not available for rent.")
    except Exception as e:
        st.write(f"An error occurred: {e}")

#Return Feature
def return_book(user_name, book_name):
    try:
        # Check if the book is rented by the specified user
        mycursor.execute("SELECT book_id FROM rent WHERE renter_id = (SELECT owner_id FROM book WHERE name = %s )", (book_name,))
        id_book = mycursor.fetchone()

        mycursor.execute("SELECT books_rented FROM user WHERE username = %s", (user_name,))
        books_rented_count = mycursor.fetchone()[0]


        if (id_book and books_rented_count>0):

            # Update books_rented for the rentee            
            mycursor.execute("UPDATE user SET books_rented = books_rented - 1 WHERE username = %s", (user_name,))   

            # Update book availability to 1 in the book table
            mycursor.execute("UPDATE book SET available = 1 WHERE name = %s", (book_name,))

            # Update return_date and status in the rent table
            mycursor.execute("UPDATE rent SET return_date = NOW() WHERE book_id = %s", (id_book[0],))

            mydb.commit()
            st.write("Book returned successfully!")
        else:
            st.write("Book is not currently rented by the specified user.")
    except Exception as e:
        st.write(f"An error occurred: {e}")   



# User logout function
def logout_user():
    st.session_state.flag = 0  # Reset flag in st.session_state

st.title("Library Management System")
options = st.sidebar.selectbox("Select an Operation", ("Register", "Login", "Search Book", "Lend","Rent", "WishList", "Return", "Logout"))

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
                # print("In wishlist session")
                # print(st.session_state)

                if wishlist_items and st.session_state.flag == 1:
                    st.write(f"Wishlist items for User ID {user_name}:")
                    for item in wishlist_items:
                        st.write(f"- {item[0]}")
                else:
                    if(st.session_state.flag!=1):
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
    rentName = st.text_input("Enter your username: ")

    if st.button("Rent"):
        rent_book(bookName, rentName)

if options == "Lend":
    st.subheader("Lend a Book")
    book_name_lend = st.text_input("Enter the book name: ")
    author = st.text_input("Enter the author: ")
    
    # Dropdown for genres
    genres = ["Mystery", "Science Fiction", "Fantasy", "Romance", "Thriller", "Historical Fiction", "Non-fiction", "Biography", "Self-Help", "Adventure"]
    selected_genre = st.selectbox("Select genre:", genres)
    
    book_info = st.text_area("Enter book information: ")
    lender_name = st.text_input("Enter your username: ")
    
    if st.button("Lend"):
        lend_book(book_name_lend, lender_name, author, selected_genre, book_info)

if options == "Return":
    st.subheader("Return Book")
    userName = st.text_input("Enter User Name:")
    bookName = st.text_input("Enter book name:")

    if st.button("Return"):
        return_book(userName, bookName)


if options == "Logout":
    logout_user()
    st.write("You have been logged out")

mydb.close()