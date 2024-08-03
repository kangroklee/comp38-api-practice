from django.shortcuts import render
from rest_framework.views import APIView
from pathlib import Path
import json, os
from rest_framework.response import Response
from rest_framework import status
import hmac, hashlib
import base64
from decouple import config

secret_key = base64.b64decode(config("B64_HMAC_SECRET"))

BASE_DIR = Path(__file__).parent.resolve()
members_json = os.path.join(BASE_DIR, 'members.json')

with open(members_json) as f:
    members = json.load(f)

class VerifyMemberAPIView(APIView):
    def get(self, request, student_id):
        for member in members:
            if member['student_id'] == student_id:
                # HMAC 해시 생성
                msg_str = student_id
                hash = hmac.new(secret_key, msg=msg_str.encode(), digestmod=hashlib.sha256).digest()
                base64_hash = base64.b64encode(hash).decode()

                return Response({"success": "콤프 38기 백엔드가 맞습니다!", "data": member, "hash": base64_hash}, status=status.HTTP_200_OK)
        return Response({"error": "해당하는 학번의 콤프 38기 백엔드를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, student_id):
        hash = request.data.get('hash')
        for member in members:
            if member['student_id'] == str(student_id):
                # 해시 값 검증
                msg_str = student_id
                expected_hash = hmac.new(secret_key, msg=msg_str.encode(), digestmod=hashlib.sha256).digest()
                base64_expected_hash = base64.b64encode(expected_hash).decode()
                if hmac.compare_digest(hash, base64_expected_hash):
                    member['homework_complete'] = True
                    try:
                        with open(members_json, 'w') as f:
                            json.dump(members, f, indent=4, ensure_ascii=False)
                    except:
                        return Response({"error": "서버 오류입니다. 잠시 후 다시 시도해주세요."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    return Response({"success": "과제가 정상적으로 완료 처리되었습니다."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "유효하지 않은 해시값입니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "해당하는 학번의 콤프 38기 백엔드를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        