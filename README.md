# OpenGL 카메라와 OBJ 뷰어

컴퓨터 그래픽스 수업에서 좌표 변환부터 카메라 조작, 메쉬 렌더링까지 직접 구현한 Python 프로젝트입니다. 도형을 그리는 실습에서 시작해 마우스로 시점을 바꾸고 OBJ 모델을 살펴보는 뷰어로 확장했습니다.

## 사용 기술

Python, NumPy, PyOpenGL, GLFW, PyGLM을 사용합니다. 행렬과 카메라 상태는 Python에서 계산하고, 정점 변환과 조명은 GLSL shader에서 처리합니다.

## 구현해 간 과정

처음에는 이동·회전·크기 변환을 조합하며 좌표계와 행렬 곱의 순서를 연습했습니다. 주차별 실습에는 계층 변환, Euler 각과 회전 보간이 나뉘어 있습니다. 같은 회전이라도 표현 방법에 따라 중간 자세가 달라지는 점을 살펴볼 수 있습니다.

[main.py](main.py)에서는 카메라 조작으로 연결했습니다. 모델·시점·투영 행렬을 분리하고 마우스 입력으로 카메라 상태를 갱신합니다. Orbit은 대상을 중심으로 회전하고, pan은 시점을 평행 이동하며, zoom은 관찰 거리를 조절합니다. Grid는 공간의 기준을 보여주도록 VAO/VBO에 올립니다.

[main1.py](main1.py)에서는 OBJ의 정점·면을 읽어 삼각형으로 바꿉니다. 면마다 정점 수가 달라 triangle fan으로 분할했고, 법선과 Phong 조명으로 물체의 굴곡을 표현했습니다.

## 렌더링 구조

```text
마우스 입력 → 카메라 상태 → Model / View / Projection
OBJ 정점·면 → 삼각형 / 법선 → VAO·VBO → shader → 화면
```

카메라 계산과 메쉬 입력을 나눠 시점 문제인지 정점 데이터 문제인지 따라갈 수 있게 구성했습니다.

## 실행

OpenGL 3.3을 지원하는 화면 환경이 필요합니다.

```bash
pip install numpy PyOpenGL glfw PyGLM
python main.py
python main1.py
```

OBJ 파일은 별도로 준비합니다. 각 프로그램의 callback에서 키·마우스 동작을 확인할 수 있습니다.

## 배운 점과 남은 범위

좌표계, 카메라 기준축, 법선이 서로 맞아야 조작과 조명이 자연스럽게 연결됩니다. Triangle fan은 복잡한 오목 다각형을 일반적으로 분할하는 방법은 아닙니다. 재질 시스템이나 물리 기반 렌더링까지 구현한 범용 엔진은 아닙니다.

[구현 노트](docs/implementation.md) · [소스 목록](docs/source-index.csv) · [출처](ATTRIBUTION.md)
