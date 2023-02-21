from fastapi import FastAPI
from fastapi import HTTPException
from models import UserProfile
import psycopg2
import re
import datetime

app = FastAPI()


conn = psycopg2.connect(
    host="localhost",
    database="test",
    user="gk",
    password="Kasi@123"
)

@app.post("/user_profiles")
async def create_user_profile(user_profile: UserProfile):
   
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user_profile.email):
        raise HTTPException(status_code=400, detail="Invalid email address")
    if len(user_profile.mobile_number) != 10:
        raise HTTPException(status_code=400, detail="Mobile number should be 10 digits long")
    try:
        datetime.datetime.strptime(user_profile.birthday, '%d-%m-%Y')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Date should be in dd-mm-yyyy format")

    today = datetime.date.today()
    birthday = datetime.datetime.strptime(user_profile.birthday, '%d-%m-%Y').date()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    if age < 18:
        raise HTTPException(status_code=400, detail="Age should be greater than 18")

    # Create a new record in the database
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO user_profiles (name, age, email, gender, mobile_number, birthday, city, state, country, address1, address2)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (user_profile.name, user_profile.age, user_profile.email, user_profile.gender, user_profile.mobile_number, user_profile.birthday, user_profile.city, user_profile.state, user_profile.country, user_profile.address1, user_profile.address2)
    )
    conn.commit()
    (user_profile_id,) = cursor.fetchone()

    # Return the newly created record
    return {"id": user_profile_id, **user_profile.dict()}


@app.get("/user_profiles/{user_profile_id}")
async def read_user_profile(user_profile_id: int):
    # Retrieve a record from the database
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name, age, email, gender, mobile_number, birthday, city, state, country, address1, address2
        FROM user_profiles
        WHERE id = %s
        """,
        (user_profile_id,)
    )
    record = cursor.fetchone()
    if not record:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Convert the record to a dictionary and return it
    keys = ("id", "name", "age", "email", "gender", "mobile_number", "birthday", "city", "state", "country", "address1", "address2")
    return dict(zip(keys, record))

@app.put("/user_profiles/{user_profile_id}")
async def update_user_profile(user_profile_id: int, user_profile: UserProfile):
    # Perform validation on the request payload
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user_profile.email):
        raise HTTPException(status_code=400, detail="Invalid email address")
    if len(user_profile.mobile_number) != 10:
        raise HTTPException(status_code=400, detail="Mobile number should be 10 digits long")
    try:
        datetime.datetime.strptime(user_profile.birthday, '%d-%m-%Y')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Date should be in dd-mm-yyyy format")

    today = datetime.date.today()
    birthday = datetime.datetime.strptime(user_profile.birthday, '%d-%m-%Y').date()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    if age < 18:
        raise HTTPException(status_code=400, detail="Age should be greater than 18")

    # Update the corresponding record in the database
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE user_profiles
        SET name = %s, age = %s, email = %s, gender = %s, mobile_number = %s, birthday = %s, city = %s, state = %s, country = %s, address1 = %s, address2 = %s
        WHERE id = %s
        """,
        (user_profile.name, user_profile.age, user_profile.email, user_profile.gender, user_profile.mobile_number, user_profile.birthday, user_profile.city, user_profile.state, user_profile.country, user_profile.address1, user_profile.address2, user_profile_id)
    )
    conn.commit()

    
    return {"id": user_profile_id, **user_profile.dict()}


@app.delete("/user_profiles/{user_profile_id}")
async def delete_user_profile(user_profile_id: int):
    # Delete the corresponding record from the database
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM user_profiles
        WHERE id = %s
        """,
        (user_profile_id,)
    )
    conn.commit()

    # Return a message to indicate success
    return {"message": "User profile deleted successfully"}




























# from fastapi import FastAPI,HTTPException
# from datetime import datetime
# from typing import Optional
# from database import connect_to_db
# from fastapi.middleware.cors import CORSMiddleware
# import asyncio
# from contextlib import asynccontextmanager
# from models import UserProfile
# import re

# app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:8080",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
# def validate_email(email: str):
#     if not email_pattern.match(email):
#         raise HTTPException(
#             status_code=404,
#             detail="Invalid email format"
#         )
# def validate_mobilenumber(mobile_number: str):
#     if len(mobile_number) != 10:
#         raise HTTPException(
#             status_code=404,
#             detail="Mobile number must be 10 digits"
#         )
# def validate_birthday(birthday: str):
#     if birthday is not None:
#         try:
#             datetime.strptime(birthday, '%d-%m-%Y')
#         except ValueError:
#             raise HTTPException(
#                 status_code=404,
#                 detail="Invalid birth data format (must be DD-MM-YYYY)"
#             )
# def validate_age(age: Optional[int]):
#     if age is not None and age<=18:
#         raise HTTPException(
#             status_code=404,
#             detail="Age must be greater than 18"
#         )

# @app.post('/user_profiles')
# async def create_user_profile(user_profile: UserProfile):
#     async with asynccontextmanager(connect_to_db())() as conn:
#         await conn.execute(
#             """
#             INSERT INTO user_profiles (name, age, email, gender, mobile_number, birthday, city, state, country, address1, address2)
#             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
#             """,
#             user_profile.name,
#             user_profile.age,
#             user_profile.email,
#             user_profile.gender,
#             user_profile.mobile_number,
#             user_profile.birthday,
#             user_profile.city,
#             user_profile.state,
#             user_profile.country,
#             user_profile.address1,
#             user_profile.address2,
#         )

#     return {
#         'code': 200,
#         'message': 'User created successfully',
#         'error': False,
#         'data': None
#     }

# @app.post('/user_profiles')
# async def create_user_profile(user_profile: UserProfile):
#     validate_email(user_profile.email)
#     validate_mobilenumber(user_profile.mobile_number)
#     validate_birthday(user_profile.birthday)
#     validate_age(user_profile.age)
#     async with pool.aquire() as conn:
#         await conn.execute(
#             """
#             INSERT INTO user_profiles (name,age,email,gender,mobile_number,birthday,city,state,country,address1,address2)
#             VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
#             """,
#             user_profile.name,
#             user_profile.age,
#             user_profile.email,
#             user_profile.mobile_number,
#             user_profile.birthday,
#             user_profile.city,
#             user_profile.state,
#             user_profile.country,
#             user_profile.address1,
#             user_profile.address2,
#         )
#     return{
#         'code': 200,
#         'message': 'User Created Successfully',
#         'error': False,
#         'data': None
#     }
# app.get('/user_profiles/{user_profile_id}')
# async def read_user_profile(user_profile_id: int):
#     async with pool.acquire() as conn:
#         user_profile = await conn.fetchrow(
#             """
#             select name,age,email,gender,mobile_number,birthday,city,state,country,address1,address2 
#             from user_profiles
#             where id = $1
#             """,
#             user_profile_id,   
#         )
#     if user_profile is None:
#         raise HTTPException(
#             status_code=404,
#             detail="user profile not found"
#         )
#     return {
#         'code': 200,
#         'message': 'User Profile Retrieved Successfully',
#         'error': False,
#         'data': dict(user_profile)
#     }
# @app.get('/user_profiles/{user_profile_id}')
# async def read_user_profile(user_profile_id: int):
#     async with connect_to_db() as conn:
#         user_profile = await conn.fetchrow(
#             """
#             SELECT name, age, email, gender, mobile_number, birthday, city, state, country, address1, address2
#             FROM user_profiles
#             WHERE id = $1
#             """,
#             user_profile_id,
#         )

#     if user_profile is None:
#         raise HTTPException(
#             status_code=404,
#             detail='User profile not found'
#         )

#     return {
#         'code': 200,
#         'message': 'User profile retrieved successfully',
#         'error': False,
#         'data': dict(user_profile)
#     }
# @app.put('/user_profiles/{user_profile_id}')
# async def update_user_profile(user_profile_id: int, user_profile: UserProfile):
#     async with connect_to_db() as conn:
#         existing_user_profile = await conn.fetchrow(
#             """
#             SELECT *
#             FROM user_profiles
#             WHERE id = $1
#             """,
#             user_profile_id,
#         )

#         if existing_user_profile is None:
#             raise HTTPException(
#                 status_code=404,
#                 detail='User profile not found'
#             )

#         existing_user_profile_dict = dict(existing_user_profile)
#         existing_user_profile_dict.update(user_profile.dict(exclude_unset=True))

#         updated_user_profile = UserProfile(**existing_user_profile_dict)

#         await conn.execute(
#             """
#             UPDATE user_profiles
#             SET name = $1, age = $2, email = $3, gender = $4, mobile_number = $5, birthday = $6, city = $7, state = $8, country = $9, address1 = $10, address2 = $11
#             WHERE id = $12
#             """,
#         )
#         updated_user_profile.name,
#         updated_user_profile.age,
#         updated_user_profile.email,
#         updated_user_profile.gender,
#         updated_user_profile.mobile_number
# @app.put('/user_profiles/{user_profile_id}')
# async def update_user_profile(user_profile_id: int, user_profile: UserProfile):
#     async with connect_to_db() as conn:
#         existing_user_profile = await conn.fetchrow(
#             """
#             SELECT *
#             FROM user_profiles
#             WHERE id = $1
#             """,
#             user_profile_id,
#         )

#         if existing_user_profile is None:
#             raise HTTPException(
#                 status_code=404,
#                 detail='User profile not found'
#             )

#         await conn.execute(
#             """
#             UPDATE user_profiles
#             SET name = $1, age = $2, email = $3, gender = $4, mobile_number = $5, birthday = $6, city = $7, state = $8, country = $9, address1 = $10, address2 = $11
#             WHERE id = $12
#             """,
#             user_profile.name,
#             user_profile.age,
#             user_profile.email,
#             user_profile.gender,
#             user_profile.mobile_number,
#             user_profile.birthday,
#             user_profile.city,
#             user_profile.state,
#             user_profile.country,
#             user_profile.address1,
#             user_profile.address2,
#             user_profile_id
#         )

#         return {
#             'code': 200,
#             'message': 'User profile updated successfully',
#             'error': False,
#             'data': None
#         }

# @app.delete('/user_profiles/{user_profile_id}')
# async def delete_user_profile(user_profile_id: int):
#     async with connect_to_db() as conn:
#         result = await conn.execute(
#             """
#             DELETE FROM user_profiles
#             WHERE id = $1
#             """,
#             user_profile_id,
#         )

#     if result == "DELETE 1":
#         return {
#             'code': 200,
#             'message': 'User profile deleted successfully',
#             'error': False,
#             'data': None
#         }
#     else:
#         raise HTTPException(
#             status_code=404,
#             detail='User profile not found'
#         )

# conn = psycopg2.connect(
#     dbname="test",
#     user="gk",
#     password="Kasi@123",
#     host="localhost",
#     port="5432"
# )
# @app.get("/")
# def read_root():
#     cur = conn.cursor()
#     cur.execute("select * from passenger")
#     rows = cur.fetchall()
#     cur.close()
#     return {"data":rows}