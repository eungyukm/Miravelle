# Python Code Convention

Python 코드를 작성할 때 가독성과 유지보수를 위해 일관된 코딩 스타일을 따르는 것이 중요합니다. Python에서는 **PEP 8**이 공식 코딩 스타일 가이드로 권장됩니다.

---

## 주요 규칙

### 1. **코드 레이아웃**
- **들여쓰기**: 4개의 스페이스를 사용합니다.

  ```python
  def example_function():
      print("Hello, World!")
  ```

- **최대 줄 길이**: 79자 이하를 권장합니다. (긴 문자열은 괄호를 사용하여 여러 줄로 나눕니다.)

  ```python
  text = (
      "This is an example of a long string that should be split "
      "into multiple lines for better readability."
  )
  ```

- **빈 줄**: 클래스와 함수 사이에 두 줄을 추가하며, 메서드 사이에는 한 줄을 추가합니다.

  ```python
  class MyClass:

      def method_one(self):
          pass

      def method_two(self):
          pass
  ```

---

### 2. **임포트**
- 임포트는 항상 파일의 맨 위에 위치시키며, 세 가지 그룹으로 나누어 작성합니다:
  1. 표준 라이브러리
  2. 서드파티 라이브러리
  3. 로컬 모듈

- 각 그룹 사이에 한 줄을 추가합니다.

  ```python
  import os
  import sys

  import requests

  from myproject import mymodule
  ```

---

### 3. **네이밍 규칙**
- **변수 및 함수**: `snake_case` 사용

  ```python
  def calculate_area(radius):
      return 3.14 * radius ** 2
  ```

- **클래스**: `PascalCase` 사용

  ```python
  class MyClass:
      pass
  ```

- **상수**: 모두 대문자, 단어는 밑줄로 구분

  ```python
  MAX_CONNECTIONS = 10
  ```

---

### 4. **문자열 사용**
- 큰따옴표(`"`)를 사용합니다.

  ```python
  message = "Hello, World!"
  ```

- 여러 줄 문자열은 삼중 따옴표를 사용합니다.

  ```python
  long_text = """This is an example
  of a multi-line string."""
  ```

---

### 5. **주석**
- **주석 작성**: 코드와 관련된 중요한 정보를 설명합니다.
- **한 줄 주석**: `#` 뒤에 작성

  ```python
  # 이 함수는 원의 면적을 계산합니다.
  def calculate_area(radius):
      return 3.14 * radius ** 2
  ```

- **Docstring**: 함수나 클래스의 사용법을 설명하는 데 사용

  ```python
  def greet(name):
      """이 함수는 사용자를 환영합니다.

      Args:
          name (str): 사용자의 이름

      Returns:
          str: 환영 메시지
      """
      return f"Hello, {name}!"
  ```

---

### 6. **예외 처리**
- 명시적으로 예외를 처리하며, 구체적인 예외 클래스를 사용합니다.

  ```python
  try:
      result = 10 / 0
  except ZeroDivisionError:
      print("Cannot divide by zero!")
  ```

---

### 7. **리스트와 딕셔너리 축약**
- 리스트와 딕셔너리를 생성할 때 축약 문법을 활용합니다.

  ```python
  squares = [x ** 2 for x in range(10)]
  student_grades = {student: grade for student, grade in zip(students, grades)}
  ```

---

### 8. **Type Hinting**
- 타입 힌트를 사용하여 코드 가독성과 유지보수성을 향상시킵니다.

  ```python
  def add_numbers(a: int, b: int) -> int:
      return a + b
  ```

---

## 참고 자료
- [PEP 8 - Python Style Guide](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---
