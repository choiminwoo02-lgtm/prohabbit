# 로그인/ 회원가입을 위한 파이썬 코드 작성
# 작성자 : 최민우
from fastapi import FastAPI, HTTPException, status # HTTPException과 status도 같이 import해두면 편해! API에서 에러(문제) 날 때, 직접 내가 "예외 처리" 해주려고 쓸 수 있는 클래스
from fastapi.middleware.cors import CORSMiddleware # CORSMiddleware를 FastAPI에 달아주면, allow_origins에 지정한 출처들이 백엔드 API를 안전하게 호출하게 허용
from pydantic import BaseModel # BaseModel은 FastAPI로 데이터를 주고받을 때, 어떤 형태의 데이터를 주고받을지 미리 '약속(정의)'하는 도구
from typing import Dict, Any # <<< 요것도 추가해두면 좋음! 코드를 좀 더 알기 쉽고 편하게 쓰기 위해 사용
from passlib.context import CryptContext # 비밀번호를 해싱하기 위해 사용

# 비밀번호 해싱을 위한 설정 (bcrypt 방식 사용)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

# 허용할 출처 (프론트엔드 주소들)
origins = [
    "http://localhost:3000",   # React/Vue 같은 프론트엔드 개발 서버
    "http://127.0.0.1:3000",
]

# CORS 미들웨어 추가 (기존 코드 그대로)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,     #서버와 얘기할 때 신분증(쿠키나 로그인 정보)도 주고 받는걸 허락해줘
    allow_methods=["*"],    #우리 서버에 보낼 수 있는 모든 종류의 '요청 방식'을 허락해줘
    allow_headers=["*"],    #요청 보낼 때 같이 보내는 모든 종류의 '추가 정보'(헤더)를 허락해줘
)

# ---------- 새로 추가할 부분! ----------

# 1. 회원가입 요청을 받을 데이터 모델 정의
class UserCreate(BaseModel):
    username: str
    password: str

# 2. (임시) 사용자 데이터 저장 공간
# 실제 앱에서는 데이터베이스(SQLite, PostgreSQL 등)를 사용해야 해!
# 지금은 테스트를 위해 딕셔너리에 저장할게!
fake_users_db: Dict[str, Dict[str, Any]] = {}


# 루트 경로 (기존 코드 그대로)
@app.get("/")
def read_root():
    return {"message": "FastAPI + CORS 뼈대 준비 완료!"}

# 3. 회원가입 API 엔드포인트
@app.post("/register", status_code=status.HTTP_201_CREATED) # FastAPI 앱한테 POST 방식으로 데이터를 보내서 뭔가 새로 만들어달라고 요청이 오면, 바로 밑에 있는 함수를 실행시켜!" 라고 명령하는 것
                                                            # status.HTTP_201_CREATED 성공적으로 새로운 것을 만들었다는 뜻의 201번 메시지를 돌려줘!" 라고 서버한테 미리 일러주는 것
async def register_user(user: UserCreate): # async를 사용하면 하던 작업이 다 끝나지 않아도 넘어감
    # 이미 존재하는 유저인지 확인 (임시 DB 기준)
    if user.username in fake_users_db:                  # 52~56 어떤 종류의 오류인지 알려줌 이미 회원일 때 알려주기 위해 오류를 터뜨림
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # 비밀번호 해싱: 절대 그냥 저장하면 안 돼!
    hashed_password = pwd_context.hash(user.password)

    # 사용자 정보를 임시 DB에 저장
    # 실제로는 이 부분을 DB 저장 로직으로 교체해야 함!
    fake_users_db[user.username] = {
        "hashed_password": hashed_password,
        # 나중에 다른 사용자 정보 (이메일, 이름 등)도 추가할 수 있어.
    }
    
    print(f"회원가입 완료: {user.username}, 해시된 비번: {hashed_password}") # 콘솔에서 확인용
    
    return {"message": "User registered successfully", "username": user.username}

