# -*- coding: utf-8 -*-
"""enterti2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LEstYjeVb-RsG5b1v9MBvBq_KYznIlO0
"""

#  !pip install konlpy
#  !pip install soynlp

from typing import List, Dict, Optional, Tuple, Set, Union

import time
import pytz
import calendar
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

import re
import nltk
import spacy

from spacy.tokens import Span
from spacy.matcher import Matcher
from spacy.util import filter_spans

from konlpy.tag import Hannanum
# from pykospacing import Spacing
from konlpy.tag import Okt, Kkma
from soynlp.normalizer import repeat_normalize
from nltk import word_tokenize, pos_tag, ne_chunk

okt = Okt()
kkma = Kkma()
# spacing = Spacing()
hannanum = Hannanum()

nltk.download('punkt', )
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

# 한국 표준시(KST) 타임존 설정
kst = pytz.timezone('Asia/Seoul')

def convert_relative_years(match: str, time: bool = False) -> Optional[List[int]]:
    """
    입력된 문자열에서 상대적 또는 절대적 연도 표현이 포함되어 있을 때 해당 연도를 계산하여 반환

    Args:
        match (str): 상대적 또는 절대적 연도를 나타내는 문자열. 예: '3년 전', '2022년', '올해', '내년'
        time (bool): 미래 연도를 포함할지 여부, 기본값은 False

    Returns:
        List[Optional[int]]: 계산된 연도를 리스트로 반환. 예: ['2023'], ['2025']
    """
    today_year = datetime.now().year

    # 상대적 연도 표현을 포함한 경우 처리
    relative_years = {
        "재작년": today_year - 2,
        "작년": today_year - 1,
        "올해": today_year,
        "내년": today_year + 1 if time else None,
        "내휴냔": today_year + 2 if time else None
    }

    # match 안에 상대적 연도 표현이 포함되어 있을 때 해당 연도 처리
    for key, year_value in relative_years.items():
        if key in match:
            return [str(year_value)] if year_value is not None else None

    # '년 전', '년 후'와 절대 연도 표현을 한번에 처리
    if year_shift := re.search(r'(\d{1,4})년(?: (전|후))?', match):
        year, shift = int(year_shift.group(1)), year_shift.group(2)
        calculated_year = [today_year - year if shift == '전' else (today_year + year if shift == '후' else year)]

        if not time and calculated_year[0] > today_year:
            return None
        return calculated_year

    return None

def convert_relative_months(match: str, time: bool = False, year: Optional[int] = None) -> List[str]:
    """
    입력된 문자열(match)에 포함된 상대적인 월 정보를 기준으로 실제 날짜(월)를 변환하는 함수.

    Args:
    - match (str): 상대적인 날짜 표현이 포함된 문자열 (예: '2분기', '3개월 전').
    - time (bool): True이면 미래 날짜를 그대로 반환하고, False이면 미래 날짜를 전년도 날짜로 변환.
    - year (int): 연도를 지정하는 선택적 인자. 지정하면 해당 연도의 날짜를 반환.

    Returns:
    - list[str]: 변환된 날짜들을 'YYYY-MM' 형식의 문자열 리스트로 반환.
    """

    today = datetime.now(kst).date()
    target_year = year if year else today.year
    specified_months = []

    match_exact_month = re.search(r'(\d{1,2})월', match)
    if match_exact_month:
        exact_month = int(match_exact_month.group(1))
        future_date = datetime(target_year, exact_month, 1).date()
        if year and future_date.year != year:
            return None if future_date > today and not time else [future_date.strftime("%Y-%m")]
        if not year and future_date > today and not time:
            future_date = future_date.replace(year=today.year - 1)
        return [future_date.strftime("%Y-%m")]
    match_month = re.search(r'(\d{1,2})개?월(?: (전|후))?', match)

    if match_month:
        months_offset = int(match_month.group(1))
        if '전' in match:
            past_date = today - relativedelta(months=months_offset)
            if year and past_date.year != year:
                return None if (past_date > today and not time) else [past_date.strftime("%Y-%m")]
            if not year and past_date > today and not time:
                past_date = past_date.replace(year=today.year - 1)
            return [past_date.strftime("%Y-%m")]

        if '후' in match:
            future_date = today + relativedelta(months=months_offset)
            if year and future_date.year != year:
                return None if (future_date > today and not time) else [future_date.strftime("%Y-%m")]
            return None if future_date > today and not time else [future_date.strftime("%Y-%m")]

        for i in range(months_offset):
            past_date = today - relativedelta(months=i)
            if year and past_date.year != year:
                return None if (past_date > today and not time) else specified_months.append(f"{past_date.year}-{past_date.month:02}")
            if not year and past_date > today and not time:
                past_date = past_date.replace(year=today.year - 1)
            specified_months.append(f"{past_date.year}-{past_date.month:02}")
        return sorted(specified_months)

    relative_months = {
        '다다음달': 2, '이번달': 0, '다음달': 1, '저저번달': -2, '저번달': -1,
        '연초': -today.month + 1,  # 1월까지의 거리
        '연말': 12 - today.month  # 12월까지의 거리
    }

    for key, offset in relative_months.items():
        if key in match:
            if key in ['다음달', '다다음달'] and not time:
                return None

            specified_month = (datetime(year if year else target_year, today.month, 1) + relativedelta(months=offset)).date()
            if specified_month > today and not time:
                specified_month -= relativedelta(years=1)
                if year is not None and specified_month.year != year:
                    return None

            return [specified_month.strftime("%Y-%m")]

    # 분기 표현 처리
    quarter_match = re.search(r'(\d)분기', match)
    if quarter_match:
        quarter = int(quarter_match.group(1))
        start_month, end_month, end_day = [(1, 3, 31), (4, 6, 30), (7, 9, 30), (10, 12, 31)][quarter - 1]
        start_date, end_date = datetime(target_year, start_month, 1).date(), datetime(target_year, end_month, end_day).date()

        if not year and not time:
            start_date, end_date = (start_date.replace(year=target_year - 1), end_date.replace(year=target_year - 1)) if today < start_date else (start_date, min(end_date, today))

        return [(start_date + relativedelta(months=i)).strftime("%Y-%m") for i in range((end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1)]

    return None

def convert_relative_weeks(match: str, time: bool = False, year: Optional[int] = None, month: Optional[int] = None) -> Union[List[str], None]:
    today = datetime.now().date()

    process_year = year if year else today.year

    process_month = [month] if month else (list(range(1, 13)) if year else [today.month])

    date_list = []

    for month in process_month:
        first_day_of_month = datetime(process_year, month, 1).date()
        last_day_of_month = (first_day_of_month + relativedelta(months=1)) - timedelta(days=1)
        start_of_week = today - timedelta(days=today.weekday())
        week_keys = ["첫째 주", "둘째 주", "셋째 주", "넷째 주", "마지막 주", "저저번 주", "지난 주", "이번 주", "다음 주", "다다음 주"]

        for week in week_keys:
            if week in match:
                if week == "첫째 주":
                    start_date = first_day_of_month
                    end_date = start_date + timedelta(days=(6 - start_date.weekday())) if start_date.weekday() != 6 else start_date
                elif week == "둘째 주":
                    start_date = first_day_of_month + timedelta(days=7 - first_day_of_month.weekday())
                    end_date = start_date + timedelta(days=6)
                elif week == "셋째 주":
                    start_date = first_day_of_month + timedelta(days=14 - first_day_of_month.weekday())
                    end_date = start_date + timedelta(days=6)
                elif week == "넷째 주":
                    start_date = first_day_of_month + timedelta(days=21 - first_day_of_month.weekday())
                    end_date = start_date + timedelta(days=6)
                elif week == "마지막 주":
                    end_date = last_day_of_month
                    start_date = end_date - timedelta(days=(end_date.weekday() + 1))
                elif week == "저저번 주":
                    start_date = start_of_week - timedelta(weeks=2)
                    end_date = start_date + timedelta(days=6)
                elif week == "지난 주":
                    start_date = start_of_week - timedelta(weeks=1)
                    end_date = start_date + timedelta(days=6)
                elif week == "이번 주":
                    start_date = start_of_week
                    end_date = start_of_week + timedelta(days=6)
                elif week == "다음 주":
                    start_date = start_of_week + timedelta(weeks=1)
                    end_date = start_date + timedelta(days=6)
                elif week == "다다음 주":
                    start_date = start_of_week + timedelta(weeks=2)
                    end_date = start_date + timedelta(days=6)
                current_date = start_date

                while current_date <= end_date:

                    if time:
                        date_list.append(current_date.strftime('%Y-%m-%d'))
                    else:
                        if week in ["다음 주", "다다음 주"]:
                            return None

                        if end_date <= today:
                            date_list.append(current_date.strftime('%Y-%m-%d'))
                        elif current_date > today:
                            start_date -= relativedelta(months=1)
                            end_date -= relativedelta(months=1)
                            current_date = start_date

                            while current_date <= end_date:
                                if current_date <= today:
                                    date_list.append(current_date.strftime('%Y-%m-%d'))
                                current_date += timedelta(days=1)
                            break
                        elif current_date <= today and today <= end_date:
                            while current_date <= today:
                                date_list.append(current_date.strftime('%Y-%m-%d'))
                                current_date += timedelta(days=1)
                            break
                    current_date += timedelta(days=1)

    if date_list:
        date_list = sorted(date_list)
        first_date = datetime.strptime(date_list[0], '%Y-%m-%d').date()
        last_date = datetime.strptime(date_list[-1], '%Y-%m-%d').date()

        if (year or month) and (first_date.year != process_year or first_date.month not in process_month):
            return None

    return date_list

def convert_relative_days(match: str, time: bool = False, year: Optional[int] = None, month: Optional[int] = None, week: Optional[List[str]] = None) -> Optional[List[str]]:
    """
    입력된 날짜 표현을 분석하여 실제 날짜로 변환하는 함수.
    """
    today = datetime.now().date()

    # 특정 날짜가 입력이 안되면 default를 올해, 이번 달, 이번 주로 설정
    processed_year = int(year) if year else today.year
    processed_month = int(month) if month else today.month

    processed_week = [today - timedelta(days=today.weekday()) + timedelta(days=i) for i in range(7)]

    if '보름' in match:
        # 연도와 월 설정
        target_year = year if year else today.year
        target_months = [month] if month else ([today.month] if not year else range(1, 13))

        # 각 월의 15일을 계산하고, 미래 날짜 처리
        dates = [datetime(target_year, m, 15).date() for m in target_months]
        dates = [d for d in dates if time or d <= today]

        return [d.strftime('%Y-%m-%d') for d in dates] if dates else None


    # 기존의 'N일 전', 'N일 후', 'N일' 형태의 날짜 처리
    relative_day_pattern = re.search(r'(\d+)일(?: (전|후))?', match)
    if relative_day_pattern:
        days = int(relative_day_pattern.group(1))
        direction = relative_day_pattern.group(2).strip() if relative_day_pattern.group(2) else None
        # 날짜 계산 로직
        if direction == '전':
            target_date = today - timedelta(days=days)
        elif direction == '후':
            target_date = today + timedelta(days=days)
        else:
            # 일(day)만 주어진 경우
            input_day = days
            input_month = processed_month
            target_year = processed_year

            while True:
                try:
                    target_date = datetime(target_year, input_month, input_day).date()
                    break  # 날짜 생성에 성공하면 루프 탈출
                except ValueError:
                    # 날짜가 유효하지 않을 경우 월이나 연도를 조정
                    if input_month > 1:
                        input_month -= 1
                    else:
                        input_month = 12
                        target_year -= 1
                    # 만약 너무 오래 반복하면 None 반환
                    if target_year < 2000:  # 임의의 기준 연도 설정
                        return None

            # 미래 날짜를 시간 플래그에 따라 조정
            if not time and target_date > today:
                if not year and month:
                    target_year -= 1
                    try:
                        target_date = datetime(target_year, input_month, input_day).date()
                    except ValueError:
                        return None

        return [target_date.strftime('%Y-%m-%d')] if target_date else None

    # '평일', '주말' 또는 특정 요일 처리
    days_ahead = {'월요일': 0, '화요일': 1, '수요일': 2,
                  '목요일': 3, '금요일': 4, '토요일': 5, '일요일': 6, '평일': 7, '주말': 8}

    if any(weekday in match for weekday in days_ahead):
        def filter_dates(dates, is_weekday):
            # 평일 또는 주말 필터링, 미래 날짜는 time이 False일 때만 제거
            filtered = [date for date in dates if (date.weekday() < 5) == is_weekday and (time or date <= today)]
            return [date.strftime('%Y-%m-%d') for date in filtered] or None

        # 1. 주어진 주의 날짜들이 있는 경우 (week 인자가 주어짐)
        if week:
            dates = [datetime.strptime(date, '%Y-%m-%d').date() for date in week]

        # 2. 연도만 주어진 경우 (year는 있고, month는 없는 경우)
        elif year and not month:
            for weekday, idx in days_ahead.items():
                if weekday in match:
                    first = datetime(processed_year, 1, 1).date()
                    first += timedelta(days=(idx - first.weekday() + 7) % 7)
                    last = datetime(processed_year, 12, 31).date()
                    return [first.strftime('%Y-%m-%d')] + [(first + timedelta(weeks=i)).strftime('%Y-%m-%d')
                                                          for i in range(1, (last - first).days // 7 + 1)
                                                          if time or first + timedelta(weeks=i) <= today]

        # 3. 연도와 월이 모두 주어진 경우 (year와 month가 모두 있음)
        elif year and month:
            start_of_month = datetime(processed_year, processed_month, 1).date()
            end_of_month = (start_of_month + relativedelta(months=1)) - timedelta(days=1)
            dates = [start_of_month + timedelta(days=i) for i in range((end_of_month - start_of_month).days + 1)]

        # 4. 월만 주어진 경우 (year가 없고 month만 있는 경우)
        elif month:
            start_of_month = datetime(today.year, month, 1).date()
            end_of_month = (start_of_month + relativedelta(months=1)) - timedelta(days=1)
            dates = [start_of_month + timedelta(days=i) for i in range((end_of_month - start_of_month).days + 1)]

        # 5. 아무런 정보가 주어지지 않은 경우: 이번 주의 날짜 조회
        else:
            start_of_week = today - timedelta(days=today.weekday())
            dates = [start_of_week + timedelta(days=i) for i in range(7)]

        # 결과 생성
        if '평일' in match:
            result = filter_dates(dates, is_weekday=True)
        elif '주말' in match:
            result = filter_dates(dates, is_weekday=False)
        else:
            # 특정 요일에 해당하는 모든 날짜 추출
            matching_weekdays = []
            for weekday in days_ahead:
                if weekday in match:
                    weekday_index = days_ahead[weekday]
                    matching_dates = [date.strftime('%Y-%m-%d') for date in dates
                                      if date.weekday() == weekday_index and (time or date <= today)]
                    matching_weekdays.extend(matching_dates)
            result = matching_weekdays or None

        return result

    # 월별 기간 표현 처리: "월초", "중순", "월말"
    if any(period in match for period in ['월초', '중순', '월말']):
        target_month = datetime(processed_year, processed_month, 1).date()

        periods = {
            '월초': (0, 9),
            '중순': (10, 19),
            '월말': (20, (target_month + relativedelta(months=1) - timedelta(days=1)).day)
        }
        start_offset, end_offset = next((s, e) for p, (s, e) in periods.items() if p in match)
        start_of_period = target_month + timedelta(days=start_offset)
        end_of_period = target_month + timedelta(days=end_offset) if '월말' not in match else (target_month + relativedelta(months=1) - timedelta(days=1))

        if not time and start_of_period > today:
            if not month:
                start_of_period -= relativedelta(months=1)
                end_of_period -= relativedelta(months=1)
            elif not year:
                start_of_period -= relativedelta(years=1)
                end_of_period -= relativedelta(years=1)

        # 미래 데이터 처리
        if not time and start_of_period <= today < end_of_period:
            end_of_period = min(end_of_period, today)

        # 모든 날짜 생성
        all_dates = [(start_of_period + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_of_period - start_of_period).days + 1)]
        return all_dates

    # 표현을 못 찾음
    return None

def convert_date_expression(text: str, time: bool=False) -> Optional[List[str]]:
    """
    주어진 텍스트에서 날짜 표현을 찾아 실제 날짜로 변환합니다.

    Args:
    - text (str): 입력 텍스트

    Returns:
    - list: 변환된 날짜 리스트 (문자열 형식 'YYYY-MM-DD')
    """
    today = datetime.now().date()  # 현재 날짜 설정
    date_expressions = ['오늘', '내일', '모레', '글피', '어제', '엊그제', '최근']
    converted_dates = []

    # 날짜 표현이 텍스트에 포함되어 있는지 확인하고 변환
    for expr in date_expressions:
        if expr in text:
            if expr == '오늘':
                converted_dates.append(today.strftime('%Y-%m-%d'))
            elif expr == '내일':
                if time:
                    converted_dates.append((today + timedelta(days=1)).strftime('%Y-%m-%d'))
                else:
                    return  None
            elif expr == '모레':
                if time:
                    converted_dates.append((today + timedelta(days=2)).strftime('%Y-%m-%d'))
                else:
                    return None
            elif expr == '글피':
                if time:
                    converted_dates.append((today + timedelta(days=3)).strftime('%Y-%m-%d'))
                else:
                    return None
            elif expr == '어제':
                converted_dates.append((today - timedelta(days=1)).strftime('%Y-%m-%d'))
            elif expr == '엊그제':
                converted_dates.append((today - timedelta(days=2)).strftime('%Y-%m-%d'))
            elif expr == '최근':
                # 최근 7일 계산
                converted_dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
            return converted_dates

    return None

def extract_date_info(text, time=False):
    """
    주어진 텍스트에서 날짜 정보를 추출하여 실제 날짜로 변환합니다.

    Args:
    - text (str): 입력 텍스트
    - time (bool): 미래 날짜를 포함할지 여부를 결정하는 플래그

    Returns:
    - list: 변환된 날짜 리스트 (문자열 형식 'YYYY-MM-DD')
    """

    # 텍스트 패턴 치환 진행
    text = replace_with_pattern_keys(text)

    # convert_date_expression으로부터 변환된 날짜가 있으면 반환
    converted_dates = convert_date_expression(text, time=time)

    # 미래 날짜 표현에 대해서만 time=False일 경우 None 반환
    future_expressions = ['내일', '모레', '글피', '다음달', '내년', '내휴냔']
    if not time and any(expr in text for expr in future_expressions):
        return None

    if converted_dates:
        return converted_dates

    year, month, month_result, week, result = None, None, None, None, None

    # 상대적 연도, 월, 주, 요일 패턴 목록
    year_patterns = [pattern for sublist in date_patterns['상대적 연도'].values() for pattern in sublist]
    month_patterns = [pattern for sublist in date_patterns['상대적 월'].values() for pattern in sublist]
    week_patterns = [pattern for sublist in date_patterns['주 관련 상대적 날짜'].values() for pattern in sublist]
    day_patterns = [pattern for sublist in date_patterns['요일'].values() for pattern in sublist]

    patterns_to_check = {
        "year": (year_patterns + [r'\b(\d{2,4}년)\b'], convert_relative_years, {'time': time}),
        "month": (month_patterns + [r'\b(\d{1,2}개월)\b', r'\b\d{1}분기\b'], convert_relative_months, {'time': time, 'year': year}),
        "week": (week_patterns, convert_relative_weeks, {'time': time, 'year': year, 'month': month}),
        "day": (day_patterns + [r'\b(\d{1,2})일\b'], convert_relative_days, {'time': time, 'year': year, 'month': month, 'week': week})
    }

    # 패턴을 순회하며 일치하는 것을 변환
    for key, (patterns, convert_function, kwargs) in patterns_to_check.items():
        for pattern in patterns:
            if re.search(pattern, text):
                if key == "year" and convert_function:
                    year_result = convert_function(text, **kwargs)
                    if year_result:
                        year = int(year_result[0])
                        patterns_to_check["month"][2]['year'] = year
                elif key == "month" and convert_function:
                    month_result = convert_function(text, **patterns_to_check["month"][2])
                    if month_result:
                        month = month_result
                elif key == "week":
                    # year와 month가 None일 때는 None으로 전달
                    kwargs['year'] = year
                    kwargs['month'] = int(month[0].split('-')[1]) if month else None
                    week = convert_function(text, **kwargs)
                    result = week
                elif key == "day":
                    kwargs['year'] = year
                    kwargs['month'] = int(month[0].split('-')[1]) if month else None
                    kwargs['week'] = week
                    result = convert_function(text, **kwargs)
                break


    final_result = result or week or month_result or ([str(year)] if year else None)

    if not (final_result and final_result[0]) or (
        not time and (any(expr in text for expr in future_expressions))):
        return None

    date_str = final_result[0]
    final_date = datetime.strptime(date_str, '%Y' if len(date_str) == 4 else '%Y-%m' if len(date_str) == 7 else '%Y-%m-%d').date()

    return None if not time and final_date > datetime.now().date() else final_result

# 각 패턴 그룹 정의
date_patterns: Dict[str, Dict[str, List[str]]] = {
    "상대적 날짜": {
        "최근": [r"\b최근|요즘|근래|최신\b"],
        "오늘": [r'\b오늘|금일|지금\b'],
        "내일": [r'\b내일|익일\b'],
        "모레": [r'\b모레|내일모레|모래\b'],
        "글피": [r'\b글피\b'],
        "어제": [r'\b어제|어저께|작일\b'],
        "엊그제": [r'\b엊그제|엊그저께|그제|그저께\b']
    },
    "상대적 연도": {
        "재작년": [r'\b재작년\b'],
        "작년": [r'\b작년\b'],
        "내년": [r'\b내년\b'],
        "올해": [r'\b올해|현재 연도\b'],
        "내휴냔": [r'\b내후년|내휴냔\b']
    },
    "상대적 월": {
        "11월": [r'\b11월\b'],
        "12월": [r'\b12월\b'],
        "1월": [r'\b1월\b'],
        "2월": [r'\b2월\b'],
        "3월": [r'\b3월\b'],
        "4월": [r'\b4월\b'],
        "5월": [r'\b5월\b'],
        "6월": [r'\b6월\b'],
        "7월": [r'\b7월\b'],
        "8월": [r'\b8월\b'],
        "9월": [r'\b9월\b'],
        "10월": [r'\b10월\b'],
        "다다음달": [r'\b다다음달\b'],
        "저저번달": [r'\b저저번달\b'],
        "다음달": [r'\b다음 달|다음달\b'],
        "저번달": [r'\b저번 달|지난 달|저번달|지난달\b'],
        "이번달": [r'\b이번달|이번 달|금월\b'],
        "연말": [r'\b연말\b'],
        "연초": [r'\b연초\b']
    },
    "주 관련 상대적 날짜": {
        "첫째 주": [r'\b첫째 주|첫쨰 주|첫째주|첫쨰주|첫쨰 주|첫번째 주|첫주|1주차'],
        "둘째 주": [r'\b둘째주|둘쨰주|둘쨰 주|둘째 주|두째주|두번째 주|2주차|두째 주'],
        "셋째 주": [r'\b셋째주|세번째 주|3주차|셋째 주'],
        "넷째 주": [r'\b넷째주|네번째 주|4주차'],
        "저저번 주": [r'\b저저번주\b'],
        "다다음 주": [r'\b다다음주\b'],
        "마지막 주": [r'\b마지막|다섯번째 주|마지막 주|5주차|다섯째 주'],
        "지난 주": [r'\b지난주|저번주|지난 주|저번 주\b'],
        "이번 주": [r'\b이번주|이번 주\b'],
        "다음 주": [r'\b다음주|다음 주\b']
    },
    "요일": {
        "월요일": [r'\b월요일\b'],
        "화요일": [r'\b화요일\b'],
        "수요일": [r'\b수요일\b'],
        "목요일": [r'\b목요일\b'],
        "금요일": [r'\b금요일\b'],
        "토요일": [r'\b토요일\b'],
        "일요일": [r'\b일요일\b'],
        "평일": [r'\b평일|평일에\b'],
        "주말": [r'\b주말|주말에\b'],
        "중순": [r'\b중순\b'],
        "보름": [r'\b보름\b'],
        "월말": [r'\b월말\b'],
        "월초": [r'\b월초\b']
    }
}

def replace_with_pattern_keys(text: str) -> str:
    """
    텍스트에서 날짜 표현을 해당 키로 치환합니다.

    Args:
    - text (str): 입력 텍스트

    Returns:
    - str: 변환된 텍스트
    """
    # 패턴 그룹을 순회하며, 매칭되는 부분을 키로 치환
    for group_name, patterns in date_patterns.items():
        for key, regex_list in patterns.items():
            for regex in regex_list:
                text = re.sub(regex, key, text)

    return text

def extract_date_info(text, time=False):
    """
    주어진 텍스트에서 날짜 정보를 추출하여 실제 날짜로 변환합니다.

    Args:
    - text (str): 입력 텍스트
    - time (bool): 미래 날짜를 포함할지 여부를 결정하는 플래그

    Returns:
    - list: 변환된 날짜 리스트 (문자열 형식 'YYYY-MM-DD')
    """

    # 텍스트 패턴 치환 진행
    text = replace_with_pattern_keys(text)

    # convert_date_expression으로부터 변환된 날짜가 있으면 반환
    converted_dates = convert_date_expression(text, time=time)

    # 미래 날짜 표현에 대해서만 time=False일 경우 None 반환
    future_expressions = ['내일', '모레', '글피', '다음달', '내년', '내휴냔']
    if not time and any(expr in text for expr in future_expressions):
        return None

    if converted_dates:
        return converted_dates

    year, month, month_result, week, result = None, None, None, None, None

    # 상대적 연도, 월, 주, 요일 패턴 목록
    year_patterns = [pattern for sublist in date_patterns['상대적 연도'].values() for pattern in sublist]
    month_patterns = [pattern for sublist in date_patterns['상대적 월'].values() for pattern in sublist]
    week_patterns = [pattern for sublist in date_patterns['주 관련 상대적 날짜'].values() for pattern in sublist]
    day_patterns = [pattern for sublist in date_patterns['요일'].values() for pattern in sublist]

    patterns_to_check = {
        "year": (year_patterns + [r'\b(\d{2,4}년)\b'], convert_relative_years, {'time': time}),
        "month": (month_patterns + [r'\b(\d{1,2}개월)\b', r'\b\d{1}분기\b'], convert_relative_months, {'time': time, 'year': year}),
        "week": (week_patterns, convert_relative_weeks, {'time': time, 'year': year, 'month': month}),
        "day": (day_patterns + [r'\b(\d{1,2})일\b'], convert_relative_days, {'time': time, 'year': year, 'month': month, 'week': week})
    }

    # 패턴을 순회하며 일치하는 것을 변환
    for key, (patterns, convert_function, kwargs) in patterns_to_check.items():
        for pattern in patterns:
            if re.search(pattern, text):
                if key == "year" and convert_function:
                    year_result = convert_function(text, **kwargs)
                    if year_result:
                        year = int(year_result[0])
                        patterns_to_check["month"][2]['year'] = year
                elif key == "month" and convert_function:
                    month_result = convert_function(text, **patterns_to_check["month"][2])
                    if month_result:
                        month = month_result
                elif key == "week":
                    # year와 month가 None일 때는 None으로 전달
                    kwargs['year'] = year
                    kwargs['month'] = int(month[0].split('-')[1]) if month else None
                    week = convert_function(text, **kwargs)
                    result = week
                elif key == "day":
                    kwargs['year'] = year
                    kwargs['month'] = int(month[0].split('-')[1]) if month else None
                    kwargs['week'] = week
                    result = convert_function(text, **kwargs)
                break


    final_result = result or week or month_result or ([str(year)] if year else None)

    if not (final_result and final_result[0]) or (
        not time and (any(expr in text for expr in future_expressions))):
        return None

    date_str = final_result[0]
    final_date = datetime.strptime(date_str, '%Y' if len(date_str) == 4 else '%Y-%m' if len(date_str) == 7 else '%Y-%m-%d').date()

    return None if not time and final_date > datetime.now().date() else final_result

def check_conjunction_and_particle_with_kkma(text: str) -> bool:
    """
    텍스트에서 특정 조사나 접속사가 포함되어 있는지 확인합니다.

    Args:
    - text (str): 입력 텍스트

    Returns:
    - bool: 조건에 맞는 조사나 접속사가 포함되어 있으면 True, 그렇지 않으면 False
    """
    # KKMA로 품사 태깅된 리스트
    kkma_tagged = kkma.pos(text)

    # 형태소를 하나로 결합하여 원래의 단어를 복원
    combined_text = ''.join([word for word, pos in kkma_tagged])

    # 타겟 조사 및 접속사 집합
    target_words = {'과', '이랑', '그리고', '에서', '부터', '까지', '와', '별', '마다'}

    # 결합된 형태소들이 '와'로 해석될 수 있는지 확인
    if combined_text in target_words:
        return True

    # 분리된 형태소가 '오'와 '아'로 나온 경우 '와'로 결합하여 처리
    if ('오', 'VA') in kkma_tagged and ('아', 'ECS') in kkma_tagged:
        return True

    # 유효한 품사 태그 집합
    valid_tags = {'XSN', 'VA', 'ECS', 'VV', 'MAC', 'JKS', 'JC', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'JX', 'JKM', 'MAJ', 'NNB', 'NNG'}

    # 태그된 텍스트에서 조건 확인
    for word, pos in kkma_tagged:
        if word in target_words and pos in valid_tags:
            return True

    return False

def get_all_dates_between(start_date_str, end_date_str, time=False):
    """
    주어진 두 날짜 사이의 모든 날짜를 반환합니다.

    Args:
    - start_date_str (str): 시작 날짜 문자열 (YYYY, YYYY-MM, YYYY-MM-DD 형식 가능)
    - end_date_str (str): 종료 날짜 문자열 (YYYY, YYYY-MM, YYYY-MM-DD 형식 가능)
    - time (bool): True면 미래 날짜 포함, False면 현재 날짜까지만 포함

    Returns:
    - list: 두 날짜 사이의 모든 날짜 목록
    """
    today = datetime.now().date()

    def parse_date(date_str, is_start=True):
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
            try:
                date = datetime.strptime(date_str.strip(), fmt)
                if fmt == "%Y":
                    return date.replace(month=1, day=1) if is_start else date.replace(month=12, day=31)
                elif fmt == "%Y-%m":
                    return date.replace(day=1) if is_start else (date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                return date
            except ValueError:
                continue
        return None

    # 시작 날짜와 종료 날짜 파싱
    start_date, end_date = parse_date(start_date_str, True), parse_date(end_date_str, False)

    if not start_date or not end_date:
        return None

    # 시작 날짜와 종료 날짜 사이의 모든 날짜 생성
    return [(start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range((end_date - start_date).days + 1)
            if time or (start_date + timedelta(days=i)).date() <= today]

def split_and_return_periods(text: str, time: bool = False) -> List[str]:
    today = datetime.now().date()

    weekday_map = {"월요일": 0, "화요일": 1, "수요일": 2, "목요일": 3, "금요일": 4, "토요일": 5, "일요일": 6}

    # 정규식 패턴 정의
    patterns = {
        'range': r"(.*?)\s*(에서|부터)\s*(.*)",
        'conjunction': r"(\S+)\s?(과|이랑|그리고|와)\s?(\S+)",
        'until': r"(.*?)\s*(까지)",
        'frequency': r"(월요일|화요일|수요일|목요일|금요일|토요일|일요일|평일|주말)?\s*(별|마다)",
        'unit': r"\s*(일|주|월|분기|년|연도)"
    }

    # match_4: "요일마다", "평일마다", "주말마다", "별", "마다"
    freq_match = re.search(patterns['frequency'], text)

    if freq_match and check_conjunction_and_particle_with_kkma(freq_match.group(2)):
        period_type, freq = freq_match.groups()

        if period_type in weekday_map:
            target_weekday = weekday_map[period_type]
            return sorted([
                (today - timedelta(days=i)).strftime('%Y-%m-%d')
                for i in range(1, 30) if (today - timedelta(days=i)).weekday() == target_weekday
            ][:3])
        elif period_type in ["평일", "주말"]:
            date_list, weeks = [], 0
            while weeks < 3:
                week_start = today - timedelta(days=today.weekday()) - timedelta(weeks=weeks)
                if period_type == "평일":
                    date_list += [(week_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]
                else:
                    date_list += [(week_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5, 7)]
                weeks += 1
            return sorted(set(date_list))
        else:
            unit_match = re.search(patterns['unit'], text)
            unit = unit_match.group(1) if unit_match else None

            if unit == "일":
                return [ (today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7) ]
            elif unit == "주":
                return sorted({ (today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(21) })
            elif unit == "월":
                return sorted({ f"{(today - relativedelta(months=i)).year}-{(today - relativedelta(months=i)).month:02d}" for i in range(3) })
            elif unit == "분기":
                return sorted({ f"{(today - relativedelta(months=i)).year}-{(today - relativedelta(months=i)).month:02d}" for i in range(12) })
            elif unit in ["년", "연도"]:
                return sorted({ f"{today.year - i}" for i in range(3) })

    # match_1: "에서", "부터"
    range_match = re.search(patterns['range'], text)

    if range_match and check_conjunction_and_particle_with_kkma(range_match.group(2)):
        start_dates = extract_date_info(range_match.group(1).strip(), time)
        end_dates = extract_date_info(range_match.group(3).strip(), time)

        if start_dates and end_dates:
            all_dates = sorted(get_all_dates_between(start_dates[0], end_dates[-1], time))
            return all_dates
        return start_dates or end_dates or None

    # match_2: "과", "이랑", "그리고", "와"
    conj_match = re.search(patterns['conjunction'], text)

    if conj_match and check_conjunction_and_particle_with_kkma(conj_match.group(2)):
        before, _, after = conj_match.groups()
        start_dates = extract_date_info(before.strip(), time)
        end_dates = extract_date_info(after.strip(), time)
        date = sorted(set(start_dates or []) | set(end_dates or []))
        return date if date else None

    # match_3: "까지"
    until_match = re.search(patterns['until'], text)

    if until_match and check_conjunction_and_particle_with_kkma(until_match.group(2)):
        final_dates = extract_date_info(until_match.group(1).strip(), time)
        result = []

        for d in final_dates:
            try:
                final_dt = datetime.strptime(d, "%Y-%m-%d").date()
            except ValueError:
                try:
                    final_dt = datetime.strptime(d, "%Y-%m").date().replace(day=calendar.monthrange(datetime.strptime(d, "%Y-%m").year, datetime.strptime(d, "%Y-%m").month)[1])
                except ValueError:
                    try:
                        final_dt = datetime.strptime(d, "%Y").date().replace(month=12, day=31)
                    except ValueError:
                        continue

        unit_mapping = {'일': 7, '주': 21, '월': 3, '년': 3}
        unit = next((u for u in unit_mapping if u in text), '일')
        days_delta = unit_mapping[unit]

        start = final_dt - (timedelta(days=days_delta) if unit == '주'
                            else relativedelta(months=days_delta) if unit == '월'
                            else relativedelta(years=days_delta) if unit == '년'
                            else timedelta(days=days_delta))

        return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, (final_dt - start).days + 1)]


    # 기본 날짜 추출
    try:
        result = sorted(extract_date_info(text, time))
        return result
    except Exception as e:
        return None