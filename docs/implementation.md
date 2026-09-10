# 화면이 만들어지는 과정

`main.py`는 카메라 상태에서 Model·View·Projection 행렬을 계산하고 MVP uniform으로 정점에 적용합니다. 마우스 callback이 orbit·pan·zoom 상태를 갱신하고 grid 정점은 VAO/VBO에 저장합니다.

`main1.py`는 OBJ 면을 triangle fan으로 나눈 뒤 법선과 조명 shader를 연결합니다. 일반적인 오목 다각형 분할이나 재질·물리 기반 렌더링까지 구현한 엔진은 아닙니다. 주차별 실습에서는 좌표계·계층 변환·회전 보간을 비교할 수 있습니다.
