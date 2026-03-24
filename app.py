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

# ---------- SAFE LOAD FUNCTIONS ----------

def load_books():

    columns=[
    'book_id','title','author',
    'genre','quantity','image'
    ]

    if os.path.exists(BOOK_FILE):

        df=pd.read_csv(BOOK_FILE)

        for col in columns:

            if col not in df.columns:

                if col=="image":
                    df[col]="none"

                elif col=="quantity":
                    df[col]=0

                else:
                    df[col]=""

        return df[columns]

    return pd.DataFrame(columns=columns)


def save_books(df):

    df.to_csv(BOOK_FILE,index=False)


def load_borrow():

    cols=['user','book_id','borrow_date']

    if os.path.exists(BORROW_FILE):

        df=pd.read_csv(BORROW_FILE)

        for col in cols:

            if col not in df.columns:

                df[col]=""

        return df[cols]

    return pd.DataFrame(columns=cols)


def save_borrow(df):

    df.to_csv(BORROW_FILE,index=False)


def load_users():

    cols=['username','password','role']

    if os.path.exists(USER_FILE):

        df=pd.read_csv(USER_FILE)

        for col in cols:

            if col not in df.columns:

                df[col]="user"

        return df[cols]

    return pd.DataFrame(columns=cols)

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

            st.error("Invalid login")

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

["Dashboard","Add Book","View Books",
"Search","Issue Book","Return Book",
"Delete Book","History","Analysis"]

)

# ---------- DASHBOARD ----------

if menu=="Dashboard":

    df=load_books()

    borrow=load_borrow()

    col1,col2,col3=st.columns(3)

    col1.metric("Titles",len(df))

    col2.metric(
    "Total Books",
    int(df.quantity.sum())
    )

    col3.metric(
    "Issued",
    len(borrow)
    )

# ---------- ADD BOOK ----------

if menu=="Add Book":

    st.subheader("Add Book")

    id=st.text_input("Book ID")

    title=st.text_input("Title")

    author=st.text_input("Author")

    genre=st.text_input("Genre")

    qty=st.number_input(
    "Quantity",
    min_value=0
    )

    img=st.text_input("Image URL")

    if st.button("Add"):

        df=load_books()

        if id in df.book_id.values:

            st.error("ID exists")

        elif id=="" or title=="":

            st.warning("Fill required fields")

        else:

            if img=="":
                img="none"

            new_row=pd.DataFrame([

            {
            "book_id":id,
            "title":title,
            "author":author,
            "genre":genre,
            "quantity":qty,
            "image":img
            }

            ])

            df=pd.concat(
            [df,new_row],
            ignore_index=True
            )

            save_books(df)

            st.success("Book added")

# ---------- VIEW ----------

if menu=="View Books":

    df=load_books()

    if df.empty:

        st.warning("No books")

    else:

        for i,row in df.iterrows():

            col1,col2=st.columns([1,3])

            with col1:

                if str(row.image).startswith("http"):

                    st.image(row.image)

            with col2:

                st.write("###",row.title)

                st.write("Author:",row.author)

                st.write("Genre:",row.genre)

                if row.quantity>0:

                    st.success("Available")

                else:

                    st.error("Out of stock")

# ---------- SEARCH ----------

if menu=="Search":

    df=load_books()

    key=st.text_input("Search")

    if st.button("Search"):

        result=df[

        df.title.str.contains(
        key,
        case=False
        )|

        df.book_id.astype(str).str.contains(
        key
        )

        ]

        if result.empty:

            st.error("Not found")

        else:

            st.dataframe(result)

# ---------- ISSUE ----------

if menu=="Issue Book":

    df=load_books()

    borrow=load_borrow()

    user=st.text_input("User")

    book=st.text_input("Book ID")

    if st.button("Issue"):

        if book not in df.book_id.values:

            st.error("Book not found")

        else:

            index=df[
            df.book_id==book
            ].index[0]

            if df.loc[index,'quantity']==0:

                st.error("Not available")

            else:

                df.loc[index,'quantity']-=1

                save_books(df)

                borrow.loc[len(borrow.index)]=[

                user,
                book,
                datetime.date.today()

                ]

                save_borrow(borrow)

                st.success("Issued")

# ---------- RETURN ----------

if menu=="Return Book":

    df=load_books()

    borrow=load_borrow()

    user=st.text_input("User")

    book=st.text_input("Book ID")

    if st.button("Return"):

        record=borrow[

        (borrow.user==user)&
        (borrow.book_id==book)

        ]

        if record.empty:

            st.error("No record")

        else:

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

# ---------- DELETE ----------

if menu=="Delete Book":

    if st.session_state.role!="admin":

        st.error("Admin only")

    else:

        df=load_books()

        id=st.text_input("Book ID")

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

    if not df.empty:

        st.bar_chart(

        df.set_index(
        'title'
        )['quantity']

        )

    if not borrow.empty:

        st.bar_chart(

        borrow.book_id.value_counts()

        )
