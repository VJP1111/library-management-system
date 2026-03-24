import streamlit as st
import pandas as pd
import os
import datetime

st.set_page_config(
page_title="Library System",
page_icon="📚",
layout="wide"
)

BOOK_FILE="books.csv"
BORROW_FILE="borrowing_records.csv"
USER_FILE="users.csv"

st.title("📚 Smart Library System")

# ---------- FUNCTIONS ----------

def load_books():
    if os.path.exists(BOOK_FILE):
        df = pd.read_csv(BOOK_FILE)

if 'image' not in df.columns:
    df['image'] = "none"

return df
return pd.DataFrame(columns=[
    'book_id','title','author',
    'genre','quantity','image'
    ])

def save_books(df):
    df.to_csv(BOOK_FILE,index=False)

def load_borrow():
    if os.path.exists(BORROW_FILE):
        return pd.read_csv(BORROW_FILE)

    return pd.DataFrame(columns=[
    'user','book_id','borrow_date'
    ])

def save_borrow(df):
    df.to_csv(BORROW_FILE,index=False)

def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)

    return pd.DataFrame(
    columns=["username","password","role"]
    )

# ---------- LOGIN ----------

if "logged" not in st.session_state:
    st.session_state.logged=False

if not st.session_state.logged:

    st.subheader("Login")

    user=st.text_input("Username")
    pw=st.text_input("Password",type="password")

    if st.button("Login"):

        users=load_users()

        record=users[
        (users.username==user)&
        (users.password==pw)
        ]

        if record.empty:

            st.error("Invalid")

        else:

            st.session_state.logged=True
            st.session_state.user=user
            st.session_state.role=record.iloc[0]['role']

            st.rerun()

    st.stop()

# ---------- SIDEBAR ----------

st.sidebar.write("User:",st.session_state.user)

if st.sidebar.button("Logout"):

    st.session_state.logged=False
    st.rerun()

menu=st.sidebar.selectbox(
"Menu",
["Dashboard","Add","View",
"Search","Issue","Return",
"Edit","Delete","History","Analysis"]
)

# ---------- DASHBOARD ----------

if menu=="Dashboard":

    df=load_books()
    borrow=load_borrow()

    col1,col2,col3=st.columns(3)

    with col1:
        st.metric("Titles",len(df))

    with col2:
        st.metric(
        "Books",
        int(df.quantity.sum())
        )

    with col3:
        st.metric(
        "Issued",
        len(borrow)
        )

# ---------- ADD ----------

if menu=="Add":

    st.subheader("Add Book")

    id=st.text_input("ID")
    title=st.text_input("Title")
    author=st.text_input("Author")
    genre=st.text_input("Genre")
    qty=st.number_input("Qty",0)
    img=st.text_input("Image URL")

    if st.button("Add"):

        df=load_books()

        df.loc[len(df.index)]=[
        id,title,author,genre,qty,img
        ]

        save_books(df)

        st.success("Added")

# ---------- VIEW ----------

if menu=="View":

    df=load_books()

    page=st.number_input(
    "Page",
    min_value=1,
    value=1
    )

    start=(page-1)*5
    end=start+5

    show=df.iloc[start:end]

    for i,row in show.iterrows():

        col1,col2=st.columns([1,3])

        with col1:

            if "http" in str(row['image']):
                st.image(row['image'])

        with col2:

            st.write("###",row['title'])

            st.write("Author:",row['author'])
            st.write("Genre:",row['genre'])

            if row['quantity']>0:
                st.success("Available")
            else:
                st.error("Out")

# ---------- SEARCH ----------

if menu=="Search":

    df=load_books()

    title=st.text_input("Title")
    genre=st.text_input("Genre")

    result=df

    if title!="":

        result=result[
        result.title.str.contains(
        title,case=False)
        ]

    if genre!="":

        result=result[
        result.genre.str.contains(
        genre,case=False)
        ]

    st.dataframe(result)

# ---------- ISSUE ----------

if menu=="Issue":

    df=load_books()
    borrow=load_borrow()

    user=st.text_input("User")
    book_id=st.text_input("Book")

    user_books=borrow[
    borrow.user==user
    ]

    if len(user_books)>=3:

        st.error("Max 3 books allowed")

    elif st.button("Issue"):

        if book_id not in df.book_id.values:

            st.error("Not found")

        else:

            index=df[
            df.book_id==book_id
            ].index[0]

            if df.loc[index,'quantity']==0:

                st.error("Out")

            else:

                df.loc[index,'quantity']-=1

                save_books(df)

                borrow.loc[len(borrow.index)]=[
                user,
                book_id,
                datetime.date.today()
                ]

                save_borrow(borrow)

                st.success("Issued")

# ---------- RETURN ----------

if menu=="Return":

    df=load_books()
    borrow=load_borrow()

    user=st.text_input("User")
    book=st.text_input("Book")

    if st.button("Return"):

        record=borrow[
        (borrow.user==user)&
        (borrow.book_id==book)
        ]

        if record.empty:

            st.error("No record")

        else:

            days=(

            pd.to_datetime(
            datetime.date.today()

            )-

            pd.to_datetime(
            record.iloc[0]['borrow_date']

            )

            ).days

            fine=0

            if days>7:

                fine=(days-7)*2

            index=df[
            df.book_id==book
            ].index[0]

            df.loc[index,'quantity']+=1

            save_books(df)

            borrow=borrow.drop(
            record.index
            )

            save_borrow(borrow)

            st.success("Returned")

            if fine>0:

                st.warning(
                f"Fine ₹{fine}"
                )

# ---------- EDIT ----------

if menu=="Edit":

    df=load_books()

    id=st.text_input("ID")

    if id in df.book_id.values:

        row=df[df.book_id==id]

        title=st.text_input(
        "Title",
        row.iloc[0]['title']
        )

        if st.button("Update"):

            df.loc[
            df.book_id==id,'title'
            ]=title

            save_books(df)

            st.success("Updated")

# ---------- DELETE ----------

if menu=="Delete":

    if st.session_state.role!="admin":

        st.error("Admin only")

    else:

        df=load_books()

        id=st.text_input("ID")

        if st.button("Delete"):

            df=df[
            df.book_id!=id
            ]

            save_books(df)

            st.success("Deleted")

# ---------- HISTORY ----------

if menu=="History":

    borrow=load_borrow()

    st.dataframe(borrow)

# ---------- ANALYSIS ----------

if menu=="Analysis":

    df=load_books()
    borrow=load_borrow()

    st.bar_chart(
    df.set_index('title')['quantity']
    )

    if not borrow.empty:

        issued=borrow.book_id.value_counts()

        st.bar_chart(issued)
