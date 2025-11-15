"""
Supabase Client
"""

from supabase import create_client, Client
from app.config import settings

# Supabase 클라이언트 초기화
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY  # service_role_key 사용하여 모든 권한 획득
)


def get_supabase() -> Client:
    """Supabase 클라이언트 의존성"""
    return supabase
