# My Asset Plan
# 1. 프로젝트 개요
## 1.1 프로젝트 제목
My Asset Plan (MAP) 통합 자산 관리 플랫폼

## 1.2 프로젝트 로고
![Logo](/readme_image/Logo.png)


## 1.3 프로젝트 정보
### 1.3.1 소개
#### 1.3.1.1 배경
- 가계부부터 주식 투자 등 자산 및 재무 관리의 관심이 증가하고 있습니다.
- 그러나, 재무 관리 플랫폼의 분산으로 인해 효율적인 자산 관리가 제한적입니다.
- 또한, 다양한 종류의 복잡한 경제지표 등 한 눈에 경제를 파악하기 어렵습니다.

#### 1.3.1.2 기획 의도
- **자산 관리와 주가 예측을 한 번에 할 수 는 없을까?** 라는 아이디어를 통해,

   **투자 정보 확인과 자산 관리를 동시에 할 수 있는 통합 자산 관리 플랫폼** 개발 프로젝트를 기획했습니다.


#### 1.3.1.3 프로젝트 요약
- 자산 관리, 주가 예측, 뉴스를 한 웹 서비스에서 이용할 수 있는 시스템을 구축했습니다.
- 챗봇을 통해 사용자가 편리하게 사이트를 이용할 수 있도록 활용했습니다.


### 1.3.2 개발 기간 (총 13주)
⏰ 1차 프로젝트: 2024년 7월 17일 ~ 2024년 8월 13일

⏰ 2차 프로젝트 (최종): 2024년 8월 13일 ~ 2024년 10월 9일


### 1.3.3 주요 기능
#### 가. 자산 관리
- 대시보드, 캘린더, 내역 검색
#### 나. 주가 비교 및 예측
- 경제지표와 비교, 예측값 확인
#### 다. 오늘의 뉴스
- 뉴스 요약, 호재/악재 분류
#### 라. 통합 채팅방
- 익명 대화, 실시간 채팅
#### 마. 챗봇
- 질문 응답, STT/TTS 기능


## 1.4 팀 소개
### AICC 인공지능 컨택센터 웹 서비스 개발 (코드랩 아카데미) 2기 1팀 MAP (My Asset Plan)
#### 👩‍💻 송민영 (팀장)
#### 👩‍💻 박상희 (AI 파트장)
#### 👩‍💻 인진석 (DB 파트장)
#### 👩‍💻 임세빈 (Web 파트장)
#### 👩‍💻 김준우
#### 👩‍💻 신재준
#### 👩‍💻 심유경


## 1.5 시연 영상 링크
🎞 1차 시연 영상 [보러가기](https://youtu.be/0-AUfXGRqjs?si=w3WYdJuGxRb6RS89).

🎞 2차 시연 영상 [보러가기](https://youtu.be/0VPEfPMUddE?si=yvHlWJ5vCSeIFK8T).


# 2. 프로젝트 아키텍처
## 2.1 시스템 구성도
![System Architecture](/readme_image/SystemArchitecture.png)

## 2.2 유스케이스 다이어그램
| **메인 페이지**  | **MAP 페이지** |
|:------------:|:------------:|
| ![Main Page](./readme_image/UD_Main.png) | ![MAP](./readme_image/UD_MAP.png) |
| **주식 페이지**    | **뉴스 페이지** |
| ![Stock](./readme_image/UD_Stock.png) | ![News](./readme_image/UD_News.png) |

## 2.3 ERD (Entity Relationship Diagram)
![ERD](/readme_image/ERD.png)


# 3. 프로젝트 시작 가이드
## 3.1 요구사항
### 3.1.1 requirements (Link)[].

## 3.2 설치 및 실행



# 4. 기술 스택
![image](https://github.com/user-attachments/assets/c48d5793-5eeb-45d2-8c7f-64c0ee97c2fc)



# 5. 화면
| **메인화면**  | **회원가입** |
|:------------:|:------------:|
| ![Main Page](./readme_image/main.png) | ![Sign Up](./readme_image/signUp.png) |
| **로그인**    | **마이페이지** |
| ![Login Page](./readme_image/login.png) | ![MyPage](./readme_image/mypage.png) |
| **MAP**        | **가계부** |
| ![MAP](./readme_image/map.png)  | ![Household](./readme_image/household.png) |
| **주식 비교** | **주식 예측** |
| ![Stock Compare](./readme_image/compareStock.png)  | ![Stock Prediction](./readme_image/predicStock.png) |
| **뉴스**     | **통합 채팅방** |
| ![News Page](./readme_image/news.png)  | ![News Talk](./readme_image/newsTalk.png) |
| **FAQ**   | **관리자 화면** |
| ![FAQ](./readme_image/FAQ.png) | ![Adim](./readme_image/admin.png) |
| **챗봇**    | - |
| ![Chatbot](./readme_image/chatbot.png) | -|



# 6. 데이터
## 6.1 데이터 수집
![image](https://github.com/user-attachments/assets/73feeb55-81fc-4220-a522-4bb65c219c6c)
+ 한국은행 API 추가

## 6.2 데이터베이스



# 7. 기능 설명
## 7.1 로그인
- 회원가입 시, 가입한 이메일과 비밀번호로 로그인이 가능합니다. 
- 로그인하면 사용자의 세션이 생성됩니다. 

 📌 [상세 설명](https://github.com/LittlePrince327/AICC_MyAssetPlan/wiki/Login)


## 7.2 로그인


## 7.3 마이페이지


## 7.4 관리자 화면
- 관리자 권한을 가지고있는 사용자만 접근 가능합니다. 
- 사용자 관리가 가능합니다. 

📌 [상세 설명](https://github.com/LittlePrince327/AICC_MyAssetPlan/wiki/Admin)


## 7.5 MAP 재무 관리 화면
- 계좌번호가 등록되어 있는 사용자만 이용 가능합니다. 
- 총 자산, 예적금, 대출, 보유 투자 정보를 확인할 수 있습니다. 
- 보유 투자의 경우 추가가 가능합니다. 

📌 [상세 설명](https://github.com/LittlePrince327/AICC_MyAssetPlan/wiki/MAP)


## 7.6 가계부


## 7.7 주식 비교


## 7.8 주식 예측


## 7.9 뉴스


## 7.10 통합 채팅방


## 7.11 FAQ


## 7.12 챗봇



# 8. 총평
## 8.1 팀 회고
### 8.1.1 학습 데이터 수집
### 8.1.2 MyData
### 8.1.3 시간 및 자원 부족
### 8.1.4 배포
- WEB Service만 배포할 때는 한 인스턴스에 모두 배포할 수 있었습니다.
- AI 모델을 모두 합치자 한 곳에만 배포가 어려웠고 각 Client, Server, Database 세가지로 나누게 되었습니다.
- 이에 따라 AWS VPC를 구성하여 배포를 시도했습니다. 
- 그러나 Server 인스턴스의 메모리와 용량 부족으로 배포가 중단되었습니다.

### AWS VPC 구조도
![AWS VPC](./readme_image/AWS_VPC_배포구조도.png)

### 시도했던 GitHub Link
- 상세 배포 설명은 아래 링크에서 확인해주세요.

📋 [***Notion Arrangement***](https://creative-fox-a1a.notion.site/AWS-VPC-11328e6ef1ff802685b2f72017fbdffe?pvs=4)

📤 [***AWS VPC 클라이언트***](https://github.com/sebin0918/aiccmap_client)

📤 [***AWS VPC 서버***](https://github.com/sebin0918/aiccmap_server)

📤 [***AWS VPC 데이터베이스***](https://github.com/sebin0918/aiccmap_database)

## 8.2 개인 회고
👩‍💻 김준우

👩‍💻 박상희

👩‍💻 송민영

👩‍💻 신재준

👩‍💻 심유경

👩‍💻 인진석

👩‍💻 임세빈


