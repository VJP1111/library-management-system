import streamlit as st
import pandas as pd
import os
import datetime

BOOK_FILE="books.csv"
BORROW_FILE="borrowing_records.csv"

st.title("Library Management System")

def load_books():
    if os.path.exists(BOOK_FILE):
        return pd.read_csv(BOOK_FILE)
    return pd.DataFrame(columns=['book_id','title','author','genre','quantity'])

def save_books(df):
    df.to_csv(BOOK_FILE,index=False)

def load_borrow():
    if os.path.exists(BORROW_FILE):
        return pd.read_csv(BORROW_FILE)
    return pd.DataFrame(columns=['user','book_id','borrow_date'])

def save_borrow(df):
    df.to_csv(BORROW_FILE,index=False)

menu=st.sidebar.selectbox("Menu",
["Add Book","View Books","Search Book","Delete Book","Borrow Book","Return Book","Analysis"])

if menu=="Add Book":
    st.subheader("Add New Book")
    id=st.text_input("Book ID")
    title=st.text_input("Title")
    author=st.text_input("Author")
    genre=st.text_input("Genre")
    qty=st.number_input("Quantity",min_value=0)

    if st.button("Add Book"):
        df=load_books()
        if id in df['book_id'].values:
            st.error("Book ID exists")
        else:
            df.loc[len(df.index)]=[id,title,author,genre,qty]
            save_books(df)
            st.success("Book Added")

if menu=="View Books":
    st.subheader("Library Books")
    df=load_books()
    st.dataframe(df)

if menu=="Search Book":
    st.subheader("Search Book")
    q=st.text_input("Enter title/author/id")
    if st.button("Search"):
        df=load_books()
        result=df[df['title'].str.contains(q,case=False,na=False) |
                  df['author'].str.contains(q,case=False,na=False) |
                  df['book_id'].str.contains(q,case=False,na=False)]
        st.dataframe(result)

if menu=="Delete Book":
    st.subheader("Delete Book")
    did=st.text_input("Book ID")
    if st.button("Delete"):
        df=load_books()
        df=df[df.book_id!=did]
        save_books(df)
        st.success("Deleted")

if menu=="Borrow Book":
    st.subheader("Borrow Book")
    user=st.text_input("User Name")
    bid=st.text_input("Book ID")

    if st.button("Borrow"):
        df=load_books()
        borrow=load_borrow()
        row=df[df.book_id==bid]

        if row.empty:
            st.error("Book not found")
        else:
            qty=int(row['quantity'].values[0])
            if qty==0:
                st.error("Out of stock")
            else:
                df.loc[df.book_id==bid,'quantity']=qty-1
                borrow.loc[len(borrow.index)]=[user,bid,datetime.date.today()]
                save_books(df)
                save_borrow(borrow)
                st.success("Borrowed")

if menu=="Return Book":
    st.subheader("Return Book")
    user=st.text_input("User")
    bid=st.text_input("Book ID")

    if st.button("Return"):
        df=load_books()
        borrow=load_borrow()

        mask=(borrow.user==user)&(borrow.book_id==bid)

        if borrow[mask].empty:
            st.error("No record")
        else:
            borrow=borrow[~mask]
            qty=int(df[df.book_id==bid]['quantity'].values[0])
            df.loc[df.book_id==bid,'quantity']=qty+1

            save_books(df)
            save_borrow(borrow)

            st.success("Returned")

if menu=="Analysis":
    st.subheader("Library Analysis")
    df=load_books()

    total=len(df)
    available=df[df.quantity>0].shape[0]

    st.write("Total Books:",total)
    st.write("Available Books:",available)

    top=df.sort_values('quantity',ascending=False).head(1)

    st.write("Highest Quantity Book:")
    st.dataframe(top)
